"""
Base Scenario Evaluator

Provides the base class for a Scenario evaluator and common functionality.
"""

from absl import logging
from typing import List, Dict, Any, Optional
import random

from scendroid.apps.base import BaseAppEvaluator
from scendroid.apps.scenario.context import ScenarioContext
from scendroid.apps.scenario import utils as scenario_utils


class BaseScenarioEvaluator(BaseAppEvaluator):
    """
    Base class for a Scenario evaluator
    
    core features:
    1. Manages multiple subtasks
    2. Maintains the scenario context (ScenarioContext)
    3. Serializes execution of subtasks
    4. Aggregates subtask evaluation results
    5. Supports weighted scoring
    
    usage:
        class MyScenarioEvaluator(BaseScenarioEvaluator):
            def __init__(self, params):
                super().__init__(params)
                self.add_subtask(...)  # Add a subtask
                self.add_subtask(...)  # Add a subtask
    
    Note:
    - Subtasks are executed serially in the order they were added
    - initialize_subtask is called before each subtask's execution
    - evaluate_subtask is called after each subtask's execution
    - evaluate is called after all subtasks are completed to aggregate results
    """
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # scenariocontext
        self.context = ScenarioContext()
        self.context.scenario_id = params.get('scenario_id')
        self.context.scenario_name = params.get('name', self.__class__.__name__)
        self.context.base_date = params.get('base_date')
        
        # List of subtasks
        self.subtasks: List[Dict[str, Any]] = []
        
        # scenarioconfiguration
        self.total_max_steps = params.get('total_max_steps', 200)
        self.success_criteria = params.get('success_criteria', {})
        
        # Whether to continue after a subtask fails
        self.continue_on_failure = params.get('continue_on_failure', True)
        
        # Save generated random parameters (for sharing across tasks)
        self.generated_params = params.get('generated_params', {})
        
        # 🆕 Obfuscation level (L0/L1/L2; if None, use the original instruction)
        # None = Use the original instruction (/scenario mode)
        # L0/L1/L2 = Use the corresponding obfuscated instruction (/scenario-L mode)
        #   L0: Precise instruction (includes all parameters and steps)
        #   L1: Obtainable via reasoning or exploration
        #   L2: Fewer parameters or intent-level (task-dependent)
        self.clarity_level = params.get('clarity_level', None)
        if self.clarity_level:
            logging.info(f"Scenario clarity level: {self.clarity_level}")
        else:
            logging.info("Scenario using original instructions (no clarity level specified)")
        
        # 🆕 Per-Task Reset mode (for ablation studies)
        # False = Scenario mode (batch initialization, status persistence, supports task dependencies)
        # True = Per-Task Reset mode (independent initialization per task, clean environment, no dependencies, enforces L0 instruction)
        self.reset_mode = params.get('reset_mode', False)
        if self.reset_mode:
            logging.info("⚡ Per-Task Reset Mode ENABLED: Each task will be independently initialized with L0 instructions")
            logging.info("   - Each subtask starts with a clean environment")
            logging.info("   - No state persistence between tasks")
            logging.info("   - All instructions forced to L0 (most explicit)")
            logging.info("   - No task dependencies (failure of one task won't affect others)")
        else:
            logging.info("📚 Scenario Mode (default): Batch initialization with state persistence")
    
    @classmethod
    def generate_random_params(cls, seed: Optional[int] = None) -> dict:
        """
        Generates random parameters for the scenario (optional implementation in subclasses)
        
        This method implements parameterization of the scenario and supports:
        1. Controlling randomness via seed (reproducible)
        2. Generating parameters shared across subtasks
        3. Generating subtask-specific parameters
        
        Args:
            seed: Random seed used to ensure reproducibility. If None, true randomness is used.
            
        Returns:
            A dictionary containing all subtask parameters; recommended format:
            {
                'seed': seed,
                'shared': {...},  # Parameters shared across tasks
                'subtask_N': {...},  # Parameters specific to subtask N
            }
        
        Note:
            - Default implementation returns an empty dictionary (no parameterization)
            - Subclasses can override this method to implement custom parameter generation
            - Generated parameters are passed to the `generated_params` field in `__init__`
        
        Example:
            @classmethod
            def generate_random_params(cls, seed=None):
                if seed is not None:
                    random.seed(seed)
                return {
                    'seed': seed,
                    'shared': {
                        'user_name': random.choice(['Alice', 'Bob', 'Carol']),
                    },
                    'subtask_1': {
                        'value': random.randint(1, 100),
                    },
                }
        """
        return {}
    
    def add_subtask(
        self,
        subtask_id: int,
        evaluator_name: str,
        params: dict,
        weight: float = 1.0,
        narration: str = "",
        user_instruction: str = "",
        user_instruction_L0: str = "",
        user_instruction_L1: str = "",
        user_instruction_L2: str = "",
        reset_user_instruction: str = "",
        time: str = None,
        max_steps: int = 20,
        on_fail: str = "continue",
        requires_answer: bool = False,
    ):
        """
        Adds a subtask
        
        Args:
            subtask_id: Subtask ID
            evaluator_name: Evaluator registration name (e.g., "LayeredClockSetAlarm")
            params: evaluatorparameter
            weight: Weight (used for weighted averaging)
            narration: Task narration (provides context)
            user_instruction: Original user instruction (default instruction for the scenario, used in /scenario mode)
            user_instruction_L0: L0-level instruction (precise instruction, including all parameters and steps)
            user_instruction_L1: L1-level instruction (obtainable via reasoning or exploration)
            user_instruction_L2: L2-level instruction (fewer parameters or intent-level, determined by task characteristics)
            reset_user_instruction: Instruction dedicated to Reset mode (more explicit than L0, including all specific parameters)
            time: Task time (HH:MM format, used to set up device time)
            max_steps: Maximum number of steps
            on_fail: Failure handling strategy ("continue" or "stop")
            requires_answer: Whether the task is a question-answering task
        """
        self.subtasks.append({
            'subtask_id': subtask_id,
            'evaluator_name': evaluator_name,
            'params': params,
            'weight': weight,
            'narration': narration,
            'user_instruction': user_instruction,  # Original instruction
            'user_instruction_L0': user_instruction_L0 or user_instruction,  # Defaults to original instruction
            'user_instruction_L1': user_instruction_L1 or user_instruction,  # Defaults to original instruction
            'user_instruction_L2': user_instruction_L2 or user_instruction,  # Defaults to original instruction
            'reset_user_instruction': reset_user_instruction,  # Instruction dedicated to Reset mode
            'time': time,
            'max_steps': max_steps,
            'on_fail': on_fail,
            'requires_answer': requires_answer,
            'evaluator_instance': None,  # latencycreate
            'status': 'pending',  # pending, running, completed, failed
            'score': 0.0,
        })
        
        logging.info(f"Added subtask {subtask_id}: {evaluator_name} (weight: {weight})")
    
    def get_subtask_instruction(self, subtask_idx: int, level: str = None) -> str:
        """
        Get the instruction for a subtask (based on the specified clarity level or using the original instruction)
        
        Three modes:
        1. /scenario mode: clarity_level = None, uses the original instruction (user_instruction)
        2. /scenario-L mode: clarity_level = L0/L1/L2, uses the corresponding abstracted instruction
        3. Reset mode: reset_mode = True, prioritizes reset_user_instruction (if available); otherwise, uses the L0 instruction
        
        Args:
            subtask_idx: Subtask index
            level: Clarity level (L0/L1/L2); if None, uses the scenario's clarity_level
        
        Returns:
            The user instruction corresponding to the specified clarity level; if clarity_level is None, returns the original instruction
        """
        if subtask_idx < 0 or subtask_idx >= len(self.subtasks):
            return ""
        
        subtask = self.subtasks[subtask_idx]
        
        # ⚡ Reset mode: Prioritize reset_user_instruction (more explicit); otherwise, fall back to the L0 instruction
        if self.reset_mode:
            # Method 1: Check whether reset_user_instruction exists in the subtask dictionary (scenario_b approach)
            reset_instruction = subtask.get('reset_user_instruction')
            if reset_instruction:
                return reset_instruction
            
            # Method 2: Check whether reset_user_instruction exists in params (scenario_a approach)
            params = subtask.get('params', {})
            reset_instruction = params.get('reset_user_instruction')
            if reset_instruction:
                return reset_instruction
            
            # If reset_user_instruction is absent in both cases, fall back to the L0 instruction
            return subtask['user_instruction_L0']
        
        # Use the provided level; if not provided, use the scenario's clarity_level
        if level is not None:
            use_level = level
        else:
            use_level = self.clarity_level
        
        # If no setup clarity level is specified, use the original instruction (/scenario mode)
        if use_level is None:
            return subtask['user_instruction']
        
        # Use the abstracted instruction (/scenario-L mode)
        if use_level == "L0":
            return subtask['user_instruction_L0']
        elif use_level == "L1":
            return subtask['user_instruction_L1']
        elif use_level == "L2":
            return subtask['user_instruction_L2']
        else:
            logging.warning(f"Unknown clarity level: {use_level}, using original instruction")
            return subtask['user_instruction']
    
    def initialize_task(self, env):
        """
        initializescenario
        
        Note: Not all subtasks are initialized at once; instead, they are initialized one by one.
        Subclasses may override this method to add scenario-level initialization logic.
        """
        super().initialize_task(env)
        
        logging.info("=" * 70)
        logging.info(f"🎬 Initializing Scenario: {self.context.scenario_name}")
        logging.info(f"   Scenario ID: {self.context.scenario_id}")
        logging.info(f"   Total subtasks: {len(self.subtasks)}")
        logging.info(f"   Total max steps: {self.total_max_steps}")
        if self.context.base_date:
            logging.info(f"   Base date: {self.context.base_date}")
        logging.info("=" * 70)
        
        # ✅ Set up WebArena environment variables (if the scenario includes a Shopping task)
        self._setup_webarena_env_vars(env)
    
    def _setup_webarena_env_vars(self, env):
        """Set up the environment variables required by WebArena
        
        WebArena's env_config.py requires setting up URLs for all websites.
        For scenario tasks, we only use the Shopping website; other websites are set up as placeholders.
        """
        import os
        from scendroid.task_evals.webarena import port_utils
        
        # Check whether there is a Shopping task
        has_shopping_task = any(
            subtask['evaluator_name'].startswith('LayeredShopping')
            for subtask in self.subtasks
        )
        
        if not has_shopping_task:
            logging.info("   ℹ️  No Shopping tasks, skipping WebArena env setup")
            return
        
        # Get the Shopping URL (based on the emulator port)
        try:
            shopping_url = port_utils.get_shopping_base_url(env)
            console_port = None
            try:
                console_port = env.controller._env._coordinator._simulator._config.emulator_launcher.emulator_console_port
            except:
                pass
            
            shopping_port = port_utils.calculate_shopping_port(console_port) if console_port else 7770
            
            # set environment variables
            os.environ['SHOPPING'] = shopping_url
            os.environ['SHOPPING_ADMIN'] = f"{shopping_url}/admin"
            
            # Other WebArena websites (we do not use them, but env_config.py requires them to be set up)
            os.environ['REDDIT'] = 'http://placeholder.reddit.com'
            os.environ['GITLAB'] = 'http://placeholder.gitlab.com'
            os.environ['WIKIPEDIA'] = 'http://placeholder.wikipedia.com'
            os.environ['MAP'] = 'http://placeholder.map.com'
            os.environ['HOMEPAGE'] = 'http://placeholder.homepage.com'
            
            logging.info("   ✅ WebArena environment variables set:")
            logging.info(f"      SHOPPING: {shopping_url}")
            logging.info(f"      SHOPPING_ADMIN: {shopping_url}/admin")
            logging.info(f"      (Other sites: placeholder URLs)")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Failed to setup WebArena env vars: {e}")
            # Set up default value to avoid assertion error
            os.environ.setdefault('SHOPPING', 'http://localhost:7770')
            os.environ.setdefault('SHOPPING_ADMIN', 'http://localhost:7770/admin')
            os.environ.setdefault('REDDIT', 'http://placeholder.reddit.com')
            os.environ.setdefault('GITLAB', 'http://placeholder.gitlab.com')
            os.environ.setdefault('WIKIPEDIA', 'http://placeholder.wikipedia.com')
            os.environ.setdefault('MAP', 'http://placeholder.map.com')
            os.environ.setdefault('HOMEPAGE', 'http://placeholder.homepage.com')
    
    def _get_shopping_mode(self) -> str:
        """Get the current shopping mode from environment or config.
        
        Returns:
            'chrome' or 'app'
        """
        import os
        
        # 1. Check environment variable
        mode = os.environ.get("SHOPPING_MODE", "").lower()
        if mode in ("chrome", "app"):
            return mode
        
        # 2. Check config file
        config_file = "/tmp/shopping_mode.conf"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("SHOPPING_MODE="):
                            mode = line.split("=", 1)[1].strip().lower()
                            if mode in ("chrome", "app"):
                                return mode
            except Exception:
                pass
        
        # 3. Default to chrome
        return "chrome"
    
    def initialize_subtask(self, subtask_idx: int, env):
        """
        Initialize a single subtask
        
        This method is called before each subtask starts
        Subclasses can override this method to add custom initialization logic
        
        Args:
            subtask_idx: Subtask index (0-based)
            env: ScenDroid environment
        """
        if subtask_idx < 0 or subtask_idx >= len(self.subtasks):
            raise IndexError(f"Subtask index out of range: {subtask_idx}")
        
        subtask = self.subtasks[subtask_idx]
        
        logging.info("=" * 70)
        logging.info(f"📝 Subtask {subtask['subtask_id']}/{len(self.subtasks)}: {subtask['evaluator_name']}")
        if subtask['narration']:
            logging.info(f"   📖 Narration: {subtask['narration']}")
        # 🆕 Display instruction (based on mode)
        current_instruction = self.get_subtask_instruction(subtask_idx)
        if current_instruction:
            if self.reset_mode:
                # Reset mode: Prefer reset_user_instruction; otherwise, fall back to L0
                if subtask.get('reset_user_instruction'):
                    logging.info(f"   💬 Instruction (Reset Instruction ⚡): {current_instruction}")
                else:
                    logging.info(f"   💬 Instruction (L0 - Reset Mode fallback): {current_instruction}")
            elif self.clarity_level is None:
                # /scenario mode: Use the original instruction
                logging.info(f"   💬 Instruction (Original): {current_instruction}")
            else:
                # /scenario-L mode: Display blurred etc.-level instruction
                logging.info(f"   💬 Instruction ({self.clarity_level}): {current_instruction}")
        if subtask['time']:
            logging.info(f"   🕐 Time: {subtask['time']}")
        logging.info(f"   Max steps: {subtask['max_steps']}")
        if self.reset_mode:
            logging.info("   ⚡ Mode: Per-Task Reset (Independent initialization)")
        logging.info("=" * 70)
        
        # updatecontext
        self.context.current_subtask_idx = subtask_idx
        
        # Clean up potentially interfering running apps (unless switching to Shopping task)
        # Reference: Legacy architecture scenario_env_setup.py setup_subtask_environment_minimal() Lines 862–886
        is_shopping_task = subtask['evaluator_name'].startswith('LayeredShopping')
        
        if not is_shopping_task:
            try:
                from scendroid.env import adb_utils
                import time
                
                # ⚠️ Critical: Check whether the scenario contains a Shopping task
                # If so, do not close Chrome (to preserve login status)
                has_shopping_task = any(
                    st['evaluator_name'].startswith('LayeredShopping') 
                    for st in self.subtasks
                )
                
                # Close potentially interfering apps
                apps_to_close = ["opentracks"]  # OpenTracks may be recording
                
                # Only close Chrome if the scenario does not contain a Shopping task
                if not has_shopping_task:
                    apps_to_close.append("chrome")
                else:
                    logging.info(f"   ℹ️  Keeping Chrome running (Shopping task present in scenario, preserving login status)")
                
                for app_name in apps_to_close:
                    try:
                        adb_utils.close_app(app_name, env.controller)
                        logging.info(f"   ✅ Closed {app_name}")
                    except Exception as e:
                        logging.debug(f"   Could not close {app_name}: {e}")
                
                time.sleep(0.5)
            except Exception as e:
                logging.warning(f"Failed to clean up running apps: {e}")
        
        # Set up device time (if specified)
        if subtask['time'] and self.context.base_date:
            scenario_utils.set_device_time(env, self.context.base_date, subtask['time'])
        
        # createevaluatorinstance(latencycreate)
        if subtask['evaluator_instance'] is None:
            from scendroid.apps.registry import AppRegistry
            
            evaluator_class = AppRegistry.get_evaluator(subtask['evaluator_name'])
            if evaluator_class is None:
                raise ValueError(f"Evaluator not found: {subtask['evaluator_name']}")
            
            # Support dynamic parameters (retrieved from context)
            resolved_params = self._resolve_params(subtask['params'])
            
            subtask['evaluator_instance'] = evaluator_class(resolved_params)
            logging.info(f"   Created evaluator instance: {subtask['evaluator_instance'].name}")
        
        # updatestatus
        subtask['status'] = 'running'
        
        # ⚡ Per-Task Reset mode: Each task is independently initialized
        if self.reset_mode:
            logging.info("=" * 70)
            logging.info(f"⚡ RESET MODE: Initializing task {subtask['subtask_id']} independently")
            logging.info("=" * 70)
            try:
                # Call the overridable hook method (subclasses can implement per-task independent initialization logic)
                self._reset_initialize_subtask(subtask_idx, env)
                logging.info(f"   ✅ Task {subtask['subtask_id']} initialized successfully (clean environment)")
            except Exception as e:
                logging.warning(f"   ⚠️  Task {subtask['subtask_id']} initialization failed: {e}")
                import traceback
                logging.warning(traceback.format_exc())
            return
        
        # 📚 Scenario mode: Batch initialization; only special tasks require individual initialization
        # ⚠️ Important: In Scenario mode, subtask.initialize_task() is generally not called
        # Reason:
        # 1. Batch initialization of the scenario (initialize_task) has already set up the entire environment
        # 2. Each subtask's initialize_task() would clear previously set-up data
        # 3. E.g., ClockSetAlarmEvaluator.initialize_task() clears all alarms
        # 4. This would break environment data created during batch initialization
        #
        # ⚠️ Exception: Shopping task (WebArena)
        # The Shopping task requires calling initialize_task() to:
        # 1. Tap the Shopping shortcut on the home screen (at coordinates 162, 1615)
        # 2. Automatically log in via CDP
        # 3. Navigate to the starting page
        # Reference: Legacy architecture scenario_env_setup.py setup_subtask_environment_minimal() Lines 914–949
        
        # Check whether this is a Shopping task
        is_shopping_task = subtask['evaluator_name'].startswith('LayeredShopping')
        
        logging.info(f"🔍 Subtask {subtask['subtask_id']}: evaluator_name = {subtask['evaluator_name']}")
        logging.info(f"🔍 Is Shopping task: {is_shopping_task}")
        
        if is_shopping_task:
            logging.info("=" * 70)
            logging.info("🛒 Detected Shopping task in Scenario")
            logging.info("=" * 70)
            
            try:
                # ✅ Support dual modes: Chrome or Shopping App
                # Mode is determined by environment variable SHOPPING_MODE or configuration file /tmp/shopping_mode.conf
                # - Chrome mode: Automatic login via CDP
                # - App mode: Requires manual login
                
                # Detect the current mode
                shopping_mode = self._get_shopping_mode()
                logging.info(f"   🎯 Shopping mode: {shopping_mode}")
                
                evaluator = subtask['evaluator_instance']
                logging.info(f"   📋 Evaluator type: {type(evaluator).__name__}")
                logging.info(f"   📋 Evaluator params keys: {list(evaluator._params.keys()) if hasattr(evaluator, '_params') else 'N/A'}")
                
                if shopping_mode == "app":
                    logging.info("   📱 Launching Shopping App...")
                    logging.info("   🔐 App mode: ADB UI auto login...")
                else:
                    logging.info("   📱 Clicking Shopping shortcut on home screen...")
                    logging.info("   🔐 Chrome mode: CDP auto login...")
                logging.info("   🌐 Navigating to starting page...")
                
                # Call the Shopping evaluator's initialize_task
                # This launches Chrome or the app based on the mode
                evaluator.initialize_task(env)
                
                if shopping_mode == "app":
                    logging.info("   ✅ Shopping App launched!")
                else:
                    logging.info("   ✅ Shopping app opened and logged in successfully!")
                logging.info("   ✅ Shopping website ready!")
                logging.info("=" * 70)
                
            except Exception as e:
                logging.error("=" * 70)
                logging.error(f"   ❌ Shopping initialization failed: {e}")
                logging.error("=" * 70)
                import traceback
                logging.error(traceback.format_exc())
        else:
            logging.info(f"   ℹ️  Skipping subtask initialize_task() (Scenario mode preserves environment)")
        
        logging.info(f"   ✅ Subtask {subtask['subtask_id']} ready for execution")
    
    def evaluate_subtask(self, subtask_idx: int, env) -> float:
        """
        Evaluate a single subtask
        
        Args:
            subtask_idx: Subtask index (0-based)
            env: ScenDroid environment
            
        Returns:
            float: Evaluation score (0.0 - 1.0)
        """
        if subtask_idx < 0 or subtask_idx >= len(self.subtasks):
            raise IndexError(f"Subtask index out of range: {subtask_idx}")
        
        subtask = self.subtasks[subtask_idx]
        
        logging.info(f"📊 Evaluating Subtask {subtask['subtask_id']}...")
        
        try:
            evaluator = subtask['evaluator_instance']
            if evaluator is None:
                logging.error(f"   ❌ Evaluator not initialized for subtask {subtask['subtask_id']}")
                return 0.0
            
            score = evaluator.evaluate(env)
            
            # Update subtask status
            subtask['score'] = score
            subtask['status'] = 'completed' if score >= 0.99 else 'failed'
            
            # Record the result to the context
            self.context.add_subtask_result(
                subtask_id=subtask['subtask_id'],
                score=score,
                details={
                    'evaluator_name': subtask['evaluator_name'],
                    'max_steps': subtask['max_steps'],
                    'status': subtask['status'],
                }
            )
            
            # outputresult
            status_emoji = "✅" if score >= 0.99 else "❌"
            logging.warning(f"{status_emoji} Subtask {subtask['subtask_id']}: {score:.2f}")
            
            return score
            
        except Exception as e:
            logging.error(f"   ❌ Error evaluating subtask {subtask['subtask_id']}: {e}")
            import traceback
            logging.error(traceback.format_exc())
            
            subtask['score'] = 0.0
            subtask['status'] = 'failed'
            
            self.context.add_subtask_result(
                subtask_id=subtask['subtask_id'],
                score=0.0,
                details={
                    'evaluator_name': subtask['evaluator_name'],
                    'error': str(e),
                    'status': 'failed',
                }
            )
            
            return 0.0
    
    def evaluate(self, env) -> float:
        """
        Evaluate the entire scenario
        
        Note: This method is typically called after all subtasks are completed
              It aggregates the results of all subtasks
        
        Returns:
            float: Average score (0.0 - 1.0)
        """
        logging.warning("=" * 70)
        logging.warning(f"📊 Scenario Results: {self.context.scenario_name}")
        logging.warning("=" * 70)
        
        if not self.subtasks:
            logging.warning("   ⚠️  No subtasks to evaluate")
            return 0.0
        
        # Count the completion status of all subtasks (unweighted)
        passed_count = 0
        failed_count = 0
        
        for subtask in self.subtasks:
            score = subtask.get('score', 0.0)
            status = "✅ PASSED" if score >= 0.99 else "❌ FAILED"
            
            if score >= 0.99:
                passed_count += 1
            else:
                failed_count += 1
            
            # Simplify output: display only task ID, name, and status
            logging.warning(
                f"  {status} - Subtask {subtask['subtask_id']}: "
                f"{subtask['evaluator_name']} (Score: {score:.2f})"
            )
        
        # Compute the simple average score (unweighted)
        scores = [subtask.get('score', 0.0) for subtask in self.subtasks]
        final_score = sum(scores) / len(scores) if scores else 0.0
        
        total_count = len(self.subtasks)
        
        logging.warning("=" * 70)
        logging.warning(f"📊 Summary:")
        logging.warning(f"   ✅ Passed: {passed_count}/{total_count}")
        logging.warning(f"   ❌ Failed: {failed_count}/{total_count}")
        logging.warning(f"   📈 Average Score: {final_score:.2f}")
        logging.warning("=" * 70)
        
        return final_score
    
    def _reset_initialize_subtask(self, subtask_idx: int, env):
        """
        Per-Task Reset: subtask initialization in mode (subclasses should override)
        
        Default implementation: calls only the evaluator's initialize_task().
        
        ⚠️ For most Scenario tasks, the default implementation is insufficient!
        Subclasses should override this method to provide independent initialization logic for each subtask, including:
        1. clear related app data
        2. Create prerequisite condition data (e.g., calendar event, alarm, contact, etc.)
        3. Set up the environment (e.g., timezone, permissions, etc.)
        
        In Scenario mode, these prerequisite conditions are provided by:
        - Batch initialization (initialize_task) creating them all at once
        - Or naturally satisfied after preceding tasks complete
        
        However, in Reset mode, each task must independently set up its own prerequisite conditions.
        
        Args:
            subtask_idx: Subtask index (0-based)
            env: ScenDroid environment
        """
        subtask = self.subtasks[subtask_idx]
        logging.info(f"   ℹ️  Using default reset initialization (evaluator.initialize_task)")
        logging.info(f"   ⚠️  Subclass should override _reset_initialize_subtask() for proper per-task setup")
        subtask['evaluator_instance'].initialize_task(env)
    
    def tear_down(self, env):
        """
        cleanupscenario
        
        Subclasses may override this method to add scenario-level cleanup logic
        """
        logging.info("=" * 70)
        logging.info(f"🧹 Tearing down Scenario: {self.context.scenario_name}")
        
        # Clean up all subtasks
        for subtask in self.subtasks:
            if subtask['evaluator_instance'] is not None:
                try:
                    subtask['evaluator_instance'].tear_down(env)
                except Exception as e:
                    logging.warning(f"   ⚠️  Error tearing down subtask {subtask['subtask_id']}: {e}")
        
        logging.info("=" * 70)
        
        super().tear_down(env)
    
    def _resolve_params(self, params: dict) -> dict:
        """
        Parse dynamic parameters
        
        Supports retrieving parameters from the context, e.g.:
        - "{{context.meeting_title}}" -> retrieved from the context
        - "{{subtask_2.event_id}}" -> retrieved from subtask 2's result
        
        Args:
            params: Original parameter dictionary
            
        Returns:
            dict: Parsed parameter dictionary
        """
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Dynamic parameters
                path = value[2:-2].strip()
                resolved[key] = self._get_from_context(path)
            else:
                resolved[key] = value
        return resolved
    
    def _get_from_context(self, path: str):
        """
        Retrieve a value from the context
        
        Args:
            path: Path, e.g., "context.key" or "subtask_2.field"
            
        Returns:
            Value retrieved from the context
        """
        if path.startswith("context."):
            key = path[8:]
            return self.context.get(key)
        elif path.startswith("subtask_"):
            # e.g.:subtask_2.event_id
            parts = path.split(".", 1)
            subtask_id = int(parts[0].split("_")[1])
            field = parts[1] if len(parts) > 1 else None
            
            result = self.context.get_previous_result(subtask_id)
            if result and field:
                return result['details'].get(field)
            return result
        else:
            return self.context.get(path)

