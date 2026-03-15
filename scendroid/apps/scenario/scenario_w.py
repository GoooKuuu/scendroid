"""
Scenario W: Weekly Work (7-Day Work Week Scenario)

A complex 7-day scenario with 70 subtasks simulating a complete work week:

Day 1 (Mon): Establish baseline and long-term preferences (10 tasks)
Day 2 (Tue): Cross-day reference resolution and preference alignment (10 tasks)
Day 3 (Wed): Spatiotemporal conflict handling and quality feedback (10 tasks)
Day 4 (Thu): Proactive budget warnings and structured extraction (10 tasks)
Day 5 (Fri): Closure handling and financial audit (10 tasks)
Day 6 (Sat): Cross-app organization and preference verification (10 tasks)
Day 7 (Sun): Automated cleanup and weekly analysis (10 tasks)

Core testing capabilities:
- [REF] Reference resolution: Understanding cross-day references
- [CAU] Causal consistency: Maintaining event chains
- [PRE] Preference alignment: Following user preferences
- [ALT] Active alignment: Proactive reminders when violating preferences
- [CON] Spatiotemporal conflict: Detecting time conflicts
- [AGG] Data aggregation: Summarizing weekly data
- [STR] Structured extraction: Extracting and transforming information
"""

from absl import logging
from typing import List, Dict, Any, Optional
import random

from scendroid.apps.registry import AppRegistry
from scendroid.apps.scenario.seven_day_base import (
    SevenDayScenarioEvaluator,
    SevenDaySubtask,
)


