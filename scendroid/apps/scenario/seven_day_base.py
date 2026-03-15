"""
Seven-Day Scenario Evaluator Base Class

Seven-day scenario evaluator base class, extending BaseScenarioEvaluator, supporting:
1. Multi-day task management
2. Cross-day status persistence
3. User preference management
4. Reference parsing
5. Conflict detection
"""

from absl import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
import random

from scendroid.apps.scenario.base import BaseScenarioEvaluator
from scendroid.apps.scenario.extended_context import ExtendedScenarioContext
from scendroid.apps.scenario.preference_store import PreferenceStore
from scendroid.apps.scenario.reference_resolver import ReferenceResolver
from scendroid.apps.scenario import utils as scenario_utils


@dataclass
class DayConfig:
    """Single-day configuration"""
    day_idx: int                     # day index (0-6)
    date: str                        # Date in "YYYY-MM-DD" format
    day_name: str                    # Day name, e.g., "Monday"
    subtask_indices: List[int] = field(default_factory=list)  # List of subtask indices for this day
    initialized: bool = False        # Whether initialized


@dataclass 
class SevenDaySubtask:
    """
    Seven-day scenario subtask configuration
    
    Extends the base subtask, adding:
    - day_idx: Associated day number
    - task_id: Task ID (e.g., "W1-03")
    - tags: Capability tags ([REF], [PRE], [CON], [ALT], [AGG], [STR], [CAU])
    - reference_params: Parameters requiring reference parsing
    - preference_check: Preference checks to perform
    """
    subtask_id: int
    day_idx: int
    task_id: str                     # Format: "W1-03"
    evaluator_name: str
    params: Dict[str, Any]
    
    weight: float = 1.0
    narration: str = ""
    user_instruction: str = ""
    reset_user_instruction: str = ""  # Reset-mode-specific instruction (self-contained, no cross-task references required)
    time: str = None                 # Time in "HH:MM" format
    max_steps: int = 20
    on_fail: str = "continue"
    requires_answer: bool = False
    
    # Seven-day scenario-specific fields
    tags: List[str] = field(default_factory=list)  # [REF], [PRE], [CON], [ALT], [AGG], [STR], [CAU]
    reference_params: Dict[str, str] = field(default_factory=dict)  # Parameters requiring reference parsing
    preference_check: Dict[str, Any] = field(default_factory=dict)  # Preference check configuration
    context_updates: Dict[str, Any] = field(default_factory=dict)  # Updates to apply to context after task completion
    
    # Runtime status
    evaluator_instance: Any = None
    status: str = "pending"          # pending, running, completed, failed
    score: float = 0.0


