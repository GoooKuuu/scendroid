"""
Layered Task Loader - Layered task loader

Loads and manages tasks with multiple levels of ambiguity (L0–L3).
Each task contains progressively ambiguous instructions, ranging from precise instructions (L0) to intent-level ambiguity (L3).

Ground Truth: All evaluations at every level are based on the execution result of the L0 instruction.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Optional import for ScenDroid integration
try:
    from scendroid import registry as aw_registry
except ImportError:
    aw_registry = None

# Optional import for layered tasks evaluators (legacy architecture, deprecated)
# Import them separately so one failure doesn't affect the other
# Note: The legacy architecture has been removed; these imports will fail, but they do not affect the operation of the new architecture
lt = None
lt_ir = None

try:
    from scendroid.task_evals.single import layered_tasks as lt
except ImportError as e:
    # The legacy architecture has been deleted; this is an expected import failure, logged at the info level
    logging.info(f"Old architecture layered_tasks not available (expected): {e}")
    lt = None

try:
    from scendroid.task_evals.single import layered_tasks_info_retrieval as lt_ir
except ImportError as e:
    # The legacy architecture has been deleted; this is an expected import failure, logged at the info level
    logging.info(f"Old architecture layered_tasks_info_retrieval not available (expected): {e}")
    lt_ir = None

# Import the new App Registry for modular evaluators
try:
    from scendroid.apps.registry import AppRegistry
except ImportError as e:
    logging.error(f"Cannot import AppRegistry: {e}")
    AppRegistry = None


@dataclass
class InstructionLevel:
    """Data class for a single instruction at a specific level"""
    instruction: str
    clarity: str  # precise, environment_disambiguated, parameter_underspecified, intent_level
    parameters: Dict[str, Any]
    missing: Optional[List[str]] = None
    intent: Optional[str] = None


@dataclass
class LayeredTask:
    """Layered task data class"""
    task_id: int
    app: str
    category: str
    name: str
    levels: Dict[str, InstructionLevel]  # L0, L1, L2, L3
    ground_truth: str  # Always "L0"
    evaluation: Dict[str, Any]
    requires_answer: bool = False  # Whether the agent must provide an answer
    
    def get_instruction(self, level: str) -> str:
        """Get the instruction at the specified level"""
        if level not in self.levels:
            raise ValueError(f"Level {level} not found in task {self.task_id}")
        return self.levels[level].instruction
    
    def get_l0_instruction(self) -> str:
        """Get the L0 (precise) instruction"""
        return self.levels['L0'].instruction
    
    def get_l0_parameters(self) -> Dict[str, Any]:
        """Get the L0 parameters (for evaluation)"""
        return self.levels['L0'].parameters
    
    def get_evaluation_config(self) -> Dict[str, Any]:
        """getevaluationconfiguration"""
        return self.evaluation
    
    def requires_user_answer(self) -> bool:
        """Determine whether the task requires the user to provide an answer (e.g., information retrieval tasks)"""
        return self.requires_answer


class LayeredTaskLoader:
    """Layered task loader"""
    
    def __init__(self, config_path: str = "layered_tasks.json"):
        """
        initialize taskloader
        
        Args:
            config_path: taskconfiguration filepath
        """
        self.config_path = Path(config_path)
        self.tasks: List[LayeredTask] = []
        self.version: str = ""
        self.description: str = ""
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        self._load_config()
    
    def _load_config(self):
        """loadconfiguration file"""
        logging.info(f"📂 Loading layered tasks from {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.version = config.get('version', 'unknown')
        self.description = config.get('description', '')
        
        logging.info(f"📋 Config version: {self.version}")
        logging.info(f"📝 Description: {self.description}")
        
        # parsetask
        for task_data in config.get('tasks', []):
            task = self._parse_task(task_data)
            self.tasks.append(task)
        
        logging.info(f"✅ Loaded {len(self.tasks)} layered tasks")
    
    def _parse_task(self, task_data: Dict[str, Any]) -> LayeredTask:
        """Parse a single task"""
        # Parse instructions at each level
        levels = {}
        for level_name, level_data in task_data.get('levels', {}).items():
            levels[level_name] = InstructionLevel(
                instruction=level_data.get('instruction', ''),
                clarity=level_data.get('clarity', ''),
                parameters=level_data.get('parameters', {}),
                missing=level_data.get('missing'),
                intent=level_data.get('intent')
            )
        
        return LayeredTask(
            task_id=task_data.get('task_id'),
            app=task_data.get('app', ''),
            category=task_data.get('category', ''),
            name=task_data.get('name', ''),
            levels=levels,
            ground_truth=task_data.get('ground_truth', 'L0'),
            evaluation=task_data.get('evaluation', {}),
            requires_answer=task_data.get('requires_answer', False)
        )
    
    def get_task(self, task_id: int) -> Optional[LayeredTask]:
        """Retrieve a task by task ID"""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None
    
    def get_all_tasks(self) -> List[LayeredTask]:
        """Retrieve all tasks"""
        return self.tasks
    
    def get_tasks_by_app(self, app: str) -> List[LayeredTask]:
        """Filter tasks by app"""
        return [task for task in self.tasks if task.app.lower() == app.lower()]
    
    def get_tasks_by_category(self, category: str) -> List[LayeredTask]:
        """Filter tasks by category"""
        return [task for task in self.tasks if task.category == category]
    
    def print_task_summary(self):
        """Print task summary"""
        print("\n" + "="*80)
        print(f"📋 Layered Tasks Summary (Version {self.version})")
        print("="*80)
        print(f"Total Tasks: {len(self.tasks)}")
        print(f"\nLevels:")
        print(f"  L0: Precise instruction (ground truth)")
        print(f"  L1: Environment-disambiguated")
        print(f"  L2: Parameter-underspecified")
        print(f"  L3: Intent-level ambiguity")
        print("\n" + "-"*80)
        
        # Group by app
        apps = {}
        for task in self.tasks:
            if task.app not in apps:
                apps[task.app] = []
            apps[task.app].append(task)
        
        for app, app_tasks in sorted(apps.items()):
            print(f"\n📱 {app} ({len(app_tasks)} tasks)")
            for task in app_tasks:
                print(f"  [{task.task_id}] {task.name}")
                print(f"      L0: {task.get_instruction('L0')}")
                print(f"      L3: {task.get_instruction('L3')}")
        
        print("\n" + "="*80 + "\n")
    
    def get_androidworld_evaluator(self, task: LayeredTask):
        """
        get ScenDroid evaluator
        
        Based on the task's evaluation configuration, create the corresponding ScenDroid evaluator instance
        
        Args:
            task: LayeredTask instance
            
        Returns:
            TaskEval instance, or None if creation fails
        """
        eval_config = task.get_evaluation_config()
        eval_type = eval_config.get('type')
        androidworld_ref = eval_config.get('androidworld_reference')
        
        if not androidworld_ref:
            logging.warning(f"No ScenDroid reference found for task {task.task_id}")
            return None
        
        # createevaluatorinstance
        return self._create_evaluator_from_reference(task, androidworld_ref, eval_config)
    
    def _create_evaluator_from_reference(self, task: LayeredTask, reference: str, eval_config: Dict[str, Any]):
        """
        Create an evaluator based on the ScenDroid reference
        
        This method creates the actual ScenDroid TaskEval instance according to the task type
        
        Args:
            task: LayeredTask instance
            reference: ScenDroid evaluator class name
            eval_config: evaluationconfiguration
            
        Returns:
            TaskEval instanceor None
        """
        eval_type = eval_config.get('type')
        expected_state = eval_config.get('expected_state', {})
        l0_params = task.get_l0_parameters()
        
        # Create the corresponding ScenDroid evaluator based on the evaluation type
        try:
            # WebArena Shopping task (URL match)
            if eval_type == 'url_match':
                try:
                    from scendroid.task_evals.webarena import webarena_task
                except ImportError as e:
                    logging.error(f"Cannot import webarena_task: {e}")
                    return None
                
                # Construct parameters (do not hardcode URLs; use configuration from JSON)
                # webarena_task.URLMatchWebArenaTask automatically replaces the __SHOPPING__ placeholder
                params = {
                    'task_id': eval_config.get('webarena_task_id', task.task_id),
                    'intent': task.get_l0_instruction(),
                    'start_url': eval_config.get('start_url', '__SHOPPING__'),  # Use placeholder
                    'eval_config': {
                        'eval_types': ['url_match'],
                        'reference_url': expected_state.get('reference_url', ''),
                    },
                    'require_login': eval_config.get('require_login', False),
                }
                return webarena_task.URLMatchWebArenaTask(params)
            
            # WebArena Shopping task (HTML content matching, e.g., shopping cart check)
            if eval_type == 'program_html':
                try:
                    from scendroid.task_evals.webarena import webarena_task
                except ImportError as e:
                    logging.error(f"Cannot import webarena_task: {e}")
                    return None
                
                # Construct parameters
                params = {
                    'task_id': eval_config.get('webarena_task_id', task.task_id),
                    'intent': task.get_l0_instruction(),
                    'start_url': eval_config.get('start_url', '__SHOPPING__'),  # Use placeholder
                    'eval_config': {
                        'eval_types': eval_config.get('eval_types', ['program_html']),
                        'program_html': expected_state.get('program_html', []),
                    },
                    'require_login': eval_config.get('require_login', False),
                }
                return webarena_task.ProgramHTMLWebArenaTask(params)
            
            # For tasks using the lt_ir module, first check lt_ir
            if eval_type == 'information_retrieval_llm_assisted':
                if lt_ir is None:
                    logging.error("layered_tasks_info_retrieval module not available")
                    return None
                
                params = {
                    'has_free_time': expected_state.get('has_free_time', False),
                    'num_events': expected_state.get('num_events', 3),
                }
                return lt_ir.LayeredCalendarCheckFreeFriday(params)
            
            # For other tasks, check the lt module
            if lt is None:
                logging.error("layered_tasks module not available")
                return None
            
            if eval_type == 'clock_alarm':
                # createalarmevaluator
                params = {
                    'alarm_time_hour': expected_state.get('alarm_time_hour', 
                            int(expected_state.get('alarm_time', '08:00').split(':')[0])),
                    'alarm_time_minute': expected_state.get('alarm_time_minute',
                                int(expected_state.get('alarm_time', '08:00').split(':')[1])),
                    'day_offset': expected_state.get('day_offset', 0),
                    'alarm_enabled': expected_state.get('alarm_enabled', True),
                }
                
                # Prioritize attempting to use the new modular evaluator
                if AppRegistry is not None:
                    try:
                        evaluator_class = AppRegistry.get_evaluator('LayeredClockSetAlarm')
                        if evaluator_class is not None:
                            logging.info(f"✅ Using new evaluator: ClockSetAlarmEvaluator")
                            return evaluator_class(params)
                    except Exception as e:
                        logging.warning(f"Failed to load new evaluator, falling back to old evaluator: {e}")
                
                # Fall back to old evaluator
                return lt.LayeredClockSetAlarm(params)
                
            elif eval_type == 'calendar_event':
                # createcalendareventevaluator
                params = {
                    'title': expected_state.get('event_title', 'meeting'),
                    'hour': int(expected_state.get('event_time', '10:00').split(':')[0]),
                    'day_offset': expected_state.get('day_offset', 1),
                    'location': expected_state.get('location', ''),
                    'duration_mins': expected_state.get('duration_minutes', 60),
                }
                
                # Preferentially attempt to use the new modular evaluator
                if AppRegistry is not None:
                    try:
                        evaluator_class = AppRegistry.get_evaluator('LayeredCalendarCreateMeeting')
                        if evaluator_class is not None:
                            logging.info(f"Using new evaluator: CalendarCreateMeetingEvaluator")
                            return evaluator_class(params)
                    except Exception as e:
                        logging.warning(f"Failed to load new evaluator, falling back to old evaluator: {e}")
                
                # Fall back to old evaluator
                return lt.LayeredCalendarCreateMeeting(params)
                
            elif eval_type == 'sms_sent':
                # Create SMS message evaluator
                params = {
                    'contact_name': expected_state.get('recipient', 'Unknown'),
                    'number': expected_state.get('recipient_number', '1234567890'),
                    'message': expected_state.get('message_content', ''),
                }
                return lt.LayeredSmsSendMessage(params)
                
            elif eval_type == 'sms_reply_most_recent':
                # Create SMS reply evaluator
                params = {
                    'contact_name': 'Recent Sender',
                    'number': expected_state.get('sender_number', '5559876543'),
                    'message': expected_state.get('reply_message', ''),
                }
                return lt.LayeredSmsReplyMostRecent(params)
                
            elif eval_type == 'sms_deleted_from_sender':
                # Create SMS delete evaluator
                params = {
                    'sender_name': expected_state.get('sender_name', 'BankAlert'),
                    'sender_number': expected_state.get('sender_number', '5552638265'),
                    'num_target_messages': expected_state.get('num_target_messages', 3),
                    'num_noise_messages': expected_state.get('num_noise_messages', 2),
                    # Parent class requires these but they're not used
                    'contact_name': 'Unused',
                    'number': expected_state.get('sender_number', '5552638265'),
                    'message': 'Unused',
                }
                return lt.LayeredSmsDeleteMessagesFromSender(params)
                
            elif eval_type == 'photo_taken':
                # Create photo capture evaluator
                return lt.LayeredCameraTakePhoto({})
                
            elif eval_type == 'video_taken':
                # Create video recording evaluator
                return lt.LayeredCameraTakeVideo({})
                
            elif eval_type == 'audio_recorded':
                # createaudio recordingevaluator
                return lt.LayeredAudioRecorderRecordAudio({})
                
            elif eval_type == 'file_deleted':
                # createfiledeleteevaluator
                params = {
                    'file_name': expected_state.get('file_name', 'report.pdf'),
                    'subfolder': expected_state.get('subfolder', 'Download'),
                    'noise_candidates': expected_state.get('noise_candidates', [
                        "setup_exe.exe",
                        "sample_pdf.pdf",
                        "test_download.zip",
                        "image_file.png",
                        "movie_trailer.mp4",
                        "software_patch.exe",
                        "ebook_reader.apk",
                        "music_album.zip",
                    ]),
                }
                return lt.LayeredFilesDeleteFile(params)
                
            elif eval_type == 'note_created':
                # create Markor noteevaluator
                params = {
                    'file_name': expected_state.get('file_name', 'grocery_list.md'),
                    'text': expected_state.get('text', 'Milk\nEggs\nRice'),
                }
                return lt.LayeredMarkorCreateNote(params)
                
            elif eval_type == 'expense_added':
                # Create expense evaluator
                params = {
                    'name': expected_state.get('name', 'Lunch'),
                    'amount': expected_state.get('amount', 12.80),
                    'category': expected_state.get('category', 'Food'),
                    'date': expected_state.get('date', '2023-10-15'),
                }
                return lt.LayeredExpenseAddSingle(params)
                
            elif eval_type == 'cross_app_sms_meeting':
                # Create cross-app meeting notification evaluator
                params = {
                    'meeting_hour': expected_state.get('meeting_hour', 11),
                    'meeting_minute': expected_state.get('meeting_minute', 0),
                    'meeting_location': expected_state.get('meeting_location', 'Conference Room A'),
                    'attendees': expected_state.get('attendees', []),
                    'distractor_contacts': expected_state.get('distractor_contacts', []),
                    'other_meetings': expected_state.get('other_meetings', []),
                }
                return lt.LayeredCrossAppMeetingNotification(params)
                
            elif eval_type == 'cross_app_calendar_sms':
                # Create cross-app calendar update + SMS notification evaluator
                params = {
                    'meeting_hour': expected_state.get('meeting_hour', 15),
                    'meeting_minute': expected_state.get('meeting_minute', 30),
                    'meeting_title': expected_state.get('meeting_title', 'Weekly Standup'),
                    'old_location': expected_state.get('old_location', 'Room 302'),
                    'new_location': expected_state.get('new_location', 'Room 405'),
                    'attendees': expected_state.get('attendees', []),
                    'distractor_contacts': expected_state.get('distractor_contacts', []),
                    'other_meetings': expected_state.get('other_meetings', []),
                }
                return lt.LayeredCrossAppMeetingUpdateNotify(params)
                
            elif eval_type == 'opentracks_count':
                # Create OpenTracks statistics evaluator
                if lt_ir is None:
                    logging.error("layered_tasks_info_retrieval module not available")
                    return None
                params = {
                    'category': expected_state.get('category', 'running'),
                    'expected_count': expected_state.get('expected_count', 5),
                }
                return lt_ir.LayeredOpenTracksCountActivities(params)
                
            elif eval_type == 'opentracks_list_categories':
                # create OpenTracks listevaluator
                if lt_ir is None:
                    logging.error("layered_tasks_info_retrieval module not available")
                    return None
                params = {
                    'target_date': expected_state.get('target_date', '2025-12-20'),
                    'categories': expected_state.get('categories', ['Running', 'Cycling']),
                }
                return lt_ir.LayeredOpenTracksListCategories(params)
                
            elif eval_type == 'opentracks_duration':
                # create OpenTracks durationevaluator
                if lt_ir is None:
                    logging.error("layered_tasks_info_retrieval module not available")
                    return None
                params = {
                    'category': expected_state.get('category', 'cycling'),
                    'target_date': expected_state.get('target_date', '2025-12-19'),
                    'duration_minutes': expected_state.get('duration_minutes', 45),
                }
                return lt_ir.LayeredOpenTracksGetDuration(params)
                
            elif eval_type == 'contact_created':
                # create contactevaluator
                # Note: AddContact base class expects 'name', not 'full_name'
                params = {
                    'name': expected_state.get('contact_name', ''),
                    'number': expected_state.get('phone_number', ''),
                    'phone_label': expected_state.get('phone_label', 'Mobile'),
                }
                return lt.LayeredContactsAddContact(params)
                
            elif eval_type == 'timer_running':
                # create Timer evaluator
                params = {
                    'hours': expected_state.get('hours', 0),
                    'minutes': expected_state.get('minutes', 0),
                    'seconds': expected_state.get('seconds', 0),
                }
                return lt.LayeredClockStartTimer(params)
                
            elif eval_type == 'all_alarms_disabled':
                # Create disabled all alarms evaluator
                params = {
                    'num_alarms': expected_state.get('num_initial_alarms', 3),
                }
                return lt.LayeredClockDisableAllAlarms(params)
                
            elif eval_type == 'recurring_event_created':
                # Create recurring event evaluator
                params = {
                    'title': expected_state.get('title', ''),
                    'hour': expected_state.get('hour', 0),
                    'minute': expected_state.get('minute', 0),
                    'day_of_week': expected_state.get('day_of_week', 1),  # 1=Monday
                    'duration_mins': expected_state.get('duration_mins', 60),
                    'description': expected_state.get('description', ''),
                    'repeat_type': expected_state.get('repeat_type', 'weekly'),
                }
                return lt.LayeredCalendarCreateRecurringEvent(params)
                
            elif eval_type == 'events_deleted_on_date':
                # Create delete all events on a specific date evaluator
                params = {
                    'year': expected_state.get('year', 2023),
                    'month': expected_state.get('month', 10),
                    'day': expected_state.get('day', 16),
                    'num_events': expected_state.get('num_initial_events', 3),
                }
                return lt.LayeredCalendarDeleteEventsOnDate(params)
                
            elif eval_type == 'information_retrieval_answer':
                # Create info retrieval evaluator (requires agent response)
                params = {
                    'next_event_title': expected_state.get('next_event_title', 'Project Review'),
                    'next_event_time_hour': expected_state.get('next_event_time_hour', 16),
                    'next_event_time_minute': expected_state.get('next_event_time_minute', 0),
                }
                return lt.LayeredCalendarGetNextEvent(params)
                
            elif eval_type == 'event_deleted_by_time':
                # Create delete event at a specific time evaluator
                params = {
                    'target_hour': expected_state.get('target_hour', 15),
                    'target_minute': expected_state.get('target_minute', 0),
                    'target_title': expected_state.get('target_title', 'Team Meeting'),
                    'num_noise_events': expected_state.get('num_initial_noise_events', 3),
                }
                return lt.LayeredCalendarDeleteEventByTime(params)
                
            elif eval_type == 'cross_app_shopping_expense':
                # Create cross-app Shopping + Expense evaluator
                params = {
                    'product_keywords': expected_state.get('product_keywords', []),
                    'expense_keywords': expected_state.get('expense_keywords', []),
                    'expense_category': expected_state.get('expense_category', 'Others'),
                }
                return lt.LayeredCrossAppShoppingExpense(params)
                
            elif eval_type == 'shopping_address_and_order':
                # Create Shopping address update + order evaluator
                params = {
                    'address_keywords': expected_state.get('address_keywords', []),
                    'product_keywords': expected_state.get('product_keywords', []),
                }
                return lt.LayeredShoppingAddressAndOrder(params)
                
            elif eval_type == 'cross_app_sports_summary':
                # Create cross-app OpenTracks + Markor exercise summary evaluator
                params = {
                    'file_name': expected_state.get('file_name', 'sports_summary.md'),
                    'required_sports': expected_state.get('required_sports', []),
                    'required_fields': expected_state.get('required_fields', []),
                }
                return lt.LayeredCrossAppSportsSummary(params)
                
            elif eval_type == 'shopping_string_match':
                # Create Shopping Q&A evaluator (string match)
                # Use the complete eval_config
                params = {
                    'eval_types': eval_config.get('eval_types', ['string_match']),
                    'reference_answers': eval_config.get('reference_answers', {}),
                    'require_login': eval_config.get('require_login', True),
                    'start_url': eval_config.get('start_url', '__SHOPPING__'),
                    'webarena_task_id': eval_config.get('webarena_task_id', task.task_id),
                    'intent': task.name,  # Use task name as intent
                }
                # add eval_config (required by WebArena)
                params['eval_config'] = {
                    'eval_types': params['eval_types'],
                    'reference_answers': params['reference_answers'],
                }
                return lt.LayeredShoppingStringMatch(params)
                
            elif eval_type == 'shopping_reorder':
                # Create Shopping reorder evaluator (program_html)
                params = {
                    'product_sku': expected_state.get('product_sku', ''),
                    'eval_types': eval_config.get('eval_types', ['program_html']),
                    'program_html': eval_config.get('program_html', []),
                    'require_login': eval_config.get('require_login', True),
                    'start_url': eval_config.get('start_url', '__SHOPPING__'),
                    'webarena_task_id': eval_config.get('webarena_task_id', task.task_id),
                    'intent': task.name,
                }
                # add eval_config (required by WebArena)
                params['eval_config'] = {
                    'eval_types': params['eval_types'],
                    'program_html': params['program_html'],
                }
                return lt.LayeredShoppingReorder(params)
                
            elif eval_type == 'shopping_constrained_purchase':
                # Create Shopping constrained purchase evaluator (program_html)
                params = {
                    'product_sku': expected_state.get('product_sku', ''),
                    'category': expected_state.get('category', ''),
                    'constraints': expected_state.get('constraints', {}),
                    'eval_types': eval_config.get('eval_types', ['program_html']),
                    'program_html': eval_config.get('program_html', []),
                    'require_login': eval_config.get('require_login', True),
                    'start_url': eval_config.get('start_url', '__SHOPPING__'),
                    'webarena_task_id': eval_config.get('webarena_task_id', task.task_id),
                    'intent': task.name,
                }
                # add eval_config (required by WebArena)
                params['eval_config'] = {
                    'eval_types': params['eval_types'],
                    'program_html': params['program_html'],
                }
                return lt.LayeredShoppingConstrainedPurchase(params)
                
            elif eval_type == 'shopping_newsletter':
                # Create Shopping news subscription evaluator (program_html)
                params = {
                    'email': expected_state.get('email', ''),
                    'eval_types': eval_config.get('eval_types', ['program_html']),
                    'program_html': eval_config.get('program_html', []),
                    'require_login': eval_config.get('require_login', True),
                    'start_url': eval_config.get('start_url', '__SHOPPING__'),
                    'webarena_task_id': eval_config.get('webarena_task_id', task.task_id),
                    'intent': task.name,
                }
                # add eval_config (required by WebArena)
                params['eval_config'] = {
                    'eval_types': params['eval_types'],
                    'program_html': params['program_html'],
                }
                return lt.LayeredShoppingNewsletter(params)
                
            elif eval_type == 'shopping_contact_us':
                # Create Shopping contact form evaluator (program_html)
                params = {
                    'order_id': expected_state.get('order_id', ''),
                    'reason': expected_state.get('reason', ''),
                    'refund_amount': expected_state.get('refund_amount', ''),
                    'name': expected_state.get('name', ''),
                    'email': expected_state.get('email', ''),
                    'eval_types': eval_config.get('eval_types', ['program_html']),
                    'program_html': eval_config.get('program_html', []),
                    'require_login': eval_config.get('require_login', True),
                    'start_url': eval_config.get('start_url', '__SHOPPING__'),
                    'webarena_task_id': eval_config.get('webarena_task_id', task.task_id),
                    'intent': task.name,
                }
                # add eval_config (required by WebArena)
                params['eval_config'] = {
                    'eval_types': params['eval_types'],
                    'program_html': params['program_html'],
                }
                return lt.LayeredShoppingContactUs(params)
                
            elif eval_type == 'shopping_update_address':
                # createShoppingaddressupdateevaluator(program_html)
                params = {
                    'street': expected_state.get('street', ''),
                    'suite': expected_state.get('suite', ''),
                    'city': expected_state.get('city', ''),
                    'state': expected_state.get('state', ''),
                    'zipcode': expected_state.get('zipcode', ''),
                    'eval_types': eval_config.get('eval_types', ['program_html']),
                    'program_html': eval_config.get('program_html', []),
                    'require_login': eval_config.get('require_login', True),
                    'start_url': eval_config.get('start_url', '__SHOPPING__'),
                    'webarena_task_id': eval_config.get('webarena_task_id', task.task_id),
                    'intent': task.name,
                }
                # add eval_config (required by WebArena)
                params['eval_config'] = {
                    'eval_types': params['eval_types'],
                    'program_html': params['program_html'],
                }
                return lt.LayeredShoppingUpdateAddress(params)
                
            else:
                logging.warning(f"Unknown evaluation type: {eval_type}")
                return None
                
        except Exception as e:
            logging.error(f"Error creating evaluator for {eval_type}: {e}")
            return None




def main():
    """testfunction"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # loadtask
    loader = LayeredTaskLoader()
    
    # Print summary
    loader.print_task_summary()
    
    # Test get single task
    task = loader.get_task(1)
    if task:
        print(f"\ntestgettask 1:")
        print(f"App: {task.app}")
        print(f"Name: {task.name}")
        print(f"L0: {task.get_instruction('L0')}")
        print(f"L3: {task.get_instruction('L3')}")
        print(f"L0 Parameters: {task.get_l0_parameters()}")


if __name__ == '__main__':
    main()

