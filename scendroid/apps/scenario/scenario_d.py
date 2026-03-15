"""
Scenario E: Tech Conference Trip (Business trip scenario)

A complex scenario comprising 10 subtasks, simulating a day of business travel:
1. Time zone preparation and itinerary synchronization (Clock + Files + Calendar)
2. Departure alarm and luggage reminder (Clock + Tasks)
3. Airport waiting area silent mode and connection management (System Settings)
4. Emergency replenishment of business travel equipment (Shopping)
5. Partner contact and information sharing (Contacts + SMS + VCF)
6. Professional meeting audio recording configuration (Audio Recorder)
7. Capture reimbursement receipts and archive them (Camera + Files)
8. Business travel expense accounting (Pro Expense)
9. Cross-app audio recording note organization (Audio Recorder + Markor)
10. Financial trend analysis and cost control for the past 3 days (Pro Expense QA)

Characteristics:
- Cross-time-zone time management
- Precise replenishment of business travel supplies
- Multimodal meeting recording
- Cross-app financial auditing
- Dependencies among tasks
"""

from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.scenario.base import BaseScenarioEvaluator


@AppRegistry.register_evaluator("ScenarioD_TechConferenceTrip")
class ScenarioDTechConferenceTripEvaluator(BaseScenarioEvaluator):
    """
    Scenario E: Tech Conference Trip for {user_name} - Parameterized version
    
    Description:
    Simulates a day of business travel, from preparation through meeting recording to financial auditing
    Covers time zone management, supply procurement, meeting recording, and expense tracking
    
    Subtasks (10):
    1. Time zone preparation and itinerary synchronization (Clock + Files + Calendar)
    2. Departure alarm and luggage reminder (Clock + Tasks)
    3. Airport waiting area silent mode and connection management (System Settings)
    4. Emergency replenishment of business travel equipment (Shopping)
    5. Partner contact and information sharing (Contacts + SMS + VCF)
    6. Professional meeting audio recording configuration (Audio Recorder)
    7. Capture reimbursement receipts and archive them (Camera + Files)
    8. Business travel expense accounting (Pro Expense)
    9. Cross-app audio recording note organization (Audio Recorder + Markor)
    10. Financial trend analysis and cost control for the past 3 days (Pro Expense QA)
    
    Characteristics:
    - Cross-time-zone time management
    - Tasks have dependencies (E1→E4, E6→E9, E8→E9/E10)
    - Includes QA tasks
    
    Scoring:
    - All tasks have equal weight
    - After completion, report the completion status of each task
    """
    
    app_names = (
        "clock", "files", "simple calendar pro", "tasks",
        "settings", "chrome", "contacts", "simple sms messenger",
        "audio recorder", "camera", "pro expense", "markor"
    )
    
    scenario_id = "E"
    complexity = 4.8
    
    # ========== Parameter template definition ==========
    PARAM_TEMPLATES = {
        # Shared parameters (used across tasks)
        'shared': {
            'user_names': ['David', 'Michael', 'Sarah', 'Emily', 'Alex'],
            'destinations': [
                {'city': 'San Francisco', 'timezone': 'PST', 'abbr': 'SF'},
                {'city': 'Los Angeles', 'timezone': 'PST', 'abbr': 'LA'},
                {'city': 'Seattle', 'timezone': 'PST', 'abbr': 'SEA'},
                {'city': 'Boston', 'timezone': 'EST', 'abbr': 'BOS'},
                {'city': 'Chicago', 'timezone': 'CST', 'abbr': 'CHI'},
            ],
            'flights': [
                {'number': 'UA 456', 'departure': '09:30', 'arrival': '12:45'},
                {'number': 'AA 789', 'departure': '10:15', 'arrival': '13:30'},
                {'number': 'DL 321', 'departure': '08:45', 'arrival': '11:50'},
                {'number': 'SW 654', 'departure': '11:00', 'arrival': '14:15'},
            ],
            'hotels': [
                {'name': 'Marriott Union Square', 'address': '480 Sutter Street', 'phone': '415-555-0199'},
                {'name': 'Hilton Downtown', 'address': '333 O\'Farrell Street', 'phone': '415-555-0288'},
                {'name': 'Hyatt Regency', 'address': '5 Embarcadero Center', 'phone': '415-555-0377'},
            ],
            'office_addresses': [
                {'name': 'TechCorp SF Branch', 'address': '123 Tech Park Drive, Suite 400'},
                {'name': 'Innovation Hub', 'address': '456 Market Street, Floor 12'},
                {'name': 'StartupHQ', 'address': '789 Mission Street, Suite 200'},
            ],
            'colleagues': [
                {'name': 'Sarah Miller', 'phone': '555-0102'},
                {'name': 'John Davis', 'phone': '555-0103'},
                {'name': 'Emily Chen', 'phone': '555-0104'},
                {'name': 'Michael Brown', 'phone': '555-0105'},
            ],
        },
        
        # E2: Alarm time
        'subtask_2': {
            'alarm_times': ['07:15', '07:30', '07:45', '08:00'],
            'checklist_items': [
                'Check Passport and Laptop Charger',
                'Verify Passport and Power Adapter',
                'Confirm Passport and USB-C Cable',
                'Double-check Passport and Presentation Files',
            ],
        },
        
        # E4: Shopping item (fixed) - The variable parameter is the shipping address
        # The item is fixed as SanDisk Cruzer Glide 16GB (2 Pack), SKU: B00J2FALDK
        'subtask_4': {
            'product': {
                'sku': 'B00J2FALDK', 
                'name': 'SanDisk Cruzer Glide 16GB (2 Pack) USB 2.0 Flash Drive',
                'price': 19.99,  # Actual website price
            },
        },
        
        # E6: Audio recording configuration
        'subtask_6': {
            'recording_names': ['Keynote_AI', 'Tech_Summit_Main', 'Conference_Session1', 'Innovation_Talk'],
            'formats': ['Wav', 'M4a'],
            'sample_rates': ['48kHz', '44.1kHz', '32kHz'],
        },
        
        # E7: Receipt folder
        'subtask_7': {
            'folder_names': [
                'Jan_Trip/Receipts',
                'Business_Trip/Expenses',
                'Conference_2026/Receipts',
                'Travel_Docs/Jan15',
            ],
        },
        
        # E8: Expense amount
        'subtask_8': {
            'taxi_amounts': [30.00, 35.00, 40.00, 45.00],
            'hotel_amounts': [200.00, 250.00, 280.00, 300.00],
        },
        
        # E9: Note file
        'subtask_9': {
            'note_files': ['Day1_Summary.md', 'Trip_Notes.md', 'Conference_Log.md', 'Daily_Review.md'],
        },
        
        # E10: Budget (reduced, for the most recent 3 days)
        'subtask_10': {
            'budgets': [150.00, 180.00, 200.00, 220.00],
        },
    }
    
    @classmethod
    def generate_random_params(cls, seed=None):
        """
        Generate random parameters for Scenario E
        
        Args:
            seed: Random seed
            
        Returns:
            Dictionary of parameters, containing parameters for all subtasks
        """
        import random
        
        if seed is not None:
            random.seed(seed)
        
        # 1. Generate shared parameters
        user_name = random.choice(cls.PARAM_TEMPLATES['shared']['user_names'])
        destination = random.choice(cls.PARAM_TEMPLATES['shared']['destinations'])
        flight = random.choice(cls.PARAM_TEMPLATES['shared']['flights'])
        hotel = random.choice(cls.PARAM_TEMPLATES['shared']['hotels'])
        office = random.choice(cls.PARAM_TEMPLATES['shared']['office_addresses'])
        colleague = random.choice(cls.PARAM_TEMPLATES['shared']['colleagues'])
        
        shared_params = {
            'user_name': user_name,
            'destination_city': destination['city'],
            'destination_abbr': destination['abbr'],
            'flight_number': flight['number'],
            'flight_departure': flight['departure'],
            'flight_arrival': flight['arrival'],
            'hotel_name': hotel['name'],
            'hotel_address': hotel['address'],
            'hotel_phone': hotel['phone'],
            'office_name': office['name'],
            'office_address': office['address'],
            'colleague_name': colleague['name'],
            'colleague_phone': colleague['phone'],
        }
        
        # 2. Generate E2 parameters (alarm and task)
        alarm_time = random.choice(cls.PARAM_TEMPLATES['subtask_2']['alarm_times'])
        checklist_item = random.choice(cls.PARAM_TEMPLATES['subtask_2']['checklist_items'])
        alarm_hour, alarm_minute = map(int, alarm_time.split(':'))
        
        subtask_2_params = {
            'alarm_time': alarm_time,
            'alarm_hour': alarm_hour,
            'alarm_minute': alarm_minute,
            'checklist_item': checklist_item,
        }
        
        # 3. Generate E4 parameters (shopping) - Item is fixed; the variable parameter is the address (from shared)
        product = cls.PARAM_TEMPLATES['subtask_4']['product']
        subtask_4_params = {
            'sku': product['sku'],
            'name': product['name'],
            'price': product['price'],
            # Address retrieved from shared parameters
            'office_name': office['name'],
            'office_address': office['address'],
        }
        
        # 4. Generate E6 parameters (audio recording)
        recording_name = random.choice(cls.PARAM_TEMPLATES['subtask_6']['recording_names'])
        recording_format = random.choice(cls.PARAM_TEMPLATES['subtask_6']['formats'])
        sample_rate = random.choice(cls.PARAM_TEMPLATES['subtask_6']['sample_rates'])
        
        subtask_6_params = {
            'recording_name': recording_name,
            'recording_format': recording_format,
            'sample_rate': sample_rate,
        }
        
        # 5. Generate E7 parameters (receipt folder)
        folder_name = random.choice(cls.PARAM_TEMPLATES['subtask_7']['folder_names'])
        subtask_7_params = {
            'folder_name': folder_name,
        }
        
        # 6. Generate E8 parameters (expense)
        taxi_amount = random.choice(cls.PARAM_TEMPLATES['subtask_8']['taxi_amounts'])
        hotel_amount = random.choice(cls.PARAM_TEMPLATES['subtask_8']['hotel_amounts'])
        usb_amount = 19.99  # Fixed USB drive price (from Task 4 shopping)
        
        subtask_8_params = {
            'taxi_amount': taxi_amount,
            'hotel_amount': hotel_amount,
            'usb_amount': usb_amount,
            'total_today': taxi_amount + hotel_amount + usb_amount,  # Includes USB drive
        }
        
        # 7. Generate E9 parameters (note)
        note_file = random.choice(cls.PARAM_TEMPLATES['subtask_9']['note_files'])
        subtask_9_params = {
            'note_file': note_file,
        }
        
        # 8. Generate E10 parameters (budget - for the most recent 3 days)
        budget = random.choice(cls.PARAM_TEMPLATES['subtask_10']['budgets'])
        
        # Today's expense: taxi + hotel + usb(19.99)
        today_total = taxi_amount + hotel_amount + usb_amount
        
        # Historical expense allocation strategy:
        # - Initialize by creating one week of historical expenses (Day-6 to Day-1)
        # - However, during evaluation, only the most recent 3 days are calculated (Day-2, Day-1, Today)
        # - Thus, expenses from Day-6 to Day-3 serve as distractors
        
        # To make the task challenging, we design historical expenses such that:
        # - The total historical expenses (for one week) are slightly higher than the budget (distractor)
        # - However, the total expenses for the most recent three days are close to or slightly exceed the budget
        
        # Historical expenses (for one week, as a complete distractor)
        historical_week_base = budget * 0.8  # Historical weekly amount is approximately 80% of the budget
        historical_week_offset = random.choice([-10, 0, 10, 20, 30])
        historical_week_amount = max(30.00, historical_week_base + historical_week_offset)
        
        # Historical expenses for the most recent three days (Day-2 and Day-1)
        # Allocate approximately 40% of historical expenses to the most recent two days
        historical_3days_ratio = random.uniform(0.3, 0.5)  # 30%-50%
        historical_3days_amount = historical_week_amount * historical_3days_ratio
        
        # Calculate the total expenses for the most recent three days (this is the ground truth)
        total_3days = today_total + historical_3days_amount
        is_over_budget = total_3days > budget
        
        subtask_10_params = {
            'budget': budget,
            'historical_week_amount': historical_week_amount,  # Total historical expenses for one week (used for initialization)
            'historical_3days_amount': historical_3days_amount,  # Historical expenses for the most recent three days (used for evaluation)
            'usb_amount': usb_amount,
            'today_total': today_total,
            'total_3days': total_3days,  # Ground truth: total expenses for the most recent three days
            'is_over_budget': is_over_budget,
        }
        
        # 9. Return the complete parameter set
        return {
            'seed': seed,
            'shared': shared_params,
            'subtask_2': subtask_2_params,
            'subtask_4': subtask_4_params,
            'subtask_6': subtask_6_params,
            'subtask_7': subtask_7_params,
            'subtask_8': subtask_8_params,
            'subtask_9': subtask_9_params,
            'subtask_10': subtask_10_params,
        }
    
    def __init__(self, params: dict = None):
        """
        Initialize Scenario E
        
        Args:
            params: scenario parameters. If None, call generate_random_params() to generate random parameters
        """
        # 1. Check whether random parameters need to be generated
        if params is None:
            params = {}
        
        # If generated_params does not exist, generate it
        if 'generated_params' not in params:
            generated_params = self.generate_random_params()
            params['generated_params'] = generated_params
        else:
            generated_params = params['generated_params']
        
        # Extract shared parameters
        shared = generated_params.get('shared', {})
        user_name = shared.get('user_name', 'David')
        destination = shared.get('destination_city', 'San Francisco')
        
        # Set scenario metadata
        scenario_params = {
            'scenario_id': 'E',
            'name': f'Tech Conference Trip to {destination} for {user_name}',
            'base_date': '2026-01-15',  # Thursday, January 15, 2026
            'total_max_steps': 350,
            'success_criteria': {
                'all_subtasks_pass': False,
                'min_subtasks_pass': 0,
            },
            'generated_params': generated_params,
            'clarity_level': params.get('clarity_level'),  # ⚡ Pass clarity_level
            'reset_mode': params.get('reset_mode', False),  # ⚡ Pass reset_mode
        }
        
        super().__init__(scenario_params)
        
        # Save generated_params for use by the initialization method
        self.generated_params = generated_params
        
        # Add subtasks using parameterized approach
        self._add_parameterized_subtasks(generated_params)
        
        # Set complexity
        self.complexity = 4.8
    
    def _add_parameterized_subtasks(self, generated_params: dict):
        """Add all subtasks using the generated parameters"""
        shared = generated_params.get('shared', {})
        st2 = generated_params.get('subtask_2', {})
        st4 = generated_params.get('subtask_4', {})
        st6 = generated_params.get('subtask_6', {})
        st7 = generated_params.get('subtask_7', {})
        st8 = generated_params.get('subtask_8', {})
        st9 = generated_params.get('subtask_9', {})
        st10 = generated_params.get('subtask_10', {})
        
        # Extract shared parameters
        user_name = shared.get('user_name', 'David')
        dest_city = shared.get('destination_city', 'San Francisco')
        dest_abbr = shared.get('destination_abbr', 'SF')
        flight_number = shared.get('flight_number', 'UA 456')
        flight_departure = shared.get('flight_departure', '09:30')
        flight_arrival = shared.get('flight_arrival', '12:45')
        hotel_name = shared.get('hotel_name', 'Marriott Union Square')
        hotel_address = shared.get('hotel_address', '480 Sutter Street')
        hotel_phone = shared.get('hotel_phone', '415-555-0199')
        office_name = shared.get('office_name', 'TechCorp SF Branch')
        office_address = shared.get('office_address', '123 Tech Park Drive, Suite 400')
        colleague_name = shared.get('colleague_name', 'Sarah Miller')
        colleague_phone = shared.get('colleague_phone', '555-0102')
        
        # ========== E1: Timezone preparation and itinerary synchronization ==========
        self.add_subtask(
            subtask_id=1,
            evaluator_name="LayeredCrossAppWorldClockCalendar",
            params={
                "city_name": dest_city,
                "event_title": f"Flight to {dest_abbr}",
                "event_hour": int(flight_departure.split(':')[0]),
                "event_minute": int(flight_departure.split(':')[1]),
                "info_file": "Conference_Trip_Info.png",
            },
            weight=1.0,
            time="06:50",
            narration=f"{user_name} is preparing for a tech summit in {dest_city}. "
                     f"He needs to balance local and destination time zones, and sync the flight schedule to the calendar.",
            user_instruction=f"Morning. Open the Clock app and add '{dest_city}' to World Clock. "
                            f"Then, open Files, find 'Conference_Trip_Info.png' in Download, "
                            f"check the flight time and add a calendar event titled 'Flight to {dest_abbr}' at that time.",
            user_instruction_L0=f"Open the Clock app, navigate to World Clock, and add '{dest_city}'. Then open the Files app, go to the Download folder, open 'Conference_Trip_Info.png' to check the flight time, and create a calendar event in Simple Calendar Pro titled 'Flight to {dest_abbr}' at the departure time shown in the image.",
            user_instruction_L1=f"Add '{dest_city}' to World Clock and create a calendar event 'Flight to {dest_abbr}' based on the time in 'Conference_Trip_Info.png'.",
            user_instruction_L2=f"Prepare for my trip to {dest_city}.",
            reset_user_instruction=(
                f"Complete two tasks: "
                f"(1) Open the Clock app, go to the 'Clock' (World Clock) tab, and add '{dest_city}' to World Clock. "
                f"Then, open Files, find 'Conference_Trip_Info.png' in Download, "
                f"check the flight time"
                f"(2) Open Simple Calendar Pro and create a new event with the following details: "
                f"title 'Flight to {dest_abbr}', date January 15 2026, "
                f"start time {flight_departure}, "
                f"end time {(int(flight_departure.split(':')[0]) + 6) % 24:02d}:{flight_departure.split(':')[1]}. "
                f"Save the event."
            ),
            max_steps=35,
            requires_answer=False,
        )
        
        # ========== E2: Departure alarm and luggage reminder ==========
        alarm_time = st2.get('alarm_time', '07:30')
        alarm_hour = st2.get('alarm_hour', 7)
        alarm_minute = st2.get('alarm_minute', 30)
        checklist_item = st2.get('checklist_item', 'Check Passport and Laptop Charger')
        
        self.add_subtask(
            subtask_id=2,
            evaluator_name="LayeredCrossAppClockTasks",
            params={
                "alarm_hour": alarm_hour,
                "alarm_minute": alarm_minute,
                "alarm_label": "Leave for Airport",
                "is_one_time": True,
                "task_title": checklist_item,
                "task_priority": "highest",  # importance = 2 or 3
            },
            weight=1.0,
            time="07:00",
            narration=f"While packing, {user_name} needs a final reminder to leave on time "
                     f"and a checklist item for essential items.",
            user_instruction=f"Set a one-time alarm for {alarm_time} AM labeled 'Leave for Airport'. "
                            f"Then open Tasks and add a new task '{checklist_item}' "
                            f"with the highest priority, due today.",
            user_instruction_L0=f"Open the Clock app, create a one-time alarm for {alarm_time} AM with label 'Leave for Airport'. Then open the Tasks app and create a new task '{checklist_item}' with highest priority and due date set to today.",
            user_instruction_L1=f"Set alarm for {alarm_time} AM labeled 'Leave for Airport' and create task '{checklist_item}' with highest priority.",
            user_instruction_L2="Remind me to leave on time and check my essentials.",
            max_steps=25,
            requires_answer=False,
        )
        
        # ========== E3: Airport waiting room silent mode and connection management ==========
        self.add_subtask(
            subtask_id=3,
            evaluator_name="LayeredSystemBluetoothDND",
            params={
                "bluetooth_on": True,
                "dnd_on": True,
            },
            weight=1.0,
            time="08:30",
            narration=f"In the airport lounge, {user_name} needs to connect his noise-canceling headphones "
                     f"and enable Do Not Disturb mode.",
            user_instruction="Turn on Bluetooth in Settings. Then enable Do Not Disturb mode "
                            "so I won't be interrupted during the flight.",
            user_instruction_L0="Open the Settings app, navigate to Bluetooth and turn it on. Then go to Do Not Disturb settings and enable it.",
            user_instruction_L1="Turn on Bluetooth and enable Do Not Disturb mode.",
            user_instruction_L2="Get ready for my flight without interruptions.",
            max_steps=20,
            requires_answer=False,
        )
        
        # ========== E4: Emergency travel gear replenishment ==========
        # Product is fixed as SanDisk Cruzer Glide 16GB (2 Pack), SKU: B00J2FALDK
        # The variable parameter is office_address (used for evaluation)
        product_sku = 'B00J2FALDK'
        product_name = 'SanDisk Cruzer Glide 16GB (2 Pack) USB 2.0 Flash Drive'
        
        # Address keywords used for evaluation (extracted from the PNG image)
        shipping_office_name = st4.get('office_name', office_name)
        shipping_office_address = st4.get('office_address', office_address)
        # Extract address keywords (e.g., "123 Tech Park Drive", "Suite 400")
        address_keywords = [kw.strip() for kw in shipping_office_address.split(',') if kw.strip()]
        
        self.add_subtask(
            subtask_id=4,
            evaluator_name="LayeredShoppingPurchaseProduct",
            params={
                "product_sku": product_sku,
                "product_name_keywords": ["SanDisk", "16GB"],
                "check_method": "order",
                "eval_types": ["program_html"],
                "program_html": [
                    # Check 1: Whether the order contains the correct product SKU
                    {
                        "url": "func:shopping_get_latest_order_url()",
                        "locator": "document.querySelector('.order-details-items.ordered').outerText",
                        "required_contents": {
                            "must_include": [product_sku]
                        }
                    },
                    # Check 2: Whether the shipping address in the order is correct
                    {
                        "url": "func:shopping_get_latest_order_url()",
                        "locator": "document.querySelector('.box-order-shipping-address .box-content').outerText",
                        "required_contents": {
                            "must_include": address_keywords
                        }
                    }
                ],
                "require_login": True,
                "start_url": "__SHOPPING__",
            },
            weight=1.0,
            time="10:00",
            narration=f"{user_name} realizes he needs a USB drive for handling presentation data.",
            user_instruction=f"On the current webpage (ignore the internet access), search for '{product_name}'. "
                            f"Add it to cart and complete the purchase. "
                            f"During checkout, use the office shipping address from the trip info image I viewed earlier.",
            user_instruction_L0=f"On the current webpage (ignore the internet access), search for '{product_name}' (SKU: {product_sku}), add it to cart, and complete checkout using the office address from 'Conference_Trip_Info.png'.",
            user_instruction_L1=f"On the current webpage (ignore the internet access), buy '{product_name}' and ship it to the office address from the trip info.",
            user_instruction_L2="On the current webpage (ignore the internet access), Order a USB drive for the conference.",
            reset_user_instruction=(
                f"Open the Shopping app, ignore the internet access. "
                f"Search for '{product_name}' (SKU: {product_sku}), add it to cart, "
                f"and complete the purchase. "
                f"During checkout, use the following shipping address: "
                f"{shipping_office_name}, {shipping_office_address}, {dest_city}."
            ),
            max_steps=40,
            requires_answer=False,
        )
        
        # ========== E5: Partner Contact and Information Sharing ==========
        # Share contact information in plain-text format (VCF sharing has compatibility issues)
        self.add_subtask(
            subtask_id=5,
            evaluator_name="LayeredCrossAppContactsSmsVcf",
            params={
                "recipient_name": colleague_name,
                "recipient_phone": colleague_phone,
                "message_text": "I've arrived safely",
                "vcf_contact_name": "Hotel Front Desk",
                "vcf_contact_phone": hotel_phone,
            },
            weight=1.0,
            time="13:20",
            narration=f"After arrival, {user_name} needs to share the hotel front desk contact "
                     f"with a colleague arriving later.",
            user_instruction=f"Send a simple sms messenger text to '{colleague_name}' saying I've arrived safely, and include the Hotel Front Desk contact info from my Contacts.",
            user_instruction_L0=f"Open Contacts, find 'Hotel Front Desk' contact, note the phone number. Then open Simple SMS Messenger, send a message to '{colleague_name}' saying \"I've arrived safely\" and include the Hotel Front Desk contact info.",
            user_instruction_L1=f"Text '{colleague_name}' that I've arrived and share the Hotel Front Desk contact.",
            user_instruction_L2=f"Let {colleague_name} know I arrived and give them the hotel contact.",
            reset_user_instruction=(
                f"Open Simple SMS Messenger, send a message to '{colleague_name}' "
                f"saying \"I've arrived safely\" and include the Hotel Front Desk phone number: {hotel_phone}."
            ),
            max_steps=25,
            requires_answer=False,
        )
        
        # ========== E6: Professional Meeting Audio Recording Configuration ==========
        recording_name = st6.get('recording_name', 'Keynote_AI')
        recording_format = st6.get('recording_format', 'Wav')
        sample_rate = st6.get('sample_rate', '48kHz')
        
        self.add_subtask(
            subtask_id=6,
            evaluator_name="LayeredAudioRecorderWithConfig",
            params={
                "recording_name": recording_name,
                "expected_format": recording_format.lower(),  # "wav" or "mp3"
                "expected_sample_rate": sample_rate,
            },
            weight=1.0,
            time="15:00",
            narration=f"The keynote session begins. {user_name} needs high-quality recording for later review.",
            user_instruction=f"Open Audio Settings, set the format to '{recording_format}' "
                            f"and sample rate to '{sample_rate}'. "
                            f"Then record a short clip, stop it, and rename it to '{recording_name}'.",
            user_instruction_L0=f"Open the Audio Recorder app, navigate to Settings, set recording format to '{recording_format}' and sample rate to '{sample_rate}'. Return to main screen, start recording, stop it after a few seconds, then rename the recording to '{recording_name}'.",
            user_instruction_L1=f"Record with {recording_format} format at {sample_rate} and name it '{recording_name}'.",
            user_instruction_L2="Record the keynote with high quality.",
            max_steps=30,
            requires_answer=False,
        )
        
        # ========== E7: Capture Receipts for Reimbursement and Archive Them ==========
        folder_name = st7.get('folder_name', 'Jan_Trip/Receipts')
        
        self.add_subtask(
            subtask_id=7,
            evaluator_name="LayeredCameraAndFilesOrganize",
            params={
                "photo_type": "camera",
                "target_folder": folder_name,
                "create_folder_if_missing": True,
            },
            weight=1.0,
            time="18:30",
            narration=f"After dinner, {user_name} needs to digitize the receipt immediately to avoid losing it.",
            user_instruction=f"Take a photo of my dinner receipt. Then open Files, "
                            f"create a new folder '{folder_name}' in the main directory and move the photo into it.",
            user_instruction_L0=f"Open the Camera app and take a photo. Then open the Files app, create the folder structure '{folder_name}', navigate to the Camera folder, find the most recent photo, and move it to '{folder_name}'.",
            user_instruction_L1=f"Take a photo and organize it into '{folder_name}'.",
            user_instruction_L2="Save my receipt for reimbursement.",
            reset_user_instruction=(
                f"Open the Camera app and take a photo of a receipt. "
                f"Then open the Files app and navigate to the sdk_gphone_x86_64 storage area. "
                f"In the root of sdk_gphone_x86_64 storage area, create the folder structure '{folder_name}'. "
                f"Then find the most recently taken photo, and move it to '{folder_name}' "
            ),
            max_steps=35,
            requires_answer=False,
        )
        
        # ========== E8: Business Travel Expense Accounting ==========
        taxi_amount = st8.get('taxi_amount', 35.00)
        hotel_amount = st8.get('hotel_amount', 250.00)
        usb_amount = st8.get('usb_amount', 19.99)
        
        self.add_subtask(
            subtask_id=8,
            evaluator_name="LayeredExpenseAddMultiple",
            params={
                "expenses": [
                    {"name": "Taxi to Hotel", "amount": taxi_amount, "category": "Transportation"},
                    {"name": "Hotel Stay", "amount": hotel_amount, "category": "Housing"},
                    {"name": "USB Drive", "amount": usb_amount, "category": "Others"},
                ],
            },
            weight=1.0,
            time="21:00",
            narration=f"{user_name} records today's transportation, accommodation, and shopping expenses.",
            user_instruction=f"Open Pro Expense. Record today's expenses: "
                            f"${taxi_amount:.2f} for 'Taxi to Hotel' (Transportation), "
                            f"${hotel_amount:.2f} for 'Hotel Stay' (Housing), "
                            f"and ${usb_amount:.2f} for 'USB Drive' (Others).",
            user_instruction_L0=f"Open the Pro Expense app and create three expense entries: (1) 'Taxi to Hotel' ${taxi_amount:.2f} in Transportation category, (2) 'Hotel Stay' ${hotel_amount:.2f} in Housing category, and (3) 'USB Drive' ${usb_amount:.2f} in Others category.",
            user_instruction_L1=f"Record expenses: Taxi ${taxi_amount:.2f}, Hotel ${hotel_amount:.2f}, USB Drive from my order.",
            user_instruction_L2="Log today's travel expenses.",
            max_steps=35,
            requires_answer=False,
        )
        
        # ========== E9: Organize Trip and Expense Logs ==========
        note_file = st9.get('note_file', 'Day1_Summary.md')
        
        # Calculate arrival time (departure time + 6 hours)
        dep_hour, dep_min = map(int, flight_departure.split(':'))
        arr_hour = (dep_hour + 6) % 24
        arrival_time = f"{arr_hour:02d}:{dep_min:02d}"
        
        # Calculate today's total expenses
        total_today = taxi_amount + hotel_amount + usb_amount
        
        self.add_subtask(
            subtask_id=9,
            evaluator_name="LayeredMarkorTripSummary",
            params={
                "file_name": note_file,
                # Trip information keywords (extracted from the PNG)
                "flight_info": {
                    "flight_number": flight_number,
                    "departure": flight_departure,
                    "arrival": arrival_time,
                    "destination": dest_city,
                },
                # Today's expenses
                "expense_amounts": [taxi_amount, hotel_amount, usb_amount],
            },
            weight=1.0,
            time="22:00",
            narration=f"Before sleep, {user_name} summarizes today's trip information and expenses.",
            user_instruction=f"Open Markor and create a file '{note_file}'. "
                            f"Find the flight info image I checked this morning and record the flight details. "
                            f"Also summarize today's expenses from Pro Expense.",
            user_instruction_L0=f"Open Markor, create a file '{note_file}'. Write: Flight {flight_number}, departure {flight_departure}, arrival {arrival_time}, to {dest_city}. Today's expenses: Taxi ${taxi_amount:.2f}, Hotel ${hotel_amount:.2f}, USB ${usb_amount:.2f}.",
            user_instruction_L1=f"Create '{note_file}' in Markor with flight info from the image and today's expenses.",
            user_instruction_L2="Summarize today's trip and spending.",
            max_steps=40,
            requires_answer=False,
        )
        
        # ========== E10: Financial Trend Analysis and Subsequent Cost Control (Last 3 Days) ==========
        budget = st10.get('budget', 180.00)
        total_3days = st10.get('total_3days', 185.00)
        is_over_budget = st10.get('is_over_budget', True)
        
        self.add_subtask(
            subtask_id=10,
            evaluator_name="LayeredExpenseStatisticsQA",
            params={
                "budget": budget,
                "expected_total": total_3days,  # Ground truth: total expenses over the last 3 days
                "is_over_budget": is_over_budget,
                "must_contain_keywords": [
                    # Verify total amount (allowing for minor discrepancies)
                    # Or verify overspending/non-overspending judgment
                ],
                "min_keywords_found": 0,  # Primarily rely on overspending judgment
                "time_range": "last_3_days",  # Explicitly specify the time range
            },
            weight=1.0,
            time="22:30",
            narration=f"{user_name} checks the last 3 days' financial trend to see if the trip spending is within budget.",
            user_instruction=f"Open Pro Expense. "
                            f"Tell me the total amount I've spent in the last 3 days (including today). "
                            f"Has it exceeded my ${budget:.0f} 3-day budget?",
            user_instruction_L0=f"Open the Pro Expense app, check the statistics or transaction list for the last 3 days (including today), calculate the total amount spent in the last 3 days, and tell me if it exceeds ${budget:.0f}.",
            user_instruction_L1=f"Check the last 3 days' total expenses and tell me if I'm over my ${budget:.0f} budget.",
            user_instruction_L2="Am I over budget for the last 3 days?",
            max_steps=25,
            requires_answer=True,
        )
    
    def initialize_task(self, env):
        """
        Batch initialization at scenario startup
        
        Pre-configure the environment for all subtasks:
        - Generate a PNG image containing trip information
        - Create contacts
        - Clear application data for Clock, Calendar, Tasks, Markor, and Expense
        - Add historical expense records (for E10)
        - Set initial system state (Bluetooth OFF, DND OFF)
        """
        # Call parent class method (e.g., set base_date)
        super().initialize_task(env)
        
        # ⚡ Reset mode: Skip batch initialization; each task is independently initialized in _reset_initialize_subtask()
        if self.reset_mode:
            logging.info("⚡ Reset Mode: Skipping batch initialization")
            logging.info("   Each task will be initialized independently before execution")
            # Ensure timezone is UTC only (required by nearly all tasks)
            self._ensure_utc_timezone(env)
            return
        
        logging.info("🔧 Performing batch initialization of Scenario E environment...")
        
        # ⚠️ Critical fix: First ensure timezone is UTC during scenario initialization
        # This resolves incorrect time display in Calendar
        from scendroid.env import adb_utils
        logging.info("   🌍 Ensuring device timezone is UTC...")
        try:
            # Set timezone to UTC (using ScenDroid standard method)
            adb_utils.set_root_if_needed(env.controller)
            
            adb_utils.issue_generic_request(
                ['shell', 'service', 'call', 'alarm', '3', 's16', 'UTC'],
                env.controller
            )
            
            # Also set system properties
            adb_utils.issue_generic_request(
                ['shell', 'setprop', 'persist.sys.timezone', 'UTC'],
                env.controller
            )
            
            logging.info("   ✅ Timezone confirmed as UTC")
        except Exception as e:
            logging.warning(f"   ⚠️  Could not set timezone: {e}")
        
        try:
            # 1. Generate trip information PNG (for E1, E4)
            self._create_trip_info_image(env)
            
            # 2. Clean up and configure Clock (for E1, E2)
            self._cleanup_clock(env)
            
            # 3. Clean up Calendar (for E1)
            self._cleanup_calendar(env)
            
            # 4. Clean up and set up Tasks (for E2)
            self._cleanup_tasks(env)
            
            # 5. Set system initial state (for E3)
            self._setup_system_state(env)
            
            # 6. Create contacts (for E5)
            self._setup_contacts(env)
            
            # 7. Set up Audio Recorder (for E6)
            self._cleanup_audiorecorder(env)
            
            # 8. Clean up Camera and Files (for E7)
            self._cleanup_camera_files(env)
            
            # 9. Set up Expense and add historical records (for E8, E10)
            self._setup_expense(env)
            
            # 10. Clean up Markor (for E9)
            self._cleanup_markor(env)
            
            logging.info("✅ Scenario E batch initialization completed")
            
            # Return to the home screen
            from scendroid.env import adb_utils
            import time
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
            
        except Exception as e:
            logging.error(f"❌ Batch initialization failed: {e}")
            import traceback
            logging.error(traceback.format_exc())
            raise
    
    def _create_trip_info_image(self, env):
        """Generate a PNG image of itinerary information (refer to the robust implementation of Scenario B's _create_breakfast_photo)"""
        from scendroid.task_evals.utils import user_data_generation
        from scendroid.utils import file_utils
        from scendroid.env import device_constants, adb_utils
        import os
        import tempfile
        import time
        
        logging.info("   📄 Generating itinerary information image...")
        
        # Retrieve parameters (extracted outside all try blocks for easier log-based debugging)
        shared = self.generated_params.get('shared', {})
        user_name = shared.get('user_name', 'David')
        dest_city = shared.get('destination_city', 'San Francisco')
        flight_number = shared.get('flight_number', 'UA 456')
        flight_departure = shared.get('flight_departure', '09:30')
        hotel_name = shared.get('hotel_name', 'Marriott Union Square')
        hotel_address = shared.get('hotel_address', '480 Sutter Street')
        hotel_phone = shared.get('hotel_phone', '415-555-0199')
        office_name = shared.get('office_name', 'TechCorp SF Branch')
        office_address = shared.get('office_address', '123 Tech Park Drive, Suite 400')
        
        logging.info(f"   📄 Parameters: flight={flight_number}, departure={flight_departure}")
        
        # Calculate arrival time (consistent with reset_user_instruction)
        dep_hour, dep_min = map(int, flight_departure.split(':'))
        arr_hour = (dep_hour + 6) % 24
        flight_arrival_local = f"{arr_hour:02d}:{dep_min:02d}"
        
        # ─── Step 1: Create PNG file locally ───────────────────────────────────────
        info_text = f"""
═══════════════════════════════════
    FLIGHT BOOKING CONFIRMATION
═══════════════════════════════════

Passenger: {user_name} Smith
Flight: {flight_number}
Date: January 15, 2026

Departure: {flight_departure}
Arrival: {flight_arrival_local}
Destination: {dest_city}

───────────────────────────────────
    ACCOMMODATION DETAILS
───────────────────────────────────

Hotel: {hotel_name}
Address: {hotel_address}, {dest_city}
Front Desk: {hotel_phone}

───────────────────────────────────
    SHIPPING ADDRESS (for orders)
───────────────────────────────────

Office: {office_name}
Address: {office_address}, {dest_city}

═══════════════════════════════════
"""
        
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "Conference_Trip_Info.png")
        
        # If local temporary files remain, delete them first
        try:
            os.remove(temp_path)
        except Exception:
            pass
        
        image = user_data_generation._draw_text(info_text.strip(), font_size=18)
        image.save(temp_path)
        logging.info(f"   ✅ Local PNG generated: {temp_path} ({os.path.getsize(temp_path)} bytes)")
        
        # ─── Step 2: Clear the Download directory (refer to line 1071 in scenario_omnilife.py)────
        # ⚠️ Critical: Do not use 'rm -f specific_file' (Android FUSE layer fails silently)
        # ✅ Correct approach: Use file_utils.clear_directory to clear the entire directory (internally uses 'rm -r dir/*')
        remote_path = f"{device_constants.DOWNLOAD_DATA}/Conference_Trip_Info.png"
        
        try:
            file_utils.clear_directory(device_constants.DOWNLOAD_DATA, env.controller)
            logging.info(f"   🗑️ Download directory cleared (file_utils.clear_directory)")
        except Exception as clear_err:
            logging.warning(f"   ⚠️ clear_directory failed: {clear_err}, attempting 'rm -r *'")
            adb_utils.issue_generic_request(
                ['shell', 'rm', '-r', f"{device_constants.DOWNLOAD_DATA}/*"], env.controller
            )
        time.sleep(0.5)
        
        # ─── Step 3: Push new file to device ────────────────────────────────────────────
        file_utils.copy_data_to_device(temp_path, remote_path, env.controller)
        time.sleep(0.5)
        logging.info(f"   📤 New file pushed to device")
        
        # ─── Step 4: Clean up local temporary files ────────────────────────────────────────────
        try:
            os.remove(temp_path)
        except Exception:
            pass
        
        # ─── Step 5: Verify push result ────────────────────────────────────────────────
        verify_result = adb_utils.issue_generic_request(
            ['shell', 'ls', '-la', remote_path], env.controller
        )
        logging.info(f"   📋 Device file verification: {verify_result}")
        
        # ─── Step 6: Force-close the Files app (to clear its memory cache and prevent displaying old PNG)────
        # Root cause: The Files app (Simple File Manager Pro) caches PNG thumbnails in memory;
        # even if the disk file is updated, the old version still displays upon next launch. Forcing closure clears this cache.
        for files_pkg in [
            'com.simplemobiletools.filemanager.pro',
            'com.android.documentsui',
        ]:
            try:
                adb_utils.issue_generic_request(
                    ['shell', 'am', 'force-stop', files_pkg], env.controller
                )
            except Exception:
                pass
        logging.info("   🔒 Files app force-closed (old thumbnail cache cleared)")
        
        # ─── Step 7: Clear Android system thumbnail cache directory ─────────────────────────
        for thumb_dir in [
            '/storage/emulated/0/.thumbnails',
            '/storage/emulated/0/DCIM/.thumbnails',
        ]:
            try:
                adb_utils.issue_generic_request(
                    ['shell', 'rm', '-rf', thumb_dir], env.controller
                )
            except Exception:
                pass
        
        # ─── Step 8: Trigger full MediaStore rescan (more reliable than SCAN_FILE)──────
        try:
            adb_utils.issue_generic_request(
                ['shell', 'am', 'broadcast',
                 '-a', 'android.intent.action.MEDIA_MOUNTED',
                 '--ez', 'read-only', 'false',
                 '-d', 'file:///storage/emulated/0'],
                env.controller
            )
            time.sleep(2.0)
            logging.info("   🔄 Full rescan of MediaStore has been triggered")
        except Exception as scan_err:
            logging.info(f"   ℹ️  MediaStore rescan failed: {scan_err}")
        
        logging.info(f"   ✅ Trip information image created successfully: {remote_path} (flight={flight_number}, departure={flight_departure})")
    
    def _cleanup_clock(self, env):
        """Clean up Clock app data"""
        logging.info("   ⏰ Cleaning up Clock data...")
        
        from scendroid.env import adb_utils
        import time
        
        try:
            # Clear Clock app data
            adb_utils.clear_app_data(
                adb_utils.extract_package_name(adb_utils.get_adb_activity("clock")),
                env.controller,
            )
            time.sleep(1.0)
            logging.info("   ✅ Clock data has been cleared")
        except Exception as e:
            logging.warning(f"   ⚠️ Clock cleanup failed: {e}")
    
    def _cleanup_calendar(self, env):
        """Clean up Calendar data"""
        logging.info("   📅 Cleaning up Calendar data...")
        
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.env import adb_utils
        import time
        
        try:
            # ✅ Fix 1: Use clear_app_data to fully reset the Calendar app (including view settings)
            adb_utils.clear_app_data("com.simplemobiletools.calendar.pro", env.controller)
            time.sleep(1.0)
            
            # Launch Calendar once and return to ensure app initialization is complete (skip first-launch wizard)
            adb_utils.start_activity(
                "com.simplemobiletools.calendar.pro/.activities.MainActivity",
                None,  # extra_args
                env.controller
            )
            time.sleep(2.0)
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            
            # ✅ Fix 2: Reset timezone after clearing app data (to prevent timezone reset)
            logging.info("      🌍 Reconfirming device timezone as UTC...")
            adb_utils.set_root_if_needed(env.controller)
            
            adb_utils.issue_generic_request(
                ['shell', 'service', 'call', 'alarm', '3', 's16', 'UTC'],
                env.controller
            )
            
            adb_utils.issue_generic_request(
                ['shell', 'setprop', 'persist.sys.timezone', 'UTC'],
                env.controller
            )
            
            # Clean up calendar events database
            calendar_utils.clear_calendar_db(env)
            
            logging.info("   ✅ Calendar data has been cleared")
        except Exception as e:
            logging.warning(f"   ⚠️ Calendar cleanup failed: {e}")
    
    def _cleanup_tasks(self, env):
        """Clean up and configure Tasks app"""
        logging.info("   📝 Configuring Tasks...")
        
        from scendroid.task_evals.information_retrieval import task_app_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from datetime import datetime
        import random
        import uuid
        
        try:
            # 1. Clean up database
            task_app_utils.clear_task_db(env)
            logging.info("      ✅ Tasks database has been cleared")
            
            # 2. Retrieve base_date
            base_date_str = self.context.base_date or '2026-01-15'
            base_date = datetime.strptime(base_date_str, '%Y-%m-%d')
            
            # 3. Add distractor tasks
            distractor_tasks = []
            distractor_titles = [
                'Buy groceries', 'Reply to emails', 'Schedule dentist',
                'Call mom', 'Pay bills', 'Clean room',
            ]
            
            for i, title in enumerate(distractor_titles):
                due_ts = int(base_date.replace(hour=random.randint(8, 20)).timestamp()) * 1000
                created_ts = due_ts - 7 * 24 * 3600 * 1000
                
                task = sqlite_schema_utils.Task(
                    title=title,
                    importance=random.randint(0, 1),  # low/medium priority
                    dueDate=due_ts,
                    hideUntil=0,
                    created=created_ts,
                    modified=created_ts,
                    completed=0,
                    deleted=0,
                    notes=None,
                    remoteId=str(uuid.uuid4().int),
                )
                distractor_tasks.append(task)
            
            # 4. Add tasks
            task_app_utils.add_tasks(distractor_tasks, env)
            logging.info(f"      ✅ Added {len(distractor_tasks)} distractor tasks")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Tasks configuration failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _setup_system_state(self, env):
        """Set system initial state"""
        logging.info("   ⚙️ Setting system initial state...")
        
        from scendroid.env import adb_utils
        import time
        
        try:
            # 1. Turn off Bluetooth
            adb_utils.toggle_bluetooth(env.controller, 'off')
            logging.info("      ✅ Bluetooth has been turned off")
            
            # 2. Turn off Do Not Disturb
            # Set zen_mode = 0 (OFF) - for both global and secure settings
            adb_utils.issue_generic_request([
                'shell', 'settings', 'put', 'global', 'zen_mode', '0'
            ], env.controller)
            adb_utils.issue_generic_request([
                'shell', 'settings', 'put', 'secure', 'zen_mode', '0'
            ], env.controller)
            # Additionally use cmd notification to turn off DND
            adb_utils.issue_generic_request([
                'shell', 'cmd', 'notification', 'set_dnd', 'off'
            ], env.controller)
            logging.info("      ✅ Do Not Disturb has been turned off")
            
            time.sleep(1.0)
            
        except Exception as e:
            logging.warning(f"   ⚠️ System status setting failed: {e}")
    
    def _setup_contacts(self, env):
        """Create contacts"""
        logging.info("   👥 Creating contacts...")
        
        from scendroid.utils import contacts_utils
        from scendroid.task_evals.common_validators import sms_validators
        from scendroid.env import adb_utils
        import time
        
        try:
            # Clear existing contacts
            contacts_utils.clear_contacts(env.controller)
            time.sleep(1.0)
            
            # Clear SMS
            sms_validators.clear_sms_and_threads(env.controller)
            logging.info("      ✅ SMS cleared")
            
            # Retrieve parameters
            shared = self.generated_params.get('shared', {})
            colleague_name = shared.get('colleague_name', 'Sarah Miller')
            colleague_phone = shared.get('colleague_phone', '555-0102')
            hotel_phone = shared.get('hotel_phone', '415-555-0199')
            
            # Create contact list
            contacts = [
                {"name": colleague_name, "phone": colleague_phone},
                {"name": "Hotel Front Desk", "phone": hotel_phone},
                {"name": "John Doe", "phone": "555-0201"},  # Distractor
                {"name": "Alice Wang", "phone": "555-0202"},  # Distractor
            ]
            
            # Add contacts
            successfully_added = 0
            for i, contact in enumerate(contacts, 1):
                name = contact['name']
                phone = contact['phone']
                
                for attempt in range(2):
                    try:
                        if attempt > 0:
                            logging.info(f"      ↻ Retrying '{name}'")
                        
                        adb_utils.press_home_button(env.controller)
                        time.sleep(1.5)
                        
                        contacts_utils.add_contact(
                            name, phone, env.controller, ui_delay_sec=2.0
                        )
                        logging.info(f"      ✅ Added: '{name}' ({phone})")
                        successfully_added += 1
                        time.sleep(2.0)
                        break
                    except Exception as e:
                        if attempt == 1:
                            logging.error(f"      ❌ Failed to add: '{name}'")
                        time.sleep(1.0)
            
            logging.info(f"   ✅ Contact addition completed: {successfully_added}/{len(contacts)}")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Contact setup failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _cleanup_audiorecorder(self, env):
        """Clean up the Audio Recorder app and related audio recording files"""
        logging.info("   🎤 Cleaning up Audio Recorder...")
        
        from scendroid.env import adb_utils, tools, device_constants
        import time
        
        try:
            # 1. Clean up audio recording files in the Downloads folder
            logging.info("      Cleaning up audio recording files in Downloads...")
            download_path = f"{device_constants.EMULATOR_DATA}/Download"
            adb_utils.issue_generic_request([
                'shell', 'rm', '-f', f'{download_path}/*.wav',
            ], env.controller)
            adb_utils.issue_generic_request([
                'shell', 'rm', '-f', f'{download_path}/*.mp3',
            ], env.controller)
            adb_utils.issue_generic_request([
                'shell', 'rm', '-f', f'{download_path}/*.m4a',
            ], env.controller)
            
            # 2. Clean up audio recording files stored in external storage for Audio Recorder
            logging.info("      Cleaning up audio recording files in external storage...")
            audio_dirs = [
                f"{device_constants.EMULATOR_DATA}/AudioRecorder",
                f"{device_constants.EMULATOR_DATA}/Recordings",
                f"{device_constants.EMULATOR_DATA}/Music",
            ]
            for audio_dir in audio_dirs:
                adb_utils.issue_generic_request([
                    'shell', 'rm', '-rf', audio_dir
                ], env.controller)
            
            # 3. Use 'pm clear' to completely clear app data
            adb_utils.clear_app_data(
                "com.dimowner.audiorecorder",
                env.controller,
            )
            time.sleep(0.5)
            
            # 4. Grant permissions
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
            
            # 5. Launch the app to handle the onboarding interface
            adb_utils.issue_generic_request([
                "shell", "monkey",
                "-p", "com.dimowner.audiorecorder",
                "-c", "android.intent.category.LAUNCHER",
                "1",
            ], env.controller)
            time.sleep(2.0)
            
            # 6. Tap the onboarding button
            try:
                controller = tools.AndroidToolController(env=env.controller)
                for btn_text in ['GET STARTED', 'Get Started', 'START', 'Start']:
                    try:
                        controller.click_element(btn_text)
                        time.sleep(1.5)
                        break
                    except:
                        pass
                
                for btn_text in ['APPLY', 'Apply', 'OK', 'Done']:
                    try:
                        controller.click_element(btn_text)
                        time.sleep(1.0)
                        break
                    except:
                        pass
            except:
                pass
            
            # Close the app
            adb_utils.close_app('audio recorder', env.controller)
            time.sleep(0.5)
            
            logging.info("   ✅ Audio Recorder cleaned up and configured")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Audio Recorder cleanup failed: {e}")
    
    def _cleanup_camera_files(self, env):
        """Clean up Camera and Files-related data"""
        logging.info("   📷 Cleaning up Camera and Files...")
        
        from scendroid.env import device_constants, adb_utils
        from scendroid.utils import file_utils
        import time
        
        try:
            # Clean up the DCIM directory
            file_utils.clear_directory(device_constants.GALLERY_DATA, env.controller)
            logging.info("      ✅ Camera photos cleared")
            
            # Retrieve target folders and clean them up
            st7 = self.generated_params.get('subtask_7', {})
            folder_name = st7.get('folder_name', 'Jan_Trip/Receipts')
            top_level = folder_name.split('/')[0]
            
            # Clean up possible top-level directories (including scenario D's leftover Lectures)
            folders_to_clean = [
                'Jan_Trip', 'Business_Trip', 'Conference_2026', 'Travel_Docs',
                'Lectures',  # Scenario D legacy
            ]
            for folder in folders_to_clean:
                folder_path = f"{device_constants.EMULATOR_DATA}/{folder}"
                adb_utils.issue_generic_request([
                    'shell', 'rm', '-rf', folder_path
                ], env.controller)
            
            time.sleep(0.5)
            logging.info("      ✅ Files directory cleaned")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Camera/Files cleanup failed: {e}")
    
    def _setup_expense(self, env):
        """Set up Expense and add historical records (distractors)
        
        Notes:
        - USB drive expenses are manually recorded by the user in Task 8 and are not pre-added here
        - Initialize one week of historical expenses (Day-6 to Day-1)
        - Expenses from the most recent three days (Day-2, Day-1, Today) are used for evaluation
        - Expenses from Day-6 to Day-3 serve as distractors
        """
        logging.info("   💰 Setting up Expense...")
        
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.env.setup_device import apps
        from datetime import datetime, timedelta
        import time
        import random
        
        _DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
        _TABLE = "expense"
        _APP_NAME = "pro expense"
        
        try:
            # 1. Check whether the database exists
            if not sqlite_utils.table_exists(_TABLE, _DB_PATH, env):
                logging.info("      Expense database does not exist; initializing...")
                apps.ExpenseApp.setup(env)
            
            # 2. Clear existing expenses
            sqlite_utils.delete_all_rows_from_table(
                _TABLE, _DB_PATH, env, _APP_NAME
            )
            logging.info("      ✅ Expense data cleared")
            
            # 3. Retrieve parameters
            st10 = self.generated_params.get('subtask_10', {})
            historical_week_amount = st10.get('historical_week_amount', 50.00)  # Total historical expenses for one week
            historical_3days_amount = st10.get('historical_3days_amount', 20.00)  # Historical expenses for the most recent three days
            
            base_date_str = self.context.base_date or '2026-01-15'
            base_date = datetime.strptime(base_date_str, '%Y-%m-%d')
            
            all_expenses = []
            
            # 4. Distribute historical expenses across different days
            # Day-6 to Day-3: distractors (total = historical_week_amount - historical_3days_amount)
            # Day-2 to Day-1: portion of historical expenses for the most recent three days (total = historical_3days_amount)
            
            distractor_amount = historical_week_amount - historical_3days_amount  # Day-6 to Day-3
            recent_amount = historical_3days_amount  # Day-2 to Day-1
            
            expense_names = ['Coffee', 'Lunch', 'Snacks', 'Metro', 'Supplies', 'Parking', 'Breakfast']
            categories = [4, 4, 4, 6, 7, 6, 4]  # Food=4, Transport=6, Others=7
            
            # 4.1 Add distractor expenses (Day-6 to Day-3, total of 4 days)
            # Distribute distractor_amount across 4 days
            distractor_days = [6, 5, 4, 3]  # days_ago
            distractor_per_day = distractor_amount / len(distractor_days)
            
            for days_ago in distractor_days:
                # Assign 1–2 records per day
                num_records = random.randint(1, 2)
                day_total = distractor_per_day
                
                for j in range(num_records):
                    if j == num_records - 1:
                        # Use the remaining amount for the last record
                        amount = day_total
                    else:
                        # Randomly distribute amounts
                        amount = day_total * random.uniform(0.3, 0.7)
                        day_total -= amount
                    
                    expense_date = base_date - timedelta(days=days_ago)
                    amount_cents = int(amount * 100)
                    date_ts = int(expense_date.timestamp()) * 1000
                    
                    expense = sqlite_schema_utils.Expense(
                        name=random.choice(expense_names),
                        amount=amount_cents,
                        category=random.choice(categories),
                        created_date=date_ts,
                        modified_date=date_ts,
                    )
                    all_expenses.append(expense)
            
            # 4.2 Add historical expenses for the most recent three days (Day-2 and Day-1, total of 2 days)
            # Distribute recent_amount across Day-2 and Day-1
            recent_days = [2, 1]  # days_ago
            recent_per_day = recent_amount / len(recent_days)
            
            for days_ago in recent_days:
                # Assign 1–3 records per day
                num_records = random.randint(1, 3)
                day_total = recent_per_day
                
                for j in range(num_records):
                    if j == num_records - 1:
                        # Use the remaining amount for the last record
                        amount = day_total
                    else:
                        # Randomly distribute amounts
                        amount = day_total * random.uniform(0.2, 0.6)
                        day_total -= amount
                    
                    expense_date = base_date - timedelta(days=days_ago)
                    amount_cents = int(amount * 100)
                    date_ts = int(expense_date.timestamp()) * 1000
                    
                    expense = sqlite_schema_utils.Expense(
                        name=random.choice(expense_names),
                        amount=amount_cents,
                        category=random.choice(categories),
                        created_date=date_ts,
                        modified_date=date_ts,
                    )
                    all_expenses.append(expense)
            
            # 5. Insert historical expenses
            if all_expenses:
                sqlite_utils.insert_rows_to_remote_db(
                    rows=all_expenses,
                    exclude_key='expense_id',
                    table_name=_TABLE,
                    remote_db_file_path=_DB_PATH,
                    app_name=_APP_NAME,
                    env=env,
                )
                logging.info(f"      ✅ Added {len(all_expenses)} historical expense records")
                logging.info(f"         - Weekly total: ${historical_week_amount:.2f}")
                logging.info(f"         - Last 3 days history: ${historical_3days_amount:.2f} (Day-2, Day-1)")
                logging.info(f"         - Distractor: ${distractor_amount:.2f} (Day-6 to Day-3)")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Expense setup failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _cleanup_markor(self, env):
        """Clean up Markor data"""
        logging.info("   📝 Cleaning up Markor...")
        
        from scendroid.utils import file_utils
        from scendroid.env import device_constants, adb_utils
        import time
        
        markor_dir = device_constants.MARKOR_DATA
        
        try:
            # Ensure directory exists
            adb_utils.issue_generic_request([
                'shell', 'mkdir', '-p', markor_dir
            ], env.controller)
            time.sleep(0.5)
            
            # Clean up directory
            file_utils.clear_directory(markor_dir, env.controller)
            logging.info("   ✅ Markor data cleared")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Markor cleanup failed: {e}")
    
    def initialize_subtask(self, subtask_idx: int, env):
        """
        Subtask initialization logic
        """
        # ⚡ Reset mode: skip scenario-specific preprocessing
        # All initialization is handled by _reset_initialize_subtask() in super()
        if self.reset_mode:
            super().initialize_subtask(subtask_idx, env)
            return
        
        subtask = self.subtasks[subtask_idx]
        subtask_id = subtask['subtask_id']
        
        # E4: Shopping task - requires WebArena login
        if subtask_id == 4:
            logging.info("   🛒 Shopping task - initializing WebArena login...")
            # WebArena login is handled in the parent class BaseScenarioEvaluator
        
        # E5: SMS task - refresh UI
        if subtask_id == 5:
            logging.info("   💬 SMS task - refreshing UI...")
            try:
                from scendroid.env import adb_utils
                import time
                
                adb_utils.close_app("simple sms", env.controller)
                time.sleep(1.0)
                
                adb_utils.start_activity(
                    "com.simplemobiletools.smsmessenger/.activities.MainActivity",
                    None, env.controller
                )
                time.sleep(2.0)
                
                for _ in range(3):
                    adb_utils.issue_generic_request([
                        "shell", "input", "keyevent", "KEYCODE_BACK"
                    ], env.controller)
                    time.sleep(0.3)
                
                adb_utils.press_home_button(env.controller)
                time.sleep(1.0)
            except Exception as e:
                logging.warning(f"      ⚠️ SMS UI refresh failed: {e}")
        
        # Call parent class method
        super().initialize_subtask(subtask_idx, env)
    
    def tear_down(self, env):
        """Cleanup after scenario completion
        
        Reference: Scenario D's tear_down implementation
        1. Clean up SMS messages
        2. Clean up Markor files
        3. Clean up audio recording files
        4. Rebuild the Shopping container (since E4 places orders)
        5. Restore system state
        """
        logging.info("=" * 70)
        logging.info("🧹 Scenario E - cleanup tasks")
        logging.info("=" * 70)
        
        try:
            from scendroid.env import adb_utils, device_constants
            from scendroid.task_evals.common_validators import sms_validators
            from scendroid.utils import file_utils
            import time
            
            # 1. Stop any ongoing audio recording
            logging.info("   🎤 Stopping audio recording...")
            try:
                adb_utils.close_app("audio recorder", env.controller)
            except:
                pass
            
            # 2. Clean up SMS
            logging.info("   💬 Cleaning up SMS...")
            try:
                sms_validators.clear_sms_and_threads(env.controller)
                logging.info("      ✅ SMS cleaned up")
            except Exception as e:
                logging.warning(f"      ⚠️ SMS cleanup failed: {e}")
            
            # 3. Clean up Markor files
            logging.info("   📝 Cleaning up Markor files...")
            try:
                file_utils.clear_directory(device_constants.MARKOR_DATA, env.controller)
                logging.info("      ✅ Markor files cleaned")
            except Exception as e:
                logging.warning(f"      ⚠️ Markor cleanup failed: {e}")
            
            # 4. Clean audio recording files
            logging.info("   🎵 Cleaning audio recording files...")
            try:
                download_path = f"{device_constants.EMULATOR_DATA}/Download"
                for ext in ['*.wav', '*.mp3', '*.m4a']:
                    adb_utils.issue_generic_request([
                        'shell', 'rm', '-f', f'{download_path}/{ext}'
                    ], env.controller)
                for audio_dir in ['AudioRecorder', 'Recordings']:
                    adb_utils.issue_generic_request([
                        'shell', 'rm', '-rf', f'{device_constants.EMULATOR_DATA}/{audio_dir}'
                    ], env.controller)
                logging.info("      ✅ Audio recording files cleaned")
            except Exception as e:
                logging.warning(f"      ⚠️ Audio recording file cleanup failed: {e}")
            
            # 5. Clean Camera photos and folders
            logging.info("   📷 Cleaning Camera and folders...")
            try:
                file_utils.clear_directory(device_constants.GALLERY_DATA, env.controller)
                for folder in ['Jan_Trip', 'Business_Trip', 'Conference_2026', 'Travel_Docs']:
                    adb_utils.issue_generic_request([
                        'shell', 'rm', '-rf', f'{device_constants.EMULATOR_DATA}/{folder}'
                    ], env.controller)
                logging.info("      ✅ Camera and folders cleaned")
            except Exception as e:
                logging.warning(f"      ⚠️ Camera cleanup failed: {e}")
            
            # 6. Rebuild the Shopping container (E4 places orders, so rebuilding is required)
            logging.info("   🛒 Rebuilding the Shopping container...")
            try:
                from scendroid.apps.shopping.utils import rebuild_shopping_container
                # Pass env to automatically extract console_port
                rebuild_shopping_container(env=env)
                logging.info("      ✅ Shopping container rebuilt")
            except Exception as e:
                logging.warning(f"      ⚠️ Shopping container rebuild failed: {e}")
            
            # 7. Restore system state
            logging.info("   ⚙️ Restoring system state...")
            try:
                adb_utils.toggle_bluetooth(env.controller, 'off')
                adb_utils.issue_generic_request([
                    'shell', 'settings', 'put', 'global', 'zen_mode', '0'
                ], env.controller)
                logging.info("      ✅ System state restored")
            except:
                pass
            
            # 8. Close all related applications
            logging.info("   📱 Closing all applications...")
            apps_to_close = [
                "clock", "tasks", "audio recorder", "pro expense", 
                "files", "simple calendar pro", "chrome", 
                "markor", "camera", "contacts", "simple sms messenger"
            ]
            for app in apps_to_close:
                try:
                    adb_utils.close_app(app, env.controller)
                except:
                    pass
            
            time.sleep(1.0)
            
            # 9. Return to the home screen
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            
            logging.info("✅ Scenario E cleanup completed")
            
        except Exception as e:
            logging.error(f"❌ Tear down failed: {e}")
            import traceback
            logging.error(traceback.format_exc())
        
        logging.info("=" * 70)
        
        # Call the parent class's tear_down
        super().tear_down(env)

    
    # ====================================================================
    # Per-Task Reset Mode: Independent initialization per task
    # ====================================================================
    
    def _reset_initialize_subtask(self, subtask_idx: int, env):
        """
        Subtask initialization under Per-Task Reset mode
        
        Before each subtask starts, the following steps occur:
        1. Clear related app data
        2. Create prerequisites required for that task
        3. Call the evaluator's initialize_task() (if needed)
        
        Differences from Scenario mode:
        - Scenario mode: Batch-initialize once + prerequisites naturally generated by preceding tasks
        - Reset mode: Each task initializes independently, simulating completion of all prior steps for that task
        """
        subtask = self.subtasks[subtask_idx]
        task_id = subtask['subtask_id']
        
        logging.info(f"   🔧 Per-task reset initialization for Task {task_id}: {subtask['evaluator_name']}")
        
        # Ensure timezone is UTC
        self._ensure_utc_timezone(env)
        
        if task_id == 1:
            self._reset_init_task1_clock_files_calendar(subtask, env)
        elif task_id == 2:
            self._reset_init_task2_clock_tasks(subtask, env)
        elif task_id == 3:
            self._reset_init_task3_system_settings(env)
        elif task_id == 4:
            self._reset_init_task4_shopping(subtask, env)
        elif task_id == 5:
            self._reset_init_task5_contacts_sms(subtask, env)
        elif task_id == 6:
            self._reset_init_task6_audio_recorder(subtask, env)
        elif task_id == 7:
            self._reset_init_task7_camera_files(subtask, env)
        elif task_id == 8:
            self._reset_init_task8_expense(subtask, env)
        elif task_id == 9:
            self._reset_init_task9_markor(subtask, env)
        elif task_id == 10:
            self._reset_init_task10_expense_qa(subtask, env)
        else:
            # Unknown task: Use default implementation
            logging.warning(f"   ⚠️  No custom reset init for Task {task_id}, using evaluator default")
            subtask['evaluator_instance'].initialize_task(env)
    
    def _ensure_utc_timezone(self, env):
        """Ensure the device timezone is set to UTC (shared across multiple tasks)"""
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
    
    def _reset_init_task1_clock_files_calendar(self, subtask, env):
        """
        Task 1 (Timezone Preparation and Schedule Synchronization - Clock + Files + Calendar):
        Prerequisites: Schedule information PNG + Clock cleared + Calendar cleared
        """
        logging.info("   🔧 Reset Init Task 1: Generating trip info image, clearing Clock & Calendar")
        
        # 1. Generate the schedule information PNG
        self._create_trip_info_image(env)
        
        # 2. Clear Clock
        self._cleanup_clock(env)
        
        # 3. Clear Calendar
        self._cleanup_calendar(env)
        
        # 4. Return to home
        try:
            from scendroid.env import adb_utils
            import time
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 1 initialization completed")
    
    def _reset_init_task2_clock_tasks(self, subtask, env):
        """
        Task 2 (Departure Alarm and Luggage Reminder - Clock + Tasks):
        Prerequisites: Clock cleared (with new alarm added) + Tasks cleared (with new tasks added)
        """
        logging.info("   🔧 Reset Init Task 2: Clearing Clock & Tasks")
        
        # 1. Clear Clock
        self._cleanup_clock(env)
        
        # 2. Clear and configure Tasks (add distractor tasks)
        self._cleanup_tasks(env)
        
        # 3. Return to home
        try:
            from scendroid.env import adb_utils
            import time
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 2 initialization completed")
    
    def _reset_init_task3_system_settings(self, env):
        """
        Task 3 (Airport Waiting Room Silent Mode and Connection Management - System Settings):
        Prerequisites: Bluetooth OFF + DND OFF
        """
        logging.info("   🔧 Reset Init Task 3: Setting Bluetooth OFF, DND OFF")
        
        self._setup_system_state(env)
        
        # 2. Return to home
        try:
            from scendroid.env import adb_utils
            import time
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 3 initialization completed")
    
    def _reset_init_task4_shopping(self, subtask, env):
        """
        Task 4 (Urgent Travel Equipment Replenishment - Shopping):
        Prerequisites: Schedule information PNG (including shipping address) + WebArena login
        
        ⚠️ Note: In Reset mode, the parent class initialize_subtask() returns immediately after calling _reset_initialize_subtask(),
        without executing the subsequent shopping evaluator initialization logic.
        Therefore, evaluator.initialize_task(env) must be explicitly called here.
        """
        logging.info("   🔧 Reset Init Task 4: Shopping (trip info + WebArena login)")
        
        # 1. Ensure the schedule information PNG exists (including shipping address, for the agent to check the office shipping address)
        self._create_trip_info_image(env)
        
        # 2. Call the Shopping evaluator's initialize_task (handles Chrome cleanup + WebArena login + navigation to the starting page)
        # ✅ Following the pattern of Scenarios B/C, explicit invocation is required in Reset mode
        try:
            evaluator = subtask['evaluator_instance']
            logging.info("      🛒 Initializing Shopping evaluator (Chrome cleanup + WebArena login)...")
            evaluator.initialize_task(env)
            logging.info("      ✅ Shopping evaluator initialized (logged in, on Shopping homepage)")
        except Exception as e:
            logging.warning(f"      ⚠️  Shopping evaluator initialization failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
        
        # ℹ️ Note: After Shopping task initialization, the agent should remain on the Shopping homepage (not return to the home screen)
        # evaluator.initialize_task() ends with the agent already on the Shopping homepage, enabling direct agent interaction
        # ⚠️ However, per user requirements, Shopping-type tasks must also return to the home screen
        try:
            from scendroid.env import adb_utils
            import time
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 4 initialization completed")
    
    def _reset_init_task5_contacts_sms(self, subtask, env):
        """
        Task 5 (Partner Communication and Information Sharing - Contacts + SMS):
        Prerequisites: Contacts (colleague + hotel front desk) + SMS cleared
        """
        logging.info("   🔧 Reset Init Task 5: Creating contacts + clearing SMS")
        
        from scendroid.utils import contacts_utils
        from scendroid.task_evals.common_validators import sms_validators
        from scendroid.env import adb_utils
        import time
        
        # 1. Clear SMS
        try:
            sms_validators.clear_sms_and_threads(env.controller)
            adb_utils.close_app("simple sms", env.controller)
            time.sleep(1.0)
            logging.info("      ✅ SMS cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear SMS: {e}")
        
        # 2. Create contacts
        try:
            contacts_utils.clear_contacts(env.controller)
            time.sleep(1.0)
            
            # Retrieve parameters
            shared = self.generated_params.get('shared', {})
            colleague_name = shared.get('colleague_name', 'Sarah Miller')
            colleague_phone = shared.get('colleague_phone', '555-0102')
            hotel_phone = shared.get('hotel_phone', '415-555-0199')
            
            # Create required contacts (colleague + hotel front desk)
            contacts = [
                {"name": colleague_name, "phone": colleague_phone},
                {"name": "Hotel Front Desk", "phone": hotel_phone},
            ]
            
            for contact in contacts:
                try:
                    adb_utils.press_home_button(env.controller)
                    time.sleep(1.5)
                    
                    contacts_utils.add_contact(
                        contact['name'], contact['phone'], env.controller, ui_delay_sec=2.0
                    )
                    logging.info(f"      ✅ Added: '{contact['name']}' ({contact['phone']})")
                    time.sleep(2.0)
                except Exception as e:
                    logging.warning(f"      ⚠️  Failed to add: '{contact['name']}' - {e}")
            
        except Exception as e:
            logging.warning(f"      ⚠️  Contacts setup failed: {e}")
        
        # 3. Return to home
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 5 initialization completed")
    
    def _reset_init_task6_audio_recorder(self, subtask, env):
        """
        Task 6 (Professional meeting audio recording configuration - Audio Recorder):
        Prerequisites: Clear Audio Recorder + Grant permissions
        """
        logging.info("   🔧 Reset Init Task 6: Clearing Audio Recorder")
        
        self._cleanup_audiorecorder(env)
        
        # 2. Return to home
        try:
            from scendroid.env import adb_utils
            import time
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 6 initialization completed")
    
    def _reset_init_task7_camera_files(self, subtask, env):
        """
        Task 7 (Capture reimbursement receipts and archive them - Camera + Files):
        Prerequisites: Clear Camera + Clear target folder
        """
        logging.info("   🔧 Reset Init Task 7: Clearing Camera & Files")
        
        self._cleanup_camera_files(env)
        
        # 2. Return to home
        try:
            from scendroid.env import adb_utils
            import time
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 7 initialization completed")
    
    def _reset_init_task8_expense(self, subtask, env):
        """
        Task 8 (Business travel expense tracking - Pro Expense):
        Prerequisites: Clear Expense (the agent needs to add three expenses)
        """
        logging.info("   🔧 Reset Init Task 8: Clearing Expense")
        
        from scendroid.task_evals.utils import sqlite_utils
        from scendroid.env.setup_device import apps
        import time
        
        _DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
        _TABLE = "expense"
        _APP_NAME = "pro expense"
        
        try:
            # Check whether the database exists
            if not sqlite_utils.table_exists(_TABLE, _DB_PATH, env):
                logging.info("      Expense database does not exist; initializing...")
                apps.ExpenseApp.setup(env)
            
            # Clear expense data
            sqlite_utils.delete_all_rows_from_table(
                _TABLE, _DB_PATH, env, _APP_NAME
            )
            logging.info("      ✅ Expense data cleared")
            
        except Exception as e:
            logging.warning(f"      ⚠️  Failed to clear Expense: {e}")
        
        # Return to home
        try:
            from scendroid.env import adb_utils
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 8 initialization completed")
    
    def _reset_init_task9_markor(self, subtask, env):
        """
        Task 9 (Organize trip and expense logs - Markor):
        Prerequisites:
        - Trip information PNG (for reading flight details)
        - Three existing expenses in Expense (simulating output from Task 8)
        - Clear Markor
        """
        logging.info("   🔧 Reset Init Task 9: Creating expenses + trip info, clearing Markor")
        
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.env.setup_device import apps
        from datetime import datetime
        import time
        
        _DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
        _TABLE = "expense"
        _APP_NAME = "pro expense"
        
        # 1. Ensure the trip information PNG exists
        self._create_trip_info_image(env)
        
        # 2. Configure Expense and add three expenses for today (simulating output from Task 8)
        try:
            # Check whether the database exists
            if not sqlite_utils.table_exists(_TABLE, _DB_PATH, env):
                logging.info("      Expense database does not exist; initializing...")
                apps.ExpenseApp.setup(env)
            
            # Clear existing expenses
            sqlite_utils.delete_all_rows_from_table(
                _TABLE, _DB_PATH, env, _APP_NAME
            )
            
            # Retrieve expense parameters
            st8 = self.generated_params.get('subtask_8', {})
            taxi_amount = st8.get('taxi_amount', 35.00)
            hotel_amount = st8.get('hotel_amount', 250.00)
            usb_amount = st8.get('usb_amount', 19.99)
            
            base_date_str = self.context.base_date or '2026-01-15'
            base_date = datetime.strptime(base_date_str, '%Y-%m-%d')
            date_ts = int(base_date.timestamp()) * 1000
            
            # Create three expenses for today
            expenses = [
                sqlite_schema_utils.Expense(
                    name="Taxi to Hotel",
                    amount=int(taxi_amount * 100),
                    category=6,  # Transportation
                    created_date=date_ts,
                    modified_date=date_ts,
                ),
                sqlite_schema_utils.Expense(
                    name="Hotel Stay",
                    amount=int(hotel_amount * 100),
                    category=5,  # Housing
                    created_date=date_ts,
                    modified_date=date_ts,
                ),
                sqlite_schema_utils.Expense(
                    name="USB Drive",
                    amount=int(usb_amount * 100),
                    category=7,  # Others
                    created_date=date_ts,
                    modified_date=date_ts,
                ),
            ]
            
            # Insert expenses
            sqlite_utils.insert_rows_to_remote_db(
                rows=expenses,
                exclude_key='expense_id',
                table_name=_TABLE,
                remote_db_file_path=_DB_PATH,
                app_name=_APP_NAME,
                env=env,
            )
            logging.info(f"      ✅ Added {len(expenses)} expenses for today")
            
        except Exception as e:
            logging.warning(f"      ⚠️  Failed to configure Expense: {e}")
        
        # 3. Clear Markor
        self._cleanup_markor(env)
        
        # 4. Return to home
        try:
            from scendroid.env import adb_utils
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 9 initialization completed")
    
    def _reset_init_task10_expense_qa(self, subtask, env):
        """
        Task 10 (Financial trend analysis and subsequent cost control - Pro Expense QA):
        Prerequisites:
        - One week of historical expenses (Day-6 to Day-1)
        - Today's three expenses (simulating the output of Task 8)
        - Total expenses for the most recent three days (Day-2, Day-1, Today) for evaluation
        """
        logging.info("   🔧 Reset Init Task 10: Setting up Expense with historical data")
        
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.env.setup_device import apps
        from datetime import datetime, timedelta
        import time
        import random
        
        _DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
        _TABLE = "expense"
        _APP_NAME = "pro expense"
        
        try:
            # 1. Check whether the database exists
            if not sqlite_utils.table_exists(_TABLE, _DB_PATH, env):
                logging.info("      Expense database does not exist; initializing...")
                apps.ExpenseApp.setup(env)
            
            # 2. Clear existing expenses
            sqlite_utils.delete_all_rows_from_table(
                _TABLE, _DB_PATH, env, _APP_NAME
            )
            logging.info("      ✅ Expense data cleared")
            
            # 3. Retrieve parameters
            st8 = self.generated_params.get('subtask_8', {})
            st10 = self.generated_params.get('subtask_10', {})
            
            taxi_amount = st8.get('taxi_amount', 35.00)
            hotel_amount = st8.get('hotel_amount', 250.00)
            usb_amount = st8.get('usb_amount', 19.99)
            
            historical_week_amount = st10.get('historical_week_amount', 50.00)
            historical_3days_amount = st10.get('historical_3days_amount', 20.00)
            
            base_date_str = self.context.base_date or '2026-01-15'
            base_date = datetime.strptime(base_date_str, '%Y-%m-%d')
            
            all_expenses = []
            
            # 4. Add today's three expenses (simulating the output of Task 8)
            today_ts = int(base_date.timestamp()) * 1000
            today_expenses = [
                sqlite_schema_utils.Expense(
                    name="Taxi to Hotel",
                    amount=int(taxi_amount * 100),
                    category=6,  # Transportation
                    created_date=today_ts,
                    modified_date=today_ts,
                ),
                sqlite_schema_utils.Expense(
                    name="Hotel Stay",
                    amount=int(hotel_amount * 100),
                    category=5,  # Housing
                    created_date=today_ts,
                    modified_date=today_ts,
                ),
                sqlite_schema_utils.Expense(
                    name="USB Drive",
                    amount=int(usb_amount * 100),
                    category=7,  # Others
                    created_date=today_ts,
                    modified_date=today_ts,
                ),
            ]
            all_expenses.extend(today_expenses)
            
            # 5. Add historical expenses (from Day-6 to Day-1)
            expense_names = ['Coffee', 'Lunch', 'Snacks', 'Metro', 'Supplies', 'Parking', 'Breakfast']
            categories = [4, 4, 4, 6, 7, 6, 4]  # Food=4, Transport=6, Others=7
            
            # 5.1 Distractor expenses (from Day-6 to Day-3)
            distractor_amount = historical_week_amount - historical_3days_amount
            distractor_days = [6, 5, 4, 3]
            distractor_per_day = distractor_amount / len(distractor_days)
            
            for days_ago in distractor_days:
                num_records = random.randint(1, 2)
                day_total = distractor_per_day
                
                for j in range(num_records):
                    if j == num_records - 1:
                        amount = day_total
                    else:
                        amount = day_total * random.uniform(0.3, 0.7)
                        day_total -= amount
                    
                    expense_date = base_date - timedelta(days=days_ago)
                    amount_cents = int(amount * 100)
                    date_ts = int(expense_date.timestamp()) * 1000
                    
                    expense = sqlite_schema_utils.Expense(
                        name=random.choice(expense_names),
                        amount=amount_cents,
                        category=random.choice(categories),
                        created_date=date_ts,
                        modified_date=date_ts,
                    )
                    all_expenses.append(expense)
            
            # 5.2 Historical expenses for the most recent three days (Day-2 and Day-1)
            recent_days = [2, 1]
            recent_per_day = historical_3days_amount / len(recent_days)
            
            for days_ago in recent_days:
                num_records = random.randint(1, 3)
                day_total = recent_per_day
                
                for j in range(num_records):
                    if j == num_records - 1:
                        amount = day_total
                    else:
                        amount = day_total * random.uniform(0.2, 0.6)
                        day_total -= amount
                    
                    expense_date = base_date - timedelta(days=days_ago)
                    amount_cents = int(amount * 100)
                    date_ts = int(expense_date.timestamp()) * 1000
                    
                    expense = sqlite_schema_utils.Expense(
                        name=random.choice(expense_names),
                        amount=amount_cents,
                        category=random.choice(categories),
                        created_date=date_ts,
                        modified_date=date_ts,
                    )
                    all_expenses.append(expense)
            
            # 6. Insert all expenses
            if all_expenses:
                sqlite_utils.insert_rows_to_remote_db(
                    rows=all_expenses,
                    exclude_key='expense_id',
                    table_name=_TABLE,
                    remote_db_file_path=_DB_PATH,
                    app_name=_APP_NAME,
                    env=env,
                )
                logging.info(f"      ✅ Added {len(all_expenses)} expense records")
                logging.info(f"         - Today's expenses: 3 (${taxi_amount + hotel_amount + usb_amount:.2f})")
                logging.info(f"         - Historical expenses: {len(all_expenses) - 3}")
            
        except Exception as e:
            logging.warning(f"      ⚠️  Expense setup failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
        
        # Return to home
        try:
            from scendroid.env import adb_utils
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 10 initialization completed")