@AppRegistry.register_evaluator("ScenarioW_WeeklyWork")
class ScenarioWWeeklyWorkEvaluator(SevenDayScenarioEvaluator):
    """
    Scenario W: Weekly Work for {user_name} - 7-Day Work Week Scenario
    
    Description:
    Simulates a complete work week from Monday goal-setting to Sunday review.
    Covers schedule management, project collaboration, health habits, and financial control.
    
    Features:
    - 70 subtasks spanning 7 days
    - Complex cross-day references and causal chains
    - Preference learning and active alignment
    - Spatiotemporal conflict handling
    
    Core capabilities tested:
    - Reference resolution [REF]: 6 tasks
    - Causal consistency [CAU]: 4 tasks
    - Preference alignment [PRE]: 8 tasks
    - Active alignment [ALT]: 2 tasks
    - Spatiotemporal conflict [CON]: 2 tasks
    - Data aggregation [AGG]: 2 tasks
    - Structured extraction [STR]: 2 tasks
    """
    
    app_names = (
        "clock", "simple calendar pro", "markor", "simple sms messenger",
        "audio recorder", "tasks", "chrome", "pro expense",
        "broccoli recipe", "opentracks", "files", "camera"
    )
    
    scenario_id = "W"
    complexity = 5.0  # Highest complexity
    
    # ========== Parameter Templates ==========
    PARAM_TEMPLATES = {
        'shared': {
            'user_names': ['David', 'Sarah', 'Michael', 'Emily', 'Alex'],
            'meeting_titles': {
                'kickoff': ['Sprint Kickoff', 'Sprint Planning', 'Sprint Launch'],
                'design': ['Design Review', 'Design Sync', 'UX Review'],
                'sync': ['Sprint Sync', 'Team Sync', 'Weekly Sync'],
            },
            'meeting_locations': ['Room A', 'Room B', 'Conference Room', 'Meeting Room 1'],
            'attendee_groups': [
                ['Alice Smith', 'Bob Johnson', 'Charlie Williams', 'Diana Brown'],
                ['Tom Smith', 'Jerry Johnson', 'Mike Williams', 'Lisa Brown'],
                ['Chris Smith', 'Emma Johnson', 'Ryan Williams', 'Kate Brown'],
            ],
        },
        'products': {
            'table': {
                'sku': 'B07FM3WKJ8',
                'name': 'Outdoor Patio Folding Side Table green',
                'price': 54.99,
            },
            'table_alt': {
                'sku': 'B07FM3WKJ9',
                'name': 'Outdoor Patio Folding Side Table blue',
                'price': 54.99,
            },
            'egg': {
                'sku': 'B078158XZ4',
                'name': 'Egg Organic 12-count',
                'price': 11.80,
            },
            'tide': {
                'sku': 'B074QVN413',
                'name': 'Tide PODS Spring Meadow Scent, 81 Count',
                'price': 68.97,
            },
            'iphone': {
                'sku': 'B07ZQT1L6B',
                'name': 'Apple iPhone 11 Pro, US Version, 256GB, Silver',
                'price': 539.99,
            },
        },
        'alarm': {
            'weekday_hours': [7, 8],
            'weekday_minutes': [0, 15, 30],
            'shift_minutes': [5, 10, 15],
        },
    }
    
    @classmethod
    def generate_random_params(cls, seed: Optional[int] = None) -> dict:
        """Generate random parameters for the scenario"""
        if seed is not None:
            random.seed(seed)
        
        # Shared parameters
        user_name = random.choice(cls.PARAM_TEMPLATES['shared']['user_names'])
        attendees = random.choice(cls.PARAM_TEMPLATES['shared']['attendee_groups'])
        
        # Alarm parameters
        original_hour = random.choice(cls.PARAM_TEMPLATES['alarm']['weekday_hours'])
        original_minute = random.choice(cls.PARAM_TEMPLATES['alarm']['weekday_minutes'])
        shift = random.choice(cls.PARAM_TEMPLATES['alarm']['shift_minutes'])
        
        new_total = original_hour * 60 + original_minute - shift
        new_hour = new_total // 60
        new_minute = new_total % 60
        
        return {
            'seed': seed,
            'shared': {
                'user_name': user_name,
                'kickoff_attendees': attendees,
                'kickoff_location': random.choice(cls.PARAM_TEMPLATES['shared']['meeting_locations']),
                'kickoff_title': random.choice(cls.PARAM_TEMPLATES['shared']['meeting_titles']['kickoff']),
                'design_title': random.choice(cls.PARAM_TEMPLATES['shared']['meeting_titles']['design']),
                'sync_title': random.choice(cls.PARAM_TEMPLATES['shared']['meeting_titles']['sync']),
            },
            'alarm': {
                'original_hour': original_hour,
                'original_minute': original_minute,
                'shift_minutes': shift,
                'new_hour': new_hour,
                'new_minute': new_minute,
            },
            'products': cls.PARAM_TEMPLATES['products'],
        }
    
    def __init__(self, params: dict = None):
        """
        Initialize Scenario W
        
        Args:
            params: Scenario parameters, generates random if None
        """
        if params is None:
            params = {}
        
        # Generate parameters
        if 'generated_params' not in params:
            generated_params = self.generate_random_params(params.get('seed'))
            params['generated_params'] = generated_params
        else:
            generated_params = params['generated_params']
        
        shared = generated_params.get('shared', {})
        user_name = shared.get('user_name', 'David')
        
        # Set scenario metadata
        scenario_params = {
            'scenario_id': 'W',
            'name': f'Weekly Work for {user_name}',
            'start_date': '2026-01-19',  # Monday
            'total_max_steps': 700,
            'generated_params': generated_params,
        }
        
        super().__init__(scenario_params)
        
        # Initialize 7 days
        self._init_days()
        
        # Add all subtasks
        self._add_all_subtasks(generated_params)
    
    def _init_days(self):
        """Initialize 7-day configuration"""
        dates = [
            ('2026-01-19', 'Monday'),
            ('2026-01-20', 'Tuesday'),
            ('2026-01-21', 'Wednesday'),
            ('2026-01-22', 'Thursday'),
            ('2026-01-23', 'Friday'),
            ('2026-01-24', 'Saturday'),
            ('2026-01-25', 'Sunday'),
        ]
        
        for day_idx, (date, day_name) in enumerate(dates):
            self.add_day(day_idx, date, day_name)
    
    def _add_all_subtasks(self, params: dict):
        """Add all 70 subtasks"""
        self._add_day1_subtasks(params)
        self._add_day2_subtasks(params)
        self._add_day3_subtasks(params)
        self._add_day4_subtasks(params)
        self._add_day5_subtasks(params)
        self._add_day6_subtasks(params)
        self._add_day7_subtasks(params)
    
    # ==================== Day 1: Establish Baseline and Long-term Preferences ====================
    
    def _add_day1_subtasks(self, params: dict):
        """Day 1 (Monday): Establish baseline and long-term preferences"""
        shared = params.get('shared', {})
        alarm = params.get('alarm', {})
        products = params.get('products', {})
        
        user_name = shared.get('user_name', 'David')
        attendees = shared.get('kickoff_attendees', ['Alice Smith', 'Bob Johnson', 'Charlie Williams', 'Diana Brown'])
        location = shared.get('kickoff_location', 'Room A')
        kickoff_title = shared.get('kickoff_title', 'Sprint Kickoff')
        
        new_hour = alarm.get('new_hour', 7)
        new_minute = alarm.get('new_minute', 50)
        shift = alarm.get('shift_minutes', 10)
        
        table = products.get('table', self.PARAM_TEMPLATES['products']['table'])
        
        # W1-01: Adjust weekday alarm
        self.add_subtask_to_day(
            day_idx=0,
            subtask_id=1,
            task_id="W1-01",
            evaluator_name="LayeredClockSetAlarm",
            params={
                "alarm_time_hour": new_hour,
                "alarm_time_minute": new_minute,
                "alarm_enabled": True,
                "check_original_removed": True,
                "original_hour": alarm.get('original_hour', 8),
                "original_minute": alarm.get('original_minute', 0),
            },
            time="06:55",
            narration=f"{user_name} almost overslept this morning, decides to wake up earlier this week",
            user_instruction=f"Good morning! I want to wake up {shift} minutes earlier every weekday this week. Change my weekday alarm. Don't touch the weekend alarm.",
            max_steps=20,
            context_updates={
                'alarm_adjusted': True,
                'alarm_shift': shift,
            },
        )
        
        # W1-02: Check morning schedule
        self.add_subtask_to_day(
            day_idx=0,
            subtask_id=2,
            task_id="W1-02",
            evaluator_name="LayeredCalendarCheckMeetingAnswer",
            params={
                "must_contain_keywords": ["meeting", kickoff_title.split()[0].lower()],
                "min_keywords_found": 1,
            },
            time="07:10",
            narration=f"{user_name} wants to check the morning schedule before heading out",
            user_instruction="Check Simple Calendar Pro and tell me what meetings I have this morning before 12 PM.",
            max_steps=20,
            requires_answer=True,
        )
        
        # W1-03: Create WeekPlan.md (establish preferences)
        self.add_subtask_to_day(
            day_idx=0,
            subtask_id=3,
            task_id="W1-03",
            evaluator_name="LayeredMarkorCreateOutline",
            params={
                "file_name": "WeekPlan.md",
                "required_sections": ["Diet", "Budget", "Exercise"],
                "sections_with_content": ["Diet", "Budget", "Exercise"],
            },
            time="07:25",
            narration=f"{user_name} wants to set up this week's plan and personal constraints",
            user_instruction=f"Open Markor and create a new file called WeekPlan.md. Record my weekly goals: (1) Diet - I'm on a weight loss plan, only light food, no fried stuff; (2) Budget - dining expenses should stay within $120, if I want to buy something that exceeds this, ask me first; (3) Exercise - I want to exercise at 18:30 daily for 30 minutes, if I try to schedule something at that time, remind me about this.",
            max_steps=25,
            tags=["PRE"],
            context_updates={
                'preference:diet:restriction': 'light',
                'preference:diet:forbidden': ['fried'],
                'preference:budget:dining': 120.0,
                'preference:schedule:exercise': {'time': '18:30', 'duration': 30},
            },
        )
        
        # W1-04: Extract kickoff meeting attendees
        # Note: Use first names for matching (user may only mention first names)
        attendee_first_names = [name.split()[0] for name in attendees]
        self.add_subtask_to_day(
            day_idx=0,
            subtask_id=4,
            task_id="W1-04",
            evaluator_name="LayeredCalendarExtractAttendees",
            params={
                "event_title": kickoff_title,
                "required_attendees": attendee_first_names,  # First names only for flexible matching
                "min_attendees_found": len(attendees),
            },
            time="08:25",
            narration=f"{user_name} is about to join the kickoff meeting and needs the details",
            user_instruction=f"Open Simple Calendar Pro, find the '{kickoff_title}' meeting today, and tell me the location and all the attendees.",
            max_steps=20,
            requires_answer=True,
            context_updates={
                f'meeting:{kickoff_title.lower().replace(" ", "_")}': {
                    'title': kickoff_title,
                    'attendees': attendees,
                    'location': location,
                    'day_idx': 0,
                },
            },
        )
        
        # W1-05: Send meeting reminders
        self.add_subtask_to_day(
            day_idx=0,
            subtask_id=5,
            task_id="W1-05",
            evaluator_name="LayeredSMSBatchNotify",
            params={
                "required_recipients": attendees,  # Now full names from params
                "message_must_contain_time": "09:00",
                "message_must_contain_location": [location],
                "min_messages_sent": len(attendees),
            },
            time="08:35",
            narration=f"{user_name} wants to remind all attendees about the upcoming meeting",
            user_instruction=f"Use Simple SMS Messenger to send a reminder to all those attendees from the {kickoff_title}. Include the meeting time and location.",
            max_steps=30,
        )
        
        # W1-06: Meeting recording
        self.add_subtask_to_day(
            day_idx=0,
            subtask_id=6,
            task_id="W1-06",
            evaluator_name="LayeredAudioRecorderRecordAudio",
            params={},
            time="09:05",
            narration=f"{user_name} wants to record the kickoff meeting for later reference",
            user_instruction="Open Audio Recorder app and record the meeting. Save the recording when done.",
            max_steps=20,
            context_updates={
                'audio:kickoff_recording': {
                    'filename': 'recording_temp',
                    'day_idx': 0,
                    'type': 'meeting',
                },
            },
        )
        
        # W1-07: Rename recording
        self.add_subtask_to_day(
            day_idx=0,
            subtask_id=7,
            task_id="W1-07",
            evaluator_name="LayeredAudioRecorderRename",
            params={
                "expected_filename": "SprintKickoff_Mon",
            },
            time="09:25",
            narration=f"{user_name} wants to organize the recording with a meaningful name",
            user_instruction="Open Audio Recorder, find the recording I just made, and rename it to 'SprintKickoff_Mon' so I can find it later.",
            max_steps=20,
            context_updates={
                'audio:sprint_kickoff': {
                    'filename': 'SprintKickoff_Mon',
                    'day_idx': 0,
                },
            },
        )
        
        # W1-08: Create Sprint task list with 4 tasks
        # Check all 4 tasks are created in the specified list
        self.add_subtask_to_day(
            day_idx=0,
            subtask_id=8,
            task_id="W1-08",
            evaluator_name="LayeredTasksCreateMultiple",
            params={
                "list_name": "Sprint Action Items",
                "tasks": [
                    {"title": "Send Draft", "due_day": "Wednesday"},
                    {"title": "Collect Feedback", "due_day": "Thursday"},
                    {"title": "Finalize", "due_day": "Friday"},
                    {"title": "Schedule Sync", "due_day": "Thursday"},
                ],
                "strict": True,  # All 4 tasks must exist
            },
            time="10:40",
            narration=f"{user_name} needs to create a task list for this week's sprint",
            user_instruction="Open Tasks app and create a new list called 'Sprint Action Items'. Add these 4 tasks: 'Send Draft' due Wednesday, 'Collect Feedback' due Thursday, 'Finalize' due Friday, and 'Schedule Sync' due Thursday.",
            max_steps=25,
        )
        
        # W1-09: Purchase outdoor table
        self.add_subtask_to_day(
            day_idx=0,
            subtask_id=9,
            task_id="W1-09",
            evaluator_name="LayeredShoppingPurchaseProduct",
            params={
                "product_sku": table['sku'],
                "product_price": table['price'],
                "check_method": "order",
                "eval_types": ["program_html"],
                "program_html": [
                    {
                        "url": "func:shopping_get_latest_order_url()",
                        "locator": "document.querySelector('.order-details-items.ordered').outerText",
                        "required_contents": {
                            "must_include": [table['sku']]
                        }
                    }
                ],
                "require_login": True,
                "start_url": "__SHOPPING__",
            },
            time="12:20",
            narration=f"{user_name} needs a new outdoor table for the patio",
            user_instruction=f"On the current webpage, search for the green '{table['name']}' and place an order.",
            max_steps=30,
            context_updates={
                'chain:table_purchase': {
                    'action': 'purchase',
                    'task_id': 'W1-09',
                    'sku': table['sku'],
                    'name': table['name'],
                    'price': table['price'],
                },
            },
        )
        
        # W1-10: Log expense and write summary
        # evaluation check whether WorkLog.md contains: all attendees' first names + audio recording file name + table amount (54.99)
        # Strict mode: all keywords must appear; scoring yields only 0 or 1
        # Note: only first names (e.g., Alice, Bob) are checked, not full names
        first_names = [name.split()[0] for name in attendees]  # Extract first names
        self.add_subtask_to_day(
            day_idx=0,
            subtask_id=10,
            task_id="W1-10",
            evaluator_name="LayeredMarkorAppendContent",
            params={
                "file_name": "WorkLog.md",
                "must_mention_meeting": True,
                "meeting_keywords": first_names + ["SprintKickoff_Mon"],  # first names + audio recording file name
                "require_all_keywords": True,  # Require all keywords to appear
                "must_mention_expense": True,
                "expense_amount": 54.99,  # Table amount fixed at 54.99
                "strict_scoring": True,  # Return only 0 or 1
            },
            time="21:05",
            narration=f"{user_name} wraps up the day by logging expenses and writing a summary",
            user_instruction=f"Two things: First, open Pro Expense and log the table I bought today (category: Others). Second, open Markor and create WorkLog.md, record today's summary - include the names of people I sent SMS to, the audio recording filename, and the price of the table.",
            max_steps=25,
        )
    
    # ==================== Day 2: Cross-day Reference and Preference Alignment ====================
    
    def _add_day2_subtasks(self, params: dict):
        """Day 2 (Tuesday): Cross-day reference and preference alignment"""
        shared = params.get('shared', {})
        user_name = shared.get('user_name', 'David')
        attendees = shared.get('kickoff_attendees', ['Alice Smith', 'Bob Johnson', 'Charlie Williams', 'Diana Brown'])
        kickoff_title = shared.get('kickoff_title', 'Sprint Kickoff')
        
        # W2-01: Check afternoon availability
        # Note: There's a "Client Call" at 15:00 so afternoon is NOT free
        self.add_subtask_to_day(
            day_idx=1,
            subtask_id=11,
            task_id="W2-01",
            evaluator_name="LayeredCalendarCheckAvailability",
            params={
                "start_time": "13:00",
                "end_time": "18:00",
                "expected_answer": "busy",  # There's a Client Call at 15:00
            },
            time="07:35",
            narration=f"{user_name} needs to check if the afternoon is free for a new appointment",
            user_instruction="Check my Simple Calendar Pro - am I free this afternoon between 1 PM and 6 PM?",
            max_steps=20,
            requires_answer=True,
        )
        
        # W2-02: [REF] Find yesterday's recording
        self.add_subtask_to_day(
            day_idx=1,
            subtask_id=12,
            task_id="W2-02",
            evaluator_name="LayeredFilesSearch",
            params={
                "search_pattern": "SprintKickoff",
                "expected_path_contains": "SprintKickoff_Mon",
            },
            time="09:10",
            narration=f"{user_name} needs to review yesterday's kickoff recording",
            user_instruction="I need to review yesterday's kickoff meeting. Use the Files app to find that recording I made and tell me the filename and where it's stored.",
            max_steps=20,
            requires_answer=True,
            tags=["REF"],
            reference_params={
                "hint_filename": "yesterday kickoff recording",
            },
        )
        
        # W2-03: Create follow-up document
        self.add_subtask_to_day(
            day_idx=1,
            subtask_id=13,
            task_id="W2-03",
            evaluator_name="LayeredMarkorCreateOutline",
            params={
                "file_name": "KickoffFollowup.md",
                "required_sections": ["Decisions", "Owners", "Deadlines"],
            },
            time="09:20",
            narration=f"{user_name} creates a template for meeting follow-up",
            user_instruction="Create a new file in Markor called 'KickoffFollowup.md' with placeholder sections for: Decisions, Owners, and Deadlines. I'll fill these in after I hear back from the team.",
            max_steps=20,
        )
        
        # W2-04: [REF] Follow up with attendees
        self.add_subtask_to_day(
            day_idx=1,
            subtask_id=14,
            task_id="W2-04",
            evaluator_name="LayeredSMSBatchNotify",
            params={
                "required_recipients": [f"{name} Smith" for name in attendees[:2]] + 
                                       [f"{name} Johnson" for name in attendees[2:]],
                "message_must_contain_keywords": ["confirm", "owner"],
                "min_messages_sent": len(attendees),
            },
            time="10:00",
            narration=f"{user_name} follows up with yesterday's meeting attendees",
            user_instruction=f"Send a message via SMS to everyone who was at yesterday's {kickoff_title}. Ask them to confirm who owns which tasks and when they're due.",
            max_steps=30,
            tags=["REF"],
            reference_params={
                "recipients_hint": "people from yesterday's meeting",
            },
        )
        
        # W2-05: Log lunch expense
        self.add_subtask_to_day(
            day_idx=1,
            subtask_id=15,
            task_id="W2-05",
            evaluator_name="LayeredExpenseAddSingle",
            params={
                "name": "Lunch",
                "amount": 14.0,
                "category": "Food",  # Pro Expense uses the Food category
                "note": "Keep it light this week",
            },
            time="12:05",
            narration=f"{user_name} logs the lunch expense",
            user_instruction="Just had lunch - log $14 in Pro Expense under Food category. Add note: 'Keeping it light this week'.",
            max_steps=20,
        )
        
        # W2-06: [PRE] Find dinner recipe
        # Target answer: "Steamed Vegetable Medley" - clearly light and healthy
        self.add_subtask_to_day(
            day_idx=1,
            subtask_id=16,
            task_id="W2-06",
            evaluator_name="LayeredBroccoliRecipeSearch",
            params={
                "diet_type": "light",
                "forbidden_ingredients": ["fried", "deep_fried", "oily"],
                "expected_recipe_keywords": ["steamed", "vegetable", "grilled", "salmon", "light", "healthy"],
            },
            time="17:10",
            narration=f"{user_name} looks for a dinner recipe that fits this week's diet",
            user_instruction="Find me a dinner recipe in Broccoli app - remember my preference in my WeekPlan. Tell me the recipe name.",
            max_steps=25,
            requires_answer=True,
            tags=["PRE"],
            preference_check={
                "diet": {"check": True},
            },
        )
        
        # W2-07: Save recipe
        self.add_subtask_to_day(
            day_idx=1,
            subtask_id=17,
            task_id="W2-07",
            evaluator_name="LayeredMarkorAppendContent",
            params={
                "file_name": "WeekMeals.md",
                "content_must_contain": ["recipe", "steps"],
            },
            time="17:20",
            narration=f"{user_name} saves the recipe for later",
            user_instruction="Save that recipe to WeekMeals.md (If it doesn't exist, create one.) in Markor - include the name and cooking steps.",
            max_steps=20,
        )
        
        # W2-08: Cooking timer
        self.add_subtask_to_day(
            day_idx=1,
            subtask_id=18,
            task_id="W2-08",
            evaluator_name="LayeredClockStartTimer",
            params={
                "duration_minutes": 15,
            },
            time="17:40",
            narration=f"{user_name} sets a timer for cooking",
            user_instruction="Set a 15-minute timer in Clock for cooking.",
            max_steps=15,
        )
        
        # W2-09: Exercise routine
        self.add_subtask_to_day(
            day_idx=1,
            subtask_id=19,
            task_id="W2-09",
            evaluator_name="LayeredOpenTracksRecord",
            params={
                "activity_type": "Walking",
                "min_duration_seconds": 10,
            },
            time="18:35",
            narration=f"{user_name} goes for the daily walk",
            user_instruction="Time for my daily exercise! Start recording a walk in OpenTracks, set type to Walking.",
            max_steps=20,
        )
        
        # W2-10: [REF] Daily summary
        self.add_subtask_to_day(
            day_idx=1,
            subtask_id=20,
            task_id="W2-10",
            evaluator_name="LayeredMarkorAppendContent",
            params={
                "file_name": "WorkLog.md",
                "content_must_contain": ["recipe", "exercise"],
            },
            time="22:40",
            narration=f"{user_name} wraps up the day with a summary",
            user_instruction="Add today's summary to WorkLog.md - mention what recipe I made and whether I exercised.",
            max_steps=20,
            tags=["REF"],
        )
    
    # ==================== Day 3: Spatiotemporal Conflict and Quality Feedback ====================
    
    def _add_day3_subtasks(self, params: dict):
        """Day 3 (Wednesday): Spatiotemporal conflict handling and quality feedback"""
        shared = params.get('shared', {})
        products = params.get('products', {})
        
        user_name = shared.get('user_name', 'David')
        design_title = shared.get('design_title', 'Design Review')
        kickoff_title = shared.get('kickoff_title', 'Sprint Kickoff')
        table = products.get('table', self.PARAM_TEMPLATES['products']['table'])
        
        # W3-01: Temporary alarm
        self.add_subtask_to_day(
            day_idx=2,
            subtask_id=21,
            task_id="W3-01",
            evaluator_name="LayeredClockSetAlarm",
            params={
                "alarm_time_hour": 8,
                "alarm_time_minute": 40,
                "alarm_enabled": True,
                "alarm_label": "Leave",
                "one_time": True,
            },
            time="07:15",
            narration=f"{user_name} needs a reminder to leave early for an appointment today",
            user_instruction="I have an appointment today - set a one-time alarm for 8:40 AM labeled 'Leave'. Just for today, not recurring.",
            max_steps=20,
        )
        
        # W3-02: [CON] Check conflict with exercise time
        # Agent should recognize the 18:30 exercise habit conflicts with 18:00-19:00 meeting
        # Success = agent reports conflict and does NOT create the event
        self.add_subtask_to_day(
            day_idx=2,
            subtask_id=22,
            task_id="W3-02",
            evaluator_name="LayeredCalendarCheckConflict",
            params={
                "event_title": design_title,
                "start_time": "18:00",
                "end_time": "19:00",
                "conflict_time": "18:30",  # Exercise habit time
                # If event is NOT created, task passes
            },
            time="10:10",
            narration=f"{user_name} wants to schedule a meeting but it conflicts with exercise time",
            user_instruction=f"I want to add a '{design_title}' meeting today from 6 PM to 7 PM. Is there any schedule conflict? If yes, tell me about it and don't create the meeting.",
            max_steps=25,
            requires_answer=True,
            tags=["CON"],
            preference_check={
                "schedule": {"time": "18:00", "duration": 60},
            },
        )
        
        # W3-04: Record voice memo with specific format
        # Use WAV format at 32kHz for better quality
        self.add_subtask_to_day(
            day_idx=2,
            subtask_id=23,
            task_id="W3-04",
            evaluator_name="LayeredAudioRecorderWithConfig",
            params={
                "recording_name": "DesignNotes",
                "expected_format": "wav",
                "expected_sample_rate": "32kHz",  # Can be 32kHz or 44kHz
            },
            time="15:20",
            narration=f"{user_name} wants to record design notes in high quality",
            user_instruction="Open Audio Recorder. First, go to settings and change the format to WAV and sample rate to 32kHz. Then record a memo and name it 'DesignNotes'.",
            max_steps=30,
        )
        
        # W3-05: Organize memo - rename the WAV file from W3-04
        # The file is at: /storage/emulated/0/Android/data/com.dimowner.audiorecorder/files/Music/records/
        self.add_subtask_to_day(
            day_idx=2,
            subtask_id=24,
            task_id="W3-05",
            evaluator_name="LayeredAudioRecorderRename",
            params={
                "expected_filename": "DesignReview_Wed",  # Renamed from "DesignNotes" (W3-04)
            },
            time="15:35",
            narration=f"{user_name} organizes the voice memo just recorded",
            user_instruction="Find the 'DesignNotes' recording I just made in Audio Recorder and rename it to 'DesignReview_Wed'.",
            max_steps=25,
        )
        
        # W3-06: [REF] Update task note
        # Note: Use a generic keyword list instead of relying on kickoff_title from note_content
        # Because the user instruction uses "Monday's kickoff meeting" rather than a specific meeting name
        self.add_subtask_to_day(
            day_idx=2,
            subtask_id=25,
            task_id="W3-06",
            evaluator_name="LayeredTasksUpdateNote",
            params={
                "list_name": "Sprint Action Items",
                "task_title": "Send Draft",
                "note_keywords": ["attendee", "list", "Monday", "kickoff"],  # Explicitly specify keywords
            },
            time="16:10",
            narration=f"{user_name} adds a reminder note to the Sprint task",
            user_instruction="In my Tasks app, find 'Send Draft' in the 'Sprint Action Items' list and add a note: 'Use the attendee list from Monday's kickoff meeting'.",
            max_steps=20,
            tags=["REF"],
        )
        
        # W3-07: [CAU] Request return
        # W3-07 uses program_html evaluation to check contact form content
        self.add_subtask_to_day(
            day_idx=2,
            subtask_id=26,
            task_id="W3-07",
            evaluator_name="LayeredShoppingContactUs",
            params={
                "subject": "Return Request",
                "message_must_contain": ["unstable", "wobbly", table['sku']],
                "reference_order_sku": table['sku'],
                # program_html config for evaluation - checks Contact Us form textarea content
                "eval_types": ["program_html"],
                "program_html": [
                    {
                        "url": "last",  # Check current page
                        "locator": "document.querySelector('[title=\"What\\'s on your mind?\"]').value",
                        "required_contents": {
                            "must_include": [
                                "unstable",  # Reason for return
                                table['sku'],  # SKU code
                            ]
                        }
                    }
                ],
            },
            time="19:40",
            narration=f"{user_name} discovered the table from Monday is defective",
            user_instruction=f"Ugh, that outdoor table I ordered Monday is wobbly and unstable! Go to the Shopping website, find their 'Contact Us' page, and send a message about wanting to return it. Mention it's unstable, and include the SKU ({table['sku']}). Don't submit yet.",
            max_steps=30,
            tags=["CAU"],
            reference_params={
                "order_reference": "table bought on Monday",
            },
            context_updates={
                'chain:table_purchase': {
                    'action': 'return_request',
                    'task_id': 'W3-07',
                    'reason': 'unstable',
                },
            },
        )
        
        # W3-08: Record return
        self.add_subtask_to_day(
            day_idx=2,
            subtask_id=27,
            task_id="W3-08",
            evaluator_name="LayeredMarkorAppendContent",
            params={
                "file_name": "WorkLog.md",
                "content_must_contain": ["return", "table"],
            },
            time="20:00",
            narration=f"{user_name} logs the return issue for reference",
            user_instruction="Add a note to WorkLog.md: Started return process for the patio table because it's unstable.",
            max_steps=20,
        )
        
        # W3-09: Delayed exercise
        self.add_subtask_to_day(
            day_idx=2,
            subtask_id=28,
            task_id="W3-09",
            evaluator_name="LayeredOpenTracksCreateActivity",  # ✅ Correct evaluator name
            params={
                "activity_type": "Walking",
                "min_duration_seconds": 10,
            },
            time="20:30",
            narration=f"{user_name} finally has time for the delayed exercise",
            user_instruction="Finally done with the meeting! Start recording my exercise in OpenTracks.",
            max_steps=20,
        )
        
        # W3-10: Conflict review
        self.add_subtask_to_day(
            day_idx=2,
            subtask_id=29,
            task_id="W3-10",
            evaluator_name="LayeredMarkorAppendContent",
            params={
                "file_name": "WorkLog.md",
                "content_must_contain": ["conflict", "exercise", "table"],
            },
            time="22:30",
            narration=f"{user_name} reflects on today's schedule challenges",
            user_instruction="Add my Wednesday summary to WorkLog.md: Had to handle meeting conflict (delayed exercise), also filed complaint about the defective table.",
            max_steps=20,
        )
    
    # ==================== Day 4: Proactive Budget Warning and Structured Extraction ====================
    
    def _add_day4_subtasks(self, params: dict):
        """Day 4 (Thursday): Proactive budget warning and structured extraction"""
        shared = params.get('shared', {})
        products = params.get('products', {})
        
        user_name = shared.get('user_name', 'David')
        attendees = shared.get('kickoff_attendees', ['Alice Smith', 'Bob Johnson', 'Charlie Williams', 'Diana Brown'])
        design_title = shared.get('design_title', 'Design Review')
        sync_title = shared.get('sync_title', 'Sprint Sync')
        egg = products.get('egg', self.PARAM_TEMPLATES['products']['egg'])
        
        # W4-01: Adjust recording settings
        self.add_subtask_to_day(
            day_idx=3,
            subtask_id=30,
            task_id="W4-01",
            evaluator_name="LayeredAudioRecorderWithConfig",  # ✅ Correct evaluator name
            params={
                "recording_name": "AudioTest",  # Name of the test audio recording
                "expected_format": "wav",
                "expected_sample_rate": "32kHz",
            },
            time="07:50",
            narration=f"{user_name} wants to improve audio quality for recordings",
            user_instruction="Open Audio Recorder settings and change the format to WAV at 32kHz for better quality. Make a quick test recording and name it 'AudioTest'.",
            max_steps=25,
        )
        
        # W4-02: Store test file
        self.add_subtask_to_day(
            day_idx=3,
            subtask_id=31,
            task_id="W4-02",
            evaluator_name="LayeredFilesCreateFolder",  # ✅ Correct evaluator
            params={
                "folder_path": "AudioTests",  # ✅ Correct parameter name
            },
            time="08:05",
            narration=f"{user_name} keeps test recordings organized separately",
            user_instruction="Create a folder called 'AudioTests' in Files.",  # Simplified instruction: create only the folder
            max_steps=20,
        )
        
        # W4-03: Schedule next meeting
        self.add_subtask_to_day(
            day_idx=3,
            subtask_id=32,
            task_id="W4-03",
            evaluator_name="LayeredCalendarCreateMeeting",  # ✅ Correct evaluator name
            params={
                "event_title": sync_title,
                "start_time": "10:00",
                "location": "Room A",
                "day_offset": 1,  # Tomorrow
            },
            time="09:30",
            narration=f"{user_name} sets up tomorrow's sync meeting",
            user_instruction=f"Schedule a '{sync_title}' meeting for tomorrow at 10 AM in Room A. Invite the same people from Monday's kickoff.",
            max_steps=25,
            context_updates={
                f'meeting:{sync_title.lower().replace(" ", "_")}': {
                    'title': sync_title,
                    'attendees': attendees,
                    'location': 'Room A',
                    'day_idx': 4,
                },
            },
        )
        
        # W4-04: [REF] Contact design review attendees
        self.add_subtask_to_day(
            day_idx=3,
            subtask_id=33,
            task_id="W4-04",
            evaluator_name="LayeredSMSBatchNotify",
            params={
                "required_recipients": [f"{name} Smith" for name in attendees[:2]] + 
                                       [f"{name} Johnson" for name in attendees[2:]],
                "message_must_contain_keywords": ["opinion", "sync"],
                "min_messages_sent": len(attendees),
            },
            time="11:20",
            narration=f"{user_name} needs feedback from yesterday's design review",
            user_instruction=f"Text the people who were at yesterday's {design_title} - ask them to send their final opinions before tomorrow's sync meeting.",
            max_steps=30,
            tags=["REF"],
            reference_params={
                "recipients_hint": "people from yesterday's design review",
            },
        )
        
        # W4-05: [ALT] Budget check
        self.add_subtask_to_day(
            day_idx=3,
            subtask_id=34,
            task_id="W4-05",
            evaluator_name="LayeredExpenseCheckBudget",
            params={
                "category": "Dining",
                "budget_limit": 120.0,
            },
            time="12:10",
            narration=f"{user_name} wants to check if the dining budget is on track",
            user_instruction="Open Pro Expense and check my Dining category total for this week. Am I close to the $120 budget I set?",
            max_steps=20,
            requires_answer=True,
            tags=["ALT"],
        )
        
        # W4-06: [PRE] Budget-aligned task
        self.add_subtask_to_day(
            day_idx=3,
            subtask_id=35,
            task_id="W4-06",
            evaluator_name="LayeredTasksCreateTask",
            params={
                "title": "Cook at Home",
                "due_day_offset": 1,  # Tomorrow
                "note": "Follow WeekPlan budget and light diet requirements",
            },
            time="12:25",
            narration=f"{user_name} plans to save money by cooking at home",
            user_instruction="Create a task for tomorrow called 'Cook at Home' - add a note reminding me to follow the budget and light diet goals from WeekPlan.",
            max_steps=20,
            tags=["PRE"],
        )
        
        # W4-07: [PRE] Find tomorrow's recipe
        self.add_subtask_to_day(
            day_idx=3,
            subtask_id=36,
            task_id="W4-07",
            evaluator_name="LayeredBroccoliRecipeSearch",
            params={
                "diet_type": "light",
                "for_tomorrow": True,
            },
            time="16:40",
            narration=f"{user_name} looks for a recipe for tomorrow's dinner",
            user_instruction="Find me a nice light recipe for tomorrow night's dinner - something that fits my diet plan.",
            max_steps=25,
            requires_answer=True,
            tags=["PRE"],
        )
        
        # W4-08: [STR] Generate shopping list
        self.add_subtask_to_day(
            day_idx=3,
            subtask_id=37,
            task_id="W4-08",
            evaluator_name="LayeredTasksCreateFromContent",
            params={
                "source": "latest_recipe",
                "list_name": "Friday Grocery List",
                "extract_type": "ingredients",
            },
            time="16:55",
            narration=f"{user_name} extracts ingredients into a shopping list",
            user_instruction="Take the ingredients from that recipe and create a 'Friday Grocery List' in Tasks with quantities.",
            max_steps=25,
            tags=["STR"],
        )
        
        # W4-09: Buy eggs
        self.add_subtask_to_day(
            day_idx=3,
            subtask_id=38,
            task_id="W4-09",
            evaluator_name="LayeredShoppingPurchaseProduct",
            params={
                "product_sku": egg['sku'],
                "product_price": egg['price'],
                "check_method": "order",
                "eval_types": ["program_html"],
                "program_html": [
                    {
                        "url": "func:shopping_get_latest_order_url()",
                        "locator": "document.querySelector('.order-details-items.ordered').outerText",
                        "required_contents": {
                            "must_include": [egg['sku']]
                        }
                    }
                ],
                "require_login": True,
                "start_url": "__SHOPPING__",
            },
            time="17:20",
            narration=f"{user_name} orders the key ingredient online",
            user_instruction=f"Order '{egg['name']}' from Shopping - it's the main ingredient I need for tomorrow.",
            max_steps=30,
            context_updates={
                'chain:egg_purchase': {
                    'action': 'purchase',
                    'task_id': 'W4-09',
                    'sku': egg['sku'],
                    'name': egg['name'],
                    'price': egg['price'],
                },
            },
        )
        
        # W4-10: Record budget logic
        self.add_subtask_to_day(
            day_idx=3,
            subtask_id=39,
            task_id="W4-10",
            evaluator_name="LayeredMarkorAppendContent",
            params={
                "file_name": "WorkLog.md",
                "content_must_contain": ["budget", "light"],
            },
            time="22:00",
            narration=f"{user_name} reflects on budget-conscious decisions",
            user_instruction="Add Thursday's summary to WorkLog.md - mention checking budget and planning to cook light at home tomorrow.",
            max_steps=20,
        )
    
    # ==================== Day 5: Closure and Financial Audit ====================
    
    def _add_day5_subtasks(self, params: dict):
        """Day 5 (Friday): Closure handling and financial audit"""
        shared = params.get('shared', {})
        products = params.get('products', {})
        
        user_name = shared.get('user_name', 'David')
        attendees = shared.get('kickoff_attendees', ['Alice Smith', 'Bob Johnson', 'Charlie Williams', 'Diana Brown'])
        sync_title = shared.get('sync_title', 'Sprint Sync')
        table = products.get('table', self.PARAM_TEMPLATES['products']['table'])
        table_alt = products.get('table_alt', self.PARAM_TEMPLATES['products']['table_alt'])
        egg = products.get('egg', self.PARAM_TEMPLATES['products']['egg'])
        
        # W5-01: Disable Saturday alarm
        self.add_subtask_to_day(
            day_idx=4,
            subtask_id=40,
            task_id="W5-01",
            evaluator_name="LayeredClockDisableAlarm",
            params={
                "day_of_week": "Saturday",
                "preserve_weekday": True,
            },
            time="07:30",
            narration=f"{user_name} wants to sleep in tomorrow",
            user_instruction="It's Friday! Turn off my Saturday morning alarm so I can sleep in - but don't touch the weekday alarms.",
            max_steps=20,
        )
        
        # W5-02: Confirm sync meeting
        self.add_subtask_to_day(
            day_idx=4,
            subtask_id=41,
            task_id="W5-02",
            evaluator_name="LayeredCalendarEventDetails",
            params={
                "event_title": sync_title,
                "expected_attendees": attendees,
            },
            time="08:40",
            narration=f"{user_name} double-checks today's meeting details",
            user_instruction=f"Check the calendar - when is today's {sync_title}? What's the location and who's attending?",
            max_steps=20,
            requires_answer=True,
        )
        
        # W5-03: Complete task
        self.add_subtask_to_day(
            day_idx=4,
            subtask_id=42,
            task_id="W5-03",
            evaluator_name="LayeredTasksComplete",
            params={
                "task_title": "Cook at Home",
                "update_file": "WeekMeals.md",
            },
            time="18:10",
            narration=f"{user_name} finished cooking and wants to update tasks",
            user_instruction="Done cooking! Mark 'Cook at Home' as complete in Tasks, and log what I made in WeekMeals.md.",
            max_steps=25,
        )
        
        # W5-04: Precise expense tracking
        self.add_subtask_to_day(
            day_idx=4,
            subtask_id=43,
            task_id="W5-04",
            evaluator_name="LayeredExpenseAddMultiple",
            params={
                "expenses": [
                    {"name": "Groceries", "amount": 9.0, "category": "Food", "note": "Follows WeekPlan"},
                    {"name": "Egg", "amount": egg['price'], "category": "Food"},
                ],
            },
            time="18:25",
            narration=f"{user_name} logs today's grocery expenses",
            user_instruction=f"Add two expenses in Pro Expense: $9 for today's groceries (Food category, note 'Follows WeekPlan'), and ${egg['price']} for the eggs I ordered yesterday.",
            max_steps=25,
        )
        
        # W5-06: [CAU] Financial refund
        self.add_subtask_to_day(
            day_idx=4,
            subtask_id=44,
            task_id="W5-06",
            evaluator_name="LayeredExpenseAddRefund",
            params={
                "name": "Table Refund",
                "amount": table['price'],
                "category": "Refund",
                "note": "Return initiated on Wednesday",
            },
            time="19:25",
            narration=f"{user_name} got the table refund processed",
            user_instruction=f"Got my refund for the table! Log ${table['price']} as 'Table Refund' income - note that I started the return on Wednesday.",
            max_steps=20,
            tags=["CAU"],
            context_updates={
                'chain:table_purchase': {
                    'action': 'refund',
                    'task_id': 'W5-06',
                    'amount': table['price'],
                },
            },
        )
        
        # W5-07: [CAU] Repurchase
        self.add_subtask_to_day(
            day_idx=4,
            subtask_id=45,
            task_id="W5-07",
            evaluator_name="LayeredShoppingRepurchase",
            params={
                "product_sku": table_alt['sku'],
                "product_name": table_alt['name'],
                "same_address": True,
                "reference_order_sku": table['sku'],
            },
            time="19:45",
            narration=f"{user_name} reorders the table in a different color",
            user_instruction=f"Now let me reorder that patio table - get the '{table_alt['name']}' this time (different color). Ship to the same address as Monday's order.",
            max_steps=30,
            tags=["CAU"],
            reference_params={
                "order_reference": "Monday's table order",
            },
            context_updates={
                'chain:table_purchase': {
                    'action': 'repurchase',
                    'task_id': 'W5-07',
                    'sku': table_alt['sku'],
                    'name': table_alt['name'],
                    'same_address': True,
                },
            },
        )
        
        # W5-08: [REF] Send closure summary
        self.add_subtask_to_day(
            day_idx=4,
            subtask_id=46,
            task_id="W5-08",
            evaluator_name="LayeredSMSBatchNotify",
            params={
                "required_recipients": [f"{name} Smith" for name in attendees[:2]] + 
                                       [f"{name} Johnson" for name in attendees[2:]],
                "message_must_contain_keywords": ["progress", "sync"],
                "min_messages_sent": len(attendees),
            },
            time="20:15",
            narration=f"{user_name} reminds team to sync before the weekend",
            user_instruction="Text everyone from Monday's kickoff - remind them to sync their progress tonight before the weekend.",
            max_steps=30,
            tags=["REF"],
            reference_params={
                "recipients_hint": "Monday's kickoff meeting owners",
            },
        )
        
        # W5-09: Record exercise
        self.add_subtask_to_day(
            day_idx=4,
            subtask_id=47,
            task_id="W5-09",
            evaluator_name="LayeredOpenTracksRecord",
            params={
                "activity_type": "Walking",
                "min_duration_seconds": 10,
            },
            time="20:45",
            narration=f"{user_name} squeezes in a quick walk before the weekend",
            user_instruction="Quick walk before the weekend - start recording in OpenTracks.",
            max_steps=20,
        )
        
        # W5-10: Long-term summary
        self.add_subtask_to_day(
            day_idx=4,
            subtask_id=48,
            task_id="W5-10",
            evaluator_name="LayeredMarkorAppendContent",
            params={
                "file_name": "WorkLog.md",
                "content_must_contain": ["Sync", "refund", "repurchase"],
            },
            time="22:20",
            narration=f"{user_name} wraps up the work week in the log",
            user_instruction="Add Friday's summary to WorkLog.md - sync meeting done, followed up with team, got table refund and reordered it.",
            max_steps=20,
        )
    
    # ==================== Day 6: Cross-app Organization and Preference Verification ====================
    
    def _add_day6_subtasks(self, params: dict):
        """Day 6 (Saturday): Cross-app organization and preference verification"""
        shared = params.get('shared', {})
        products = params.get('products', {})
        
        user_name = shared.get('user_name', 'David')
        tide = products.get('tide', self.PARAM_TEMPLATES['products']['tide'])
        
        # W6-01: Task migration
        self.add_subtask_to_day(
            day_idx=5,
            subtask_id=49,
            task_id="W6-01",
            evaluator_name="LayeredCrossAppSync",
            params={
                "source_file": "WeekPlan.md",
                "target_list": "Saturday Meal Prep",
                "section": "Next Week Meal Prep List",
            },
            time="09:10",
            narration=f"{user_name} wants to organize meal prep for next week",
            user_instruction="Take the 'Next Week Meal Prep List' section from WeekPlan.md and create a 'Saturday Meal Prep' list in Tasks with those items.",
            max_steps=25,
        )
        
        # W6-02: [PRE] Find batch recipe
        self.add_subtask_to_day(
            day_idx=5,
            subtask_id=50,
            task_id="W6-02",
            evaluator_name="LayeredBroccoliRecipeSearch",
            params={
                "diet_type": "light",
                "batch_cooking": True,
            },
            time="09:30",
            narration=f"{user_name} wants to batch cook for the week ahead",
            user_instruction="Find me a light recipe that's good for batch cooking - I want to prep meals for next week.",
            max_steps=25,
            requires_answer=True,
            tags=["PRE"],
        )
        
        # W6-03: Generate grocery list
        self.add_subtask_to_day(
            day_idx=5,
            subtask_id=51,
            task_id="W6-03",
            evaluator_name="LayeredTasksCreateFromContent",
            params={
                "source": "latest_recipe",
                "list_name": "Grocery Shopping",
                "extract_type": "ingredients",
            },
            time="09:45",
            narration=f"{user_name} extracts ingredients for grocery shopping",
            user_instruction="Take the ingredients from that recipe and add them as tasks in a 'Grocery Shopping' list for tomorrow.",
            max_steps=20,
            tags=["STR"],
        )
        
        # W6-04: Buy cleaning supplies
        self.add_subtask_to_day(
            day_idx=5,
            subtask_id=52,
            task_id="W6-04",
            evaluator_name="LayeredShoppingPurchaseProduct",
            params={
                "product_sku": tide['sku'],
                "product_price": tide['price'],
                "check_method": "order",
                "eval_types": ["program_html"],
                "program_html": [
                    {
                        "url": "func:shopping_get_latest_order_url()",
                        "locator": "document.querySelector('.order-details-items.ordered').outerText",
                        "required_contents": {
                            "must_include": [tide['sku']]
                        }
                    }
                ],
                "require_login": True,
                "start_url": "__SHOPPING__",
            },
            time="10:20",
            narration=f"{user_name} needs cleaning supplies for meal prep",
            user_instruction=f"Order '{tide['name']}' from Shopping - need it for the meal prep cleanup.",
            max_steps=30,
        )
        
        # W6-05: Log expense
        self.add_subtask_to_day(
            day_idx=5,
            subtask_id=53,
            task_id="W6-05",
            evaluator_name="LayeredExpenseAddSingle",
            params={
                "name": "Tide PODS",
                "amount": tide['price'],
                "category": "Household",
                "note": "Supports WeekPlan goals",
            },
            time="10:40",
            narration=f"{user_name} tracks the cleaning supplies purchase",
            user_instruction=f"Log the Tide purchase (${tide['price']}) in Pro Expense under Household - note it supports my WeekPlan goals.",
            max_steps=20,
        )
        
        # W6-06: Long timer
        self.add_subtask_to_day(
            day_idx=5,
            subtask_id=54,
            task_id="W6-06",
            evaluator_name="LayeredClockStartTimer",
            params={
                "duration_minutes": 40,
            },
            time="11:10",
            narration=f"{user_name} starts batch cooking",
            user_instruction="Set a 40-minute timer for cooking.",
            max_steps=15,
        )
        
        # W6-07: Visual archiving
        self.add_subtask_to_day(
            day_idx=5,
            subtask_id=55,
            task_id="W6-07",
            evaluator_name="LayeredCameraCapture",
            params={
                "save_to_folder": "Health/Photos",
            },
            time="12:05",
            narration=f"{user_name} documents the meal prep for motivation",
            user_instruction="Take a photo of the meals I prepped and save it to Health/Photos.",
            max_steps=25,
        )
        
        # W6-09: File organization
        self.add_subtask_to_day(
            day_idx=5,
            subtask_id=56,
            task_id="W6-09",
            evaluator_name="LayeredFilesMove",
            params={
                "source_type": "audio",
                "target_folder": "Health/Audio",
            },
            time="12:35",
            narration=f"{user_name} organizes files from the week",
            user_instruction="Move that recent audio recording to Health/Audio folder to keep things organized.",
            max_steps=20,
        )
        
        # W6-10: Record outdoor activity
        self.add_subtask_to_day(
            day_idx=5,
            subtask_id=57,
            task_id="W6-10",
            evaluator_name="LayeredOpenTracksRecord",
            params={
                "activity_type": "Hiking",
                "min_duration_seconds": 10,
            },
            time="16:50",
            narration=f"{user_name} enjoys some weekend outdoor time",
            user_instruction="Going for a hike! Start recording in OpenTracks - set it to Hiking.",
            max_steps=20,
        )
    
    # ==================== Day 7: Automated Cleanup and Weekly Analysis ====================
    
    def _add_day7_subtasks(self, params: dict):
        """Day 7 (Sunday): Automated cleanup and weekly analysis"""
        shared = params.get('shared', {})
        products = params.get('products', {})
        
        user_name = shared.get('user_name', 'David')
        iphone = products.get('iphone', self.PARAM_TEMPLATES['products']['iphone'])
        
        # W7-01: Clean up space
        self.add_subtask_to_day(
            day_idx=6,
            subtask_id=58,
            task_id="W7-01",
            evaluator_name="LayeredFilesDedupe",
            params={
                "file_extension": ".png",
                "search_this_week": True,
            },
            time="10:10",
            narration=f"{user_name} does some digital housekeeping",
            user_instruction="My storage is getting full. Search for .png files from this week and delete any duplicates.",
            max_steps=25,
        )
        
        # W7-02: [AGG] Exercise summary
        self.add_subtask_to_day(
            day_idx=6,
            subtask_id=59,
            task_id="W7-02",
            evaluator_name="LayeredOpenTracksWeeklySummary",
            params={
                "metric": "distance",
                "start_day": 0,
                "end_day": 6,
            },
            time="10:40",
            narration=f"{user_name} wants to see the weekly exercise stats",
            user_instruction="Check OpenTracks and tell me - how much total distance did I walk/hike this week from Monday through today?",
            max_steps=25,
            requires_answer=True,
            tags=["AGG"],
        )
        
        # W7-03: [AGG][PRE] Financial audit
        self.add_subtask_to_day(
            day_idx=6,
            subtask_id=60,
            task_id="W7-03",
            evaluator_name="LayeredExpenseWeeklySummary",
            params={
                "category": "Dining",
                "budget_limit": 120.0,
            },
            time="11:00",
            narration=f"{user_name} checks if dining budget was met",
            user_instruction="Time to check the budget! How much did I spend on Dining this week total? Did I stay under my $120 limit?",
            max_steps=20,
            requires_answer=True,
            tags=["AGG", "PRE"],
        )
        
        # W7-04: Logic closure
        self.add_subtask_to_day(
            day_idx=6,
            subtask_id=61,
            task_id="W7-04",
            evaluator_name="LayeredMarkorCreateOutline",
            params={
                "file_name": "WeekReview.md",
                "required_sections": ["Exercise Total", "Budget Achievement", "Conflict Handling", "Shopping Summary"],
                "sections_with_content": ["Exercise Total", "Budget Achievement", "Conflict Handling", "Shopping Summary"],
            },
            time="11:20",
            narration=f"{user_name} reflects on the week's achievements and challenges",
            user_instruction="Create a WeekReview.md file in Markor summarizing: 1) Total exercise distance, 2) Whether I met my budget goal, 3) How I handled the meeting/exercise conflict, 4) The whole table saga (buy → return → rebuy).",
            max_steps=30,
        )
        
        # W7-05: Plan next week
        self.add_subtask_to_day(
            day_idx=6,
            subtask_id=62,
            task_id="W7-05",
            evaluator_name="LayeredCrossAppPlan",
            params={
                "calendar_event": {
                    "title": "Proposal Presentation",
                    "day_offset": 3,  # Next Wednesday
                    "time": "15:00",
                },
                "task": {
                    "title": "Create PPT",
                    "priority": "high",
                    "due_before": "Proposal Presentation",
                },
            },
            time="15:00",
            narration=f"{user_name} starts planning for next week",
            user_instruction="I have a presentation next week! Add 'Proposal Presentation' to my calendar for next Wednesday at 3 PM. Also create a high-priority task 'Create PPT' due before that.",
            max_steps=30,
        )
        
        # W7-06: Habit evolution
        self.add_subtask_to_day(
            day_idx=6,
            subtask_id=63,
            task_id="W7-06",
            evaluator_name="LayeredClockSetAlarm",
            params={
                "adjust_existing": True,
                "shift_minutes": -5,  # Another 5 minutes earlier
                "weekday_only": True,
            },
            time="16:10",
            narration=f"{user_name} decides to wake up even earlier next week",
            user_instruction="Waking up earlier this week worked well! Adjust my weekday alarm another 5 minutes earlier for next week.",
            max_steps=20,
        )
        
        # W7-07: [ALT][CON] Conflict resolution (over-budget purchase)
        self.add_subtask_to_day(
            day_idx=6,
            subtask_id=64,
            task_id="W7-07",
            evaluator_name="LayeredActiveConfirmation",
            params={
                "product_name": iphone['name'],
                "product_price": iphone['price'],
                "budget_category": "total",
                "expected_action": "confirm_or_reject",  # Should ask user to confirm
            },
            time="17:00",
            narration=f"{user_name} considers a big purchase",
            user_instruction=f"Hmm, I've been thinking about getting an {iphone['name']}. Should I buy it?",
            max_steps=25,
            requires_answer=True,
            tags=["ALT", "CON"],
            preference_check={
                "budget": {"amount": iphone['price'], "category": "total"},
            },
        )
        
        # W7-08: Evolve goals
        self.add_subtask_to_day(
            day_idx=6,
            subtask_id=65,
            task_id="W7-08",
            evaluator_name="LayeredFilesRename",
            params={
                "source_name": "WeekPlan.md",
                "target_name": "NextWeekPlan.md",
            },
            time="20:20",
            narration=f"{user_name} prepares the plan for next week",
            user_instruction="Rename WeekPlan.md to NextWeekPlan.md and update it - maybe adjust the budget or exercise times based on how this week went.",
            max_steps=25,
        )
        
        # W7-09: Create routine checklist
        self.add_subtask_to_day(
            day_idx=6,
            subtask_id=66,
            task_id="W7-09",
            evaluator_name="LayeredTasksCreateChecklist",
            params={
                "list_name": "Monday Morning Checklist",
                "items": ["Check calendar", "Review progress", "Pack lunch", "Confirm exercise time", "Check emails", "Prepare for meetings"],
            },
            time="20:40",
            narration=f"{user_name} creates a checklist for next Monday",
            user_instruction="Create a 'Monday Morning Checklist' in Tasks with these items: check calendar, review progress, pack lunch, confirm exercise time, check emails, prepare for meetings.",
            max_steps=25,
        )
        
        # W7-10: Full scenario summary
        self.add_subtask_to_day(
            day_idx=6,
            subtask_id=67,
            task_id="W7-10",
            evaluator_name="LayeredMarkorAppendContent",
            params={
                "file_name": "WorkLog.md",
                "content_must_contain": ["meeting", "health", "shopping"],
            },
            time="22:10",
            narration=f"{user_name} wraps up the week with final reflections",
            user_instruction="Add 'Sunday Final Thoughts' to WorkLog.md - reflect on the week: how the meeting chain went from kickoff to sync, whether I stuck to my health goals, and the whole table ordering adventure.",
            max_steps=25,
        )
    
    # ==================== Environment Initialization ====================
    
    # Flag: whether the environment has been initialized (to prevent duplicate cleanup of data)
    _environment_initialized = False
    
    def initialize_task(self, env):
        """
        Initialize the 7-day scenario environment
        
        Performs batch initialization for all days:
        1. Clear and create initial alarms (for W1-01)
        2. Create calendar events (for W1-02, W1-04, W3-02, W4-03, W4-04)
        3. Create contacts (for W1-05, W2-04, W4-04, W5-08)
        4. Set initial preferences (simulating W1-03)
        5. Clear app data (Markor, Expense, OpenTracks, Audio Recorder, Tasks)
        
        ⚠️ IMPORTANT: This method should only be called ONCE at the start of the scenario.
        Data created in Day 1 must persist through Day 7 (e.g., SMS conversations, audio recordings).
        """
        # Prevent duplicate initialization (to protect cross-day data)
        if self._environment_initialized:
            logging.warning("⚠️ Environment already initialized - skipping to preserve cross-day data")
            return
        
        super().initialize_task(env)
        
        logging.info("🔧 Batch initializing Scenario W environment...")
        logging.info("   ⚠️ This initialization happens ONLY ONCE at scenario start")
        
        # ⚠️ critical fix: ensure timezone is UTC first during scenario initialization
        # this fixes the Calendar displaying incorrect time issue
        from scendroid.env import adb_utils
        logging.info("   🌍 ensuring device timezone is UTC...")
        try:
            # set timezone to UTC (using ScenDroid standard method)
            adb_utils.set_root_if_needed(env.controller)
            
            adb_utils.issue_generic_request(
                ['shell', 'service', 'call', 'alarm', '3', 's16', 'UTC'],
                env.controller
            )
            
            # also set system properties
            adb_utils.issue_generic_request(
                ['shell', 'setprop', 'persist.sys.timezone', 'UTC'],
                env.controller
            )
            
            logging.info("   ✅ timezone confirmed as UTC")
        except Exception as e:
            logging.warning(f"   ⚠️  Could not set timezone: {e}")
        
        try:
            # 1. Create initial alarms (for W1-01 adjustment)
            self._setup_clocks(env)
            
            # 2. Create calendar events (for Day 1-4 tasks)
            self._setup_calendar_events(env)
            
            # 3. Create contacts (for SMS tasks)
            self._setup_contacts(env)
            
            # 4. Clean up app data
            self._cleanup_app_data(env)
            
            # 5. Set initial preferences
            self._setup_preferences()
            
            # 6. Setup Broccoli recipes (for W2-06, W4-07, W6-02)
            self._setup_broccoli_recipes(env)
            
            # Note: Chrome login is handled by seven_day_base._initialize_shopping_subtask()
            # when Shopping task starts, not during batch initialization
            
            # Flag initialization as complete (to prevent subsequent duplicate cleanup)
            self._environment_initialized = True
            
            logging.info("✅ Batch initialization complete")
            logging.info("   ✅ Cross-day data will be preserved throughout the 7-day scenario")
            
        except Exception as e:
            logging.error(f"❌ Batch initialization error: {e}")
            import traceback
            logging.error(traceback.format_exc())
    
    def _setup_clocks(self, env):
        """Create initial alarms (for W1-01 adjustment)"""
        logging.info("   ⏰ Creating initial alarms...")
        
        from scendroid.env import adb_utils
        import time
        
        # Clear existing alarm data
        try:
            logging.info("      🗑️  Clearing existing alarms...")
            adb_utils.clear_app_data(
                adb_utils.extract_package_name(adb_utils.get_adb_activity("clock")),
                env.controller,
            )
            time.sleep(1.0)
            logging.info("      ✅ Alarm data cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear clock data: {e}")
        
        # Get alarm parameters
        alarm = self.generated_params.get('alarm', {})
        original_hour = alarm.get('original_hour', 8)
        original_minute = alarm.get('original_minute', 0)
        
        # Create weekday alarm (to be adjusted in W1-01)
        self._set_alarm_with_days(env, hour=original_hour, minute=original_minute, 
                                  message="Work", days=[2, 3, 4, 5, 6])  # Mon-Fri
        time.sleep(1.0)
        
        # Create weekend alarm (should not be changed in W1-01)
        self._set_alarm_with_days(env, hour=9, minute=30, 
                                  message="Weekend", days=[1, 7])  # Sat-Sun
        time.sleep(1.0)
        
        # Create sleep alarm (daily)
        self._set_alarm_with_days(env, hour=22, minute=30, 
                                  message="Sleep", days=[1, 2, 3, 4, 5, 6, 7])
        time.sleep(1.0)
        
        logging.info(f"   ✅ Alarms created (Work: {original_hour:02d}:{original_minute:02d})")
    
    def _set_alarm_with_days(self, env, hour: int, minute: int, message: str, days: list):
        """Set alarm with repeat days"""
        from scendroid.env import adb_utils
        import time
        
        safe_message = message.replace(' ', '_')
        
        cmd = [
            'shell', 'am', 'start',
            '-a', 'android.intent.action.SET_ALARM',
            '--ei', 'android.intent.extra.alarm.HOUR', str(hour),
            '--ei', 'android.intent.extra.alarm.MINUTES', str(minute),
            '--es', 'android.intent.extra.alarm.MESSAGE', safe_message,
        ]
        
        if days:
            days_str = ','.join(str(d) for d in days)
            cmd.extend(['--eia', 'android.intent.extra.alarm.DAYS', days_str])
        
        adb_utils.issue_generic_request(cmd, env.controller)
        time.sleep(3.0)
        
        adb_utils.press_home_button(env.controller)
        time.sleep(0.5)
    
    def _setup_calendar_events(self, env):
        """Create calendar events for the 7-day scenario"""
        logging.info("   📅 Creating calendar events...")
        
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from datetime import datetime
        import calendar as cal_module
        import time
        from scendroid.env import adb_utils
        
        # ✅ fix 1: use clear_app_data to fully reset Calendar app (including view settings)
        adb_utils.clear_app_data("com.simplemobiletools.calendar.pro", env.controller)
        time.sleep(1.0)
        
        # launch Calendar once and return, ensure app initialization complete (skip first-run wizard)
        adb_utils.start_activity(
            "com.simplemobiletools.calendar.pro/.activities.MainActivity",
            None,  # extra_args
            env.controller
        )
        time.sleep(2.0)
        adb_utils.press_home_button(env.controller)
        time.sleep(0.5)
        
        # ✅ fix 2: re-set timezone after clearing app data (prevent timezone reset)
        logging.info("      🌍 re-confirming device timezone is UTC...")
        adb_utils.set_root_if_needed(env.controller)
        
        adb_utils.issue_generic_request(
            ['shell', 'service', 'call', 'alarm', '3', 's16', 'UTC'],
            env.controller
        )
        
        adb_utils.issue_generic_request(
            ['shell', 'setprop', 'persist.sys.timezone', 'UTC'],
            env.controller
        )
        
        # Clear existing events
        calendar_utils.clear_calendar_db(env)
        
        # Base date: Monday 2026-01-19
        base_date = datetime(2026, 1, 19, 0, 0, 0)
        
        shared = self.generated_params.get('shared', {})
        kickoff_title = shared.get('kickoff_title', 'Sprint Kickoff')
        kickoff_location = shared.get('kickoff_location', 'Conference Room A')
        attendees = shared.get('kickoff_attendees', ['Alice Smith', 'Bob Johnson', 'Charlie Williams', 'Diana Brown'])
        user_name = shared.get('user_name', 'Emily')
        design_title = shared.get('design_title', 'Design Review')
        sync_title = shared.get('sync_title', 'Sprint Sync')
        
        events = []
        
        # Day 1 (Mon): Sprint Kickoff at 09:00 (for W1-04, W1-05)
        kickoff_dt = base_date.replace(hour=9, minute=0)
        kickoff_start_ts = cal_module.timegm(kickoff_dt.timetuple())
        kickoff_end_ts = kickoff_start_ts + (60 * 60)  # 1 hour
        
        attendees_str = f"Attendees: {user_name}, " + ", ".join(attendees)
        event1 = sqlite_schema_utils.CalendarEvent(
            start_ts=kickoff_start_ts,
            end_ts=kickoff_end_ts,
            title=kickoff_title,
            location=kickoff_location,
            description=attendees_str,
        )
        events.append(event1)
        logging.info(f"   📌 Day 1: {kickoff_title} @ 09:00")
        
        # Day 1: Afternoon meeting at 14:00 (distractor)
        pm_dt = base_date.replace(hour=14, minute=0)
        pm_start_ts = cal_module.timegm(pm_dt.timetuple())
        pm_end_ts = pm_start_ts + (60 * 60)
        
        event2 = sqlite_schema_utils.CalendarEvent(
            start_ts=pm_start_ts,
            end_ts=pm_end_ts,
            title="Project Status Update",
            location="Meeting Room B",
            description="Weekly project sync",
        )
        events.append(event2)
        
        # Day 2 (Tue): Afternoon meeting at 15:00-16:00 (DISTRACTOR for W2-01)
        # W2-01 checks 13:00-18:00, this event makes afternoon NOT free
        tue_date = base_date.replace(day=20)  # 2026-01-20 (Tuesday)
        tue_pm_dt = tue_date.replace(hour=15, minute=0)
        tue_pm_start_ts = cal_module.timegm(tue_pm_dt.timetuple())
        tue_pm_end_ts = tue_pm_start_ts + (60 * 60)  # 1 hour
        
        event_tue_distractor = sqlite_schema_utils.CalendarEvent(
            start_ts=tue_pm_start_ts,
            end_ts=tue_pm_end_ts,
            title="Client Call",  # Distractor: afternoon conflict
            location="Phone",
            description="Follow up with client about project requirements",
        )
        events.append(event_tue_distractor)
        logging.info(f"   📌 Day 2: Client Call @ 15:00 (distractor for W2-01)")
        
        # Day 2: Another morning event (additional distractor)
        tue_am_dt = tue_date.replace(hour=10, minute=30)
        tue_am_start_ts = cal_module.timegm(tue_am_dt.timetuple())
        tue_am_end_ts = tue_am_start_ts + (45 * 60)  # 45 min
        
        event_tue_am = sqlite_schema_utils.CalendarEvent(
            start_ts=tue_am_start_ts,
            end_ts=tue_am_end_ts,
            title="Code Review",
            location="Online",
            description="PR review session",
        )
        events.append(event_tue_am)
        
        # Day 3 (Wed): ❌ Do not pre-create the Design Review meeting
        # The goal of W3-02 is to have the agent detect the conflict with the exercise time (18:30) and avoid creating this meeting
        # If this meeting is pre-created, the evaluation logic will become confused
        # logging.info(f"   ⚠️  Day 3: Not creating {design_title} - let W3-02 handle conflict detection")
        
        # Day 4 (Thu): Sprint Sync at 10:00 (for W4-03)
        thu_date = base_date.replace(day=22)  # 2026-01-22
        sync_dt = thu_date.replace(hour=10, minute=0)
        sync_start_ts = cal_module.timegm(sync_dt.timetuple())
        sync_end_ts = sync_start_ts + (60 * 60)
        
        event4 = sqlite_schema_utils.CalendarEvent(
            start_ts=sync_start_ts,
            end_ts=sync_end_ts,
            title=sync_title,
            location="Conference Room A",
            description=attendees_str,  # Same attendees as kickoff
        )
        events.append(event4)
        logging.info(f"   📌 Day 4: {sync_title} @ 10:00")
        
        # Add all events
        calendar_utils.add_events(events, env)
        time.sleep(2.0)
        
        logging.info("   ✅ Calendar events created")
    
    # Flag: whether contacts have been set up (to prevent duplicate cleanup in subsequent tasks)
    _contacts_initialized = False
    
    def _setup_contacts(self, env):
        """Create contacts for SMS tasks
        
        Reference: scenario_a.py _setup_contacts() - includes retry mechanism and verification step
        
        ⚠️ IMPORTANT: This method clears SMS and contacts, so it should ONLY be called
        once during initial setup. Cross-day SMS conversations must be preserved.
        """
        # Prevent duplicate cleanup (to protect cross-day SMS data)
        if self._contacts_initialized:
            logging.warning("   ⚠️ Contacts already initialized - skipping to preserve SMS data")
            return
        
        logging.info("   👥 Creating contacts...")
        logging.info("   ⚠️ This clears existing SMS data - only runs once at scenario start")
        
        from scendroid.utils import contacts_utils
        from scendroid.env import adb_utils
        import time
        
        # Clear existing contacts
        contacts_utils.clear_contacts(env.controller)
        time.sleep(1.0)
        
        # Clear existing SMS and refresh UI
        logging.info("   💬 Clearing existing SMS (only at scenario start)...")
        try:
            from scendroid.task_evals.common_validators import sms_validators
            sms_validators.clear_sms_and_threads(env.controller)
            logging.info("      ✅ SMS database cleared")
            
            adb_utils.close_app("simple sms", env.controller)
            time.sleep(1.0)
            
            # Open and close SMS app to refresh UI (like scenario_a)
            logging.info("      📱 Opening SMS app to refresh UI...")
            adb_utils.start_activity(
                "com.simplemobiletools.smsmessenger/.activities.MainActivity",
                None,
                env.controller
            )
            time.sleep(2.0)
            
            adb_utils.issue_generic_request(
                ["shell", "input", "keyevent", "KEYCODE_BACK"],
                env.controller
            )
            time.sleep(1.0)
            logging.info("      ✅ SMS app UI refreshed")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear SMS: {e}")
        
        # Get attendees from parameters
        shared = self.generated_params.get('shared', {})
        attendees = shared.get('kickoff_attendees', ['Alice Smith', 'Bob Johnson', 'Charlie Williams', 'Diana Brown'])
        
        # Create contacts for attendees
        contacts = []
        for i, name in enumerate(attendees):
            contacts.append({"name": name, "phone": f"555-010{i+1}"})
        
        # Add some distractors
        contacts.extend([
            {"name": "Charlie Wilson", "phone": "555-0201"},
            {"name": "David Lee", "phone": "555-0202"},
        ])
        
        logging.info(f"   📞 Adding {len(contacts)} contacts...")
        
        successfully_added = 0
        for i, contact in enumerate(contacts, 1):
            name = contact.get('name')
            phone = contact.get('phone')
            if not name or not phone:
                continue
            
            # Retry mechanism (refer to scenario_a.py)
            for attempt in range(2):
                try:
                    adb_utils.press_home_button(env.controller)
                    time.sleep(1.0)
                    
                    contacts_utils.add_contact(
                        name,
                        phone,
                        env.controller,
                        ui_delay_sec=2.0
                    )
                    logging.info(f"      ✅ Added {i}/{len(contacts)}: {name} ({phone})")
                    successfully_added += 1
                    time.sleep(2.0)  # etc. wait for UI response (scenario_a uses 2.0)
                    break  # success, continue to next
                    
                except Exception as e:
                    if attempt == 1:  # Final attempt fails
                        logging.error(f"      ❌ Failed to add '{name}' (after 2 attempts): {e}")
                    else:
                        logging.warning(f"      ⚠️  Attempt {attempt + 1} failed for '{name}': {e}")
                    time.sleep(1.0)
        
        # Report result
        logging.info("   " + "=" * 50)
        logging.info(f"   📊 Contact summary:")
        logging.info(f"      Total: {len(contacts)}")
        logging.info(f"      Success: {successfully_added}")
        if successfully_added < len(contacts):
            logging.warning(f"      ⚠️  Failed: {len(contacts) - successfully_added}")
        logging.info("   " + "=" * 50)
        
        # etc. wait for contact sync
        logging.info("   ⏳ Waiting for contacts to sync...")
        time.sleep(3.0)
        
        # Verify whether the contact was actually added
        try:
            actual_contacts = contacts_utils.list_contacts(env.controller)
            logging.info("   " + "=" * 50)
            logging.info(f"   📋 Contact verification:")
            logging.info(f"      In database: {len(actual_contacts)} contacts")
            
            added_names = {c.name for c in actual_contacts}
            expected_names = {contact['name'] for contact in contacts}
            missing_names = expected_names - added_names
            
            if missing_names:
                logging.warning(f"      ⚠️  Missing: {', '.join(missing_names)}")
            else:
                logging.info(f"      ✅ All {len(contacts)} contacts verified")
            logging.info("   " + "=" * 50)
        except Exception as e:
            logging.warning(f"   ⚠️  Could not verify contacts: {e}")
        
        adb_utils.press_home_button(env.controller)
        time.sleep(0.5)
        
        # Flag contacts as initialized (to prevent subsequent duplicate cleanup)
        self._contacts_initialized = True
        
        logging.info("   ✅ Contacts created")
        
        # Add distractor SMS history (for W2-04 reference task)
        self._setup_sms_distractors(env, contacts)
        
        logging.info("   ✅ SMS data from this point will be preserved throughout the scenario")
    
    def _setup_sms_distractors(self, env, contacts):
        """Add distractor SMS history for reference resolution tasks
        
        W2-04 asks to "send message to everyone from yesterday's meeting".
        We add some unrelated messages to make the task more challenging.
        """
        logging.info("   💬 Adding distractor SMS history...")
        
        from scendroid.env import adb_utils
        import time
        
        try:
            # Get distractor contacts (not meeting attendees)
            distractor_contacts = [c for c in contacts if "Wilson" in c['name'] or "Lee" in c['name']]
            
            if not distractor_contacts:
                logging.info("      No distractor contacts found, skipping")
                return
            
            # Add some historical messages from distractors
            distractor_messages = [
                ("Charlie Wilson", "555-0201", "Hey, are you free for lunch next week?"),
                ("David Lee", "555-0202", "Don't forget about the team building event on Friday!"),
                ("Charlie Wilson", "555-0201", "Got the document you sent, looks good!"),
            ]
            
            for name, phone, body in distractor_messages:
                try:
                    # Insert SMS via content provider
                    # This creates historical messages that should NOT be replied to in W2-04
                    cmd = [
                        'shell', 'content', 'insert',
                        '--uri', 'content://sms/inbox',
                        '--bind', f'address:s:{phone}',
                        '--bind', f'body:s:{body}',
                        '--bind', 'read:i:1',  # Mark as read
                        '--bind', 'type:i:1',  # Inbox
                    ]
                    adb_utils.issue_generic_request(cmd, env.controller)
                    logging.info(f"      ✅ Added distractor from {name}: '{body[:30]}...'")
                    time.sleep(0.5)
                except Exception as e:
                    logging.warning(f"      ⚠️  Failed to add distractor from {name}: {e}")
            
            logging.info("   ✅ Distractor SMS history added")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Could not add distractor SMS: {e}")
    
    def _cleanup_app_data(self, env):
        """
        Clean up app data and ensure apps are properly initialized
        
        Key insight from scenario_c.py:
        - If we just clear data without handling the welcome wizard, apps will show setup screens
        - We need to either: (1) only clear data files, OR (2) clear all data AND complete setup wizard
        
        Reference: scenario_a.py, scenario_c.py, env/setup_device/apps.py
        """
        logging.info("   🗑️  Cleaning up app data...")
        
        from scendroid.env import adb_utils, device_constants
        from scendroid.utils import file_utils
        from scendroid.env import tools
        import time
        
        # 1. Markor - only clear directory, keep app initialized
        # Reference: scenario_a.py line 842-855
        try:
            logging.info(f"      📁 Clearing Markor directory...")
            markor_dir = device_constants.MARKOR_DATA  # "/storage/emulated/0/Documents/Markor"
            
            # Ensure directory exists
            cmd = ['shell', 'mkdir', '-p', markor_dir]
            adb_utils.issue_generic_request(cmd, env.controller)
            
            # Clear all files in directory
            file_utils.clear_directory(markor_dir, env.controller)
            logging.info(f"      ✅ Markor directory cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Markor directory cleanup failed: {str(e)[:100]}")
        
        # 2. Setup Markor wizard if needed
        # Reference: env/setup_device/apps.py MarkorApp.setup()
        try:
            logging.info(f"      📝 Ensuring Markor is initialized...")
            self._setup_markor_wizard(env)
        except Exception as e:
            logging.warning(f"      ⚠️  Markor setup failed: {str(e)[:100]}")
        
        # 3. Clean Expense database (NOT app data)
        # Reference: scenario_a.py line 857-878
        try:
            logging.info(f"      💰 Clearing Expense database...")
            from scendroid.task_evals.utils import sqlite_utils
            from scendroid.env.setup_device import apps
            
            _EXPENSE_DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
            _EXPENSE_TABLE = "expense"
            _EXPENSE_APP_NAME = "pro expense"
            
            # Check if database exists
            if not sqlite_utils.table_exists(_EXPENSE_TABLE, _EXPENSE_DB_PATH, env):
                logging.info(f"         Expense database doesn't exist, initializing...")
                apps.ExpenseApp.setup(env)
            
            # Clear database
            sqlite_utils.delete_all_rows_from_table(
                _EXPENSE_TABLE, _EXPENSE_DB_PATH, env, _EXPENSE_APP_NAME
            )
            logging.info(f"      ✅ Expense database cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Expense cleanup failed: {str(e)[:100]}")
        
        # 4. Clean OpenTracks database and setup permissions
        # Reference: scenario_a.py line 880-950
        try:
            logging.info(f"      🏃 Clearing OpenTracks database...")
            from scendroid.task_evals.information_retrieval import activity_app_utils
            
            activity_app_utils.clear_db(env)
            logging.info(f"      ✅ OpenTracks database cleared")
            
            # Setup OpenTracks with permissions and handle popups
            self._setup_opentracks(env)
        except Exception as e:
            logging.warning(f"      ⚠️  OpenTracks cleanup failed: {str(e)[:100]}")
        
        # 5. Clean and setup Audio Recorder
        # Reference: scenario_c.py _cleanup_audiorecorder() + _setup_audiorecorder_permissions()
        try:
            logging.info(f"      🎙️ Setting up Audio Recorder...")
            self._setup_audiorecorder(env)
        except Exception as e:
            logging.warning(f"      ⚠️  Audio Recorder setup failed: {str(e)[:100]}")
        
        # 6. Clean Tasks app data only (not full clear)
        try:
            logging.info(f"      📋 Clearing Tasks database...")
            
            # Clear tasks database
            tasks_db_path = "/data/data/org.tasks/databases/database"
            adb_utils.issue_generic_request(
                ['shell', 'rm', '-f', tasks_db_path],
                env.controller
            )
            
            # Launch and close to reinitialize
            adb_utils.launch_app("tasks", env.controller)
            time.sleep(2.0)
            adb_utils.close_app("tasks", env.controller)
            time.sleep(0.5)
            logging.info(f"      ✅ Tasks database cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Tasks cleanup failed: {str(e)[:100]}")
        
        adb_utils.press_home_button(env.controller)
        time.sleep(0.5)
        
        logging.info("   ✅ App data cleaned")
    
    def _setup_markor_wizard(self, env):
        """
        Complete Markor welcome wizard if needed
        Reference: env/setup_device/apps.py MarkorApp.setup()
        """
        from scendroid.env import adb_utils, tools
        import time
        
        logging.info("      🔧 Checking Markor wizard...")
        
        try:
            # Launch Markor
            adb_utils.launch_app("markor", env.controller)
            time.sleep(1.5)  # Reduced from 2.0
            
            # Try to complete wizard by clicking NEXT/DONE buttons
            controller = tools.AndroidToolController(env=env.controller)
            
            # Click through wizard pages (up to 5 pages)
            for i in range(5):
                try:
                    controller.click_element("NEXT")
                    logging.info(f"         ✓ Clicked NEXT ({i+1})")
                    time.sleep(0.8)  # Reduced from 1.5
                except:
                    break
            
            # Click DONE
            try:
                controller.click_element("DONE")
                logging.info("         ✓ Clicked DONE")
                time.sleep(0.8)  # Reduced from 1.5
            except:
                pass
            
            # Click OK for any dialogs
            try:
                controller.click_element("OK")
                logging.info("         ✓ Clicked OK")
                time.sleep(0.5)  # Reduced from 1.0
            except:
                pass
            
            # Handle file access permission
            try:
                controller.click_element("Allow access to manage all files")
                logging.info("         ✓ Granted file access")
                time.sleep(0.5)  # Reduced from 1.0
            except:
                pass
            
            # Close app
            adb_utils.close_app("markor", env.controller)
            time.sleep(0.3)  # Reduced from 0.5
            
            logging.info("      ✅ Markor wizard completed")
            
        except Exception as e:
            logging.warning(f"      ⚠️  Markor wizard failed: {str(e)[:50]}")
            try:
                adb_utils.close_app("markor", env.controller)
            except:
                pass
    
    def _setup_opentracks(self, env):
        """
        Setup OpenTracks with permissions and handle welcome popups
        Reference: scenario_a.py line 888-950
        """
        from scendroid.env import adb_utils, tools
        import time
        
        logging.info("      🔧 Setting up OpenTracks...")
        
        try:
            # Get package name
            open_tracks_package = adb_utils.extract_package_name(
                adb_utils.get_adb_activity("open tracks")
            )
            
            # Grant permissions
            adb_utils.grant_permissions(
                open_tracks_package,
                "android.permission.ACCESS_COARSE_LOCATION",
                env.controller,
            )
            adb_utils.grant_permissions(
                open_tracks_package,
                "android.permission.ACCESS_FINE_LOCATION",
                env.controller,
            )
            adb_utils.grant_permissions(
                open_tracks_package,
                "android.permission.POST_NOTIFICATIONS",
                env.controller,
            )
            logging.info("         ✓ Permissions granted")
            
            # Launch app
            try:
                adb_utils.launch_app("open tracks sports tracker", env.controller)
            except Exception as e:
                logging.debug(f"         Launch timeout (expected): {e}")
            
            time.sleep(2.0)  # Reduced from 3.0
            
            # Handle bluetooth permission popup
            try:
                controller = tools.AndroidToolController(env=env.controller)
                controller.click_element("Allow")
                logging.info("         ✓ Clicked Allow button")
                time.sleep(0.5)  # Reduced from 1.0
            except:
                pass
            
            # Close app
            adb_utils.close_app("open tracks sports tracker", env.controller)
            time.sleep(0.3)  # Reduced from 0.5
            
            # Launch again to ensure initialization complete
            try:
                adb_utils.start_activity(
                    "de.dennisguse.opentracks/.TrackListActivity",
                    None,
                    env.controller
                )
                time.sleep(1.5)  # Reduced from 2.0
                adb_utils.close_app("activity tracker", env.controller)
            except:
                pass
            
            logging.info("      ✅ OpenTracks setup completed")
            
        except Exception as e:
            logging.warning(f"      ⚠️  OpenTracks setup failed: {str(e)[:50]}")
    
    def _setup_audiorecorder(self, env):
        """
        Setup Audio Recorder - use pm clear and re-setup permissions
        Reference: scenario_c.py _cleanup_audiorecorder() + _setup_audiorecorder_permissions()
        
        Important: Using pm clear ensures complete cleanup of recordings AND database
        to avoid "some of your records was deleted or moved" popup
        """
        from scendroid.env import adb_utils, tools, device_constants
        import time
        
        logging.info("      🔧 Setting up Audio Recorder...")
        
        try:
            # 1. Use pm clear to completely clean app data (database + recordings)
            # This avoids "records deleted" popup and ensures clean state
            logging.info("         Clearing Audio Recorder data (pm clear)...")
            adb_utils.clear_app_data(
                "com.dimowner.audiorecorder",
                env.controller,
            )
            time.sleep(0.5)
            logging.info("         ✓ App data cleared")
            
            # 2. Also clear external storage directories (in case pm clear missed them)
            audio_dirs = [
                f"{device_constants.EMULATOR_DATA}/AudioRecorder",
                f"{device_constants.EMULATOR_DATA}/Recordings",
                device_constants.AUDIORECORDER_DATA,  # The actual recordings path
            ]
            for audio_dir in audio_dirs:
                adb_utils.issue_generic_request(
                    ['shell', 'rm', '-rf', audio_dir],
                    env.controller
                )
            logging.info("         ✓ External directories cleared")
            
            # 3. Grant permissions (required after pm clear)
            adb_utils.grant_permissions(
                "com.dimowner.audiorecorder",
                "android.permission.RECORD_AUDIO",
                env.controller,
            )
            adb_utils.grant_permissions(
                "com.dimowner.audiorecorder",
                "android.permission.POST_NOTIFICATIONS",
                env.controller,
            )
            logging.info("         ✓ Permissions granted")
            
            # 4. Launch app using monkey
            adb_utils.issue_generic_request([
                "shell", "monkey",
                "-p", "com.dimowner.audiorecorder",
                "-c", "android.intent.category.LAUNCHER",
                "1",
            ], env.controller)
            time.sleep(2.0)  # Need more time for first launch after pm clear
            
            # 5. Handle welcome wizard (required after pm clear)
            try:
                controller = tools.AndroidToolController(env=env.controller)
                
                # Try "GET STARTED" button (main welcome screen)
                for btn_text in ['GET STARTED', 'Get Started', 'START', 'Start', 'OK']:
                    try:
                        controller.click_element(btn_text)
                        logging.info(f"         ✓ Clicked welcome: {btn_text}")
                        time.sleep(1.5)
                        break
                    except:
                        pass
                
                # Try confirm/apply buttons (settings or dialog)
                for btn_text in ['APPLY', 'Apply', 'OK', 'Done', 'DONE']:
                    try:
                        controller.click_element(btn_text)
                        logging.info(f"         ✓ Clicked confirm: {btn_text}")
                        time.sleep(1.0)
                        break
                    except:
                        pass
            except Exception as e:
                logging.debug(f"         Wizard handling: {e}")
            
            # 6. Close app
            adb_utils.close_app('audio recorder', env.controller)
            time.sleep(0.5)
            
            logging.info("      ✅ Audio Recorder setup completed")
            
        except Exception as e:
            logging.warning(f"      ⚠️  Audio Recorder setup failed: {str(e)[:50]}")
            try:
                adb_utils.close_app('audio recorder', env.controller)
            except:
                pass
    
    def _setup_preferences(self):
        """Set initial preferences (simulating W1-03)"""
        logging.info("   ⚙️  Setting up preferences...")
        
        # Preset preferences (simulating preferences established in W1-03)
        # These preferences take effect after W1-03 execution
        # But preset here so subsequent tasks can check them
        
        self.preference_store.set_diet_restriction(
            restriction_type='light',
            forbidden=['fried', 'deep_fried', 'high_fat', 'oily'],
        )
        
        self.preference_store.set_budget(
            category='dining',
            limit=120.0,
            requires_confirmation=True,
        )
        
        self.preference_store.set_schedule_habit(
            activity='exercise',
            time='18:30',
            duration_minutes=30,
            requires_confirmation=True,
        )
        
        logging.info("   ✅ Preferences configured")
        logging.info(f"      Diet: light, forbidden: ['fried', 'deep_fried', 'high_fat', 'oily']")
        logging.info(f"      Budget: dining <= $120")
        logging.info(f"      Schedule: exercise at 18:30 for 30min")
    
    def _setup_broccoli_recipes(self, env):
        """Initialize Broccoli Recipe database with light/healthy recipes and distractors
        
        For W2-06, W4-07, W6-02: Recipe search tasks requiring "light" options
        
        Setup:
        - 1 clearly LIGHT recipe (target answer for W2-06)
        - 2-3 distractor recipes that include "fried" or "oily" ingredients (NOT light)
        """
        logging.info("   📚 Setting up Broccoli Recipes...")
        
        from scendroid.task_evals.utils import sqlite_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from scendroid.env import adb_utils
        import time
        import subprocess
        
        _DB_PATH = '/data/data/com.flauschcode.broccoli/databases/broccoli'
        _TABLE_NAME = 'recipes'
        _APP_NAME = 'broccoli app'
        
        # 1. Launch app to ensure database is created
        logging.info("      Step 1: Launching Broccoli app to initialize database...")
        try:
            adb_utils.launch_app(_APP_NAME, env.controller)
            time.sleep(2.0)
        except subprocess.TimeoutExpired:
            logging.info("      Broccoli launch timed out (expected)")
            time.sleep(1.0)
        
        adb_utils.close_app(_APP_NAME, env.controller)
        time.sleep(1.0)
        
        # 2. Clear existing recipes
        logging.info("      Step 2: Clearing existing recipes...")
        try:
            sqlite_utils.delete_all_rows_from_table(
                table_name=_TABLE_NAME,
                remote_db_file_path=_DB_PATH,
                env=env,
                app_name=_APP_NAME
            )
        except Exception as e:
            logging.warning(f"      ⚠️  Failed to clear recipes: {e}")
        
        # 3. Create recipes with clear light vs non-light distinction
        all_recipes = []
        
        # TARGET RECIPE: Clearly LIGHT (for W2-06 answer)
        light_recipe = sqlite_schema_utils.Recipe(
            title='Steamed Vegetable Medley',  # TARGET: clearly "light" and healthy
            description='A simple, light, and healthy steamed vegetable dish. Perfect for a diet-conscious dinner.',
            servings='2',
            preparationTime='20 minutes',
            ingredients='broccoli, carrots, zucchini, garlic, olive oil (light drizzle), salt, pepper, lemon juice',
            directions='1. Cut vegetables into bite-sized pieces. 2. Steam for 8-10 minutes. 3. Drizzle with olive oil and lemon. 4. Season to taste.',
            favorite=1  # Mark as favorite to make it more visible
        )
        all_recipes.append(light_recipe)
        logging.info("      ✅ Added: Steamed Vegetable Medley (TARGET - light)")
        
        # DISTRACTOR 1: Fried food (NOT light - violates diet)
        fried_recipe = sqlite_schema_utils.Recipe(
            title='Southern Fried Chicken',
            description='Classic crispy fried chicken with a crunchy coating.',
            servings='4',
            preparationTime='45 minutes',
            ingredients='chicken pieces, flour, eggs, breadcrumbs, vegetable oil (for deep frying), salt, pepper, paprika',
            directions='1. Season chicken. 2. Coat in flour, egg, and breadcrumbs. 3. Deep fry until golden.',
            favorite=0
        )
        all_recipes.append(fried_recipe)
        logging.info("      ❌ Added: Southern Fried Chicken (distractor - fried)")
        
        # DISTRACTOR 2: Oily/heavy food (NOT light)
        oily_recipe = sqlite_schema_utils.Recipe(
            title='Rich Beef Stew',
            description='A hearty and rich beef stew with thick gravy.',
            servings='6',
            preparationTime='2 hours',
            ingredients='beef chunks, potatoes, onions, carrots, beef broth, butter, flour, red wine',
            directions='1. Brown beef in butter. 2. Add vegetables. 3. Simmer with broth for 2 hours.',
            favorite=0
        )
        all_recipes.append(oily_recipe)
        logging.info("      ❌ Added: Rich Beef Stew (distractor - heavy)")
        
        # DISTRACTOR 3: Another fried option
        fried_recipe2 = sqlite_schema_utils.Recipe(
            title='Crispy Fried Fish',
            description='Beer-battered fried fish with tartar sauce.',
            servings='2',
            preparationTime='30 minutes',
            ingredients='white fish fillets, beer, flour, baking powder, oil for frying, salt',
            directions='1. Make beer batter. 2. Dip fish. 3. Deep fry until crispy golden.',
            favorite=0
        )
        all_recipes.append(fried_recipe2)
        logging.info("      ❌ Added: Crispy Fried Fish (distractor - fried)")
        
        # Additional light option for W4-07 and W6-02
        light_recipe2 = sqlite_schema_utils.Recipe(
            title='Grilled Salmon with Herbs',
            description='A light and healthy grilled salmon with fresh herbs.',
            servings='2',
            preparationTime='25 minutes',
            ingredients='salmon fillet, lemon, dill, parsley, olive oil (light coating), salt, pepper',
            directions='1. Season salmon. 2. Grill for 4-5 minutes per side. 3. Serve with lemon.',
            favorite=0
        )
        all_recipes.append(light_recipe2)
        logging.info("      ✅ Added: Grilled Salmon with Herbs (light option)")
        
        # 4. Insert recipes into database
        logging.info(f"      Step 3: Inserting {len(all_recipes)} recipes...")
        try:
            sqlite_utils.insert_rows_to_remote_db(
                rows=all_recipes,
                exclude_key='recipeId',
                table_name=_TABLE_NAME,
                remote_db_file_path=_DB_PATH,
                app_name=_APP_NAME,
                env=env,
            )
            logging.info(f"   ✅ Added {len(all_recipes)} recipes to Broccoli")
            logging.info("      - TARGET for W2-06: 'Steamed Vegetable Medley' (light)")
            logging.info("      - Distractors: Fried Chicken, Beef Stew, Fried Fish (NOT light)")
        except Exception as e:
            logging.error(f"   ❌ Failed to add recipes: {e}")
    
    # ==================== Subtask Initialization ====================
    
    def initialize_subtask(self, subtask_idx: int, env):
        """
        Custom subtask initialization
        
        Handle special environment setup for specific subtasks:
        - SMS tasks: Refresh UI and fill contacts map
        - Calendar QA tasks: Ensure events exist
        - Audio Recorder tasks: Clear previous recordings
        """
        from scendroid.env import adb_utils
        import time
        
        subtask = self.seven_day_subtasks[subtask_idx]
        task_id = subtask.task_id
        
        # SMS tasks: W1-05, W2-04, W4-04, W5-08
        sms_task_ids = ['W1-05', 'W2-04', 'W4-04', 'W5-08']
        if task_id in sms_task_ids:
            logging.info(f"   💬 SMS task {task_id} - preparing environment...")
            self._prepare_sms_environment(env)
        
        # Audio Recorder tasks: W1-06, W3-04, W4-01
        audio_task_ids = ['W1-06', 'W3-04', 'W4-01']
        if task_id in audio_task_ids:
            logging.info(f"   🎙️ Audio task {task_id} - ensuring clean state...")
            # Audio state is managed by the evaluator, just log
        
        # Call parent method (creates evaluator instance, sets time, etc.)
        super().initialize_subtask(subtask_idx, env)
        
        # Post-initialization: Fill SMS contacts map
        if task_id in sms_task_ids:
            self._fill_sms_contacts_map(subtask)
    
    def _prepare_sms_environment(self, env):
        """Prepare SMS environment before task execution
        
        ⚠️ NOTE: This method ONLY refreshes the SMS app UI.
        It does NOT clear SMS data - cross-day conversations are preserved.
        """
        from scendroid.env import adb_utils
        import time
        
        try:
            logging.info("      📱 Refreshing SMS UI (preserving existing messages)...")
            
            # Force stop SMS app to clear UI cache
            adb_utils.close_app("simple sms", env.controller)
            time.sleep(1.0)
            
            # Open SMS app
            logging.info("      📱 Opening SMS app...")
            adb_utils.start_activity(
                "com.simplemobiletools.smsmessenger/.activities.MainActivity",
                None,
                env.controller
            )
            time.sleep(2.0)
            
            # Press back to ensure we're at main screen
            logging.info("      📱 Pressing back to main screen...")
            for _ in range(3):
                adb_utils.issue_generic_request(
                    ["shell", "input", "keyevent", "KEYCODE_BACK"],
                    env.controller
                )
                time.sleep(0.3)
            
            # Press Home to exit
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
            
            logging.info("      ✅ SMS UI refreshed")
        except Exception as e:
            logging.warning(f"      ⚠️  SMS UI refresh failed: {e}")
    
    def _fill_sms_contacts_map(self, subtask):
        """Fill SMS evaluator's contacts map after initialization"""
        try:
            evaluator = subtask.evaluator_instance
            logging.info("      🔧 Filling contacts map...")
            
            if evaluator and hasattr(evaluator, '_contacts_map'):
                # Get attendees from parameters
                shared = self.generated_params.get('shared', {})
                attendees = shared.get('kickoff_attendees', ['Alice Smith', 'Bob Johnson', 'Charlie Williams', 'Diana Brown'])
                
                # Build contacts mapping
                contacts_mapping = {}
                for i, name in enumerate(attendees):
                    contacts_mapping[name] = f"555-010{i+1}"
                
                # Add distractors
                contacts_mapping["Charlie Wilson"] = "555-0201"
                contacts_mapping["David Lee"] = "555-0202"
                
                evaluator._contacts_map = contacts_mapping
                logging.info(f"      ✅ Contacts map filled: {len(contacts_mapping)} entries")
            else:
                logging.warning(f"      ⚠️  Evaluator has no _contacts_map attribute")
        except Exception as e:
            logging.warning(f"      ⚠️  Failed to fill contacts map: {e}")
    
    def tear_down(self, env):
        """
        Cleanup work after the 7-day scenario ends
        
        Important:
        - The 7-day scenario rebuilds the container only after the final day (Day 7) ends
        - The container is not rebuilt every day; it is rebuilt only after the 7-day period ends
        - Because the scenario contains multiple shopping tasks (W1-09, W3-07, etc.)
        """
        logging.info("=" * 70)
        logging.info("🧹 Scenario W (Weekly Work 7-Day) - Cleanup")
        logging.info("=" * 70)
        
        try:
            # Rebuild the Shopping container (restore the initial status after seven days)
            logging.info("   🛒 rebuild Shopping container(7daysscenarioend)...")
            try:
                from scendroid.task_evals.webarena import container_manager
                
                # extract console_port to ensure correct container rebuild
                # emulator-5554 → shopping (7770)
                # emulator-5556 → shopping_5556 (7772)
                # emulator-5558 → shopping_5558 (7774)
                console_port = None
                try:
                    console_port = env.controller._env._coordinator._simulator._config.emulator_launcher.emulator_console_port
                    logging.info(f"      📱 Emulator console port: {console_port}")
                except Exception as e:
                    logging.warning(f"      ⚠️  Could not extract console_port: {e}")
                
                manager = container_manager.ShoppingContainerManager(console_port=console_port)
                success = manager.rebuild_container()
                
                if success:
                    logging.info(f"      ✅ Shopping container rebuilt")
                    logging.info(f"         Container: {manager.docker_container}")
                    logging.info(f"         Port: {manager.host_port}")
                else:
                    logging.warning(f"      ⚠️  Failed to rebuild the Shopping container")
            except Exception as e:
                logging.warning(f"      ⚠️  Shopping container rebuild failed: {e}")
                import traceback
                logging.warning(traceback.format_exc())
        
        except Exception as e:
            logging.warning(f"   ⚠️  An error occurred during cleanup: {e}")
        
        # Call the parent class's tear_down (which cleans up all subtasks)
        super().tear_down(env)
        
        logging.info("✅ Scenario W (Weekly Work 7-Day) cleanup complete")
