"""
Scenario A: Busy Monday for David

Complex scenario containing 11 subtasks, simulating a busy workday: 
1. Adjust Weekday Alarm (Clock)
2. Check Morning Schedule (Calendar QA)
3. Extract Meeting Attendees (Calendar QA)
4. Send Meeting Reminder (SMS)
5. Prepare Meeting Outline (Markor)
6. Mark John Out of Office (Calendar)
7. Order Outdoor Table (Shopping)
8. Record Lunch Purchase (Expense)
9. Record Exercise Activity (OpenTracks)
10. Evening Summary (Markor)
11. Adjust Alarm Again Before Sleep (Clock) - depends on Task 1

features:
- Complex task sequence
- Dependencies between tasks (Task 11 depends on Task 1)
- Simulates a realistic one-day usage scenario
- Supports parameterized generation
"""

from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.scenario.base import BaseScenarioEvaluator


@AppRegistry.register_evaluator("ScenarioA_BusyMonday")
class ScenarioABusyMondayEvaluator(BaseScenarioEvaluator):
    """
    scenario A: Busy Monday for {user_name} - parameterized version
    
    description:
    Simulates David's busy Monday, from adjusting the alarm in the morning to summarizing in the evening and readjusting the alarm before sleep
    Covers schedule management, communication, shopping, and expense tracking
    
    Subtasks (11 total): 
    1. Adjust Weekday Alarm (Clock)
    2. Check Morning Schedule (Calendar QA)
    3. Extract Meeting Attendees (Calendar QA)
    4. Send Meeting Reminder (SMS)
    5. Prepare Meeting Outline (Markor)
    6. Mark John Out of Office (Calendar)
    7. Order Outdoor Table (Shopping)
    8. Record Lunch Purchase (Expense)
    9. Record Exercise Activity (OpenTracks)
    10. Evening Summary (Markor)
    11. Adjust Alarm Again Before Sleep (Clock) - depends on Task 1
    
    features:
    - Complex task sequence
    - Dependencies between tasks (Task 11 depends on Task 1)
    - Simulates a realistic one-day usage scenario
    - Uses base_date + time to set up device time
    
    rating:
    - Weights for all tasks, etc.
    - report completion status of each task when done
    """
    
    app_names = ("clock", "simple calendar pro", "simple sms messenger", 
                  "markor", "chrome", "pro expense", "opentracks")
    
    # ========== parameter template definition ==========
    PARAM_TEMPLATES = {
        # shared parameters (used across tasks)
        'shared': {
            'user_names': ['David', 'Sarah', 'Michael', 'Emily', 'Alex'],
            'meeting_titles': ['Company Weekly Meeting', 'Team Standup', 'Project Review', 'Sprint Planning', 'Client Sync'],
            'meeting_locations': ['Conference Room A', 'Meeting Room B', 'Board Room', 'Office 301', 'Zoom Room'],
            'attendee_groups': [
                ['John', 'Bob', 'Nierson', 'Hession'],
                ['Tom', 'Jerry', 'Mike', 'Lisa'],
                ['Chris', 'Emma', 'Ryan', 'Kate'],
                ['Anna', 'Peter', 'Diana', 'Frank'],
            ],
        },
        
        # Subtask 1: Adjust alarm
        'subtask_1': {
            'alarm_shift_minutes': [5, 10, 15, 20],  # Number of minutes to advance
            'original_hours': [7, 8, 9, 10],
            'original_minutes': [0, 15, 30, 35, 45],
        },
        
        # Subtask 11: Adjust alarm again before sleep (depends on subtask 1)
        'subtask_11': {
            'additional_shift_minutes': [3, 5, 8, 10],  # Number of additional minutes to advance
        },
        
        # Subtask 7: Shopping items
        'subtask_7': {
            'products': [
                {'sku': 'B07FM3WKJ8', 'name': 'Outdoor Patio Folding Side Table green', 'price': 54.99},
                {'sku': 'B078158XZ4', 'name': 'Egg Organic 12-count', 'price': 11.8},
                {'sku': 'B07KB88W7G', 'name': 'Dentemp Ora-GUARD Bruxism Night Guard (Two Pack)', 'price': 54.99},
                {'sku': 'B074QVN413', 'name': 'Tide PODS Spring Meadow Scent, 81 Count', 'price': 68.97},
                {'sku': 'B07ZQT1L6B', 'name': 'Apple iPhone 11 Pro, US Version, 256GB, Silver', 'price': 539.99},
            ],
        },
        
        # Subtask 8: Expense recording (associated with subtask 7 shopping)
        'subtask_8': {
            # expense_name now directly uses "Shopping" to match Task 7's shopping activity
            'expense_name': 'Shopping',
        },
        
        # Subtask 9: Check calendar availability before exercising (linked to Calendar)
        'subtask_9': {
            # Whether there is a meeting during Task 9's time slot (parameterized: sometimes available, sometimes not)
            'has_meeting_options': [True, False],
            # If there is a meeting, possible meeting titles
            'blocking_meeting_titles': ['Evening Sync', 'Quick Call', 'Status Update', 'Team Check-in'],
        },
    }
    
    @classmethod
    def generate_random_params(cls, seed=None):
        """
        Generate random parameters for Scenario B
        
        Args:
            seed: random seed
            
        Returns:
            parameter dictionary containing all subtask parameters
        """
        import random
        
        if seed is not None:
            random.seed(seed)
        
        # 1. generate shared parameters
        user_name = random.choice(cls.PARAM_TEMPLATES['shared']['user_names'])
        meeting_title = random.choice(cls.PARAM_TEMPLATES['shared']['meeting_titles'])
        meeting_location = random.choice(cls.PARAM_TEMPLATES['shared']['meeting_locations'])
        attendee_names = random.choice(cls.PARAM_TEMPLATES['shared']['attendee_groups'])
        
        shared_params = {
            'user_name': user_name,
            'meeting_title': meeting_title,
            'meeting_location': meeting_location,
            'attendee_names': attendee_names,
            # Generate full contact name for SMS
            'attendee_full_names': [f"{name} Smith" if name == attendee_names[0] else 
                                   f"{name} Johnson" if name == attendee_names[1] else 
                                   f"{name} Williams" if name == attendee_names[2] else 
                                   f"{name} Brown" for name in attendee_names],
        }
        
        # 2. Generate subtask 1 parameters (alarm)
        original_hour = random.choice(cls.PARAM_TEMPLATES['subtask_1']['original_hours'])
        original_minute = random.choice(cls.PARAM_TEMPLATES['subtask_1']['original_minutes'])
        shift_minutes = random.choice(cls.PARAM_TEMPLATES['subtask_1']['alarm_shift_minutes'])
        
        # Calculate new time (advanced by shift_minutes minutes)
        new_total_minutes = original_hour * 60 + original_minute - shift_minutes
        new_hour = (new_total_minutes // 60) % 24
        new_minute = new_total_minutes % 60
        
        subtask_1_params = {
            'original_hour': original_hour,
            'original_minute': original_minute,
            'shift_minutes': shift_minutes,
            'new_hour': new_hour,
            'new_minute': new_minute,
        }
        
        # 3. Generate subtask 7 parameters (shopping)
        selected_product = random.choice(cls.PARAM_TEMPLATES['subtask_7']['products'])
        subtask_7_params = selected_product.copy()
        
        # 4. Generate subtask 8 parameters (expense recording)
        # Use subtask 7's price as the expense amount (reflecting inter-task dependency)
        # expense_name is fixed as "Shopping" to match Task 7's shopping behavior
        subtask_8_params = {
            'expense_name': 'Shopping',
            'expense_amount': selected_product['price'],
        }
        
        # 5. Generate subtask 9 parameters (check calendar availability before exercising)
        # Parameterized: sometimes there is a meeting (cannot exercise), sometimes no meeting (can exercise)
        has_meeting = random.choice(cls.PARAM_TEMPLATES['subtask_9']['has_meeting_options'])
        blocking_meeting_title = random.choice(cls.PARAM_TEMPLATES['subtask_9']['blocking_meeting_titles'])
        
        subtask_9_params = {
            'has_blocking_meeting': has_meeting,
            'blocking_meeting_title': blocking_meeting_title if has_meeting else None,
            # Task 9 time is 18:00; check for meetings within 30 minutes
            'task_time': '18:00',
            'check_duration_minutes': 30,
        }
        
        # 6. Generate subtask 11 parameters (adjust alarm again before sleep, depends on subtask 1)
        additional_shift = random.choice(cls.PARAM_TEMPLATES['subtask_11']['additional_shift_minutes'])
        
        # Calculate new time advanced again from the time adjusted in Task 1
        # Time after Task 1 adjustment is new_hour:new_minute
        # Task 11 must be scheduled additional_shift minutes earlier
        task11_total_minutes = new_hour * 60 + new_minute - additional_shift
        task11_new_hour = (task11_total_minutes // 60) % 24
        task11_new_minute = task11_total_minutes % 60
        
        # Ensure the number of minutes is a multiple of 5
        task11_new_minute = (task11_new_minute // 5) * 5
        
        subtask_11_params = {
            'previous_hour': new_hour,  # Adjusted time for Task 1 (starting point for Task 11)
            'previous_minute': new_minute,
            'additional_shift_minutes': additional_shift,
            'final_hour': task11_new_hour,
            'final_minute': task11_new_minute,
        }
        
        # 7. Return the complete set of parameters
        return {
            'seed': seed,
            'shared': shared_params,
            'subtask_1': subtask_1_params,
            'subtask_7': subtask_7_params,
            'subtask_8': subtask_8_params,
            'subtask_9': subtask_9_params,
            'subtask_11': subtask_11_params,
        }
    
    def __init__(self, params: dict = None):
        """
        initialize Scenario B
        
        Args:
            params: scenario parameters. If None, calls generate_random_params() to generate random parameters
                   If the 'generated_params' key is provided, use the parameterized data from it
        """
        # 1. check if random parameters need to be generated
        if params is None:
            params = {}
        
        # generate if no generated_params exist
        if 'generated_params' not in params:
            generated_params = self.generate_random_params()
            params['generated_params'] = generated_params
        else:
            generated_params = params['generated_params']
        
        # extract shared parameters
        shared = generated_params.get('shared', {})
        user_name = shared.get('user_name', 'David')
        
        # set scenario metadata
        scenario_params = {
            'scenario_id': 'A',
            'name': f'Busy Monday for {user_name}',
            'base_date': '2025-12-26',  # Friday, December 26, 2025
            'total_max_steps': 270,  # 11 subtasks, averaging 20–30 steps each
            'success_criteria': {
                'all_subtasks_pass': False,
                'min_subtasks_pass': 0,  # No minimum pass requirement enforced; only report completion status
            },
            'generated_params': generated_params,  # Pass parameters to the parent class
            'clarity_level': params.get('clarity_level'),  # ⚡ pass clarity_level
            'reset_mode': params.get('reset_mode', False),  # ⚡ pass reset_mode
        }
        
        super().__init__(scenario_params)
        
        # add subtasks using parameterized approach
        self._add_parameterized_subtasks(generated_params)
        
        # set complexity
        self.complexity = 4.5
    
    def _add_parameterized_subtasks(self, generated_params: dict):
        """Add all subtasks using the generated parameters"""
        shared = generated_params.get('shared', {})
        st1 = generated_params.get('subtask_1', {})
        st7 = generated_params.get('subtask_7', {})
        st8 = generated_params.get('subtask_8', {})
        
        # Extract shared parameters (provide default values in case parameter generation fails)
        user_name = shared.get('user_name', 'David')
        meeting_title = shared.get('meeting_title', 'Company Weekly Meeting')
        meeting_location = shared.get('meeting_location', 'Conference Room A')
        attendee_names = shared.get('attendee_names', ['John', 'Bob', 'Nierson', 'Hession'])
        attendee_full_names = shared.get('attendee_full_names', ['John Smith', 'Bob Johnson', 'Nierson Williams', 'Hession Brown'])
        
        # Subtask 1: Adjust the weekday alarm (parameterized, supports L0–L2)
        shift_min = st1.get('shift_minutes', 10)
        original_hour = st1.get('original_hour', 10)
        original_minute = st1.get('original_minute', 35)
        new_hour = st1.get('new_hour', 10)
        new_minute = st1.get('new_minute', 25)
        # Format the time string (e.g., "10:35" → "10:25")
        original_time_str = f"{original_hour}:{original_minute:02d}"
        new_time_str = f"{new_hour}:{new_minute:02d}"
        
        self.add_subtask(
            subtask_id=1,
            evaluator_name="LayeredClockSetAlarm",
            params={
                "alarm_time_hour": new_hour,
                "alarm_time_minute": new_minute,
                "alarm_enabled": True,
                "check_original_removed": True,
                "original_hour": original_hour,
                "original_minute": original_minute,
            },
            weight=1.0,
            time="10:40",
            narration=f"{user_name} almost missed work this morning and decides to set the weekday alarm {shift_min} minutes earlier",
            user_instruction=f"Morning, Agent, I'm {user_name}. Move my work alarm {shift_min} minutes earlier, only change the weekday one.",
            user_instruction_L0=f"Open Clock app and change my weekday alarm from {original_time_str} to {new_time_str}.",
            user_instruction_L1=f"Move my work alarm {shift_min} minutes earlier, only change the weekday one.",
            user_instruction_L2="I've been waking up too late recently, help me adjust my weekday alarm.",
            max_steps=20,
            requires_answer=False,
        )
        
        # Subtask 2: Check the morning schedule (Q&A task, parameterized, supports L0–L2)
        self.add_subtask(
            subtask_id=2,
            evaluator_name="LayeredCalendarCheckMeetingAnswer",
            params={
                "must_contain_keywords": ["11:30", "meeting", meeting_title.lower().split()[0]],
                "min_keywords_found": 2,
            },
            weight=1.0,
            time="11:10",
            narration=f"Arrived at office, {user_name} wants to confirm the morning schedule",
            user_instruction="Check my Simple Calendar Pro and tell me what meetings I have this morning before noon",
            user_instruction_L0="Check my Simple Calendar Pro and tell me what meetings I have this morning before noon",
            user_instruction_L1="Check my calendar and tell me what meetings I have this morning before noon",
            user_instruction_L2="What's on my schedule for this morning?",
            max_steps=25,
            requires_answer=True,
        )
        
        # Subtask 3: Extract meeting attendees (Q&A task, parameterized, supports L0–L2)
        self.add_subtask(
            subtask_id=3,
            evaluator_name="LayeredCalendarExtractAttendees",
            params={
                "event_title": meeting_title,
                "required_attendees": attendee_names,
                "min_attendees_found": 4,
                "exclude_self": True,
            },
            weight=1.0,
            time="11:18",
            narration=f"{user_name} doesn't want to manually check the calendar for the attendee list",
            user_instruction=f"Read the attendee list from that meeting you have checked and list them for me",
            user_instruction_L0=f"Read the attendee list from the {meeting_title} in Simple Calendar Pro and list them for me",
            user_instruction_L1=f"Read the attendee list from the {meeting_title} and list them for me",
            user_instruction_L2="I need to know who's coming to the meeting.",
            max_steps=20,
            requires_answer=True,
        )
        
        # Subtask 4: Send a meeting reminder (parameterized, supports L0–L2)
        # Extract keywords for the meeting location for evaluation
        location_keywords = [meeting_location, meeting_location.split()[0]]
        if 'Room' in meeting_location:
            location_keywords.append('Room')
        
        # Construct a clear instruction for reset mode (explicitly specify recipient and content)
        attendee_names_str = ', '.join(attendee_names)
        attendee_full_names_str = ', '.join(attendee_full_names)
        
        self.add_subtask(
            subtask_id=4,
            evaluator_name="LayeredSMSBatchNotify",
            params={
                "required_recipients": attendee_full_names,
                "message_must_contain_time": "11:30",
                "message_must_contain_location": location_keywords,
                "forbidden_recipients": ["Alice Davis", "Charlie Wilson"],
                "min_messages_sent": 4,
                "reset_user_instruction": f"Open Simple SMS Messenger and send a meeting reminder to these 4 people: {attendee_full_names_str}. The message must include: meeting time '11:30' and meeting location '{meeting_location}'.",
            },
            weight=1.0,
            time="11:20",
            narration=f"{user_name} wants to remind everyone about the in-person meeting location",
            user_instruction="Use Simple SMS Messenger to remind them to attend the meeting (include time and location)",
            user_instruction_L0=f"First, open Simple Calendar Pro to check the attendee list of '{meeting_title}'. Then, use Simple SMS Messenger to send messages to all attendees reminding them to attend the meeting (include the time and location in the message).",
            user_instruction_L1="Send them SMS to remind about the meeting (include time and location)",
            user_instruction_L2="Let everyone know about the meeting.",
            max_steps=30,
            requires_answer=False,
        )
        
        # Subtask 5: Prepare the meeting agenda (parameterized, supports L0–L2)
        self.add_subtask(
            subtask_id=5,
            evaluator_name="LayeredMarkorCreateOutline",
            params={
                "file_name": "WorkLog.md",
                "required_sections": ["Title", "Time", "Location", "Attendees", "Discussion"],
                "sections_with_content": ["Title", "Time", "Location", "Attendees"],
                "header_only_sections": ["Discussion"],
                "reset_user_instruction": f"Open Markor, create a new file 'WorkLog.md' with the title '# Weekly Meeting Notes Outline'. Add these sections with content: Title: {meeting_title}, Time: 11:30 AM - 12:30 PM, Location: {meeting_location}, Attendees: {user_name}, {attendee_names_str}. Add a 'Discussion Notes' section header (no content needed).",
            },
            weight=1.0,
            time="11:25",
            narration=f"{user_name} wants to prepare a meeting notes template to fill in during the meeting",
            user_instruction="Open Markor, create a 'Weekly Meeting Notes Outline' in a new file 'WorkLog.md' with structured sections: Title (fill in content), Time (fill in content), Location (fill in content), Attendees (fill in content), Discussion Notes (header only)",
            user_instruction_L0="Open Markor, create a 'Weekly Meeting Notes Outline' in a new file 'WorkLog.md' with structured sections: Title (fill in content), Time (fill in content), Location (fill in content), Attendees (fill in content), Discussion Notes (header only)",
            user_instruction_L1="Create a meeting notes outline in WorkLog.md with sections: Title, Time, Location, Attendees, Discussion Notes",
            user_instruction_L2="Help me to prepare a meeting template.",
            max_steps=25,
            requires_answer=False,
        )
        
        # Subtask 6: Mark the first attendee as out of office (parameterized, supports L0–L2)
        first_attendee = attendee_names[0]
        # 🆕 In addition to checking newly added content, also verify that original content remains intact
        # Original description: "Attendees: {user_name}, {attendee_1}, {attendee_2}, {attendee_3}, {attendee_4}"
        # Keywords to check: newly added content + names from the original content
        note_keywords = [
            first_attendee,       # Newly added: name of the first attendee
            "out of office",      # Newly added: out-of-office indication
            user_name,            # Original content: user name must be retained
            "attendees",          # Original content: "Attendees" heading must be retained
        ]
        # Add other attendee names (ensuring original content remains unaltered)
        for name in attendee_names[1:]:  # skip the first (already included in first_attendee)
            note_keywords.append(name)
        
        self.add_subtask(
            subtask_id=6,
            evaluator_name="LayeredCalendarEditNote",
            params={
                "event_title": meeting_title,
                "note_must_contain": note_keywords,
                "should_not_create_new_event": True,
            },
            weight=1.0,
            time="11:50",
            narration=f"{first_attendee} is traveling, won't need to invite them in-person for next two weeks",
            user_instruction=f"Add a note to the meeting we just discussed in calendar: '{first_attendee}, out of office'",
            user_instruction_L0=f"Open Simple Calendar Pro, find '{meeting_title}', and add a note '{first_attendee}, out of office' in the third line",
            user_instruction_L1=f"Add '{first_attendee}, out of office' to that meeting's notes",
            user_instruction_L2=f"Someone won't be here, update the meeting note accordingly.",
            max_steps=25,
            requires_answer=False,
        )
        
        # Subtask 7: Order an item (parameterized, supports L0–L2)
        product_sku = st7.get('sku', 'B07FM3WKJ8')
        product_name = st7.get('name', 'Outdoor Patio Folding Side Table green')
        product_price = st7.get('price', 49.99)
        
        # Extract product keywords for L2
        product_keywords = product_name.split()[:3]  # Take the first three words
        product_type = "table" if "table" in product_name.lower() else "product"
        
        self.add_subtask(
            subtask_id=7,
            evaluator_name="LayeredShoppingPurchaseProduct",
            params={
                "product_sku": product_sku,
                "product_price": product_price,
                "check_method": "order",
                "eval_types": ["program_html"],
                "program_html": [
                    {
                        "url": "func:shopping_get_latest_order_url()",
                        "locator": "document.querySelector('.order-details-items.ordered').outerText",
                        "required_contents": {
                            "must_include": [product_sku]
                        }
                    }
                ],
                "require_login": True,
                "start_url": "__SHOPPING__",
            },
            weight=1.0,
            time="12:50",
            narration=f"{user_name} sees the reminder to buy {product_name}",
            user_instruction=f"On the current webpage (ignore the internet access), clear my cart, add the '{product_name}' to my cart and place an order.",
            user_instruction_L0=f"On the current webpage (ignore the internet access), clear my cart first, then add the '{product_name}' to my cart and place an order.",
            user_instruction_L1=f"On the current webpage (ignore the internet access), place an order for the '{product_name}'.",
            user_instruction_L2=f"On the current webpage (ignore the internet access), buy one {product_name}.",
            max_steps=30,
            requires_answer=False,
        )
        
        # Subtask 8: Record an expense (depends on shopping from Subtask 7, supports L0–L2)
        expense_name = st8.get('expense_name', 'Shopping')  # Fixed as "Shopping", linked to Task 7
        expense_amount = st8.get('expense_amount', product_price)  # Use the shopping amount
        
        self.add_subtask(
            subtask_id=8,
            evaluator_name="LayeredExpenseAddSingle",
            params={
                "name": expense_name,
                "amount": expense_amount,
                # "category": "Others",
                "date": "2025-12-26",
            },
            weight=1.0,
            time="12:40",
            narration=f"{user_name} wants to track the shopping expense from the order just placed",
            user_instruction=f"Record this shopping purchase in Pro Expense app, note it as 'Shopping', use the order total I just placed as amount",
            user_instruction_L0=f"Open Pro Expense app, record a new expense: name 'Shopping', amount ${expense_amount} (from the order I just placed)",
            user_instruction_L1=f"Record the shopping I just placed in Pro Expense",
            user_instruction_L2="Log what I just spent on the order.",
            max_steps=20,
            requires_answer=False,
        )
        
        # Subtask 9: Exercise after checking calendar availability (interacts with Calendar, parameterized)
        st9 = generated_params.get('subtask_9', {})
        has_blocking_meeting = st9.get('has_blocking_meeting', False)
        blocking_meeting_title = st9.get('blocking_meeting_title', 'Evening Sync')
        
        # Set up different evaluation parameters depending on whether a meeting exists
        task9_params = {
            "has_blocking_meeting": has_blocking_meeting,
            "blocking_meeting_title": blocking_meeting_title,
            "task_time": "18:00",
            "check_duration_minutes": 30,
        }
        
        # Construct the instruction
        # Evaluation logic:
        #   - With a meeting: the agent must mention the meeting name/time and must not initiate an exercise recording
        #   - Without a meeting: the agent must initiate OpenTracks exercise recording
        if has_blocking_meeting:
            # Scenario with meetings: Expect the agent to detect the meeting and inform the user of the meeting information, without launching exercise
            task9_narration = f"{user_name} wants to exercise but needs to check calendar first. There IS a meeting '{blocking_meeting_title}' at 18:15."
            task9_instruction = f"Do I have any meetings in the next 30 minutes? If yes, tell me the meeting name. If I'm free, start recording exercise in OpenTracks."
            task9_instruction_L0 = f"Open Simple Calendar Pro and check if there are any events between 18:00-18:30. If there's a meeting, tell me its name and don't start exercise. If free, open OpenTracks and start recording."
            task9_instruction_L1 = f"Check if I have any meetings in the next 30 minutes. If yes, tell me which one. If not, record my exercise."
            task9_instruction_L2 = "Am I free for the next half hour? Tell me if I have any appointments."
        else:
            # Scenario without meetings: Expect the agent to confirm the absence of meetings and then record the start of exercise
            task9_narration = f"{user_name} wants to exercise and needs to verify calendar is clear. No meetings scheduled."
            task9_instruction = f"Do I have any meetings in the next 30 minutes? If I'm free, start recording exercise in OpenTracks."
            task9_instruction_L0 = f"Open Simple Calendar Pro and check if there are any events between 18:00-18:30. If free, open OpenTracks and start recording."
            task9_instruction_L1 = "Check if I have any meetings in the next 30 minutes. If not, record my exercise."
            task9_instruction_L2 = "Am I free for the next half hour? If so, track my run."
        
        self.add_subtask(
            subtask_id=9,
            evaluator_name="LayeredCalendarCheckThenExercise",
            params=task9_params,
            weight=1.0,
            time="18:00",
            narration=task9_narration,
            user_instruction=task9_instruction,
            user_instruction_L0=task9_instruction_L0,
            user_instruction_L1=task9_instruction_L1,
            user_instruction_L2=task9_instruction_L2,
            max_steps=30,
            on_fail="continue",
            requires_answer=has_blocking_meeting,  # Requires agent response when a meeting exists
        )
        
        # Subtask 10: Evening summary (parameterized, supports L0-L2)
        meeting_keywords = ["meeting", meeting_title.split()[0], meeting_title.split()[1] if len(meeting_title.split()) > 1 else ""]
        
        self.add_subtask(
            subtask_id=10,
            evaluator_name="LayeredMarkorAppendContent",
            params={
                "file_name": "WorkLog.md",
                # 🆕 No longer detect section_title; detect only keywords
                "must_mention_meeting": True,
                "meeting_keywords": meeting_keywords,
                "must_mention_expense": True,
                "expense_amount": product_price,
            },
            weight=1.0,
            time="21:05",
            narration=f"{user_name} wants to wrap up the day's key events",
            user_instruction="Open Markor and add a daily summary to WorkLog.md mentioning today's key events (meeting, expense)",
            user_instruction_L0=f"Open Markor and add a daily summary to WorkLog.md. Include: meeting '{meeting_title}' and expense ${product_price}.",
            user_instruction_L1="Add a daily summary to WorkLog.md about today's key events and details (meeting, expense)",
            user_instruction_L2="Help me to record what happened today.",
            max_steps=30,
            on_fail="continue",
            requires_answer=False,
        )
        
        # Subtask 11: Adjust alarm again before bedtime (depends on subtask 1, parameterized, supports L0-L2)
        st11 = generated_params.get('subtask_11', {})
        previous_hour = st11.get('previous_hour', new_hour)  # Time after adjustment in Task 1
        previous_minute = st11.get('previous_minute', new_minute)
        additional_shift = st11.get('additional_shift_minutes', 5)
        final_hour = st11.get('final_hour', previous_hour)
        final_minute = st11.get('final_minute', previous_minute - 5)
        
        # Format time string
        previous_time_str = f"{previous_hour}:{previous_minute:02d}"
        final_time_str = f"{final_hour}:{final_minute:02d}"
        
        self.add_subtask(
            subtask_id=11,
            evaluator_name="LayeredClockSetAlarm",
            params={
                "alarm_time_hour": final_hour,
                "alarm_time_minute": final_minute,
                "alarm_enabled": True,
                "check_original_removed": True,
                "original_hour": previous_hour,
                "original_minute": previous_minute,
            },
            weight=1.0,
            time="21:55",
            narration=f"Before sleep, {user_name} is still worried about waking up late tomorrow and decides to set the alarm even earlier",
            user_instruction=f"I'm worried about waking up late. Move my morning alarm {additional_shift} minutes earlier again.",
            user_instruction_L0=f"Open Clock app and change my work alarm from {previous_time_str} to {final_time_str}.",
            user_instruction_L1=f"Move my morning alarm {additional_shift} minutes earlier again.",
            user_instruction_L2="I'm still worried about tomorrow morning. Make sure I wake up earlier.",
            max_steps=20,
            requires_answer=False,
        )
    
    def initialize_task(self, env):
        """
        batch initialization at scenario start
        
        pre-configure environment for all subtasks:
        - createalarm (for subtask 1)
        - createcalendarevent (for subtasks 2, 3, 6)
        - create contact (for subtask 4)
        - Chrome login (for subtask 7)
        - cleanupfile(Markor, Expense etc.)
        
        Note: Device time is set up in each subtask's initialize_subtask()!
        """
        # Call parent class method (set up base_date etc. + WebArena environment variables)
        super().initialize_task(env)
        
        # ⚡ Resetmode: skip batch init, each task initializes independently in _reset_initialize_subtask()
        if self.reset_mode:
            logging.info("⚡ Reset Mode: Skipping batch initialization")
            logging.info("   Each task will be initialized independently before execution")
            # only ensure timezone is UTC (needed by almost all tasks)
            self._ensure_utc_timezone(env)
            return
        
        logging.info("🔧 Batch-initializing Scenario A environment...")
        
        # ⚠️ critical fix: ensure timezone is UTC first during scenario initialization
        # This fixes the Calendar displaying incorrect time (e.g., showing 19:30 instead of 11:30)
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
            # 1. createalarm (for subtask 1)
            self._setup_clocks(env)
            
            # 2. createcalendarevent (for subtasks 2, 3, 6)
            self._setup_calendar_events(env)
            
            # 3. create contact (for subtask 4)
            self._setup_contacts(env)
            
            # 4. cleanup Markor, Expense and OpenTracks data
            # Note: Execute Chrome login latency during subtask 7 (more reliable)
            self._cleanup_app_data(env)
            
            # 5. Initialize OpenTracks (for subtask 9)
            self._setup_opentracks(env)
            
            logging.info("✅ batch initialization complete")
            
        except Exception as e:
            logging.error(f"❌ batch initialization failed: {e}")
            import traceback
            logging.error(traceback.format_exc())
            raise
    
    def _setup_clocks(self, env):
        """createalarm – parameterized version"""
        logging.info("   📱 createalarm...")
        
        from scendroid.env import adb_utils
        import time
        
        # ⚠️ Key: Clear existing alarm data (not just closing the app)
        # Reference: clock/utils.py close_clock_app() uses clear_app_data
        try:
            logging.info("      🗑️  Clearing existing alarms...")
            adb_utils.clear_app_data(
                adb_utils.extract_package_name(adb_utils.get_adb_activity("clock")),
                env.controller,
            )
            time.sleep(1.0)
            logging.info("      ✅ alarmdata cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear clock data: {e}")
        
        # Retrieve the original weekday alarm time from parameters
        st1 = self.generated_params.get('subtask_1', {})
        work_alarm_hour = st1.get('original_hour', 10)
        work_alarm_minute = st1.get('original_minute', 35)
        
        # Create 3 alarms (the first one is parameterized)
        self._set_alarm_with_days(env, hour=work_alarm_hour, minute=work_alarm_minute, 
                                 message="Work", days=[2, 3, 4, 5, 6])
        time.sleep(1.0)
        
        self._set_alarm_with_days(env, hour=17, minute=10, message="Leave_Work", days=[2, 3, 4, 5, 6])
        time.sleep(1.0)
        
        self._set_alarm_with_days(env, hour=22, minute=0, message="Sleep", days=[1, 2, 3, 4, 5, 6, 7])
        time.sleep(1.0)
        
        logging.info("   ✅ alarmcreatecomplete")
    
    def _set_alarm_with_days(self, env, hour: int, minute: int, message: str, days: list):
        """Set up recurring alarms"""
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
        """createcalendarevent – parameterized version"""
        logging.info("   📅 createcalendarevent...")
        
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from scendroid.env import adb_utils
        from datetime import datetime
        import calendar as cal_module
        import time
        
        # ⚠️ Clear Calendar app data (to reset view, setup, etc.)
        logging.info("      🗑️  Clearing Simple Calendar Pro app data...")
        try:
            adb_utils.clear_app_data(
                "com.simplemobiletools.calendar.pro",  # Simple Calendar Pro package name
                env.controller,
            )
            time.sleep(1.5)
            logging.info("      ✅ Calendar app data cleared (view reset)")
            
            # ⚠️ Key fix: After clearing app data, reconfirm timezone as UTC
            # This resolves the Calendar time display issue (19:30 vs 11:30)
            logging.info("      🌍 Re-setting device timezone to UTC...")
            from scendroid.utils import datetime_utils
            
            # Method 1: Use ScenDroid's standard method
            adb_utils.issue_generic_request(
                ['shell', 'service', 'call', 'alarm', '3', 's16', 'UTC'],
                env.controller
            )
            time.sleep(0.5)
            
            # Method 2: Also set system property (double safeguard)
            adb_utils.issue_generic_request(
                ['shell', 'setprop', 'persist.sys.timezone', 'UTC'],
                env.controller
            )
            time.sleep(0.5)
            logging.info("      ✅ Device timezone set to UTC")
            
            # Launch Calendar app once for initialization (skip welcome screen)
            logging.info("      📱 Launching Calendar app for initialization...")
            adb_utils.start_activity(
                "com.simplemobiletools.calendar.pro/.activities.MainActivity",
                None,
                env.controller
            )
            time.sleep(2.5)  # etc. Wait for the app to fully load and complete timezone setup
            
            # Return to the main screen
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            logging.info("      ✅ Calendar app has been initialized")
            
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear calendar app data: {e}")
        
        # Clear existing events (double safety)
        calendar_utils.clear_calendar_db(env)
        
        # ✅ Use a fixed base_date (2025-12-26), timezone-agnostic!
        # Refer to the implementation in the old architecture (scenario_env_setup.py lines 526–527)
        # Use calendar.timegm() instead of .timestamp() to avoid timezone issues
        base_date = datetime(2025, 12, 26, 0, 0, 0)
        
        logging.info(f"   📅 Using FIXED base date (UTC): {base_date.strftime('%Y-%m-%d')}")
        
        # Extract meeting information from the generated parameters
        shared = self.generated_params.get('shared', {})
        meeting_title = shared.get('meeting_title', 'Company Weekly Meeting')
        meeting_location = shared.get('meeting_location', 'Conference Room A')
        user_name = shared.get('user_name', 'David')
        attendee_names = shared.get('attendee_names', ['John', 'Bob', 'Nierson', 'Hession'])
        
        # createeventlist
        events = []
        
        # Event 1: Main meeting at 11:30 (for subtasks 2, 3, and 6) (parameterized)
        meeting_dt = base_date.replace(hour=11, minute=30, second=0, microsecond=0)
        # Use calendar.timegm() — timezone-agnostic conversion (treats naive datetime as UTC)
        meeting_start_ts = cal_module.timegm(meeting_dt.timetuple())
        meeting_end_ts = meeting_start_ts + (60 * 60)
        
        # Construct attendee description
        attendees_str = f"Attendees: {user_name}, " + ", ".join(attendee_names)
        
        event1 = sqlite_schema_utils.CalendarEvent(
            start_ts=meeting_start_ts,
            end_ts=meeting_end_ts,
            title=meeting_title,
            location=meeting_location,
            description=attendees_str,
        )
        events.append(event1)
        logging.info(f"   📌 Event: {meeting_title} @ 11:30 (UTC ts: {meeting_start_ts})")
        
        # Event 2: Client Presentation at 15:00 (distractor event)
        presentation_dt = base_date.replace(hour=15, minute=0, second=0, microsecond=0)
        presentation_start_ts = cal_module.timegm(presentation_dt.timetuple())
        presentation_end_ts = presentation_start_ts + (90 * 60)
        
        event2 = sqlite_schema_utils.CalendarEvent(
            start_ts=presentation_start_ts,
            end_ts=presentation_end_ts,
            title="Client Presentation",
            location="Meeting Room B",
            description="Attendees: Alice, Tom",
        )
        events.append(event2)
        logging.info(f"   📌 Event: Client Presentation @ 15:00 (UTC ts: {presentation_start_ts})")
        
        # 🆕 Event 3 (optional): Meeting during the Task 9 time window (parameterized)
        # Determine whether a meeting exists between 18:00–18:30 based on the subtask_9 parameter
        st9 = self.generated_params.get('subtask_9', {})
        has_blocking_meeting = st9.get('has_blocking_meeting', False)
        blocking_meeting_title = st9.get('blocking_meeting_title', 'Evening Sync')
        
        if has_blocking_meeting:
            # Create a meeting from 18:15–18:45 (overlapping with Task 9's 18:00 check time)
            blocking_dt = base_date.replace(hour=18, minute=15, second=0, microsecond=0)
            blocking_start_ts = cal_module.timegm(blocking_dt.timetuple())
            blocking_end_ts = blocking_start_ts + (30 * 60)  # 30-minute meeting
            
            event3 = sqlite_schema_utils.CalendarEvent(
                start_ts=blocking_start_ts,
                end_ts=blocking_end_ts,
                title=blocking_meeting_title,
                location="Phone Call",
                description="Quick sync call",
            )
            events.append(event3)
            logging.info(f"   📌 Event: {blocking_meeting_title} @ 18:15 (Task 9 blocking meeting)")
        else:
            logging.info(f"   ℹ️  No blocking meeting for Task 9 (user is free to exercise)")
        
        # Add event to database
        calendar_utils.add_events(events, env)
        time.sleep(2.0)
        
        logging.info("   ✅ calendareventcreatecomplete")
    
    def _setup_contacts(self, env):
        """Create contact (for SMS task) — parameterized version"""
        logging.info("   👥 create contact...")
        
        from scendroid.utils import contacts_utils
        from scendroid.env import adb_utils
        import time
        
        # Clear existing contacts
        contacts_utils.clear_contacts(env.controller)
        time.sleep(1.0)
        
        # ✅ Clear existing SMS messages (refer to old architecture scenario_env_setup.py lines 606–635)
        logging.info("   💬 Clearing existing SMS messages...")
        try:
            from scendroid.task_evals.common_validators import sms_validators
            
            # SMS messages are stored in Android's telephony provider, not in Simple SMS Messenger's database
            sms_validators.clear_sms_and_threads(env.controller)
            logging.info("      ✅ SMSdatabase cleared")
            
            # Force-stop Simple SMS Messenger
            adb_utils.close_app("simple sms", env.controller)
            time.sleep(1.0)
            
            # Open and close the app to force UI refresh
            logging.info("      📱 Opening SMS app to refresh UI...")
            adb_utils.start_activity(
                "com.simplemobiletools.smsmessenger/.activities.MainActivity",
                None,
                env.controller
            )
            time.sleep(2.0)  # etc. Wait for app to fully load
            
            # Press back button to exit
            adb_utils.issue_generic_request(
                ["shell", "input", "keyevent", "KEYCODE_BACK"],
                env.controller
            )
            time.sleep(1.0)
            logging.info("      ✅ SMS app UI has been refreshed")
        except Exception as e:
            logging.warning(f"      ⚠️  Failed to clear SMS: {e}")
        
        # Extract contact information from the generated parameters
        shared = self.generated_params.get('shared', {})
        attendee_full_names = shared.get('attendee_full_names', 
                                         ['John Smith', 'Bob Johnson', 'Nierson Williams', 'Hession Brown'])
        
        # Create meeting attendees and distractor contacts (parameterized)
        contacts = [
            {"name": attendee_full_names[0], "phone": "555-0101"},
            {"name": attendee_full_names[1], "phone": "555-0102"},
            {"name": attendee_full_names[2], "phone": "555-0103"},
            {"name": attendee_full_names[3], "phone": "555-0104"},
            {"name": "Alice Davis", "phone": "555-0201"},  # Distractor
            {"name": "Charlie Wilson", "phone": "555-0202"},  # Distractor
        ]
        
        logging.info(f"   📞 Adding {len(contacts)} contacts (with retry mechanism)...")
        
        successfully_added = 0
        for i, contact in enumerate(contacts, 1):
            name = contact.get('name')
            phone = contact.get('phone')
            if not name or not phone:
                continue
            
            # Refer to old architecture: retry mechanism (scenario_env_setup.py lines 653–682)
            success = False
            for attempt in range(2):
                try:
                    if attempt > 0:
                        logging.info(f"      ↻ retry '{name}' (attempt {attempt + 1})")
                    
                    # Key: Press Home key before each contact (to ensure stable status)
                    adb_utils.press_home_button(env.controller)
                    time.sleep(1.5)
                    
                    # Key: Pass ui_delay_sec=2.0 parameter (etc. wait for UI response)
                    contacts_utils.add_contact(
                        name, 
                        phone, 
                        env.controller,
                        ui_delay_sec=2.0
                    )
                    logging.info(f"      ✅ Added {i}/{len(contacts)}: '{name}' ({phone})")
                    successfully_added += 1
                    success = True
                    time.sleep(2.0)
                    break  # Success, continue to next
                    
                except Exception as e:
                    if attempt == 1:  # Final attempt failed
                        logging.error(f"      ❌ Failed to add '{name}' (after 2 attempts): {e}")
                    else:
                        logging.warning(f"      ⚠️  attempt {attempt + 1} failed: '{name}': {e}")
                    time.sleep(1.0)
        
        # Report result
        logging.info("   " + "=" * 50)
        logging.info(f"   📊 Contact addition summary:")
        logging.info(f"      Total count: {len(contacts)}")
        logging.info(f"      success: {successfully_added}")
        if successfully_added < len(contacts):
            logging.warning(f"      ⚠️  Failed: {len(contacts) - successfully_added} contacts")
        logging.info("   " + "=" * 50)
        
        # etc. Pending contact sync
        logging.info("   ⏳ etc. Pending contact sync...")
        time.sleep(3.0)
        
        # Verify whether contacts were actually added
        try:
            actual_contacts = contacts_utils.list_contacts(env.controller)
            logging.info("   " + "=" * 50)
            logging.info(f"   📋 contactverify:")
            logging.info(f"      In database: {len(actual_contacts)} contacts")
            
            # Check which contacts were added
            added_names = {c.name for c in actual_contacts}
            expected_names = {contact['name'] for contact in contacts}
            missing_names = expected_names - added_names
            
            if missing_names:
                logging.warning(f"      ⚠️  Missing: {', '.join(missing_names)}")
            else:
                logging.info(f"      ✅ All {len(contacts)} contacts verified")
            logging.info("   " + "=" * 50)
        except Exception as e:
            logging.warning(f"   ⚠️  Failed to verify contacts: {e}")
        
        logging.info("   ✅ contactsetupcomplete")
    
    def _setup_chrome(self, env):
        """Initialize Chrome and log in (for Shopping task)"""
        logging.info("   🌐 Initialize Chrome and log in...")
        
        try:
            # Refer to the old architecture: create a complete WebArena evaluator and call its initialize_task()
            # This ensures Chrome is correctly initialized and logged in
            
            # Parameters for Subtask 7 (Shopping task)
            shopping_params = {
                "product_sku": "B07FM3WKJ8",
                "product_price": 49.99,
                "check_method": "order",
                "eval_types": ["program_html"],
                "program_html": [
                    {
                        "url": "func:shopping_get_latest_order_url()",
                        "locator": "document.querySelector('.order-details-items.ordered').outerText",
                        "required_contents": {
                            "must_include": ["B07FM3WKJ8"]
                        }
                    }
                ],
                "require_login": True,
                "start_url": "__SHOPPING__",
            }
            
            # create WebArena evaluator
            from scendroid.task_evals.webarena import webarena_task
            webarena_evaluator = webarena_task.ProgramHTMLWebArenaTask(shopping_params)
            
            # Call its initialize_task() — this launches Chrome, logs in, and navigates
            logging.info("   📱 create WebArena evaluator...")
            webarena_evaluator.initialize_task(env)
            
            logging.info("   ✅ Chrome initialized and login successful")
            
            # ⚠️ Critical: Do NOT close Chrome!
            # The old architecture found that force-stopping clears the login status (cookies)
            # Correct approach: Keep Chrome open, or press Home to move it to the background
            import subprocess
            import time
            
            device_name = "emulator-5554"
            try:
                result = subprocess.run(
                    ["adb", "devices"],
                    capture_output=True, text=True, check=True
                )
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:
                    if '\t' in line:
                        device_name = line.split('\t')[0]
                        break
            except:
                pass
            
            # Press Home to move Chrome to the background (instead of force-stopping)
            from scendroid.env import adb_utils
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
            
            logging.info("   ✅ Chrome remains in the background; login status saved")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Chrome initialization failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
            logging.warning("   Shopping task may require manual login")
    
    def _cleanup_app_data(self, env):
        """Clean up app data (only for already installed apps)"""
        logging.info("   🧹 cleanup app data...")
        
        try:
            from scendroid.env import adb_utils, device_constants
            from scendroid.utils import file_utils
            import subprocess
            
            # getdevicename
            device_name = "emulator-5554"
            try:
                result = subprocess.run(
                    ["adb", "devices"],
                    capture_output=True, text=True, check=True
                )
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:
                    if '\t' in line:
                        device_name = line.split('\t')[0]
                        break
            except:
                pass
            
            # 1. Special handling for Markor (more reliable cleanup method: delete the entire directory and rebuild)
            try:
                import time
                logging.info(f"      📁 cleanup Markor directory...")
                markor_dir = device_constants.MARKOR_DATA  # "/storage/emulated/0/Documents/Markor"
                
                # 🆕 Step 0: First, close the Markor app (to release file locks)
                try:
                    adb_utils.close_app("markor", env.controller)
                    time.sleep(0.5)
                except Exception:
                    pass
                
                # 🆕 Step 1: Delete the entire directory (rather than using wildcards)
                # Execute using shell string format to ensure correct command parsing
                adb_utils.issue_generic_request(
                    ['shell', 'rm', '-rf', markor_dir], env.controller
                )
                time.sleep(0.5)
                
                # 🆕 Step 2: recreate directory
                adb_utils.issue_generic_request(
                    ['shell', 'mkdir', '-p', markor_dir], env.controller
                )
                time.sleep(0.5)
                
                # 🆕 Step 3: Verify whether cleanup succeeded
                logging.info(f"      🔍 verify Markor directorycleanup...")
                check_result = adb_utils.issue_generic_request(
                    ['shell', 'ls', '-la', markor_dir], env.controller
                )
                if check_result and check_result.generic and check_result.generic.output:
                    output = check_result.generic.output.decode('utf-8', errors='ignore')
                    # Check whether the directory is empty (contains only . and .. or total count is 0)
                    lines = [l for l in output.strip().split('\n') if l and not l.startswith('total')]
                    if len(lines) <= 2:  # Only . and ..
                        logging.info(f"      ✅ Markor directory cleared")
                    else:
                        logging.warning(f"      ⚠️ Directory may not be fully cleared: {output[:100]}")
                
                logging.info(f"      ✅ Markor directory cleaned up")
            except Exception as e:
                logging.warning(f"      ⚠️  Markor directorycleanup failed: {str(e)[:100]}")
            
            # 2. cleanup Expense database
            try:
                logging.info(f"      💰 cleanup Expense database...")
                from scendroid.task_evals.utils import sqlite_utils
                from scendroid.env.setup_device import apps
                
                _EXPENSE_DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
                _EXPENSE_TABLE = "expense"
                _EXPENSE_APP_NAME = "pro expense"
                
                # check if database exists
                if not sqlite_utils.table_exists(_EXPENSE_TABLE, _EXPENSE_DB_PATH, env):
                    logging.info(f"         Expensedatabase does not exist, initializing...")
                    apps.ExpenseApp.setup(env)
                
                # clean database
                sqlite_utils.delete_all_rows_from_table(
                    _EXPENSE_TABLE, _EXPENSE_DB_PATH, env, _EXPENSE_APP_NAME
                )
                logging.info(f"      ✅ Expense database cleaned up")
            except Exception as e:
                logging.warning(f"      ⚠️  Expense cleanup failed: {str(e)[:100]}")
            
            # 3. Clean up OpenTracks database (refer to activity_app_utils.clear_db)
            try:
                logging.info(f"      🏃 cleanup OpenTracks database...")
                from scendroid.task_evals.information_retrieval import activity_app_utils
                
                activity_app_utils.clear_db(env)
                logging.info(f"      ✅ OpenTracks database cleaned up")
                
                # 4. Grant OpenTracks permission and handle the popup/dialog
                # Reference: env/setup_device/apps.py OpenTracksApp.setup() Line 609-638
                logging.info(f"      🔐 granting OpenTracks permissions...")
                import time
                from scendroid.env import tools
                
                # Launch and close the app (to trigger first-run)
                # Note: launch_app may timeout, but this is normal (the app is launching)
                try:
                    adb_utils.launch_app("open tracks sports tracker", env.controller)
                except Exception as e:
                    logging.debug(f"      Launch app timeout (expected): {e}")
                
                time.sleep(3.0)  # etc., wait for the app to fully start
                adb_utils.close_app("open tracks sports tracker", env.controller)
                
                # get package name
                open_tracks_package = adb_utils.extract_package_name(
                    adb_utils.get_adb_activity("open tracks")
                )
                
                # Grant location permission
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
                # Grant notification permission
                adb_utils.grant_permissions(
                    open_tracks_package,
                    "android.permission.POST_NOTIFICATIONS",
                    env.controller,
                )
                
                time.sleep(2.0)
                
                # Handle Bluetooth permission popup/dialog (cannot be granted via adb)
                try:
                    controller = tools.AndroidToolController(env=env.controller)
                    controller.click_element("Allow")
                    logging.info(f"      ✅ bluetooth permission clicked 'Allow' button")
                except Exception as e:
                    logging.debug(f"      'Allow' button not found or already authorized: {e}")
                
                # Launch and close again to ensure initialization is complete
                # Use start_activity instead of launch_app to avoid timeout error logs
                try:
                    adb_utils.start_activity(
                        "de.dennisguse.opentracks/.TrackListActivity",
                        None,
                        env.controller
                    )
                    time.sleep(2.0)
                    adb_utils.close_app("activity tracker", env.controller)
                except Exception as e:
                    logging.debug(f"      OpenTracks launch/close failed (can be ignored): {e}")
                
                logging.info(f"      ✅ OpenTracks permission granted")
                
            except Exception as e:
                logging.warning(f"      ⚠️  OpenTracks initialization failed: {str(e)[:100]}")
            
            logging.info("   ✅ datacleanup complete")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Error occurred during data cleanup: {e}")
    
    def initialize_subtask(self, subtask_idx: int, env):
        """
        Custom initialization logic
        
        Some subtasks require special environment setup.
        
        ⚠️ In Reset mode: directly call super(), handled by _reset_initialize_subtask()
        📚 In Scenario mode: execute scenario-specific pre-handling, then call super()
        """
        subtask = self.subtasks[subtask_idx]
        
        # ⚡ Resetmode: skip Scenario-specific preprocessing
        # all initialization handled by _reset_initialize_subtask() in super()
        if self.reset_mode:
            super().initialize_subtask(subtask_idx, env)
            return
        
        # ---- Execute the following only in Scenario mode ----
        
        # Subtask 1: Need to create multiple alarms
        if subtask['subtask_id'] == 1:
            logging.info("   🔧 Setting up multiple alarms...")
            # The original JSON requires creating 3 alarms:
            # - 10:35 weekdays ON (Work)
            # - 17:10 weekdays ON (Leave Work)
            # - 22:00 daily ON (Sleep)
            # This will be handled in ClockSetAlarm's initialize_task
        
        # Subtask 2 & 3: Calendar events have already been created during batch initialization
        elif subtask['subtask_id'] in [2, 3]:
            logging.info("   📅 Using Calendar events created during batch initialization...")
            # Calendar events have already been created during batch initialization in initialize_task():
            # 1. Company Weekly Meeting at 11:30 (60 mins)
            # 2. Client Presentation at 15:00 (90 mins)
            
            # 🆕 When initializing Task 3, return to the home screen (Task 2 may end while still in the Calendar app)
            if subtask['subtask_id'] == 3:
                try:
                    from scendroid.env import adb_utils
                    import time
                    
                    logging.info("   📱 Task 3: return to home screen...")
                    
                    # Press the Home key to return to the home screen
                    adb_utils.press_home_button(env.controller)
                    time.sleep(1.0)
                    
                    logging.info("   ✅ Returned to home screen")
                except Exception as e:
                    logging.warning(f"   ⚠️  return to home screenfailed: {e}")
        
        # 🆕 Subtask 5: Markor create outline task – need to ensure WorkLog.md does not exist
        if subtask['subtask_id'] == 5:
            logging.info("   📝 Task 5: cleanup Markor file...")
            try:
                from scendroid.env import adb_utils, device_constants
                import time
                
                markor_dir = device_constants.MARKOR_DATA
                
                # 🆕 Use a more reliable approach: delete the entire directory and rebuild it (consistent with initialize_task)
                # Step 0: First, close the Markor app (to release file locks)
                logging.info(f"      Step 0: Closing Markor app...")
                try:
                    adb_utils.close_app("markor", env.controller)
                    time.sleep(0.5)
                except Exception:
                    pass
                
                # Step 1: Delete the entire directory
                logging.info(f"      Step 1: Deleting entire directory {markor_dir}...")
                adb_utils.issue_generic_request(
                    ['shell', 'rm', '-rf', markor_dir], env.controller
                )
                time.sleep(0.5)
                
                # Step 2: recreate directory
                logging.info(f"      Step 2: recreate directory...")
                adb_utils.issue_generic_request(
                    ['shell', 'mkdir', '-p', markor_dir], env.controller
                )
                time.sleep(0.5)
                
                # Step 3: verifycleanupresult
                try:
                    check_result = adb_utils.issue_generic_request(
                        ['shell', 'ls', '-la', markor_dir], env.controller
                    )
                    if check_result and check_result.generic and check_result.generic.output:
                        output = check_result.generic.output.decode('utf-8', errors='ignore')
                        if 'WorkLog.md' in output:
                            logging.warning(f"      ⚠️ WorkLog.md still exists! ")
                        else:
                            logging.info(f"      ✅ Directory cleared")
                except Exception:
                    pass
                
                logging.info("      ✅ Markor directory cleaned up")
                    
            except Exception as e:
                logging.warning(f"      ⚠️  cleanup Markor failed: {e}")
        
        # Subtask 4: SMS task – need to refresh the UI and populate the contact mapping
        if subtask['subtask_id'] == 4:
            logging.info("   💬 SMS task – preparing environment...")
            
            # 1. Refresh the UI and ensure returning to the home screen
            # Refer to the old architecture: lines 5200–5219 in layered_tasks.py
            # Although SMS was cleaned up during scenario initialization, the UI might still retain cached data.
            # Additionally, the UI might remain on the previous conversation screen.
            try:
                from scendroid.env import adb_utils
                import time
                
                logging.info("      📱 refreshSMS UI...")
                
                # ⚠️ Critical step 1: First force-stop (to clear UI cache).
                adb_utils.close_app("simple sms", env.controller)
                time.sleep(1.0)
                
                # Step 2: Open the SMS app.
                logging.info("      📱 opening SMS app...")
                adb_utils.start_activity(
                    "com.simplemobiletools.smsmessenger/.activities.MainActivity",
                    None,
                    env.controller
                )
                time.sleep(2.0)  # etc., wait for the app to fully load.
                
                # 🆕 Step 3: Press the Back button to ensure returning to the home screen (rather than remaining on the conversation screen).
                logging.info("      📱 pressing back to return to home screen...")
                for _ in range(3):  # press back button multiple times to ensure return to home screen
                    adb_utils.issue_generic_request(
                        ["shell", "input", "keyevent", "KEYCODE_BACK"],
                        env.controller
                    )
                    time.sleep(0.3)
                
                # Step 4: Press the Home button to exit to the desktop.
                logging.info("      📱 pressing Home to exit to desktop...")
                adb_utils.press_home_button(env.controller)
                time.sleep(1.0)
                
                logging.info("      ✅ SMS UI has been refreshed (force-stop + open + Back button + Home button).")
            except Exception as e:
                logging.warning(f"      ⚠️  SMS UIrefreshfailed: {e}")
        
        # Call the parent class method (create evaluator instance + Scenario mode logic).
        super().initialize_subtask(subtask_idx, env)
        
        # ⚠️ Important: Populate _contacts_map *after* the parent class method (Scenario mode only).
        # Because the evaluator_instance is created within the parent class method.
        if subtask['subtask_id'] == 4:
            # 2. Populate the contact mapping (critical!).
            # Under Scenario mode, the SMS evaluator's initialize_task() is not invoked.
            # Therefore, _contacts_map must be manually populated using the contact information created in the scenario.
            try:
                evaluator = subtask['evaluator_instance']
                logging.info("      🔧 Populating contact mapping...")
                logging.info(f"         Evaluator type: {type(evaluator).__name__}")
                logging.info(f"         Has _contacts_map: {hasattr(evaluator, '_contacts_map')}")
                
                if evaluator and hasattr(evaluator, '_contacts_map'):
                    # Use the contact phone number created during scenario initialization (parameterized).
                    # Reference: _setup_contacts() method.
                    shared = self.generated_params.get('shared', {})
                    attendee_full_names = shared.get('attendee_full_names', 
                                                     ['John Smith', 'Bob Johnson', 'Nierson Williams', 'Hession Brown'])
                    
                    contacts_mapping = {
                        attendee_full_names[0]: "555-0101",
                        attendee_full_names[1]: "555-0102",
                        attendee_full_names[2]: "555-0103",
                        attendee_full_names[3]: "555-0104",
                        "Alice Davis": "555-0201",
                        "Charlie Wilson": "555-0202",
                    }
                    
                    evaluator._contacts_map = contacts_mapping
                    logging.info("      ✅ Contact mapping has been populated.")
                    logging.info(f"         {len(contacts_mapping)} contacts:")
                    for name, number in contacts_mapping.items():
                        logging.info(f"         - {name}: {number}")
                else:
                    logging.warning(f"      ❌ Cannot fill _contacts_map: evaluator={evaluator}")
            except Exception as e:
                logging.warning(f"      ⚠️ Contact mapping population failed: {e}")
                import traceback
                logging.warning(traceback.format_exc())
    
    def _setup_opentracks(self, env):
        """
        Initialize OpenTracks (for subtask 9).
        
        Reuse the implementation from Scenario F (scenario_e.py).
        """
        logging.info("   🏃 initialize OpenTracks...")
        
        from scendroid.task_evals.information_retrieval import activity_app_utils
        from scendroid.env import adb_utils
        from scendroid.env import tools
        import time
        
        try:
            # 1. clean database
            logging.info("      Step 1: cleanup OpenTracks database...")
            try:
                activity_app_utils.clear_db(env)
                logging.info("      ✅ OpenTracks database cleared")
            except Exception as e:
                logging.debug(f"      Database clear failed (might be first run): {e}")
            
            # 2. Grant permissions and handle popups/dialogs.
            logging.info("      Step 2: granting OpenTracks permissions...")
            
            # get package name
            open_tracks_package = adb_utils.extract_package_name(
                adb_utils.get_adb_activity("open tracks")
            )
            
            # Grant location permission (before launching the app).
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
            # Grant notification permission.
            adb_utils.grant_permissions(
                open_tracks_package,
                "android.permission.POST_NOTIFICATIONS",
                env.controller,
            )
            
            # Launch the app and handle the Bluetooth permission popup/dialog.
            # Critical: The Bluetooth permission popup/dialog appears *only while the app is running!*
            try:
                adb_utils.launch_app("activity tracker", env.controller)
                time.sleep(3.0)
                
                # Click the Bluetooth permission Allow button.
                try:
                    controller = tools.AndroidToolController(env=env.controller)
                    controller.click_element("Allow")
                    logging.info("      ✅ bluetooth permission clicked 'Allow' button")
                    time.sleep(1.0)
                except Exception as e:
                    logging.debug(f"      Bluetooth permission already authorized or does not require handling: {e}")
                
                # Close the app.
                adb_utils.close_app("activity tracker", env.controller)
            except Exception as e:
                logging.debug(f"      OpenTracks launch/handling: {e}")
            
            logging.info("      ✅ OpenTracks permissions have been granted and initialization is complete.")
            
        except Exception as e:
            logging.error(f"      ❌ OpenTracks initialization failed: {e}")
            import traceback
            logging.error(traceback.format_exc())
    
    # ====================================================================
    # Per-Task Reset Mode: per-task independent initialization
    # ====================================================================
    
    def _reset_initialize_subtask(self, subtask_idx: int, env):
        """
        Per-Task Resetsubtask initialization in mode
        
        each subtask will before starting:
        1. clear related app data
        2. create prerequisites needed for this task
        3. call evaluator's initialize_task() (if needed)
        
        difference from Scenario mode:
        - Scenario mode: batch initialize once + preceding tasks naturally create prerequisites
        - Reset mode: each task initializes independently, simulating all prior steps completed
        """
        subtask = self.subtasks[subtask_idx]
        task_id = subtask['subtask_id']
        
        logging.info(f"   🔧 Per-task reset initialization for Task {task_id}: {subtask['evaluator_name']}")
        
        # ensure timezone is UTC
        self._ensure_utc_timezone(env)
        
        if task_id == 1:
            self._reset_init_task1_clock(env)
        elif task_id == 2:
            self._reset_init_task2_calendar_qa(env)
        elif task_id == 3:
            self._reset_init_task3_extract_attendees(env)
        elif task_id == 4:
            self._reset_init_task4_sms(subtask, env)
        elif task_id == 5:
            self._reset_init_task5_markor_create(subtask, env)
        elif task_id == 6:
            self._reset_init_task6_calendar_edit(subtask, env)
        elif task_id == 7:
            self._reset_init_task7_shopping(subtask, env)
        elif task_id == 8:
            self._reset_init_task8_expense(subtask, env)
        elif task_id == 9:
            self._reset_init_task9_calendar_exercise(subtask, env)
        elif task_id == 10:
            self._reset_init_task10_markor_append(subtask, env)
        elif task_id == 11:
            self._reset_init_task11_clock_again(env)
        else:
            # unknown task: using default implementation
            logging.warning(f"   ⚠️  No custom reset init for Task {task_id}, using evaluator default")
            subtask['evaluator_instance'].initialize_task(env)
    
    def _ensure_utc_timezone(self, env):
        """ensure device timezone is UTC (shared by multiple tasks)"""
        from scendroid.env import adb_utils
        import time
        
        try:
            adb_utils.set_root_if_needed(env.controller)
            adb_utils.issue_generic_request(
                ['shell', 'service', 'call', 'alarm', '3', 's16', 'UTC'],
                env.controller
            )
            adb_utils.issue_generic_request(
                ['shell', 'setprop', 'persist.sys.timezone', 'UTC'],
                env.controller
            )
            time.sleep(0.5)
            logging.info("   ✅ Timezone confirmed: UTC")
        except Exception as e:
            logging.warning(f"   ⚠️  Could not set timezone: {e}")
    
    def _reset_setup_calendar_events(self, env, include_blocking_meeting=False):
        """
        Create calendar event under Reset mode (shared by Tasks 2/3/4/6/9).
        
        Created events:
        1. Main meeting (meeting_title @ 11:30) — includes attendees.
        2. Distractor event (Client Presentation @ 15:00).
        3. (Optional) Task 9 blocking meeting (blocking_meeting @ 18:15).
        """
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from scendroid.env import adb_utils
        from datetime import datetime
        import calendar as cal_module
        import time
        
        # Clear Calendar app data.
        logging.info("      🗑️  Clearing Calendar app data...")
        try:
            adb_utils.clear_app_data(
                "com.simplemobiletools.calendar.pro",
                env.controller,
            )
            time.sleep(1.5)
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear calendar: {e}")
        
        # Reset timezone.
        self._ensure_utc_timezone(env)
        
        # Open the calendar once to initialize
        try:
            adb_utils.start_activity(
                "com.simplemobiletools.calendar.pro/.activities.MainActivity",
                None,
                env.controller
            )
            time.sleep(2.5)
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
        except Exception as e:
            logging.warning(f"      ⚠️  Could not init Calendar app: {e}")
        
        # Clear existing events
        calendar_utils.clear_calendar_db(env)
        
        # get parameters
        shared = self.generated_params.get('shared', {})
        meeting_title = shared.get('meeting_title', 'Company Weekly Meeting')
        meeting_location = shared.get('meeting_location', 'Conference Room A')
        user_name = shared.get('user_name', 'David')
        attendee_names = shared.get('attendee_names', ['John', 'Bob', 'Nierson', 'Hession'])
        
        base_date = datetime(2025, 12, 26, 0, 0, 0)
        events = []
        
        # Event 1: Main meeting at 11:30
        meeting_dt = base_date.replace(hour=11, minute=30)
        meeting_start_ts = cal_module.timegm(meeting_dt.timetuple())
        meeting_end_ts = meeting_start_ts + (60 * 60)
        attendees_str = f"Attendees: {user_name}, " + ", ".join(attendee_names)
        
        event1 = sqlite_schema_utils.CalendarEvent(
            start_ts=meeting_start_ts,
            end_ts=meeting_end_ts,
            title=meeting_title,
            location=meeting_location,
            description=attendees_str,
        )
        events.append(event1)
        logging.info(f"      📌 Event: {meeting_title} @ 11:30")
        
        # Event 2: Distractor event at 15:00
        presentation_dt = base_date.replace(hour=15, minute=0)
        presentation_start_ts = cal_module.timegm(presentation_dt.timetuple())
        presentation_end_ts = presentation_start_ts + (90 * 60)
        
        event2 = sqlite_schema_utils.CalendarEvent(
            start_ts=presentation_start_ts,
            end_ts=presentation_end_ts,
            title="Client Presentation",
            location="Meeting Room B",
            description="Attendees: Alice, Tom",
        )
        events.append(event2)
        logging.info(f"      📌 Event: Client Presentation @ 15:00")
        
        # Event 3 (optional): Task 9 blocks the meeting
        if include_blocking_meeting:
            st9 = self.generated_params.get('subtask_9', {})
            has_blocking = st9.get('has_blocking_meeting', False)
            blocking_title = st9.get('blocking_meeting_title', 'Evening Sync')
            
            if has_blocking:
                blocking_dt = base_date.replace(hour=18, minute=15)
                blocking_start_ts = cal_module.timegm(blocking_dt.timetuple())
                blocking_end_ts = blocking_start_ts + (30 * 60)
                
                event3 = sqlite_schema_utils.CalendarEvent(
                    start_ts=blocking_start_ts,
                    end_ts=blocking_end_ts,
                    title=blocking_title,
                    location="Phone Call",
                    description="Quick sync call",
                )
                events.append(event3)
                logging.info(f"      📌 Event: {blocking_title} @ 18:15 (blocking)")
        
        calendar_utils.add_events(events, env)
        time.sleep(2.0)
        logging.info("      ✅ Calendar events created")
    
    def _reset_setup_contacts(self, env):
        """Create contact (used for Task 4) in reset mode"""
        from scendroid.utils import contacts_utils
        from scendroid.env import adb_utils
        import time
        
        contacts_utils.clear_contacts(env.controller)
        time.sleep(1.0)
        
        shared = self.generated_params.get('shared', {})
        attendee_full_names = shared.get('attendee_full_names',
                                         ['John Smith', 'Bob Johnson', 'Nierson Williams', 'Hession Brown'])
        
        contacts = [
            {"name": attendee_full_names[0], "phone": "555-0101"},
            {"name": attendee_full_names[1], "phone": "555-0102"},
            {"name": attendee_full_names[2], "phone": "555-0103"},
            {"name": attendee_full_names[3], "phone": "555-0104"},
            {"name": "Alice Davis", "phone": "555-0201"},
            {"name": "Charlie Wilson", "phone": "555-0202"},
        ]
        
        for contact in contacts:
            try:
                adb_utils.press_home_button(env.controller)
                time.sleep(1.0)
                contacts_utils.add_contact(
                    contact['name'], contact['phone'],
                    env.controller, ui_delay_sec=2.0
                )
                time.sleep(1.5)
                logging.info(f"      ✅ Contact: {contact['name']} ({contact['phone']})")
            except Exception as e:
                logging.warning(f"      ⚠️  Failed to add {contact['name']}: {e}")
        
        time.sleep(2.0)
        logging.info("      ✅ Contacts created")
    
    # ---- Per-Task Reset Initialization Methods ----
    
    def _reset_init_task1_clock(self, env):
        """
        Task 1 (Adjust Weekday Alarm): 
        Prerequisites: Three alarms (Work/Leave_Work/Sleep); the agent needs to adjust the Work alarm
        """
        logging.info("   🔧 Reset Init Task 1: Creating alarms for adjustment task")
        
        from scendroid.env import adb_utils
        import time
        
        # 1. Clear Clock data
        try:
            adb_utils.clear_app_data(
                adb_utils.extract_package_name(adb_utils.get_adb_activity("clock")),
                env.controller,
            )
            time.sleep(1.0)
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear clock data: {e}")
        
        # 2. Create three alarms (using original times; the agent needs to adjust the first one)
        st1 = self.generated_params.get('subtask_1', {})
        work_hour = st1.get('original_hour', 10)
        work_minute = st1.get('original_minute', 35)
        
        self._set_alarm_with_days(env, hour=work_hour, minute=work_minute,
                                  message="Work", days=[2, 3, 4, 5, 6])
        time.sleep(1.0)
        self._set_alarm_with_days(env, hour=17, minute=10,
                                  message="Leave_Work", days=[2, 3, 4, 5, 6])
        time.sleep(1.0)
        self._set_alarm_with_days(env, hour=22, minute=0,
                                  message="Sleep", days=[1, 2, 3, 4, 5, 6, 7])
        time.sleep(1.0)
        
        logging.info(f"      ✅ 3 alarms created (Work@{work_hour}:{work_minute:02d}, Leave_Work@17:10, Sleep@22:00)")
    
    def _reset_init_task2_calendar_qa(self, env):
        """
        Task 2 (Check Morning Schedule QA):
        Prerequisites: Calendar events (meeting at 11:30 + distractor event at 15:00)
        """
        logging.info("   🔧 Reset Init Task 2: Creating calendar events for QA task")
        self._reset_setup_calendar_events(env, include_blocking_meeting=False)
    
    def _reset_init_task3_extract_attendees(self, env):
        """
        Task 3 (Extract Meeting Attendees QA):
        Prerequisites: Calendar event with attendees
        """
        logging.info("   🔧 Reset Init Task 3: Creating calendar events with attendees")
        self._reset_setup_calendar_events(env, include_blocking_meeting=False)
    
    def _reset_init_task4_sms(self, subtask, env):
        """
        Task 4 (Send Meeting Reminder SMS):
        Prerequisites: Contact + calendar event (L0 instruction requires first checking the calendar to find attendees, then sending an SMS)
        """
        logging.info("   🔧 Reset Init Task 4: Creating contacts + calendar events for SMS task")
        
        from scendroid.task_evals.common_validators import sms_validators
        from scendroid.env import adb_utils
        import time
        
        # 1. Create a calendar event (agent needs to find attendees from the calendar)
        self._reset_setup_calendar_events(env, include_blocking_meeting=False)
        
        # 2. Clear SMS
        try:
            sms_validators.clear_sms_and_threads(env.controller)
            adb_utils.close_app("simple sms", env.controller)
            time.sleep(1.0)
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear SMS: {e}")
        
        # 3. create contact
        self._reset_setup_contacts(env)
        
        # 4. Populate the evaluator's _contacts_map (required during evaluation)
        evaluator = subtask['evaluator_instance']
        if evaluator and hasattr(evaluator, '_contacts_map'):
            shared = self.generated_params.get('shared', {})
            attendee_full_names = shared.get('attendee_full_names',
                                             ['John Smith', 'Bob Johnson', 'Nierson Williams', 'Hession Brown'])
            evaluator._contacts_map = {
                attendee_full_names[0]: "555-0101",
                attendee_full_names[1]: "555-0102",
                attendee_full_names[2]: "555-0103",
                attendee_full_names[3]: "555-0104",
                "Alice Davis": "555-0201",
                "Charlie Wilson": "555-0202",
            }
            logging.info("      ✅ Contacts map populated for evaluator")
    
    def _reset_init_task5_markor_create(self, subtask, env):
        """
        Task 5 (Create Meeting Outline):
        Prerequisites: Markor directory clear (no WorkLog.md) + return-to-home interface
        """
        logging.info("   🔧 Reset Init Task 5: Clearing Markor directory and returning to home")
        
        from scendroid.env import adb_utils, device_constants
        import time
        
        # 1. Clear the Markor directory (using the same reliable method as bulk initialization)
        try:
            markor_dir = device_constants.MARKOR_DATA  # "/storage/emulated/0/Documents/Markor"
            
            # Step 0: Close the Markor app (to release file locks)
            logging.info("      Step 0: Closing Markor app...")
            try:
                adb_utils.close_app("markor", env.controller)
                time.sleep(0.5)
            except Exception:
                pass  # App may not be running
            
            # Step 1: Delete the entire directory
            logging.info(f"      Step 1: Removing directory {markor_dir}...")
            adb_utils.issue_generic_request(
                ['shell', 'rm', '-rf', markor_dir], env.controller
            )
            time.sleep(0.5)
            
            # Step 2: recreate directory
            logging.info(f"      Step 2: Recreating directory...")
            adb_utils.issue_generic_request(
                ['shell', 'mkdir', '-p', markor_dir], env.controller
            )
            time.sleep(0.5)
            
            # Step 3: Verify whether cleanup succeeded
            logging.info(f"      Step 3: Verifying cleanup...")
            try:
                check_result = adb_utils.issue_generic_request(
                    ['shell', 'ls', '-la', markor_dir], env.controller
                )
                if check_result and check_result.generic and check_result.generic.output:
                    output = check_result.generic.output.decode('utf-8', errors='ignore')
                    lines = [l for l in output.strip().split('\n') if l and not l.startswith('total')]
                    if len(lines) <= 2:  # Only "." and ".."
                        logging.info(f"      ✅ Markor directory is clean")
                    else:
                        logging.warning(f"      ⚠️  Directory may not be completely clean: {output[:100]}")
            except Exception:
                pass
            
            logging.info("      ✅ Markor directory cleared")
            
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear Markor directory: {e}")
        
        # 2. Return to the home interface
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
            logging.info("      ✅ Returned to home screen")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not return to home: {e}")
    
    def _reset_init_task6_calendar_edit(self, subtask, env):
        """
        Task 6 (Mark Out of Office - Calendar Edit):
        Prerequisites: The calendar must contain a meeting event (with attendee description); the agent edits the notes for this event
        """
        logging.info("   🔧 Reset Init Task 6: Creating calendar event for note editing")
        
        # 1. Create a calendar event (including attendee information)
        self._reset_setup_calendar_events(env, include_blocking_meeting=False)
        
        # 2. Call the evaluator's initialize_task() to store the initial event snapshot
        subtask['evaluator_instance'].initialize_task(env)
    
    def _reset_init_task7_shopping(self, subtask, env):
        """
        Task 7 (Order Product - Shopping):
        prerequisites:Chrome/Shopping App initialize+login
        evaluator.initialize_task() is sufficient
        """
        logging.info("   🔧 Reset Init Task 7: Initializing Shopping (Chrome/Login)")
        subtask['evaluator_instance'].initialize_task(env)
    
    def _reset_init_task8_expense(self, subtask, env):
        """
        Task 8 (Record Expense):
        Prerequisites: Expense database clear + return-to-home interface
        """
        logging.info("   🔧 Reset Init Task 8: Clearing Expense database and returning to home")
        
        from scendroid.env import adb_utils
        import time
        
        # 1. Call the evaluator's initialize_task() to clean the database
        try:
            subtask['evaluator_instance'].initialize_task(env)
            logging.info("      ✅ Expense database cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear Expense database: {e}")
        
        # 2. Return to the home interface
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
            logging.info("      ✅ Returned to home screen")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not return to home: {e}")
    
    def _reset_init_task9_calendar_exercise(self, subtask, env):
        """
        Task 9 (Calendar Check Then Exercise):
        prerequisites:
        1. Calendar event (may include blocking meetings)
        2. OpenTracks permission + clear data + ensure no ongoing recording
        """
        logging.info("   🔧 Reset Init Task 9: Calendar events + OpenTracks setup")
        
        from scendroid.env import adb_utils
        import time
        
        # 1. Create a calendar event (including possible blocking meetings)
        self._reset_setup_calendar_events(env, include_blocking_meeting=True)
        
        # 2. Set up OpenTracks (clear database + authorization)
        self._setup_opentracks(env)
        
        # 3. ⚠️ Critical: Ensure any ongoing recording is stopped and notifications are cleared
        try:
            # Force stop the OpenTracks app (this stops any foreground services and recordings)
            open_tracks_package = adb_utils.extract_package_name(
                adb_utils.get_adb_activity("open tracks")
            )
            adb_utils.issue_generic_request([
                'shell', 'am', 'force-stop', open_tracks_package
            ], env.controller)
            time.sleep(1.0)
            logging.info("      ✅ Force stopped OpenTracks to ensure no active recording")
            
            # Return to home to ensure the app is not in the foreground
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
        except Exception as e:
            logging.warning(f"      ⚠️ Could not force stop OpenTracks: {e}")
        
        # 4. Call the evaluator's initialize_task() to record OpenTracks' initial status
        subtask['evaluator_instance'].initialize_task(env)
    
    def _reset_init_task10_markor_append(self, subtask, env):
        """
        Task 10 (Evening Summary - Markor Append):
        Prerequisites: WorkLog.md must already exist (created by Task 5 in Scenario mode)
        In reset mode, WorkLog.md must be pre-created
        """
        logging.info("   🔧 Reset Init Task 10: Creating pre-existing WorkLog.md")
        
        from scendroid.env import device_constants, adb_utils
        from scendroid.utils import file_utils
        import os
        
        # 1. Clear the Markor file (using the correct method)
        try:
            markor_dir = device_constants.MARKOR_DATA
            
            # Close Markor
            try:
                adb_utils.close_app("markor", env.controller)
                import time
                time.sleep(0.5)
            except Exception:
                pass
            
            # cleanupdirectory
            file_utils.clear_directory(markor_dir, env.controller)
            logging.info("      ✅ Markor files cleared")
        except Exception as e:
            logging.warning(f"      ⚠️ Markor clear failed: {e}")
        
        # 2. Pre-create WorkLog.md (simulate Task 5's output)
        # Create a basic meeting outline file (as the basis for appending content in Task 10)
        shared = self.generated_params.get('shared', {})
        meeting_title = shared.get('meeting_title', 'Company Weekly Meeting')
        meeting_location = shared.get('meeting_location', 'Conference Room A')
        user_name = shared.get('user_name', 'David')
        attendee_names = shared.get('attendee_names', ['John', 'Bob', 'Nierson', 'Hession'])
        
        initial_content = f"""# Weekly Meeting Notes Outline

## Title
{meeting_title}

## Time
11:30 AM - 12:30 PM

## Location
{meeting_location}

## Attendees
{user_name}, {', '.join(attendee_names)}

## Discussion Notes
"""
        
        # Use adb to directly create a file
        import tempfile
        import time
        
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as tmp_file:
                tmp_file.write(initial_content)
                tmp_path = tmp_file.name
            
            # Push to device
            target_path = f"{device_constants.MARKOR_DATA}/WorkLog.md"
            adb_utils.issue_generic_request([
                'push', tmp_path, target_path
            ], env.controller)
            
            # Delete the temporary file
            os.remove(tmp_path)
            
            logging.info("      ✅ WorkLog.md created with meeting outline")
        except Exception as e:
            logging.warning(f"      ⚠️ Could not create WorkLog.md: {e}")
        
        # 3. Call the evaluator's initialize_task()
        # Note: The evaluator will clear Markor and then create initial_content
        # However, the initial_content parameter for Task 10 is empty, so only clearing occurs
        # Therefore, we do not call the evaluator's init, but instead handle it manually
        # subtask['evaluator_instance'].initialize_task(env)  # Do not call! It would clear the files we created
    
    def _reset_init_task11_clock_again(self, env):
        """
        Task 11 (Adjust Alarm Again):
        Prerequisites: The alarm was adjusted by Task 1 to new_hour:new_minute; the agent needs to adjust it again
        In Reset mode, the adjusted alarm status must be created
        """
        logging.info("   🔧 Reset Init Task 11: Creating alarms at Task-1-adjusted times")
        
        from scendroid.env import adb_utils
        import time
        
        # 1. Clear Clock data
        try:
            adb_utils.clear_app_data(
                adb_utils.extract_package_name(adb_utils.get_adb_activity("clock")),
                env.controller,
            )
            time.sleep(1.0)
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear clock data: {e}")
        
        # 2. Create an alarm (using the time adjusted by Task 1 as the starting point)
        # Task 11's prerequisite condition is that Task 1 has been completed: The work alarm has changed from original to new
        st1 = self.generated_params.get('subtask_1', {})
        st11 = self.generated_params.get('subtask_11', {})
        
        # Time adjusted by Task 1 (i.e., the starting point for Task 11)
        work_hour = st11.get('previous_hour', st1.get('new_hour', 10))
        work_minute = st11.get('previous_minute', st1.get('new_minute', 25))
        
        self._set_alarm_with_days(env, hour=work_hour, minute=work_minute,
                                  message="Work", days=[2, 3, 4, 5, 6])
        time.sleep(1.0)
        self._set_alarm_with_days(env, hour=17, minute=10,
                                  message="Leave_Work", days=[2, 3, 4, 5, 6])
        time.sleep(1.0)
        self._set_alarm_with_days(env, hour=22, minute=0,
                                  message="Sleep", days=[1, 2, 3, 4, 5, 6, 7])
        time.sleep(1.0)
        
        logging.info(f"      ✅ 3 alarms created (Work@{work_hour}:{work_minute:02d} [post-Task1], Leave_Work@17:10, Sleep@22:00)")
    
    def tear_down(self, env):
        """
        Cleanup work after scenario end
        
        1. cleanup SMS message
        2. Rebuild the Shopping container (to ensure the next test environment is clean)
        """
        logging.info("=" * 70)
        logging.info("🧹 Scenario B - cleanup work")
        logging.info("=" * 70)
        
        try:
            # ✅ Cleanup SMS messages (to ensure they do not affect subsequent tests)
            logging.info("   💬 cleanupSMSmessage...")
            from scendroid.task_evals.common_validators import sms_validators
            from scendroid.env import adb_utils
            import time
            
            try:
                sms_validators.clear_sms_and_threads(env.controller)
                logging.info("      ✅ SMSdatabase cleared")
                
                # Force-stop Simple SMS Messenger
                adb_utils.close_app("simple sms", env.controller)
                time.sleep(0.5)
                
                logging.info("      ✅ SMScleanup complete")
            except Exception as e:
                logging.warning(f"      ⚠️  SMScleanup failed: {e}")
            
            # ✅ Rebuild the Shopping container (to ensure the next test environment is clean)
            logging.info("   🔄 rebuild Shopping container...")
            try:
                from scendroid.task_evals.webarena import container_manager
                
                # extract console_port to ensure correct container rebuild
                console_port = None
                try:
                    console_port = env.controller._env._coordinator._simulator._config.emulator_launcher.emulator_console_port
                    logging.info(f"      📱 Emulator console port: {console_port}")
                except Exception as e:
                    logging.warning(f"      ⚠️  Could not extract console_port: {e}")
                
                manager = container_manager.ShoppingContainerManager(console_port=console_port)
                manager.rebuild_container()
                logging.info(f"      ✅ Shopping container rebuilt (container: {manager.docker_container}, port: {manager.host_port})")
            except Exception as e:
                logging.warning(f"      ⚠️  Shopping container rebuild failed: {e}")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Cleanup work failed: {e}")
        
        # Call the parent class's tear_down
        super().tear_down(env)
        
        logging.info("✅ Scenario B cleanup complete")