class SevenDayScenarioEvaluator(BaseScenarioEvaluator):
    """
    Seven-day scenario evaluator base class
    
    core features:
    1. Managing subtasks across seven days
    2. Cross-day status persistence (ExtendedScenarioContext)
    3. User preference management (PreferenceStore)
    4. Reference parsing (ReferenceResolver)
    5. Date boundary handling
    6. Conflict detection
    
    usage:
        class MyWeekScenario(SevenDayScenarioEvaluator):
            def __init__(self, params):
                super().__init__(params)
                
                # Add subtasks for each day
                self.add_day(0, "2026-01-19", "Monday")
                self.add_seven_day_subtask(SevenDaySubtask(...))
    """
    
    # Day names
    DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                 "Friday", "Saturday", "Sunday"]
    
    def __init__(self, params: dict):
        """
        initialize 7 daysscenarioevaluator
        
        Args:
            params: scenario parameter, containing:
                - scenario_id: Scenario ID (e.g., "W")
                - name: scenarioname
                - start_date: Start date in "YYYY-MM-DD" format
                - total_max_steps: Total maximum steps (default 700)
        """
        # setupdefault value
        params.setdefault('total_max_steps', 700)  # 7 days * 100 steps/day
        
        super().__init__(params)
        
        # Replace with the extended context
        self.context = ExtendedScenarioContext()
        self.context.scenario_id = params.get('scenario_id')
        self.context.scenario_name = params.get('name', self.__class__.__name__)
        self.context.base_date = params.get('start_date', params.get('base_date'))
        
        # 7 daysconfiguration
        self.num_days = 7
        self.days: Dict[int, DayConfig] = {}
        self.current_day_idx = 0
        
        # Start date
        self.start_date = params.get('start_date', params.get('base_date', '2026-01-19'))
        
        # Preference storage
        self.preference_store = PreferenceStore()
        
        # Reference parser (latencyinitialize)
        self._reference_resolver: Optional[ReferenceResolver] = None
        
        # Seven-day subtask list (replaces the parent class's subtasks)
        self.seven_day_subtasks: List[SevenDaySubtask] = []
        
        # Callback function (called after a subtask completes)
        self.on_subtask_complete: Optional[Callable] = None
        
        # statistics
        self.stats = {
            'total_subtasks': 0,
            'completed': 0,
            'failed': 0,
            'by_day': {i: {'total': 0, 'completed': 0} for i in range(7)},
            'by_tag': {},
        }
    
    @property
    def reference_resolver(self) -> ReferenceResolver:
        """Get reference parser (latencyinitialize)"""
        if self._reference_resolver is None:
            self._reference_resolver = ReferenceResolver(self.context)
        return self._reference_resolver
    
    # ==================== Day management ====================
    
    def add_day(self, day_idx: int, date: str, day_name: str = None):
        """
        Add a day's configuration
        
        Args:
            day_idx: day index (0-6)
            date: Date in "YYYY-MM-DD" format
            day_name: Day name; if not provided, it is automatically computed
        """
        if day_name is None:
            day_name = self.DAY_NAMES[day_idx % 7]
        
        self.days[day_idx] = DayConfig(
            day_idx=day_idx,
            date=date,
            day_name=day_name,
        )
        
        # Also initialize the day status in the context
        self.context.init_day(day_idx, date, day_name)
        
        logging.info(f"📅 Added Day {day_idx + 1} ({day_name}): {date}")
    
    def get_day_config(self, day_idx: int) -> Optional[DayConfig]:
        """Get a specific day's configuration"""
        return self.days.get(day_idx)
    
    def get_current_day_config(self) -> Optional[DayConfig]:
        """Get the current day's configuration"""
        return self.days.get(self.current_day_idx)
    
    # ==================== Subtask management ====================
    
    def add_seven_day_subtask(self, subtask: SevenDaySubtask):
        """
        Add seven-day scenario subtasks
        
        Args:
            subtask: SevenDaySubtask object
        """
        # Add to list
        self.seven_day_subtasks.append(subtask)
        
        # updatedaysconfiguration
        if subtask.day_idx in self.days:
            self.days[subtask.day_idx].subtask_indices.append(
                len(self.seven_day_subtasks) - 1
            )
        
        # Update statistics
        self.stats['total_subtasks'] += 1
        self.stats['by_day'][subtask.day_idx]['total'] += 1
        
        for tag in subtask.tags:
            if tag not in self.stats['by_tag']:
                self.stats['by_tag'][tag] = {'total': 0, 'completed': 0}
            self.stats['by_tag'][tag]['total'] += 1
        
        # Also add to the parent class's subtasks (for compatibility)
        self.subtasks.append({
            'subtask_id': subtask.subtask_id,
            'evaluator_name': subtask.evaluator_name,
            'params': subtask.params,
            'weight': subtask.weight,
            'narration': subtask.narration,
            'user_instruction': subtask.user_instruction,
            'reset_user_instruction': subtask.reset_user_instruction,  # ⚡ Resetmodeinstruction
            'time': subtask.time,
            'max_steps': subtask.max_steps,
            'on_fail': subtask.on_fail,
            'requires_answer': subtask.requires_answer,
            'evaluator_instance': None,
            'status': 'pending',
            'score': 0.0,
            # Additional fields
            'day_idx': subtask.day_idx,
            'task_id': subtask.task_id,
            'tags': subtask.tags,
        })
        
        logging.info(f"Added subtask {subtask.task_id}: {subtask.evaluator_name} "
                     f"(Day {subtask.day_idx + 1}, tags: {subtask.tags})")
    
    def get_subtasks_for_day(self, day_idx: int) -> List[SevenDaySubtask]:
        """Get all subtasks for a specific day"""
        return [st for st in self.seven_day_subtasks if st.day_idx == day_idx]
    
    def get_subtask_by_task_id(self, task_id: str) -> Optional[SevenDaySubtask]:
        """Get a subtask by task ID"""
        for st in self.seven_day_subtasks:
            if st.task_id == task_id:
                return st
        return None
    
    # ==================== Convenience methods ====================
    
    def add_subtask_to_day(
        self,
        day_idx: int,
        subtask_id: int,
        task_id: str,
        evaluator_name: str,
        params: dict,
        time: str = None,
        narration: str = "",
        user_instruction: str = "",
        reset_user_instruction: str = "",
        max_steps: int = 20,
        requires_answer: bool = False,
        tags: List[str] = None,
        reference_params: Dict[str, str] = None,
        preference_check: Dict[str, Any] = None,
        context_updates: Dict[str, Any] = None,
    ):
        """
        Convenience method: Add a subtask to a specified day
        
        Args:
            day_idx: Day index number
            subtask_id: Subtask ID (global sequence number)
            task_id: Task ID (e.g., "W1-03")
            evaluator_name: evaluatorname
            params: evaluatorparameter
            time: Task time in "HH:MM" format
            narration: Narration
            user_instruction: User instruction
            max_steps: Maximum number of steps
            requires_answer: Whether an answer is required
            tags: List of capability tags
            reference_params: Parameters requiring reference parsing
            preference_check: Preference check configuration
            context_updates: Context updates after task completion
        """
        subtask = SevenDaySubtask(
            subtask_id=subtask_id,
            day_idx=day_idx,
            task_id=task_id,
            evaluator_name=evaluator_name,
            params=params,
            time=time,
            narration=narration,
            user_instruction=user_instruction,
            reset_user_instruction=reset_user_instruction,
            max_steps=max_steps,
            requires_answer=requires_answer,
            tags=tags or [],
            reference_params=reference_params or {},
            preference_check=preference_check or {},
            context_updates=context_updates or {},
        )
        
        self.add_seven_day_subtask(subtask)
    
    # ==================== initialize ====================
    
    def initialize_task(self, env):
        """
        initialize 7 daysscenario
        
        This method is called once at the start of the entire scenario
        """
        super().initialize_task(env)
        
        logging.info("=" * 70)
        logging.info(f"🗓️ Initializing 7-Day Scenario: {self.context.scenario_name}")
        logging.info(f"   Scenario ID: {self.context.scenario_id}")
        logging.info(f"   Start Date: {self.start_date}")
        logging.info(f"   Total Days: {len(self.days)}")
        logging.info(f"   Total Subtasks: {len(self.seven_day_subtasks)}")
        logging.info("=" * 70)
        
        # Print the number of tasks per day
        for day_idx in sorted(self.days.keys()):
            day_config = self.days[day_idx]
            subtask_count = len(day_config.subtask_indices)
            logging.info(f"   Day {day_idx + 1} ({day_config.day_name}): "
                         f"{subtask_count} subtasks")
    
    def initialize_day(self, day_idx: int, env):
        """
        Initialize a specific day
        
        This method is called at the start of each day
        
        Args:
            day_idx: day index (0-6)
            env: ScenDroid environment
        """
        day_config = self.days.get(day_idx)
        if day_config is None:
            raise ValueError(f"Day {day_idx} not configured")
        
        logging.info("=" * 70)
        logging.info(f"🌅 Starting Day {day_idx + 1} ({day_config.day_name}): {day_config.date}")
        logging.info(f"   Subtasks today: {len(day_config.subtask_indices)}")
        logging.info("=" * 70)
        
        # Update current days
        self.current_day_idx = day_idx
        self.context.current_day_idx = day_idx
        
        # Ensure the days have been initialized in the context
        if self.context.get_day_state(day_idx) is None:
            self.context.init_day(day_idx, day_config.date, day_config.day_name)
        
        # Mark as initialized
        day_config.initialized = True
    
    def initialize_subtask(self, subtask_idx: int, env):
        """
        Initialize a single subtask (7-day scenario version)
        
        Extended the parent class method, adding:
        1. Reference parsing
        2. Preference check
        3. Date setup
        
        Args:
            subtask_idx: Subtask index
            env: ScenDroid environment
        """
        if subtask_idx >= len(self.seven_day_subtasks):
            # Fall back to the parent class method
            return super().initialize_subtask(subtask_idx, env)
        
        subtask = self.seven_day_subtasks[subtask_idx]
        
        # Check whether days switching is required
        if subtask.day_idx != self.current_day_idx:
            self.initialize_day(subtask.day_idx, env)
        
        day_config = self.days.get(subtask.day_idx)
        
        logging.info("=" * 70)
        logging.info(f"📝 {subtask.task_id}: {subtask.evaluator_name}")
        logging.info(f"   Day: {subtask.day_idx + 1} ({day_config.day_name if day_config else 'N/A'})")
        if subtask.tags:
            logging.info(f"   Tags: {subtask.tags}")
        if subtask.narration:
            logging.info(f"   📖 Narration: {subtask.narration}")
        if subtask.time:
            logging.info(f"   🕐 Time: {subtask.time}")
        logging.info(f"   Max steps: {subtask.max_steps}")
        logging.info("=" * 70)
        
        # 1. Set up device date and time
        if day_config and subtask.time:
            scenario_utils.set_device_time(env, day_config.date, subtask.time)
        
        # 2. Parse referenced parameters
        resolved_params = self._resolve_reference_params(subtask)
        
        # 3. Preference check (if configured)
        if subtask.preference_check:
            self._check_preferences_for_subtask(subtask)
        
        # 4. createevaluatorinstance
        if subtask.evaluator_instance is None:
            # Use scendroid.apps to trigger auto-loading of all app modules
            from scendroid.apps import AppRegistry
            
            evaluator_class = AppRegistry.get_evaluator(subtask.evaluator_name)
            if evaluator_class is None:
                raise ValueError(f"Evaluator not found: {subtask.evaluator_name}")
            
            # Merge original parameters and parsed parameters
            final_params = {**subtask.params, **resolved_params}
            
            subtask.evaluator_instance = evaluator_class(final_params)
            logging.info(f"   Created evaluator: {subtask.evaluator_instance.name}")
        
        # 5. updatestatus
        subtask.status = 'running'
        
        # 6. Sync to parent class subtasks
        if subtask_idx < len(self.subtasks):
            self.subtasks[subtask_idx]['evaluator_instance'] = subtask.evaluator_instance
            self.subtasks[subtask_idx]['status'] = 'running'
        
        # 7. ⚡ Reset mode: Each task is independently initialized (skip the standard initialize_task for Shopping)
        if getattr(self, 'reset_mode', False):
            is_shopping_task = subtask.evaluator_name.startswith('LayeredShopping')
            # Display the instruction being used
            instr = subtask.reset_user_instruction or subtask.user_instruction
            if instr:
                if subtask.reset_user_instruction:
                    logging.info(f"   💬 Instruction (Reset Instruction ⚡): {instr}")
                else:
                    logging.info(f"   💬 Instruction (L0 - Reset Mode fallback): {instr}")
            logging.info("   ⚡ Mode: Per-Task Reset (Independent initialization)")
            try:
                self._reset_initialize_subtask(subtask_idx, env)
                logging.info(f"   ✅ Subtask {subtask.task_id} reset-initialized")
            except Exception as e:
                logging.warning(f"   ⚠️  Reset init failed for {subtask.task_id}: {e}")
                import traceback
                logging.warning(traceback.format_exc())
            return

        # 8. Handle special initialization for the Shopping task (non-reset mode)
        is_shopping_task = subtask.evaluator_name.startswith('LayeredShopping')
        if is_shopping_task:
            self._initialize_shopping_subtask(subtask, env)
        
        logging.info(f"   ✅ Subtask {subtask.task_id} ready")
    
    def _resolve_reference_params(self, subtask: SevenDaySubtask) -> Dict[str, Any]:
        """
        Parse referenced parameters in the subtask
        
        Args:
            subtask: Subtask
            
        Returns:
            Parsed parameter dictionary
        """
        resolved = {}
        
        for param_name, reference in subtask.reference_params.items():
            result = self.reference_resolver.resolve(reference, subtask.day_idx)
            
            if result.success:
                resolved[param_name] = result.resolved_data
                logging.info(f"   🔍 Resolved '{param_name}': {result.resolved_data}")
            else:
                logging.warning(f"   ⚠️ Failed to resolve '{param_name}': {reference}")
        
        return resolved
    
    def _check_preferences_for_subtask(self, subtask: SevenDaySubtask):
        """
        Check subtask preference constraints
        
        Args:
            subtask: Subtask
        """
        check_config = subtask.preference_check
        
        # Check budget
        if 'budget' in check_config:
            budget_check = check_config['budget']
            result = self.preference_store.check_budget(
                budget_check.get('category', 'total'),
                budget_check.get('amount', 0),
                self.context.global_totals.get('total_expense', 0),
            )
            
            if result.get('requires_confirmation'):
                logging.warning(f"   ⚠️ Budget check: {result['message']}")
                subtask.params['_budget_warning'] = result
        
        # Check diet
        if 'diet' in check_config:
            food_item = check_config['diet'].get('food_item')
            if food_item:
                result = self.preference_store.check_diet(food_item)
                
                if not result['allowed']:
                    logging.warning(f"   ⚠️ Diet check: {result['reason']}")
                    subtask.params['_diet_warning'] = result
        
        # Check schedule conflicts
        if 'schedule' in check_config:
            schedule_check = check_config['schedule']
            result = self.preference_store.check_schedule_conflict(
                schedule_check.get('time'),
                schedule_check.get('duration', 60),
            )
            
            if result['has_conflict']:
                logging.warning(f"   ⚠️ Schedule conflict: {result['message']}")
                subtask.params['_schedule_conflict'] = result
    
    def _initialize_shopping_subtask(self, subtask: SevenDaySubtask, env):
        """Initialize Shopping subtask
        
        Reference: base.py initialize_subtask() Shopping handling
        """
        logging.info("=" * 70)
        logging.info("🛒 Detected Shopping task")
        logging.info("=" * 70)
        
        try:
            evaluator = subtask.evaluator_instance
            
            logging.info("   📱 Clicking Shopping shortcut on home screen...")
            logging.info("   🔐 Logging into Shopping website via CDP...")
            logging.info("   🌐 Navigating to starting page...")
            
            # Call Shopping evaluator's initialize_task
            # This will click home screen shortcut, login and navigate to start page
            evaluator.initialize_task(env)
            
            logging.info("   ✅ Shopping app opened and logged in successfully!")
            logging.info("   ✅ Shopping website ready!")
            logging.info("=" * 70)
            
        except Exception as e:
            logging.error("=" * 70)
            logging.error(f"   ❌ Shopping initialization failed: {e}")
            logging.error("=" * 70)
            import traceback
            logging.error(traceback.format_exc())
            
            # Fallback: Try to open Shopping URL directly
            logging.info("   🔄 Attempting fallback: Open Shopping URL directly...")
            try:
                import os
                import subprocess
                import time
                from scendroid.env import adb_utils
                
                # Get Shopping URL from environment
                shopping_url = os.environ.get('SHOPPING', 'http://localhost:7770')
                
                # Get device name
                device_name = "emulator-5554"
                try:
                    console_port = env.controller._env._coordinator._simulator._config.emulator_launcher.emulator_console_port
                    device_name = f"emulator-{console_port}"
                except:
                    pass
                
                # Press Home first
                adb_utils.press_home_button(env.controller)
                time.sleep(1)
                
                # Open Chrome with Shopping URL
                subprocess.run([
                    "adb", "-s", device_name,
                    "shell", "am", "start",
                    "-n", "com.android.chrome/com.google.android.apps.chrome.Main",
                    "-a", "android.intent.action.VIEW",
                    "-d", shopping_url
                ], check=False, capture_output=True)
                
                time.sleep(3)
                logging.info(f"   ✅ Fallback: Opened Chrome with {shopping_url}")
                logging.info("   ⚠️ Agent may need to login manually")
                
            except Exception as fallback_error:
                logging.error(f"   ❌ Fallback also failed: {fallback_error}")
    
    # ==================== evaluation ====================
    
    def evaluate_subtask(self, subtask_idx: int, env) -> float:
        """
        Evaluate a single subtask (7-day scenario version)
        
        Args:
            subtask_idx: Subtask index
            env: ScenDroid environment
            
        Returns:
            Evaluation score (0.0–1.0)
        """
        if subtask_idx >= len(self.seven_day_subtasks):
            return super().evaluate_subtask(subtask_idx, env)
        
        subtask = self.seven_day_subtasks[subtask_idx]
        
        logging.info(f"📊 Evaluating {subtask.task_id}...")
        
        try:
            evaluator = subtask.evaluator_instance
            if evaluator is None:
                logging.error(f"   ❌ Evaluator not initialized")
                return 0.0
            
            score = evaluator.evaluate(env)
            
            # updatestatus
            subtask.score = score
            subtask.status = 'completed' if score >= 0.99 else 'failed'
            
            # Update statistics
            if score >= 0.99:
                self.stats['completed'] += 1
                self.stats['by_day'][subtask.day_idx]['completed'] += 1
                for tag in subtask.tags:
                    if tag in self.stats['by_tag']:
                        self.stats['by_tag'][tag]['completed'] += 1
            else:
                self.stats['failed'] += 1
            
            # Record to context
            self.context.add_subtask_result(
                subtask_id=subtask.subtask_id,
                score=score,
                details={
                    'task_id': subtask.task_id,
                    'evaluator_name': subtask.evaluator_name,
                    'day_idx': subtask.day_idx,
                    'tags': subtask.tags,
                    'status': subtask.status,
                }
            )
            
            # executecontextupdate
            if score >= 0.99 and subtask.context_updates:
                self._apply_context_updates(subtask)
            
            # Sync to parent class
            if subtask_idx < len(self.subtasks):
                self.subtasks[subtask_idx]['score'] = score
                self.subtasks[subtask_idx]['status'] = subtask.status
            
            # outputresult
            status_emoji = "✅" if score >= 0.99 else "❌"
            logging.warning(f"{status_emoji} {subtask.task_id}: {score:.2f}")
            
            # Invoke callback
            if self.on_subtask_complete:
                self.on_subtask_complete(subtask, score)
            
            return score
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            
            subtask.score = 0.0
            subtask.status = 'failed'
            self.stats['failed'] += 1
            
            return 0.0
    
    def _apply_context_updates(self, subtask: SevenDaySubtask):
        """
        Apply context updates after subtask completion
        
        Args:
            subtask: Completed subtask
        """
        updates = subtask.context_updates
        
        for key, value in updates.items():
            if key.startswith('preference:'):
                # Preference update
                _, category, pref_key = key.split(':', 2)
                self.context.set_preference(
                    category, pref_key, value, subtask.task_id
                )
            elif key.startswith('chain:'):
                # Event chain update
                _, chain_id = key.split(':', 1)
                if isinstance(value, dict):
                    if self.context.get_event_chain(chain_id):
                        self.context.append_to_chain(chain_id, value)
                    else:
                        self.context.start_event_chain(chain_id, value)
            else:
                # Standard data update
                self.context.set(key, value)
        
        logging.info(f"   📝 Applied {len(updates)} context updates")
    
    def evaluate(self, env) -> float:
        """
        evaluation of the entire 7-day scenario
        
        Returns:
            Average score (0.0–1.0)
        """
        logging.warning("=" * 70)
        logging.warning(f"📊 7-Day Scenario Results: {self.context.scenario_name}")
        logging.warning("=" * 70)
        
        # Output results by day
        for day_idx in sorted(self.days.keys()):
            day_config = self.days[day_idx]
            day_subtasks = self.get_subtasks_for_day(day_idx)
            
            if not day_subtasks:
                continue
            
            day_passed = sum(1 for st in day_subtasks if st.score >= 0.99)
            day_total = len(day_subtasks)
            
            logging.warning(f"\n📅 Day {day_idx + 1} ({day_config.day_name}): "
                            f"{day_passed}/{day_total} passed")
            
            for st in day_subtasks:
                status = "✅" if st.score >= 0.99 else "❌"
                tags_str = f" {st.tags}" if st.tags else ""
                logging.warning(f"   {status} {st.task_id}: {st.evaluator_name} "
                                f"({st.score:.2f}){tags_str}")
        
        # Overall statistics
        total = len(self.seven_day_subtasks)
        completed = self.stats['completed']
        failed = self.stats['failed']
        
        scores = [st.score for st in self.seven_day_subtasks]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        logging.warning("\n" + "=" * 70)
        logging.warning("📊 Summary:")
        logging.warning(f"   ✅ Passed: {completed}/{total}")
        logging.warning(f"   ❌ Failed: {failed}/{total}")
        logging.warning(f"   📈 Average Score: {avg_score:.2f}")
        
        # Statistics by label
        if self.stats['by_tag']:
            logging.warning("\n   📋 By Tag:")
            for tag, tag_stats in sorted(self.stats['by_tag'].items()):
                tag_passed = tag_stats['completed']
                tag_total = tag_stats['total']
                logging.warning(f"      {tag}: {tag_passed}/{tag_total}")
        
        # Preference fulfillment status
        weekly_summary = self.context.get_weekly_summary()
        logging.warning("\n   📊 Weekly Stats:")
        logging.warning(f"      Total Expense: ${weekly_summary['total_expense']:.2f}")
        logging.warning(f"      Dining Expense: ${weekly_summary['dining_expense']:.2f}")
        logging.warning(f"      Exercise Distance: {weekly_summary['exercise_distance']:.1f} km")
        
        # Check whether the budget is fulfilled
        budget_limit = self.preference_store.get_budget_limit('dining')
        if budget_limit:
            dining_expense = weekly_summary['dining_expense']
            budget_status = "✅ Within budget" if dining_expense <= budget_limit else "❌ Over budget"
            logging.warning(f"      Budget ({budget_limit}): {budget_status}")
        
        logging.warning("=" * 70)
        
        return avg_score
    
    # ==================== Tool methods ====================
    
    def get_task_instruction(self, subtask_idx: int, level: str = "L0") -> str:
        """
        Get the instruction text for the subtask
        
        Args:
            subtask_idx: subtask index
            level: instruction level (not currently supported; defaults to returning user_instruction)
            
        Returns:
            Instruction text
        """
        if subtask_idx >= len(self.seven_day_subtasks):
            return ""
        
        subtask = self.seven_day_subtasks[subtask_idx]
        # ⚡ Reset mode: prioritize returning reset_user_instruction
        if getattr(self, 'reset_mode', False) and subtask.reset_user_instruction:
            return subtask.reset_user_instruction
        return subtask.user_instruction
    
    def print_schedule(self):
        """Print the complete schedule"""
        print("\n" + "=" * 80)
        print(f"📅 {self.context.scenario_name} - Full Schedule")
        print("=" * 80)
        
        for day_idx in sorted(self.days.keys()):
            day_config = self.days[day_idx]
            subtasks = self.get_subtasks_for_day(day_idx)
            
            print(f"\n🌅 Day {day_idx + 1} - {day_config.day_name} ({day_config.date})")
            print("-" * 60)
            
            for st in sorted(subtasks, key=lambda x: x.time or "00:00"):
                time_str = st.time or "??:??"
                tags_str = f" {st.tags}" if st.tags else ""
                print(f"  {time_str} [{st.task_id}] {st.evaluator_name}{tags_str}")
                if st.user_instruction:
                    # Truncate long instructions
                    instr = st.user_instruction[:60] + "..." if len(st.user_instruction) > 60 else st.user_instruction
                    print(f"         └─ \"{instr}\"")
        
        print("\n" + "=" * 80)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'scenario_id': self.context.scenario_id,
            'scenario_name': self.context.scenario_name,
            'start_date': self.start_date,
            'num_days': self.num_days,
            'stats': self.stats,
            'context': self.context.to_dict(),
            'preferences': self.preference_store.to_dict(),
            'subtasks': [
                {
                    'task_id': st.task_id,
                    'day_idx': st.day_idx,
                    'evaluator_name': st.evaluator_name,
                    'time': st.time,
                    'tags': st.tags,
                    'status': st.status,
                    'score': st.score,
                }
                for st in self.seven_day_subtasks
            ],
        }
