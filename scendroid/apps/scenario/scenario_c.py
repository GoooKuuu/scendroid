"""
Scenario C: Student Research Day (Student Seminar Day)

A complex scenario comprising nine subtasks, simulating a graduate student's busy seminar day:
1. Morning Prep - Set an alarm + create a seminar schedule (Clock + Calendar)
2. Class Recording - Record a class lecture (Audio Recorder)
3. Breakfast Expense - Record breakfast expenses (Pro Expense; receipt located in Files/Pictures)
4. Recording Organization - Organize audio recording files (Audio Recorder + Files)
5. Meeting Update & Notify - Modify the seminar time and notify all participants (Calendar + SMS)
6. Lab Supplies Shopping - Purchase laboratory supplies (Shopping)
7. Exercise Prep - Create an exercise music playlist and play it randomly + launch exercise tracking (RetroMusic + OpenTracks)
8. Discussion Summary - Summarize SMS replies into Markor (SMS + Markor)
9. Daily Summary Doc - Create today's summary document, recording meeting information, breakfast expenses, and the audio recording filename (Markor; supports partial scoring)

Features:
- Academic seminar scenario spanning from morning to evening
- Data dependencies among tasks (Task 1→5, Task 3→9, Task 4→9)
- Includes cross-app collaboration tasks
- Task 9 supports partial scoring (0.3/0.6/1.0)
- Supports parameterized generation
"""

from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.scenario.base import BaseScenarioEvaluator


@AppRegistry.register_evaluator("ScenarioC_StudentResearchDay")
class ScenarioCStudentResearchDayEvaluator(BaseScenarioEvaluator):
    """
    Scenario C: Student Research Day for {student_name} - Parameterized version
    
    Description:
    Simulates a graduate student's busy seminar day, from morning preparation to evening summary
    Covers class recording, seminar management, exercise relaxation, and note organization
    
    Subtasks (9):
    1. Morning Prep (Clock + Calendar) - Set an alarm + create a seminar schedule
    2. Class Recording (Audio Recorder) - Record a class lecture
    3. Breakfast Expense (Pro Expense) - Record breakfast expenses
    4. Recording Organization (Audio Recorder + Files) - Organize audio recording files
    5. Meeting Update & Notify (Calendar + SMS) - Modify the seminar time and notify participants
    6. Lab Supplies Shopping (Shopping) - Purchase laboratory supplies
    7. Exercise Prep (RetroMusic + OpenTracks) - Exercise music playlist + exercise tracking
    8. Discussion Summary (SMS + Markor) - Summarize SMS replies
    9. Daily Summary Doc (Markor) - Create today's summary document, recording three items (supports partial scoring: 0.3/0.6/1.0)
    
    Features:
    - Dependencies among tasks (Task 1→5, Task 3→9, Task 4→9)
    - Simulates a realistic graduate student's day
    - Task 9 supports partial scoring: 0.3 points for one item, 0.6 points for two items, and 1.0 point for all three items
    
    Scoring:
    - All tasks have equal weight (partial scoring for Task 9 affects the final score)
    - Report completion status for each task upon completion
    """
    
    app_names = ("clock", "simple calendar pro", "audio recorder", "pro expense",
                 "files", "simple sms messenger", "chrome", "retro music",
                 "opentracks", "markor")
    
    scenario_id = "C"
    complexity = 3.5
    
    # ========== Parameter template definition ==========
    PARAM_TEMPLATES = {
        # Shared parameters (used across tasks)
        'shared': {
            'student_names': ['David', 'Alice', 'Michael', 'Emma', 'James'],
            'course_names': ['AI Seminar', 'Machine Learning', 'Data Mining', 
                            'Computer Vision', 'NLP Workshop'],
            'seminar_topics': {
                'AI Seminar': ['Transformers', 'CNNs', 'GANs', 'Reinforcement Learning'],
                'Machine Learning': ['Decision Trees', 'SVM', 'Neural Networks', 'K-Means'],
                'Data Mining': ['Clustering', 'Association Rules', 'Anomaly Detection'],
                'Computer Vision': ['Object Detection', 'Segmentation', 'Image Generation'],
                'NLP Workshop': ['BERT', 'GPT', 'Text Classification', 'NER'],
            },
            'seminar_locations': ['Room 402', 'Lab 305', 'Seminar Room B', 'Conference 201'],
            # Symposium participants (for Task 5 SMS notification)
            'seminar_members': [
                {'name': 'Prof. Smith', 'phone': '555-0101', 'role': 'advisor'},
                {'name': 'Bob Chen', 'phone': '555-0102', 'role': 'member'},
                {'name': 'Sarah Lee', 'phone': '555-0103', 'role': 'member'},
                {'name': 'Tom Wang', 'phone': '555-0104', 'role': 'member'},
            ],
            # Distractor contacts (should NOT be notified)
            'distractor_contacts': [
                {'name': 'Mom', 'phone': '555-9001'},
                {'name': 'John Doe', 'phone': '555-9002'},
            ],
        },
        
        # Task 1: Alarm + Calendar
        'subtask_1': {
            'alarm_times': [(7, 30), (7, 45), (8, 0), (8, 15)],  # (hour, minute)
            'alarm_labels': ['Morning Class', 'Seminar Prep', 'Research Day'],
        },
        
        # Task 3: Breakfast expense
        'subtask_3': {
            'breakfast_amounts': [5.50, 6.80, 7.50, 8.20],
            'breakfast_names': ['Campus Breakfast', 'Cafeteria Meal', 'Morning Coffee'],
            'breakfast_notes': ['Cash', 'Card', 'Campus Card'],
        },
        
        # Task 4: Audio recording organization
        'subtask_4': {
            'target_folders': ['Documents/Lectures', 'Study/Recordings', 'Research/Audio'],
        },
        
        # Task 5: Symposium time modification
        'subtask_5': {
            'original_times': [(14, 0), (14, 30), (15, 0)],  # Original time
            'new_times': [(15, 0), (15, 30), (16, 0)],  # New time (delayed by 1 hour)
            'duration_minutes': [90, 120],  # Meeting duration
        },
        
        # Task 6: Shopping (fixed items)
        'subtask_6': {
            'product_sku': 'B00J2FALDK',
            'product_name': 'SanDisk Cruzer Glide 16GB (2 Pack) USB 2.0 Flash Drive',
            'product_price': 19.99,
        },
        
        # Task 7: Workout music playlist (using ScenDroid built-in songs)
        'subtask_7': {
            'playlist_name': 'Workout Mix',
            'min_duration_minutes': 30,  # At least 30 minutes
            # Using the _SONGS list in retro_music.py
            'available_songs': [
                'My Heart is Yours', 'Endless Summer', 'Whispering Wind', 'Lost in the Echo',
                'Chasing Shadows', 'Night Drive', 'Echoes of Silence', 'Bright Lights',
                'Moments', 'Forever Young', 'Rising Sun', 'Silent Dreams',
                'City of Stars', 'Moonlight Sonata', 'Through the Storm', 'Return to Paradise',
            ],
            'noise_songs': [
                'Voices in the Hall', 'Under the Sky', "Dreamer's Awake", 'Serenity Now',
                'Falling Feathers', 'Orbiting Stars', 'Reflections', 'Beyond the Horizon',
            ],
        },
        
        # Task 8: SMS summary (symposium progress replies)
        'subtask_8': {
            'progress_replies': [
                {'from': 'Bob Chen', 'content': 'Found 3 relevant papers on Transformers'},
                {'from': 'Sarah Lee', 'content': 'Finished the literature review section'},
                {'from': 'Tom Wang', 'content': 'Code implementation is 80% done'},
            ],
            'distractor_messages': [
                {'from': 'Alice Smith', 'phone': '555-0199', 'content': 'Are you free for lunch tomorrow?'},
                {'from': 'John Doe', 'phone': '555-0188', 'content': 'Thanks for the book recommendation!'},
            ],
        },
        
        # Task 9: Daily schedule document
        'subtask_9': {
            'doc_file_name': 'DailySchedule.md',
        },
    }
    
    @classmethod
    def generate_random_params(cls, seed=None):
        """
        Generate random parameters for Scenario C
        
        Args:
            seed: Random seed
            
        Returns:
            Dictionary of parameters, containing parameters for all subtasks
        """
        import random
        
        if seed is not None:
            random.seed(seed)
        
        # 1. Generate shared parameters
        student_name = random.choice(cls.PARAM_TEMPLATES['shared']['student_names'])
        course_name = random.choice(cls.PARAM_TEMPLATES['shared']['course_names'])
        topic = random.choice(cls.PARAM_TEMPLATES['shared']['seminar_topics'][course_name])
        seminar_location = random.choice(cls.PARAM_TEMPLATES['shared']['seminar_locations'])
        seminar_members = cls.PARAM_TEMPLATES['shared']['seminar_members']
        distractor_contacts = cls.PARAM_TEMPLATES['shared']['distractor_contacts']
        
        shared_params = {
            'student_name': student_name,
            'course_name': course_name,
            'topic': topic,
            'seminar_location': seminar_location,
            'seminar_members': seminar_members,
            'distractor_contacts': distractor_contacts,
        }
        
        # 2. Task 1 parameters (alarm + calendar)
        alarm_hour, alarm_minute = random.choice(cls.PARAM_TEMPLATES['subtask_1']['alarm_times'])
        alarm_label = random.choice(cls.PARAM_TEMPLATES['subtask_1']['alarm_labels'])
        
        subtask_1_params = {
            'alarm_hour': alarm_hour,
            'alarm_minute': alarm_minute,
            'alarm_label': alarm_label,
            'event_title': f'{course_name}: {topic}',
            'event_location': seminar_location,
            'event_attendees': ', '.join([m['name'] for m in seminar_members]),
        }
        
        # 3. Task 3 parameters (breakfast expense)
        breakfast_amount = random.choice(cls.PARAM_TEMPLATES['subtask_3']['breakfast_amounts'])
        breakfast_name = random.choice(cls.PARAM_TEMPLATES['subtask_3']['breakfast_names'])
        breakfast_note = random.choice(cls.PARAM_TEMPLATES['subtask_3']['breakfast_notes'])
        
        subtask_3_params = {
            'amount': breakfast_amount,
            'name': breakfast_name,
            'note': breakfast_note,
            'category': 'Food',
        }
        
        # 4. Task 4 parameters (audio recording organization)
        recording_name = f"{topic.replace(' ', '_')}_Lecture"
        target_folder = random.choice(cls.PARAM_TEMPLATES['subtask_4']['target_folders'])
        
        subtask_4_params = {
            'recording_name': recording_name,
            'target_folder': target_folder,
        }
        
        # 5. Task 5 parameters (symposium time modification)
        idx = random.randint(0, len(cls.PARAM_TEMPLATES['subtask_5']['original_times']) - 1)
        original_hour, original_minute = cls.PARAM_TEMPLATES['subtask_5']['original_times'][idx]
        new_hour, new_minute = cls.PARAM_TEMPLATES['subtask_5']['new_times'][idx]
        duration_minutes = random.choice(cls.PARAM_TEMPLATES['subtask_5']['duration_minutes'])
        
        subtask_5_params = {
            'seminar_title': f'{course_name}: {topic}',
            'original_hour': original_hour,
            'original_minute': original_minute,
            'new_hour': new_hour,
            'new_minute': new_minute,
            'duration_minutes': duration_minutes,
            'location': seminar_location,
        }
        
        # 6. Task 6 parameters (shopping)
        subtask_6_params = {
            'product_sku': cls.PARAM_TEMPLATES['subtask_6']['product_sku'],
            'product_name': cls.PARAM_TEMPLATES['subtask_6']['product_name'],
            'product_price': cls.PARAM_TEMPLATES['subtask_6']['product_price'],
        }
        
        # 7. Task 7 parameters (workout music playlist)
        playlist_name = cls.PARAM_TEMPLATES['subtask_7']['playlist_name']
        available_songs = cls.PARAM_TEMPLATES['subtask_7']['available_songs']
        noise_songs = cls.PARAM_TEMPLATES['subtask_7']['noise_songs']
        min_duration = cls.PARAM_TEMPLATES['subtask_7']['min_duration_minutes']
        
        subtask_7_params = {
            'playlist_name': playlist_name,
            'available_songs': available_songs,
            'noise_songs': noise_songs,
            'min_duration_minutes': min_duration,
        }
        
        # 8. Task 8 parameters (SMS summary)
        progress_replies = cls.PARAM_TEMPLATES['subtask_8']['progress_replies']
        distractor_messages = cls.PARAM_TEMPLATES['subtask_8']['distractor_messages']
        summary_file = 'DiscussionSummary.md'
        
        subtask_8_params = {
            'progress_replies': progress_replies,
            'distractor_messages': distractor_messages,
            'summary_file': summary_file,
        }
        
        # 9. Task 9 parameters (daily schedule document)
        subtask_9_params = {
            'file_name': cls.PARAM_TEMPLATES['subtask_9']['doc_file_name'],
            'seminar_title': f'{course_name}: {topic}',
            'seminar_time': f'{new_hour}:{new_minute:02d}',  # Use modified time
            'seminar_location': seminar_location,
            'breakfast_amount': breakfast_amount,
            'recording_name': recording_name,  # Add audio recording filename to Task 9 parameters  
        }
        
        return {
            'seed': seed,
            'shared': shared_params,
            'subtask_1': subtask_1_params,
            'subtask_3': subtask_3_params,
            'subtask_4': subtask_4_params,
            'subtask_5': subtask_5_params,
            'subtask_6': subtask_6_params,
            'subtask_7': subtask_7_params,
            'subtask_8': subtask_8_params,
            'subtask_9': subtask_9_params,
        }
    
    def __init__(self, params: dict = None):
        """
        Initialize Scenario C
        
        Args:
            params: Scenario parameters. If None, invoke generate_random_params() to generate random parameters
        """
        # 1. Detect whether random parameters need to be generated  
        if params is None:
            params = {}
        
        # Generate if generated_params is not present  
        if 'generated_params' not in params:
            generated_params = self.generate_random_params()
            params['generated_params'] = generated_params
        else:
            generated_params = params['generated_params']
        
        # Extract shared parameters  
        shared = generated_params.get('shared', {})
        student_name = shared.get('student_name', 'David')
        
        # Set scenario metadata  
        scenario_params = {
            'scenario_id': 'C',
            'name': f'Student Research Day for {student_name}',
            'base_date': '2026-01-07',  # Wednesday, January 7, 2026
            'total_max_steps': 300,
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
        
        # Add subtasks in a parameterized way  
        self._add_parameterized_subtasks(generated_params)
        
        # Set complexity  
        self.complexity = 3.5
    
    def _add_parameterized_subtasks(self, generated_params: dict):
        """Add all subtasks using the generated parameters"""  
        shared = generated_params.get('shared', {})
        st1 = generated_params.get('subtask_1', {})
        st3 = generated_params.get('subtask_3', {})
        st4 = generated_params.get('subtask_4', {})
        st5 = generated_params.get('subtask_5', {})
        st6 = generated_params.get('subtask_6', {})
        st7 = generated_params.get('subtask_7', {})
        st8 = generated_params.get('subtask_8', {})
        st9 = generated_params.get('subtask_9', {})
        
        # Extract shared parameters  
        student_name = shared.get('student_name', 'David')
        course_name = shared.get('course_name', 'AI Seminar')
        topic = shared.get('topic', 'Transformers')
        seminar_location = shared.get('seminar_location', 'Room 402')
        seminar_members = shared.get('seminar_members', [])
        
        # ========== Task 1: Morning preparation - alarm + calendar ==========  
        alarm_hour = st1.get('alarm_hour', 7)
        alarm_minute = st1.get('alarm_minute', 30)
        alarm_label = st1.get('alarm_label', 'Morning Class')
        event_title = st1.get('event_title', f'{course_name}: {topic} Seminar')  # Add "Seminar" to make the reference more explicit  
        event_location = st1.get('event_location', seminar_location)
        event_attendees = st1.get('event_attendees', '')
        
        # Use the original time for the seminar (Task 5 will change it to the new time)  
        seminar_hour = st5.get('original_hour', 14)
        seminar_minute = st5.get('original_minute', 0)
        duration_minutes = st5.get('duration_minutes', 90)
        
        self.add_subtask(
            subtask_id=1,
            evaluator_name="LayeredCrossAppClockCalendar",
            params={
                "alarm_time_hour": alarm_hour,
                "alarm_time_minute": alarm_minute,
                "alarm_label": alarm_label,
                "event_title": event_title,
                "event_hour": seminar_hour,
                "event_minute": seminar_minute,
                "event_duration_minutes": duration_minutes,
                "event_location": event_location,
                "event_description": f"Attendees: {event_attendees}",
            },
            weight=1.0,
            time="07:00",
            narration=f"Morning. {student_name} needs to set an alarm for class and create a calendar event for today's seminar.",
            user_instruction=f"Set an alarm for {alarm_hour}:{alarm_minute:02d} AM labeled '{alarm_label}'. "
                            f"Then create a calendar event titled '{event_title}' at {seminar_hour}:{seminar_minute:02d}, "
                            f"duration {duration_minutes} minutes, in {event_location}, with attendees: {event_attendees}.",
            user_instruction_L0=f"Open the Clock app and set an alarm for {alarm_hour}:{alarm_minute:02d} AM with label '{alarm_label}'. "
                               f"Then open Simple Calendar Pro and create an event titled '{event_title}' at {seminar_hour}:{seminar_minute:02d}, "
                               f"duration {duration_minutes} minutes, location '{event_location}', description 'Attendees: {event_attendees}'.",
            user_instruction_L1=f"Set an alarm for {alarm_hour}:{alarm_minute:02d} AM and create a {duration_minutes}-minute calendar event for the {topic} seminar at {seminar_hour}:{seminar_minute:02d}.",
            user_instruction_L2="I need to wake up for class and remember today's seminar.",
            max_steps=35,
            requires_answer=False,
        )
        
        # ========== Task 2: Classroom audio recording (start and stop) ==========  
        self.add_subtask(
            subtask_id=2,
            evaluator_name="LayeredAudioRecorderRecordAudio",
            params={},
            weight=1.0,
            time="08:05",
            narration=f"Class begins. The professor starts explaining {topic}. {student_name} needs to record a segment of the lecture.",
            user_instruction="Open Audio Recorder, change the sample rate to 32kHz and set the recording format to Wav for better quality, start recording the lecture, and then stop the recording after a few seconds.",
            user_instruction_L0="Open the Audio Recorder app, navigate to settings, change the sample rate to 32kHz, set the recording format to Wav, then return to the main screen, start recording, wait a few seconds, and stop the recording.",
            user_instruction_L1="Record a segment in Audio Recorder with 32kHz sample rate and Wav format, then stop.",
            user_instruction_L2="Record and finish a short lecture segment with high quality audio.",
            max_steps=25,
            requires_answer=False,
        )
        
        # ========== Task 3: Record breakfast expense ==========  
        breakfast_amount = st3.get('amount', 6.80)
        breakfast_name = st3.get('name', 'Campus Breakfast')
        breakfast_note = st3.get('note', 'Cash')
        breakfast_category = st3.get('category', 'Food')
        
        self.add_subtask(
            subtask_id=3,
            evaluator_name="LayeredExpenseFromReceipt",
            params={
                "amount": breakfast_amount,
                "name": breakfast_name,
                "category": breakfast_category,
                "note": breakfast_note,  # Note evaluation should be optional
                "receipt_file": "breakfast_receipt.png",
                "check_note": False,  # ⚡ Do not check the note field; only check title, amount, and category  
            },
            weight=1.0,
            time="09:30",
            narration=f"After class, {student_name} had breakfast. The receipt is saved in the Download folder.",
            user_instruction=f"Check the breakfast receipt in Files (Download folder) and record the expense in Pro Expense (check title, amount, and category from the image). ",
            user_instruction_L0=f"Open Files app, go to Download folder, find 'breakfast_receipt.png' to check the amount ({breakfast_amount:.2f}). "
                               f"Then open Pro Expense and add an expense: name '{breakfast_name}', amount ${breakfast_amount:.2f}, category '{breakfast_category}'.",
            user_instruction_L1=f"Check the breakfast receipt in Download and record in Pro Expense.",
            user_instruction_L2="Record my breakfast expense from the receipt.",
            max_steps=30,
            requires_answer=False,
        )
        
        # ========== Task 4: Organize audio recording and move location (unchanged) ==========  
        recording_name = st4.get('recording_name', f'{topic}_Lecture')
        target_folder = st4.get('target_folder', 'Documents/Lectures')
        
        self.add_subtask(
            subtask_id=4,
            evaluator_name="LayeredCrossAppAudioRecorderFiles",
            params={
                "expected_filename": recording_name,
                "target_folder": target_folder,
            },
            weight=1.0,
            time="12:00",
            narration=f"To review later, {student_name} needs to organize the recording file.",
            user_instruction=f"Rename my morning audio recording to '{recording_name}'. "
                            f"Then move this file to the '{target_folder}' folder in Files. Create the folder if needed.",
            user_instruction_L0=f"Open Audio Recorder, find the most recent recording, and rename it to '{recording_name}'. "
                               f"Then open Files, navigate to the recording location, and move the renamed file to '{target_folder}'. "
                               f"Create the folder structure if it doesn't exist.",
            user_instruction_L1=f"Rename the latest recording to '{recording_name}' and move it to '{target_folder}'.",
            user_instruction_L2="Organize today's lecture recording for later review.",
            reset_user_instruction=f"Open Audio Recorder, record a short audio clip and save it as '{recording_name}'. "
                                  f"Then open Files, navigate to where the recording was saved, and move the file to '{target_folder}'. "
                                  f"Create the folder if it doesn't exist.",
            max_steps=35,
            requires_answer=False,
        )
        
        # ========== Task 5: Modify seminar time and notify ==========  
        seminar_title = st5.get('seminar_title', event_title)
        original_hour = st5.get('original_hour', 14)
        original_minute = st5.get('original_minute', 0)
        new_hour = st5.get('new_hour', 15)
        new_minute = st5.get('new_minute', 0)
        duration_minutes = st5.get('duration_minutes', 90)
        
        # Prepare participant information  
        attendees_for_sms = [{"name": m['name'], "number": m['phone']} for m in seminar_members]
        
        self.add_subtask(
            subtask_id=5,
            evaluator_name="LayeredCrossAppMeetingUpdateNotify",
            params={
                "update_type": "time",  # 🆕 Specify update type as time  
                "event_title": seminar_title,
                "original_hour": original_hour,
                "original_minute": original_minute,
                "new_hour": new_hour,
                "new_minute": new_minute,
                "duration_minutes": duration_minutes,
                "location": seminar_location,
                "attendees": attendees_for_sms,
                # ✅ Fix: Time-change task only needs to include the new time, not the location (location unchanged)  
                "message_must_contain": [f"{new_hour}:{new_minute:02d}"],
            },
            weight=1.0,
            time="13:30",
            narration=f"The advisor wants to postpone the seminar. {student_name} needs to update the calendar and notify everyone.",
            user_instruction=f"The seminar we discussed this morning needs to be moved to {new_hour}:{new_minute:02d}. "
                            f"Update it in the calendar, then use Simple SMS Messenger to notify all participants about the new time.",
            user_instruction_L0=f"Open Simple Calendar Pro, find today's event '{seminar_title}' at {original_hour}:{original_minute:02d}, "
                               f"change the start time to {new_hour}:{new_minute:02d}. "
                               f"Then open Simple SMS Messenger and send messages to all participants ({', '.join([m['name'] for m in seminar_members])}) "
                               f"informing them of the new time.",
            user_instruction_L1=f"Move the seminar we discussed this morning to {new_hour}:{new_minute:02d} and notify everyone via Simple SMS Messenger.",
            user_instruction_L2="The seminar time changed, update it and let everyone know.",
            max_steps=45,
            requires_answer=False,
        )
        
        # ========== Task 6: Shopping (unchanged) ==========  
        product_sku = st6.get('product_sku', 'B00J2FALDK')
        product_name = st6.get('product_name', 'SanDisk Cruzer Glide 16GB')
        
        self.add_subtask(
            subtask_id=6,
            evaluator_name="LayeredShoppingPurchaseProduct",
            params={
                "product_sku": product_sku,
                "product_name_keywords": [product_name.split()[0]],
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
            time="16:00",
            narration=f"After the seminar, {student_name} needs to order USB drives for data backup.",
            user_instruction=f"On the current webpage (ignore the internet access), clear my cart, add the '{product_name}' to my cart and place an order.",
            user_instruction_L0=f"On the current webpage (ignore the internet access), clear my cart first, then add the '{product_name}' to my cart and place an order.",
            user_instruction_L1=f"On the current webpage (ignore the internet access), place an order for the '{product_name}'.",
            user_instruction_L2=f"On the current webpage (ignore the internet access), buy one {product_name}.",
            max_steps=35,
            requires_answer=False,
        )
        
        # ========== Task 7: Exercise preparation - playlist + OpenTracks ==========  
        playlist_name = st7.get('playlist_name', 'Workout Mix')
        min_duration = st7.get('min_duration_minutes', 30)
        available_songs = st7.get('available_songs', [])
        
        self.add_subtask(
            subtask_id=7,
            evaluator_name="LayeredCrossAppMusicPlaylistTrack",
            params={
                "playlist_name": playlist_name,
                "min_duration_minutes": min_duration,
                "available_songs": available_songs,
                "shuffle_play": True,
                "start_tracking": True,
            },
            weight=1.0,
            time="17:30",
            narration=f"{student_name} wants to exercise. Need to create a workout playlist (at least {min_duration} minutes) and start tracking.",
            user_instruction=f"Create a {min_duration}+ minute playlist '{playlist_name}', shuffle play it, then start OpenTracks.",
            user_instruction_L0=f"Open Retro Music, create a new playlist named '{playlist_name}', add songs until the total duration is at least {min_duration} minutes, "
                               f"and start shuffle playback. Then open OpenTracks and start recording activity.",
            user_instruction_L1=f"Create a {min_duration}+ minute playlist '{playlist_name}', shuffle play it, then start OpenTracks.",
            user_instruction_L2="Prepare for exercise with music and tracking.",
            max_steps=45,
            requires_answer=False,
        )
        
        # ========== Task 8: Aggregate SMS replies into Markor ==========  
        progress_replies = st8.get('progress_replies', [])
        distractor_messages = st8.get('distractor_messages', [])
        summary_file = st8.get('summary_file', 'DiscussionSummary.md')
        
        # Construct expected content keywords (from progress replies)  
        required_keywords = []
        for reply in progress_replies:
            # Extract keywords: sender name + content keywords  
            required_keywords.append(reply['from'].split()[0].lower())  # First part of the name
            # Extract some keywords from the content  
            content_lower = reply['content'].lower()
            if 'paper' in content_lower or 'research' in content_lower:
                required_keywords.append('paper')
            if 'review' in content_lower or 'section' in content_lower:
                required_keywords.append('review')
            if 'code' in content_lower or 'implementation' in content_lower:
                required_keywords.append('code')
        
        # Deduplicate  
        required_keywords = list(set(required_keywords))
        
        # Construct distractor keywords (should not appear in the summary)  
        distractor_keywords = []
        for msg in distractor_messages:
            distractor_keywords.append(msg['from'].split()[0].lower())
            # Extract keywords from the content  
            if 'lunch' in msg['content'].lower():
                distractor_keywords.append('lunch')
            if 'book' in msg['content'].lower():
                distractor_keywords.append('book')
        
        # Deduplicate  
        distractor_keywords = list(set(distractor_keywords))
        
        self.add_subtask(
            subtask_id=8,
            evaluator_name="LayeredMarkorSMSSummary",
            params={
                "file_name": summary_file,
                "required_keywords": required_keywords,
                "distractor_keywords": distractor_keywords,
                "progress_replies": progress_replies,
                "distractor_messages": distractor_messages,
            },
            weight=1.0,
            time="19:00",
            narration=f"After the discussion, everyone replied with their progress via SMS. {student_name} needs to compile them into a document.",
            user_instruction=f"Check Simple SMS Messenger for the progress replies from the team in today's seminar. "
                            f"Create a new file '{summary_file}' in Markor and summarize what each person reported.",
            user_instruction_L0=f"Open Simple SMS Messenger, read the messages from {', '.join([r['from'] for r in progress_replies])}. "
                               f"Then open Markor, create '{summary_file}', and write a summary of each person's reported progress.",
            user_instruction_L1=f"Check SMS for team progress and summarize it in Markor as '{summary_file}'.",
            user_instruction_L2="Compile the team's progress reports from SMS.",
            max_steps=35,
            requires_answer=False,
        )
        
        # ========== Task 9: Create Calendar Summary Document (merged original Task 9 and Task 10, supports partial scoring) ==========  
        doc_file_name = st9.get('file_name', 'DailySchedule.md')
        seminar_title_9 = st9.get('seminar_title', event_title)
        seminar_time_9 = st9.get('seminar_time', f'{new_hour}:{new_minute:02d}')
        seminar_location_9 = st9.get('seminar_location', seminar_location)
        breakfast_amount_9 = st9.get('breakfast_amount', breakfast_amount)
        recording_name_9 = st9.get('recording_name', recording_name)
        
        # Build meeting keyword list (for evaluation)  
        meeting_keywords = [
            seminar_title_9.split(':')[0],  # Course name  
            seminar_time_9,  # Time  
            seminar_location_9,  # Location  
        ]
        
        self.add_subtask(
            subtask_id=9,
            evaluator_name="LayeredMarkorCreateDailySummaryPartial",
            params={
                "file_name": doc_file_name,
                "meeting_keywords": meeting_keywords,
                "breakfast_amount": breakfast_amount_9,
                "recording_name": recording_name_9,
            },
            weight=1.0,
            time="21:00",
            narration=f"Before sleep, {student_name} wants to record today's key events.",
            user_instruction=f"Create a new file '{doc_file_name}' in Markor. Record today's schedule including: "
                            f"(1) Today's meeting info (including the title, time, location), "
                            f"(2) Breakfast expense, "
                            f"(3) Today morning's recording file name.",
            user_instruction_L0=f"Open Markor and create '{doc_file_name}'. Write: "
                               f"(1) Today's meeting info: {seminar_title_9}, {seminar_time_9}, {seminar_location_9}; "
                               f"(2) Breakfast expense: ${breakfast_amount_9:.2f}; "
                               f"(3) Recording file: '{recording_name_9}'.",
            user_instruction_L1=f"Create '{doc_file_name}' with today's meeting info, breakfast expense, and recording file name.",
            user_instruction_L2="Record today's important events.",
            max_steps=35,
            requires_answer=False,
        ) 
    
    def initialize_subtask(self, subtask_idx: int, env):
        """
        Subtask initialization logic
        
        Execute corresponding initialization immediately before starting a specific subtask
        
        ⚠️ In Reset mode: directly invoke super(), handled by _reset_initialize_subtask()
        📚 In Scenario mode: perform scenario-specific preprocessing, then invoke super()
        """
        subtask = self.subtasks[subtask_idx]
        subtask_id = subtask['subtask_id']
        
        # ⚡ Reset mode: skip scenario-specific preprocessing  
        # All initialization is handled by _reset_initialize_subtask() within super()  
        if self.reset_mode:
            super().initialize_subtask(subtask_idx, env)
            return
        
        # ---- Executed only in Scenario mode ----  
        
        # Task 8: SMS Summary - requires sending progress replies and distractors  
        if subtask_id == 8:
            logging.warning("   💬 Task 8 Initialization - Setting up SMS progress replies and distractors..."  )
            self._setup_sms_for_task8(env)
        
        # Call parent class method (handles time setup, etc.)  
        super().initialize_subtask(subtask_idx, env)
    
    def initialize_task(self, env):
        """
        Batch initialization at scenario startup
        
        Pre-configure the environment for all subtasks:
        - Clear Clock and Calendar data
        - Configure Audio Recorder permissions
        - Create breakfast receipt image (Task 3)
        - Clean target folder (Task 4)
        - Create contacts (Task 5)
        - Clear SMS (SMS for Task 8 is created during subtask initialization)
        - Prepare audio files (Task 7)
        - Clean Markor, Expense, etc.
        """
        super().initialize_task(env)
        
        # ⚡ Reset mode: skip batch initialization; each task is independently initialized in _reset_initialize_subtask()  
        if self.reset_mode:
            logging.info("⚡ Reset Mode: Skipping batch initialization")
            logging.info("   Each task will be initialized independently before execution")
            # Ensure timezone is UTC only (required by nearly all tasks)  
            self._ensure_utc_timezone(env)
            return
        
        logging.info("🔧 Performing batch initialization for Scenario C environment..."  )
        
        # ⚠️ Critical fix: First ensure timezone is UTC during scenario initialization  
        # This resolves incorrect time display in Calendar  
        from scendroid.env import adb_utils
        logging.info("   🌍 Ensuring device timezone is UTC..."  )
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
            
            logging.info("   ✅ Timezone confirmed as UTC"  )
        except Exception as e:
            logging.warning(f"   ⚠️  Could not set timezone: {e}")
        
        try:
            # 1. Clear Clock data  
            self._cleanup_clock(env)
            
            # 2. Clear and configure Calendar (Task 1, 5)  
            self._setup_calendar(env)
            
            # 3. Clear and configure Audio Recorder (Task 2, 4)
            self._setup_audiorecorder(env)
            
            # 4. Clean Expense data (Task 3)  
            self._cleanup_expense(env)
            
            # 5. Clean target folder (Task 4)  
            self._cleanup_target_folders(env)
            
            # 6. Clean SMS database (do not refresh UI; refresh collectively later)  
            self._cleanup_sms_database(env)
            
            # 7. Prepare music files (Task 7) – will call clear_internal_storage to delete all files  
            self._setup_music(env)
            
            # 8. Configure OpenTracks (Task 7)  
            self._setup_opentracks(env)
            
            # 9. Clean Markor (Task 8, 9, 10)  
            self._cleanup_markor(env)
            
            # 10. Create breakfast receipt image (Task 3) – must be done after clear_internal_storage!  
            self._create_breakfast_receipt(env)
            
            # 11. Create contacts (Task 5) – includes verification and remediation logic  
            self._setup_contacts(env)
            
            # 12. ✅ Finally refresh SMS UI (after contact creation, to prevent cache residue)  
            self._refresh_sms_ui(env)
            
            # Note: Chrome login is deferred to Task 6 (refer to Scenario A for higher reliability)  
            # Do not clean Chrome during batch initialization to avoid interfering with subsequent CDP connections  
            
            logging.info("✅ Batch initialization completed"  )
            
        except Exception as e:
            logging.error(f"❌ Batch initialization failed: {e}")
            import traceback
            logging.error(traceback.format_exc())
        
        finally:
            # Return to home screen  
            try:
                from scendroid.env import adb_utils
                import time
                
                logging.info("   🏠 Returning to home screen...")
                adb_utils.press_home_button(env.controller)
                time.sleep(1.5)
            except Exception as e:
                logging.warning(f"   ⚠️ Failed to return to home: {e}")
    
    def _cleanup_clock(self, env):
        """Clean Clock data"""  
        logging.info("   ⏰ Clearing Clock data...")
        from scendroid.apps.clock import utils as clock_utils
        clock_utils.close_clock_app(env)
    
    def _setup_calendar(self, env):
        """Configure Calendar – only clean calendar data; events are created by the agent in Task 1"""  
        logging.info("   📅 Setting up Calendar...")
        
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.env import adb_utils
        import time
        
        try:
            # ✅ Fix 1: Use clear_app_data to fully reset the Calendar app (including view settings)  
            adb_utils.clear_app_data("com.simplemobiletools.calendar.pro", env.controller)
            time.sleep(1.0)
            
            # Launch Calendar once and return, ensuring app initialization completes (skip first-launch wizard)  
            adb_utils.start_activity(
                "com.simplemobiletools.calendar.pro/.activities.MainActivity",
                None,  # extra_args
                env.controller
            )
            time.sleep(2.0)
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            
            # ✅ Fix 2: Reset timezone after clearing app data (to prevent timezone reset)  
            logging.info("      🌍 Reconfirm device timezone is UTC..."  )
            adb_utils.set_root_if_needed(env.controller)
            
            adb_utils.issue_generic_request(
                ['shell', 'service', 'call', 'alarm', '3', 's16', 'UTC'],
                env.controller
            )
            
            adb_utils.issue_generic_request(
                ['shell', 'setprop', 'persist.sys.timezone', 'UTC'],
                env.controller
            )
            
            # Clean calendar events database  
            calendar_utils.clear_calendar_db(env)
            
            logging.info("   ✅ Calendar cleared (event will be created by agent in Task 1)")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Calendar setup failed: {e}")
    
    def _setup_audiorecorder(self, env):
        """Configure Audio Recorder permissions (fully refer to scenario_d implementation)"""  
        logging.info("   🎤 Setting up Audio Recorder...")
        
        from scendroid.env import adb_utils, device_constants, tools
        import time
        
        try:
            # 1. Clean external storage audio recording files for Audio Recorder  
            logging.info("      Clearing external storage recordings...")
            audio_dirs = [
                f"{device_constants.EMULATOR_DATA}AudioRecorder",
                f"{device_constants.EMULATOR_DATA}Recordings",
                f"{device_constants.EMULATOR_DATA}Music",
            ]
            for audio_dir in audio_dirs:
                adb_utils.issue_generic_request([
                    'shell', 'rm', '-rf', audio_dir
                ], env.controller)
            
            # 2. Use pm clear to completely wipe app data  
            adb_utils.clear_app_data(
                "com.dimowner.audiorecorder",
                env.controller,
            )
            time.sleep(0.5)
            
            # 3. Grant permissions  
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
            
            # 4. Launch the app to handle onboarding UI  
            adb_utils.issue_generic_request([
                "shell", "monkey",
                "-p", "com.dimowner.audiorecorder",
                "-c", "android.intent.category.LAUNCHER",
                "1",
            ], env.controller)
            time.sleep(2.0)
            
            # 5. Tap onboarding buttons (multiple taps required)  
            try:
                controller = tools.AndroidToolController(env=env.controller)
                
                # First round: GET STARTED button  
                for btn_text in ['GET STARTED', 'Get Started', 'START', 'Start']:
                    try:
                        controller.click_element(btn_text)
                        logging.info(f"      ✅ Clicked '{btn_text}'")
                        time.sleep(1.5)
                        break
                    except:
                        pass
                
                # Second round: APPLY/OK button (confirmation of settings)  
                for btn_text in ['APPLY', 'Apply', 'OK', 'Done']:
                    try:
                        controller.click_element(btn_text)
                        logging.info(f"      ✅ Clicked '{btn_text}'")
                        time.sleep(1.0)
                        break
                    except:
                        pass
            except Exception as e:
                logging.warning(f"      ⚠️ Button click failed: {e}")
            
            # 6. Close the app
            adb_utils.close_app('audio recorder', env.controller)
            time.sleep(0.5)
            
            logging.info("   ✅ Audio Recorder setup complete")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Audio Recorder setup failed: {e}")
    
    def _create_breakfast_receipt(self, env):
        """Create breakfast receipt image (fully reuse scenario_d's _create_trip_info_image method)
        
        Save to the Download directory, using the same logic as scenario_d's Conference_Trip_Info.png
        """
        logging.info("   🧾 Creating breakfast receipt image...")
        
        from scendroid.task_evals.utils import user_data_generation
        from scendroid.utils import file_utils
        from scendroid.env import device_constants, adb_utils
        from PIL import Image, ImageDraw
        import os
        import tempfile
        import time
        
        try:
            # Get parameters
            st3 = self.generated_params.get('subtask_3', {})
            amount = st3.get('amount', 6.80)
            name = st3.get('name', 'Campus Breakfast')
            note = st3.get('note', 'Cash')
            
            # Construct receipt text (using the same format characters as scenario_d)
            receipt_text = f"""
═══════════════════════════════════
       CAMPUS CAFETERIA
           RECEIPT
═══════════════════════════════════

Date: January 7, 2026
Time: 09:15 AM

───────────────────────────────────
Item                          Price
───────────────────────────────────

{name}                    ${amount:.2f}

───────────────────────────────────
Subtotal:                  ${amount:.2f}
Tax:                        $0.00
───────────────────────────────────
TOTAL:                     ${amount:.2f}

Payment Method: {note}

═══════════════════════════════════
     Thank you for dining!
═══════════════════════════════════
"""
            
            # Use _draw_text to generate the image
            image = user_data_generation._draw_text(receipt_text.strip(), font_size=18)
            
            # Save to a temporary file
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "breakfast_receipt.png")
            image.save(temp_path)
            
            # Copy to the device's Download directory
            remote_path = f"{device_constants.DOWNLOAD_DATA}/breakfast_receipt.png"
            file_utils.copy_data_to_device(temp_path, remote_path, env.controller)
            
            # Wait for file transfer to complete
            time.sleep(0.5)
            
            # Clean up temporary files
            try:
                os.remove(temp_path)
            except:
                pass
            
            # Scan media library
            action = 'android.intent.action.MEDIA_SCANNER_SCAN_FILE'
            data_uri = f'file://{remote_path}'
            adb_utils.send_android_intent(
                command='broadcast', action=action,
                env=env.controller, data_uri=data_uri
            )
            time.sleep(1.0)
            
            logging.info(f"   ✅ Receipt created: {remote_path}")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Receipt creation failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _cleanup_expense(self, env):
        """Clean up Expense data"""
        logging.info("   💰 Clearing Expense data...")
        
        from scendroid.task_evals.utils import sqlite_utils
        from scendroid.env.setup_device import apps
        
        _DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
        _TABLE = "expense"
        _APP_NAME = "pro expense"
        
        try:
            if not sqlite_utils.table_exists(_TABLE, _DB_PATH, env):
                logging.info("      Expense database not found, initializing...")
                apps.ExpenseApp.setup(env)
            
            sqlite_utils.delete_all_rows_from_table(
                _TABLE, _DB_PATH, env, _APP_NAME
            )
            logging.info("   ✅ Expense data cleared")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Expense clear failed: {e}")
    
    def _cleanup_target_folders(self, env):
        """Clean up target folder"""
        logging.info("   📁 Clearing target folders...")
        
        from scendroid.env import device_constants, adb_utils
        import time
        
        st4 = self.generated_params.get('subtask_4', {})
        folder = st4.get('target_folder', 'Documents/Lectures')
        
        # Extract top-level directory
        system_dirs = {'Documents', 'Download', 'DCIM', 'Pictures', 'Music', 'Movies'}
        folders_to_clean = set()
        
        all_paths = [folder, 'Documents/Lectures', 'Study/Recordings', 'Research/Audio']
        
        for path in all_paths:
            top_dir = path.split('/')[0]
            if top_dir in system_dirs:
                folders_to_clean.add(path)
            else:
                folders_to_clean.add(top_dir)
        
        for folder_path in folders_to_clean:
            try:
                full_path = f"{device_constants.EMULATOR_DATA}/{folder_path}"
                adb_utils.issue_generic_request([
                    'shell', 'rm', '-rf', full_path
                ], env.controller)
                logging.info(f"      ✅ Cleared: {full_path}")
            except Exception as e:
                logging.warning(f"      ⚠️ Failed to clear {folder_path}: {e}")
        
        time.sleep(0.5)
        logging.info("   ✅ Target folders cleared")
    
    def _setup_contacts(self, env):
        """Create contacts (for Task 5) — retry mechanism with verification"""
        logging.info("   👥 Creating contacts...")
        
        from scendroid.utils import contacts_utils
        from scendroid.env import adb_utils
        import time
        
        try:
            # Clear existing contacts
            contacts_utils.clear_contacts(env.controller)
            time.sleep(1.0)
            
            # Get parameters
            shared = self.generated_params.get('shared', {})
            seminar_members = shared.get('seminar_members', [])
            distractor_contacts = shared.get('distractor_contacts', [])
            
            # Add all contacts
            all_contacts = seminar_members + distractor_contacts
            
            logging.info(f"   📞 Adding {len(all_contacts)} contacts (with retry)...")
            
            successfully_added = 0
            for idx, contact in enumerate(all_contacts, 1):
                name = contact.get('name')
                phone = contact.get('phone')
                if not name or not phone:
                    continue
                
                # ✅ Add retry mechanism (maximum 2 attempts)
                success = False
                for attempt in range(2):
                    try:
                        if attempt > 0:
                            logging.info(f"      ↻ Retry '{name}' (attempt {attempt + 1})")
                        
                        # ✅ Critical: Return to home screen before each add (to ensure stable state)
                        adb_utils.press_home_button(env.controller)
                        time.sleep(1.5)
                        
                        # ✅ Critical: Use longer ui_delay (2.0 seconds, refer to Scenario A)
                        contacts_utils.add_contact(
                            name, phone, env.controller, ui_delay_sec=2.0
                        )
                        successfully_added += 1
                        logging.info(f"      ✅ [{idx}/{len(all_contacts)}] Added: {name} ({phone})")
                        
                        # ✅ Critical: Wait longer after adding (2 seconds, to ensure database synchronization)
                        time.sleep(2.0)
                        success = True
                        break
                    except Exception as e:
                        logging.warning(f"      ⚠️ Attempt {attempt + 1} failed for {name}: {e}")
                        if attempt < 1:  # If not the final attempt, wait and retry
                            time.sleep(2.0)
                
                if not success:
                    logging.error(f"      ❌ Failed to add {name} after 2 attempts!")
            
            logging.info(f"   Initial result: {successfully_added}/{len(all_contacts)} added")
            
            # ✅ New: Wait for contact database synchronization (refer to line 859 in Scenario A)
            logging.info("   ⏳ Waiting for contacts to sync...")
            time.sleep(3.0)
            
            # ✅ New: Verify that contacts were actually added successfully (refer to lines 863–880 in Scenario A)
            try:
                actual_contacts = contacts_utils.list_contacts(env.controller)
                logging.info("   " + "=" * 50)
                logging.info(f"   📋 Contact verification:")
                logging.info(f"      Database contains: {len(actual_contacts)} contacts")
                
                # Check which required contacts (seminar_members) were actually added successfully
                missing_required = []
                found_required = []
                
                for required in seminar_members:
                    required_name = required['name']
                    required_phone = required['phone'].replace('-', '').replace(' ', '')
                    
                    found = False
                    for actual in actual_contacts:
                        actual_phone = actual.number.replace('-', '').replace(' ', '')
                        # Partial name match is sufficient (to handle cases like "Prof. Smith")
                        if (required_name.lower() in actual.name.lower() or 
                            actual.name.lower() in required_name.lower()) and \
                           required_phone in actual_phone:
                            found = True
                            found_required.append(required_name)
                            break
                    
                    if not found:
                        missing_required.append(required_name)
                
                logging.info(f"      ✅ Found {len(found_required)}/{len(seminar_members)} required contacts:")
                for name in found_required:
                    logging.info(f"         ✓ {name}")
                
                if missing_required:
                    logging.error("   " + "=" * 50)
                    logging.error(f"   ❌ CRITICAL: {len(missing_required)} required contacts MISSING!")
                    for name in missing_required:
                        logging.error(f"      ✗ {name}")
                    logging.error("   💡 Possible reasons:")
                    logging.error("      1. Contact name contains special characters (e.g., 'Prof.')")
                    logging.error("      2. UI interaction timeout (SAVE button not clicked)")
                    logging.error("      3. First contact added before Contacts app fully initialized")
                    logging.error("   " + "=" * 50)
                    
                    # 🆕 Remediation: Attempt to re-add missing contacts
                    logging.warning(f"   🔧 Attempting to re-add {len(missing_required)} missing contacts...")
                    
                    for missing_name in missing_required:
                        # Find corresponding contact information
                        contact_info = None
                        for member in seminar_members:
                            if member['name'] == missing_name:
                                contact_info = member
                                break
                        
                        if contact_info:
                            logging.warning(f"      ↻ Re-adding '{contact_info['name']}'...")
                            try:
                                # Return to home screen
                                adb_utils.press_home_button(env.controller)
                                time.sleep(2.0)
                                
                                # Use longer delay (3 seconds)
                                contacts_utils.add_contact(
                                    contact_info['name'], 
                                    contact_info['phone'], 
                                    env.controller,
                                    ui_delay_sec=3.0  # Longer delay
                                )
                                logging.warning(f"      ✅ Re-added: {contact_info['name']}")
                                time.sleep(3.0)
                            except Exception as e:
                                logging.error(f"      ❌ Re-add failed: {e}")
                    
                    # Re-verify  
                    logging.warning("   🔍 Re-verifying contacts...")
                    time.sleep(2.0)
                    
                    actual_contacts_retry = contacts_utils.list_contacts(env.controller)
                    missing_after_retry = []
                    
                    for required in seminar_members:
                        required_name = required['name']
                        required_phone = required['phone'].replace('-', '').replace(' ', '')
                        
                        found = False
                        for actual in actual_contacts_retry:
                            actual_phone = actual.number.replace('-', '').replace(' ', '')
                            if (required_name.lower() in actual.name.lower() or 
                                actual.name.lower() in required_name.lower()) and \
                               required_phone in actual_phone:
                                found = True
                                break
                        
                        if not found:
                            missing_after_retry.append(required_name)
                    
                    if missing_after_retry:
                        logging.error(f"   ❌ Still missing after retry: {missing_after_retry}")
                        logging.error(f"   ⚠️⚠️⚠️ Task 5 SMS evaluation WILL FAIL!")
                    else:
                        logging.warning(f"   ✅ All contacts recovered after retry!")
                else:
                    logging.info("   ✅ All required contacts verified successfully!")
                
                logging.info("   " + "=" * 50)
                
            except Exception as e:
                logging.warning(f"   ⚠️ Contact verification failed: {e}")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Contacts setup failed: {e}")
    
    def _cleanup_sms_database(self, env):
        """Clean the SMS database (without refreshing the UI)"""  
        logging.info("   💬 Clearing SMS database...")
        
        from scendroid.task_evals.common_validators import sms_validators
        import time
        
        try:
            # Clear only the SMS database  
            sms_validators.clear_sms_and_threads(env.controller)
            time.sleep(1.0)
            logging.info("   ✅ SMS database cleared")
            
        except Exception as e:
            logging.warning(f"   ⚠️ SMS database cleanup failed: {e}")
    
    def _refresh_sms_ui(self, env):
        """Refresh the SMS app UI to prevent residual historical data (refer to lines 1220–1256 in Scenario A)
        
        ⚠️ This method must be invoked after all contacts have been created!
        """
        logging.info("   📱 Refreshing SMS app UI...")
        
        from scendroid.env import adb_utils
        import time
        
        try:
            # Step 1: Force-stop the SMS app (to clear UI cache)  
            adb_utils.close_app("simple sms", env.controller)
            time.sleep(1.0)
            
            # Step 2: Launch the SMS app (to force UI refresh)  
            logging.info("      📱 Launching the SMS app..."  )
            adb_utils.start_activity(
                "com.simplemobiletools.smsmessenger/.activities.MainActivity",
                None,
                env.controller
            )
            time.sleep(2.0)  # Wait for the app to fully load  
            
            # Step 3: Press the BACK key 4 times to ensure returning to the home screen (conversation → contacts → home screen → exit)  
            logging.info("      📱 Pressing the BACK key to return to the home screen..."  )
            for _ in range(4):  # Press the BACK key multiple times to ensure returning to the home screen  
                adb_utils.issue_generic_request(
                    ["shell", "input", "keyevent", "KEYCODE_BACK"],
                    env.controller
                )
                time.sleep(0.3)
            
            # Step 4: Press the HOME key to exit to the desktop  
            logging.info("      📱 Pressing the HOME key to exit to the desktop..."  )
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
            
            logging.info("   ✅ SMS app UI refreshed (force stop + launch + BACK key + HOME key)"  )
            
        except Exception as e:
            logging.warning(f"   ⚠️ SMS UI refresh failed: {e}")
    
    def _setup_sms_for_task8(self, env):
        """Initialize progress reply SMS messages and distractors for Task 8 (invoked during subtask initialization)
        
        ⚠️ Important: Do not clear existing SMS!
        - The Task 5 user has already sent notification SMS messages to four attendees
        - Task 8 must retain those SMS messages and add attendees' replies
        - This ensures the SMS conversation window displays the complete conversation history
        """
        logging.warning("=" * 60)
        logging.warning("💬 Setting up SMS replies and distractors for Task 8...")
        logging.warning("=" * 60)
        
        from scendroid.task_evals.common_validators import sms_validators
        from scendroid.env import adb_utils
        import time
        
        try:
            # ✅ Fix: Do NOT clear existing SMS! Retain notifications sent in Task 5  
            logging.warning("   Step 1: Checking existing SMS...")
            
            # 🆕 Display current SMS count (from Task 5)  
            try:
                response_sent = adb_utils.issue_generic_request(
                    "shell content query --uri content://sms/sent".split(),
                    env.controller
                )
                sent_messages = sms_validators._decode_messages_from_response(response_sent)
                logging.warning(f"      ℹ️  Found {len(sent_messages)} sent messages (from Task 5)")
                
                # ✅ Directly use ADB commands to retrieve incoming SMS (avoid instantiating SimpleSMSSendSms)  
                response_inbox = adb_utils.issue_generic_request(
                    "shell content query --uri content://sms/inbox".split(),
                    env.controller
                )
                inbox_output = response_inbox.generic.output.strip()
                received_count_before = len([line for line in inbox_output.split('\n') if line.strip().startswith('Row:')])
                logging.warning(f"      ℹ️  Found {received_count_before} received messages (before adding replies)")
            except Exception as e:
                logging.warning(f"      ⚠️ Could not check existing SMS: {e}")
            
            # Retrieve parameters  
            st8 = self.generated_params.get('subtask_8', {})
            shared = self.generated_params.get('shared', {})
            progress_replies = st8.get('progress_replies', [])
            distractor_messages = st8.get('distractor_messages', [])
            seminar_members = shared.get('seminar_members', [])
            
            logging.warning(f"   Step 2: Adding {len(progress_replies)} progress replies + {len(distractor_messages)} distractors...")
            logging.warning(f"   📋 Progress replies from team members:")
            for reply in progress_replies:
                logging.warning(f"      - {reply['from']}: \"{reply['content'][:60]}...\"")
            logging.warning(f"   📋 Distractor messages:")
            for distractor in distractor_messages:
                logging.warning(f"      - {distractor['from']}: \"{distractor['content'][:60]}...\"")
            
            # Create phone number mapping  
            name_to_phone = {m['name']: m['phone'] for m in seminar_members}
            
            # 1. Add progress reply SMS (target messages)  
            # ✅ Use text_emulator to simulate others sending SMS to the user  
            progress_count = 0
            for reply in progress_replies:
                from_name = reply['from']
                content = reply['content']
                
                # Retrieve phone number  
                phone = name_to_phone.get(from_name)
                if not phone:
                    # Attempt partial matching  
                    for member in seminar_members:
                        if from_name.split()[0] in member['name']:
                            phone = member['phone']
                            break
                
                if phone:
                    try:
                        # ✅ Critical fix: Use text_emulator to simulate incoming SMS  
                        # Reference: scendroid/apps/sms/evaluators.py line 455  
                        adb_utils.text_emulator(
                            env.controller,
                            phone,  # Sender's phone number  
                            content,  # SMS content  
                        )
                        progress_count += 1
                        logging.warning(f"      ✅ [{progress_count}] Progress SMS from {from_name} ({phone}): \"{content[:50]}...\"")
                        time.sleep(1.0)  # Delay 1 second between each SMS  
                    except Exception as e:
                        logging.error(f"      ❌ Failed to add SMS from {from_name}: {e}")
                else:
                    logging.error(f"      ❌ No phone found for {from_name}")
            
            time.sleep(0.5)
            logging.warning(f"   ✅ Added {progress_count} progress messages")
            
            # 2. Add distractor SMS (irrelevant messages)
            # ✅ Use text_emulator to simulate someone sending an SMS to the user  
            distractor_count = 0
            for distractor in distractor_messages:
                from_name = distractor['from']
                phone = distractor['phone']
                content = distractor['content']
                
                try:
                    # ✅ Critical fix: Use text_emulator to simulate receiving an SMS  
                    adb_utils.text_emulator(
                        env.controller,
                        phone,  # Sender phone number  
                        content,  # SMS content  
                    )
                    distractor_count += 1
                    logging.warning(f"      ✅ [{distractor_count}] Distractor SMS from {from_name} ({phone}): \"{content[:50]}...\"")
                    time.sleep(1.0)  # Wait 1 second between each SMS  
                except Exception as e:
                    logging.error(f"      ❌ Failed to add distractor SMS from {from_name}: {e}")
            
            time.sleep(1.0)
            logging.warning(f"   ✅ Added {distractor_count} distractor messages")
            
            # ✅ Wait for SMS database synchronization (see line 463 in sms/evaluators.py)  
            logging.warning("   ⏳ Waiting for SMS database to sync...")
            time.sleep(3.0)
            
            # 3. Force-refresh the SMS app (follow the correct approach in Scenario A/B)  
            logging.warning("   Step 3: Refreshing SMS app...")
            try:
                # Step 1: Close the SMS app  
                adb_utils.close_app("simple sms", env.controller)
                time.sleep(1.0)
                
                # Step 2: Open the SMS app  
                logging.warning("      📱 Opening SMS app..."  )
                adb_utils.start_activity(
                    "com.simplemobiletools.smsmessenger/.activities.MainActivity",
                    None,
                    env.controller
                )
                time.sleep(2.0)  # Wait for the app to fully load  
                
                # Step 3: Press the BACK key 4 times to ensure returning to the home screen (conversation → contacts → home screen → exit)  
                logging.warning("      📱 Pressing BACK key to return to home screen..."  )
                for _ in range(4):  # Press the BACK key multiple times to ensure returning to the home screen  
                    adb_utils.issue_generic_request(
                        ["shell", "input", "keyevent", "KEYCODE_BACK"],
                        env.controller
                    )
                    time.sleep(0.3)
                
                # Step 4: Press the HOME key to exit to the desktop  
                logging.warning("      📱 Pressing HOME key to exit to desktop..."  )
                adb_utils.press_home_button(env.controller)
                time.sleep(1.0)
                
                logging.warning("   ✅ SMS app refreshed (force stop + open + BACK key + HOME key)"  )
            except Exception as e:
                logging.warning(f"   ⚠️ Failed to refresh SMS app: {e}")
            
            # 🆕 Verification: Display the final SMS count  
            logging.warning("   Step 4: Verifying final SMS count...")
            try:
                # ✅ Directly use ADB command to retrieve received SMS  
                response_inbox_final = adb_utils.issue_generic_request(
                    "shell content query --uri content://sms/inbox".split(),
                    env.controller
                )
                inbox_output_final = response_inbox_final.generic.output.strip()
                received_count = len([line for line in inbox_output_final.split('\n') if line.strip().startswith('Row:')])
                
                response_sent_final = adb_utils.issue_generic_request(
                    "shell content query --uri content://sms/sent".split(),
                    env.controller
                )
                sent_output_final = response_sent_final.generic.output.strip()
                sent_count = len([line for line in sent_output_final.split('\n') if line.strip().startswith('Row:')])
                
                logging.warning(f"      ℹ️  Final counts:")
                logging.warning(f"         Sent messages: {sent_count} (from Task 5)")
                logging.warning(f"         Inbox messages: {received_count} (replies for Task 8)")
            except Exception as e:
                logging.warning(f"      ⚠️ Could not verify final SMS: {e}")
            
            logging.warning("=" * 60)
            logging.warning(f"✅ Task 8 SMS setup complete!")
            logging.warning(f"   Progress replies added: {progress_count}")
            logging.warning(f"   Distractor messages added: {distractor_count}")
            logging.warning(f"   Total NEW received messages: {progress_count + distractor_count}")
            logging.warning(f"   ")
            logging.warning(f"   💡 Expected SMS conversation view:")
            logging.warning(f"      📤 Sent folder:")
            logging.warning(f"         - 4 messages from Task 5 (meeting time notification)")
            logging.warning(f"      📥 Conversations with team members:")
            logging.warning(f"         - Bob Chen: Your sent + Bob's reply")
            logging.warning(f"         - Sarah Lee: Your sent + Sarah's reply")
            logging.warning(f"         - Tom Wang: Your sent + Tom's reply")
            logging.warning(f"         - Prof. Smith: Your sent (no reply)")
            logging.warning(f"      📥 Conversations with distractors:")
            logging.warning(f"         - Alice Smith: Her message")
            logging.warning(f"         - John Doe: His message")
            logging.warning("=" * 60)
            
        except Exception as e:
            logging.warning(f"   ⚠️ SMS setup failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _setup_music(self, env):
        """Prepare audio files (for Task 7)
        
        Refer to the implementation in scenario_e.py, simplifying the duration generation logic
        """
        logging.info("   🎵 Setting up music files...")
        
        from scendroid.env import device_constants, adb_utils
        from scendroid.task_evals.utils import user_data_generation
        from scendroid.task_evals.single import retro_music
        from scendroid.utils import file_utils
        import random
        import time
        
        try:
            # 1. Clean up existing music data  
            logging.info("      Step 1: Clearing music data...")
            user_data_generation.clear_internal_storage(env)
            retro_music._clear_playlist_dbs(env)
            
            # 2. Retrieve the song list  
            st7 = self.generated_params.get('subtask_7', {})
            available_songs = st7.get('available_songs', [])
            noise_songs = st7.get('noise_songs', [])
            min_duration = st7.get('min_duration_minutes', 30)
            
            all_songs = available_songs + noise_songs
            logging.info(f"      Step 2: Creating {len(all_songs)} music files...")
            
            # 3. Create an MP3 file for each song (2–4 minutes per song)  
            # Ensure the total duration of available_songs is sufficient (16 songs × 2–4 minutes = 32–64 minutes, satisfying the 30-minute requirement)  
            total_duration_ms = 0
            
            for song_name in all_songs:
                # Construct the file path  
                file_path = file_utils.convert_to_posix_path(
                    device_constants.MUSIC_DATA, f"{song_name}.mp3"
                )
                
                # Each song is 2–4 minutes long  
                duration_ms = random.randint(2 * 60 * 1000, 4 * 60 * 1000)
                total_duration_ms += duration_ms
                
                # Create the MP3 file  
                user_data_generation.write_mp3_file_to_device(
                    file_path,
                    env,
                    title=song_name,
                    artist=random.choice(user_data_generation.COMMON_GIVEN_NAMES),
                    duration_milliseconds=duration_ms,
                )
                
                logging.info(f"         🎵 Created: {song_name}.mp3 ({duration_ms // 60000}:{(duration_ms // 1000) % 60:02d})")
            
            # 4. Scan the music directory to update the media library  
            logging.info("      Step 3: Scanning music directory...")
            retro_music._scan_music_directory(env)
            time.sleep(2.0)
            
            # Calculate total duration  
            total_minutes = total_duration_ms / (60 * 1000)
            logging.info(f"   ✅ Music files created ({len(all_songs)} songs, total {total_minutes:.1f} min)")
            logging.info(f"      📋 Available songs ({len(available_songs)}): {available_songs[:3]}...")
            logging.info(f"      📋 Noise songs ({len(noise_songs)}): {noise_songs[:3]}...")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Music setup failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _setup_opentracks(self, env):
        """Configure OpenTracks"""
        logging.info("   🏃 Setting up OpenTracks...")
        
        from scendroid.task_evals.information_retrieval import activity_app_utils
        from scendroid.env import adb_utils, tools
        import time
        
        try:
            # Clean database  
            activity_app_utils.clear_db(env)
            
            # Get package name  
            open_tracks_package = adb_utils.extract_package_name(
                adb_utils.get_adb_activity("open tracks")
            )
            
            # Grant permission  
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
            
            # Launch and close app  
            try:
                adb_utils.launch_app("activity tracker", env.controller)
                time.sleep(3.0)
                
                # Handle Bluetooth permission dialog  
                try:
                    controller = tools.AndroidToolController(env=env.controller)
                    controller.click_element("Allow")
                    logging.info("      ✅ Clicked Bluetooth 'Allow' button")
                except:
                    pass
                
                adb_utils.close_app("activity tracker", env.controller)
            except:
                pass
            
            logging.info("   ✅ OpenTracks setup complete")
            
        except Exception as e:
            logging.warning(f"   ⚠️ OpenTracks setup failed: {e}")
    
    def _cleanup_markor(self, env):
        """Clean Markor data"""  
        logging.info("   📝 Clearing Markor data...")
        
        from scendroid.env import device_constants, adb_utils
        from scendroid.utils import file_utils
        
        try:
            markor_dir = device_constants.MARKOR_DATA
            
            # Ensure directory exists  
            adb_utils.issue_generic_request([
                'shell', 'mkdir', '-p', markor_dir
            ], env.controller)
            
            # Clean directory  
            file_utils.clear_directory(markor_dir, env.controller)
            logging.info("   ✅ Markor data cleared")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Markor clear failed: {e}")
    
    def _cleanup_chrome(self, env):
        """Clear Chrome to ensure proper Shopping login (preparation for Task 6)
        
        ⚠️ Note: Chrome data is not cleared to retain desktop shortcuts and configurations.
        """
        logging.info("   🌐 Cleaning up Chrome for Shopping task...")
        
        from scendroid.env import adb_utils
        import time
        import subprocess
        
        try:
            # Get device name  
            device_name = "emulator-5554"  # Default value  
            try:
                console_port = env.controller._env._coordinator._simulator._config.emulator_launcher.emulator_console_port
                device_name = f"emulator-{console_port}"
                logging.info(f"      Device: {device_name}")
            except:
                pass
            
            # 1. Force stop Chrome  
            logging.info("      Step 1: Force stopping Chrome...")
            adb_utils.close_app("com.android.chrome", env.controller)
            time.sleep(1.0)
            
            # 2. Remove all ADB port forwards (clean up old CDP connections)  
            logging.info("      Step 2: Removing all port forwards...")
            subprocess.run([
                "adb", "-s", device_name,
                "forward", "--remove-all"
            ], check=False, capture_output=True)
            time.sleep(0.5)
            
            # 3. Remove old chrome_devtools_remote socket (if exists)  
            logging.info("      Step 3: Removing old debug socket...")
            subprocess.run([
                "adb", "-s", device_name,
                "shell", "rm", "-f", "/data/local/tmp/chrome_devtools_remote"
            ], check=False, capture_output=True)
            time.sleep(0.5)
            
            # 4. ✅ Delete Chrome command-line configuration file (clear --remote-debugging-port parameter)  
            logging.info("      Step 4: Removing Chrome command line config...")
            subprocess.run([
                "adb", "-s", device_name,
                "shell", "rm", "-f", "/data/local/tmp/chrome-command-line"
            ], check=False, capture_output=True)
            time.sleep(0.5)
            
            # 5. Clear proxy settings (avoid network redirection)  
            logging.info("      Step 5: Clearing proxy settings...")
            subprocess.run([
                "adb", "-s", device_name,
                "shell", "settings", "put", "global", "http_proxy", ":0"
            ], check=False, capture_output=True)
            
            subprocess.run([
                "adb", "-s", device_name,
                "shell", "settings", "delete", "global", "http_proxy"
            ], check=False, capture_output=True)
            
            subprocess.run([
                "adb", "-s", device_name,
                "shell", "settings", "delete", "global", "https_proxy"
            ], check=False, capture_output=True)
            
            logging.info("   ✅ Chrome cleanup complete (data preserved, ready for CDP)")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Chrome cleanup failed: {e}")
    
    # ⚠️ Note: The initialize_subtask method is already defined on lines 705–720 (including SMS initialization for Task 8)  
    # Do not redefine it here, otherwise it will override Task 8's logic!  
    
    def tear_down(self, env):
        """Cleanup after scenario ends"""  
        logging.info("=" * 70)
        logging.info("🧹 Scenario C - Cleanup")
        logging.info("=" * 70)
        
        try:
            from scendroid.env import adb_utils, device_constants
            from scendroid.task_evals.common_validators import sms_validators
            from scendroid.utils import file_utils
            import time
            
            # 1. Stop music playback  
            logging.info("   🎵 Stopping music...")
            try:
                adb_utils.issue_generic_request([
                    'shell', 'input', 'keyevent', 'KEYCODE_MEDIA_STOP'
                ], env.controller)
                adb_utils.close_app("retro music", env.controller)
            except:
                pass
            
            # 2. Stop audio recording  
            logging.info("   🎤 Stopping recording...")
            try:
                adb_utils.close_app("audio recorder", env.controller)
            except:
                pass
            
            # 3. Clean up SMS  
            logging.info("   💬 Clearing SMS...")
            try:
                sms_validators.clear_sms_and_threads(env.controller)
            except:
                pass
            
            # 4. Clean up Markor files  
            logging.info("   📝 Clearing Markor files...")
            try:
                file_utils.clear_directory(device_constants.MARKOR_DATA, env.controller)
            except:
                pass
            
            # 5. Clean up OpenTracks  
            logging.info("   🏃 Clearing OpenTracks...")
            try:
                from scendroid.task_evals.information_retrieval import activity_app_utils
                activity_app_utils.clear_db(env)
            except:
                pass
            
            # 6. Rebuild Shopping container  
            logging.info("   🛒 Rebuilding Shopping container...")
            try:
                from scendroid.apps.shopping.utils import rebuild_shopping_container
                # Pass env to automatically extract console_port  
                rebuild_shopping_container(env=env)
            except Exception as e:
                logging.warning(f"      ⚠️  Container rebuild failed: {e}")
            
            # 7. Close all apps  
            logging.info("   📱 Closing all apps...")
            apps_to_close = [
                "clock", "simple calendar pro", "audio recorder", "pro expense",
                "files", "simple sms messenger", "chrome", "retro music",
                "open tracks sports tracker", "markor"
            ]
            for app in apps_to_close:
                try:
                    adb_utils.close_app(app, env.controller)
                except:
                    pass
            
            time.sleep(1.0)
            adb_utils.press_home_button(env.controller)
            
            logging.info("✅ Scenario C cleanup complete")
            
        except Exception as e:
            logging.error(f"❌ Tear down failed: {e}")
            import traceback
            logging.error(traceback.format_exc())
        
        logging.info("=" * 70)
        
        super().tear_down(env)
    
    # ====================================================================
    # Per-Task Reset Mode: Independent initialization per task  
    # ====================================================================
    
    def _reset_initialize_subtask(self, subtask_idx: int, env):
        """
        Subtask initialization under Per-Task Reset mode.
        
        Before each subtask starts, the following steps occur:
        1. Clear relevant app data.
        2. Create the prerequisites required for that task.
        3. Call the evaluator's initialize_task() (if needed).
        
        Difference from Scenario mode:
        - Scenario mode: Batch-initialize once + prerequisites naturally generated by preceding tasks.
        - Reset mode: Each task is independently initialized, simulating completion of all prior steps for that task.
        """
        subtask = self.subtasks[subtask_idx]
        task_id = subtask['subtask_id']
        
        logging.info(f"   🔧 Per-task reset initialization for Task {task_id}: {subtask['evaluator_name']}")
        
        # Ensure timezone is UTC
        self._ensure_utc_timezone(env)
        
        if task_id == 1:
            self._reset_init_task1_clock_calendar(subtask, env)
        elif task_id == 2:
            self._reset_init_task2_audio_record(env)
        elif task_id == 3:
            self._reset_init_task3_expense_receipt(env)
        elif task_id == 4:
            self._reset_init_task4_audio_organize(env)
        elif task_id == 5:
            self._reset_init_task5_meeting_notify(subtask, env)
        elif task_id == 6:
            self._reset_init_task6_shopping(subtask, env)
        elif task_id == 7:
            self._reset_init_task7_music_exercise(env)
        elif task_id == 8:
            self._reset_init_task8_sms_summary(env)
        elif task_id == 9:
            self._reset_init_task9_daily_summary(env)
        else:
            # Unknown task: use default implementation  
            logging.warning(f"   ⚠️  No custom reset init for Task {task_id}, using evaluator default")
            subtask['evaluator_instance'].initialize_task(env)
    
    def _ensure_utc_timezone(self, env):
        """Ensure device timezone is UTC (shared across multiple tasks)"""  
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
    # ====================================================================
    # Per-Task Reset Mode: Individual Task Initialization Methods
    # ====================================================================
    
    def _reset_init_task1_clock_calendar(self, subtask, env):
        """
        Task 1 (Clock + Calendar):
        Prerequisite: One alarm + one calendar event.
        """
        logging.info("   🔧 Reset Init Task 1: Creating alarm and calendar event")
        
        from scendroid.env import adb_utils
        from datetime import datetime, timedelta
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
        
        # 2. Clear and initialize Calendar (handle first launch)  
        try:
            # Clear app data  
            adb_utils.clear_app_data("com.simplemobiletools.calendar.pro", env.controller)
            time.sleep(1.0)
            
            # Launch Calendar once and return to ensure app initialization completes (skip first-launch wizard)  
            adb_utils.start_activity(
                "com.simplemobiletools.calendar.pro/.activities.MainActivity",
                None,  # extra_args
                env.controller
            )
            time.sleep(2.0)
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            
            # Reset timezone after clearing app data (prevent timezone from being reset)  
            logging.info("      🌍 Reconfirm device timezone is UTC..."  )
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
            from scendroid.task_evals.single.calendar import calendar_utils
            calendar_utils.clear_calendar_db(env)
            
            logging.info("      ✅ Calendar initialized and cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear calendar data: {e}")
        
        # 3. Retrieve parameters  
        params = subtask['params']
        alarm_hour = params.get('alarm_time_hour', 8)
        alarm_minute = params.get('alarm_time_minute', 0)
        alarm_label = params.get('alarm_label', 'Class')
        
        event_title = params.get('event_title', 'Seminar')
        event_hour = params.get('event_hour', 14)
        event_minute = params.get('event_minute', 0)
        event_duration = params.get('event_duration_minutes', 90)
        event_location = params.get('event_location', 'Lab 301')
        event_description = params.get('event_description', '')
        
        # 4. Create alarm  
        cmd = [
            'shell', 'am', 'start',
            '-a', 'android.intent.action.SET_ALARM',
            '--ei', 'android.intent.extra.alarm.HOUR', str(alarm_hour),
            '--ei', 'android.intent.extra.alarm.MINUTES', str(alarm_minute),
            '--es', 'android.intent.extra.alarm.MESSAGE', alarm_label,
        ]
        adb_utils.issue_generic_request(cmd, env.controller)
        time.sleep(3.0)
        adb_utils.press_home_button(env.controller)
        time.sleep(0.5)
        
        logging.info(f"      ✅ Alarm created: {alarm_hour}:{alarm_minute:02d} {alarm_label}")
        
        # 5. Create calendar event  
        # Use adb command to create event  
        base_date = datetime(2026, 1, 14)  # Baseline date for Scenario C  
        event_datetime = base_date.replace(hour=event_hour, minute=event_minute)
        event_end = event_datetime + timedelta(minutes=event_duration)
        
        start_ms = int(event_datetime.timestamp() * 1000)
        end_ms = int(event_end.timestamp() * 1000)
        
        cmd = [
            'shell', 'am', 'start',
            '-a', 'android.intent.action.INSERT',
            '-d', 'content://com.android.calendar/events',
            '--es', 'title', event_title,
            '--el', 'beginTime', str(start_ms),
            '--el', 'endTime', str(end_ms),
            '--es', 'eventLocation', event_location,
            '--es', 'description', event_description,
        ]
        adb_utils.issue_generic_request(cmd, env.controller)
        time.sleep(3.0)
        adb_utils.press_home_button(env.controller)
        time.sleep(0.5)
        
        logging.info(f"      ✅ Calendar event created: {event_title} at {event_hour}:{event_minute:02d}")
    
    def _reset_init_task2_audio_record(self, env):
        """
        Task 2 (Audio Recorder):
        Prerequisite: Clear old audio recordings + handle first-launch onboarding.
        """
        logging.info("   🔧 Reset Init Task 2: Setting up Audio Recorder")
        
        from scendroid.env import adb_utils, device_constants, tools
        import time
        
        try:
            # 1. Clean up external storage audio recording files for Audio Recorder  
            logging.info("      Clearing external storage recordings...")
            audio_dirs = [
                f"{device_constants.EMULATOR_DATA}AudioRecorder",
                f"{device_constants.EMULATOR_DATA}Recordings",
                f"{device_constants.EMULATOR_DATA}Music",
            ]
            for audio_dir in audio_dirs:
                adb_utils.issue_generic_request([
                    'shell', 'rm', '-rf', audio_dir
                ], env.controller)
            
            # 2. Use 'pm clear' to fully clear app data  
            adb_utils.clear_app_data(
                "com.dimowner.audiorecorder",
                env.controller,
            )
            time.sleep(0.5)
            
            # 3. Grant permissions  
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
            
            # 4. Launch app to handle onboarding interface  
            adb_utils.issue_generic_request([
                "shell", "monkey",
                "-p", "com.dimowner.audiorecorder",
                "-c", "android.intent.category.LAUNCHER",
                "1",
            ], env.controller)
            time.sleep(2.0)
            
            # 5. Tap onboarding buttons (multiple taps required)  
            try:
                controller = tools.AndroidToolController(env=env.controller)
                
                # First round: GET STARTED button  
                for btn_text in ['GET STARTED', 'Get Started', 'START', 'Start']:
                    try:
                        controller.click_element(btn_text)
                        logging.info(f"      ✅ Clicked '{btn_text}'")
                        time.sleep(1.5)
                        break
                    except:
                        pass
                
                # Second round: APPLY/OK button (confirmation of settings)  
                for btn_text in ['APPLY', 'Apply', 'OK', 'Done']:
                    try:
                        controller.click_element(btn_text)
                        logging.info(f"      ✅ Clicked '{btn_text}'")
                        time.sleep(1.0)
                        break
                    except:
                        pass
            except Exception as e:
                logging.warning(f"      ⚠️ Button click failed: {e}")
            
            # 6. Close app and return to home  
            adb_utils.close_app('audio recorder', env.controller)
            time.sleep(0.5)
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            
            logging.info("      ✅ Audio Recorder setup complete")
            
        except Exception as e:
            logging.warning(f"      ⚠️ Audio Recorder setup failed: {e}")
    
    def _reset_init_task3_expense_receipt(self, env):
        """
        Task 3 (Expense from Receipt):
        Prerequisite: Create receipt image + clear Expense database (ensuring the app has been initialized).
        """
        logging.info("   🔧 Reset Init Task 3: Creating receipt and setting up Expense")
        
        from scendroid.task_evals.utils import sqlite_utils
        from scendroid.env.setup_device import apps
        from scendroid.env import adb_utils
        import time
        
        # 1. Create receipt image  
        self._create_breakfast_receipt(env)
        
        # 2. Set up and empty Expense database (refer to scenario_d's implementation)  
        _DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
        _TABLE = "expense"
        _APP_NAME = "pro expense"
        
        try:
            # Check if database exists; if not, initialize app  
            if not sqlite_utils.table_exists(_TABLE, _DB_PATH, env):
                logging.info("      Expense database not found, initializing app...")
                apps.ExpenseApp.setup(env)
                logging.info("      ✅ Expense app initialized")
            
            # Empty expense data  
            sqlite_utils.delete_all_rows_from_table(
                _TABLE, _DB_PATH, env, _APP_NAME
            )
            logging.info("      ✅ Expense database cleared")
            
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear Expense data: {e}")
        
        # 3. Return to home
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
            logging.info("      ✅ Returned to home screen")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not return to home: {e}")
    
    def _reset_init_task4_audio_organize(self, env):
        """
        Task 4 (Audio Recorder + Files) - Reset mode:
        
        The Reset instruction is modified to: first record an audio clip using Audio Recorder and save it with the specified name,
        then move the file to the target folder.
        
        Therefore, initialization only requires cleaning the Audio Recorder environment; no dummy audio files need to be pre-created.
        """
        logging.info("   🔧 Reset Init Task 4: Setting up clean Audio Recorder environment")
        
        from scendroid.env import adb_utils, device_constants, tools
        import time
        
        try:
            # 1. Clean up old audio recording files in external storage
            logging.info("      Clearing old recordings...")
            audio_dirs = [
                f"{device_constants.EMULATOR_DATA}AudioRecorder",
                f"{device_constants.EMULATOR_DATA}Recordings",
                f"{device_constants.EMULATOR_DATA}Music",
                device_constants.AUDIORECORDER_DATA,
            ]
            for audio_dir in audio_dirs:
                adb_utils.issue_generic_request([
                    'shell', 'rm', '-rf', audio_dir
                ], env.controller)
            
            # 2. Clear app data (ensure launching from a clean state)
            adb_utils.clear_app_data(
                "com.dimowner.audiorecorder",
                env.controller,
            )
            time.sleep(0.5)
            
            # 3. Grant permissions
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
            
            # 4. Launch the app to handle the onboarding interface, ensuring the app is fully functional
            adb_utils.issue_generic_request([
                "shell", "monkey",
                "-p", "com.dimowner.audiorecorder",
                "-c", "android.intent.category.LAUNCHER",
                "1",
            ], env.controller)
            time.sleep(2.0)
            
            # Click the onboarding button
            try:
                controller = tools.AndroidToolController(env=env.controller)
                
                for btn_text in ['GET STARTED', 'Get Started', 'START', 'Start']:
                    try:
                        controller.click_element(btn_text)
                        logging.info(f"      ✅ Clicked '{btn_text}'")
                        time.sleep(1.5)
                        break
                    except:
                        pass
                
                for btn_text in ['APPLY', 'Apply', 'OK', 'Done']:
                    try:
                        controller.click_element(btn_text)
                        logging.info(f"      ✅ Clicked '{btn_text}'")
                        time.sleep(1.0)
                        break
                    except:
                        pass
            except Exception as e:
                logging.warning(f"      ⚠️ Button click failed: {e}")
            
            # 5. Close the app and return to home
            adb_utils.close_app('audio recorder', env.controller)
            time.sleep(0.5)
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            
            st4 = self.generated_params.get('subtask_4', {})
            recording_name = st4.get('recording_name', 'recording_morning')
            target_folder = st4.get('target_folder', 'Documents/Lectures')
            logging.info(f"      ✅ Task 4 Audio Recorder ready (agent will record → save as '{recording_name}' → move to '{target_folder}')")
            
        except Exception as e:
            logging.warning(f"      ⚠️ Task 4 setup failed: {e}")
    
    def _reset_init_task5_meeting_notify(self, subtask, env):
        """
        Task 5 (Meeting Update + SMS):
        Prerequisite: Initialize Calendar + create a calendar event (with an older timestamp) + contacts.
        
        ⚠️ Critical sequence (refer to Scenario A's _reset_setup_calendar_events implementation):
        1. clear_app_data
        2. _ensure_utc_timezone (must be executed before launching Calendar).
        3. Launch Calendar and wait for 2.5 seconds (to ensure the database is fully created).
        4. Force-close Calendar (to avoid WAL locking).
        5. clear_calendar_db
        6. add_events (using cal_module.timegm() to avoid timezone ambiguity).
        """
        logging.info("   🔧 Reset Init Task 5: Setting up Calendar, creating event and contacts")
        
        from scendroid.env import adb_utils
        from scendroid.utils import contacts_utils
        from scendroid.task_evals.common_validators import sms_validators
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from datetime import datetime
        import calendar as cal_module
        import time
        
        # Pre-read params to avoid variable scope issues inside subsequent try/except blocks
        params = subtask['params']
        event_title = params.get('event_title', 'Seminar')
        original_hour = params.get('original_hour', 14)
        original_minute = params.get('original_minute', 0)
        duration_minutes = params.get('duration_minutes', 90)
        location = params.get('location', 'Lab 301')
        attendees = params.get('attendees', [])
        
        # Step 1: Clear Calendar app data
        logging.info("      Step1: Clearing Calendar app data...")
        try:
            adb_utils.clear_app_data("com.simplemobiletools.calendar.pro", env.controller)
            time.sleep(1.5)
        except Exception as e:
            logging.warning(f"      ⚠️ Could not clear calendar data: {e}")
        
        # Step 2: Set timezone (must be done before Calendar's first launch to ensure DB is created with correct timezone)
        self._ensure_utc_timezone(env)
        
        # Step 3: Launch Calendar to initialize the database (wait sufficient time)
        logging.info("      Step3: Launching Calendar to initialize DB...")
        try:
            adb_utils.start_activity(
                "com.simplemobiletools.calendar.pro/.activities.MainActivity",
                None,
                env.controller
            )
            time.sleep(2.5)  # ⚠️ Must wait long enough to ensure the events table is fully created (refer to Scenario A)
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            logging.info("      ✅ Calendar launched and DB initialized")
        except Exception as e:
            logging.warning(f"      ⚠️ Could not launch Calendar: {e}")
        
        # Step 4: Force-stop Calendar (to avoid DB read/write failures caused by WAL mode)
        try:
            adb_utils.close_app('simple calendar pro', env.controller)
            time.sleep(0.5)
        except Exception:
            pass
        
        # Step 5: Empty the calendar DB
        try:
            calendar_utils.clear_calendar_db(env)
            logging.info("      ✅ Calendar DB cleared")
        except Exception as e:
            logging.warning(f"      ⚠️ clear_calendar_db failed (continuing anyway): {e}")
            import traceback
            logging.warning(traceback.format_exc())
        
        # Step 6: Write events using cal_module.timegm() (consistent with Scenario A, timezone-agnostic)
        try:
            # ✅ Use context.base_date to obtain the scenario base date ('2026-01-07'), avoiding hardcoding
            base_date_str = self.context.base_date or '2026-01-07'
            base_date = datetime.strptime(base_date_str, '%Y-%m-%d')
            event_dt = base_date.replace(hour=original_hour, minute=original_minute, second=0)
            start_ts = cal_module.timegm(event_dt.timetuple())
            end_ts = start_ts + duration_minutes * 60
            
            # Refer to normal mode (Task 1, line 392): description stores the attendee list
            # The Task 5 evaluator needs to extract attendees from description to verify SMS sending
            attendees_desc = "Attendees: " + ", ".join(a['name'] for a in attendees) if attendees else ""
            
            event = sqlite_schema_utils.CalendarEvent(
                start_ts=start_ts,
                end_ts=end_ts,
                title=event_title,
                description=attendees_desc,
                location=location,
            )
            
            logging.info(f"      Creating event: '{event_title}' @ {original_hour}:{original_minute:02d} "
                        f"(start_ts={start_ts}, duration={duration_minutes}min, location='{location}', "
                        f"description='{attendees_desc}')")
            calendar_utils.add_events([event], env)
            time.sleep(2.0)
            logging.info(f"      ✅ Calendar event created: '{event_title}' @ {original_hour}:{original_minute:02d} "
                        f"with attendees: {[a['name'] for a in attendees]}")
        except Exception as e:
            logging.warning(f"      ⚠️ Failed to create calendar event: {e}")
            import traceback
            logging.warning(traceback.format_exc())
        
        # Step 7: Clear contacts and SMS
        try:
            logging.info("      Step7: Clearing contacts and SMS...")
            contacts_utils.clear_contacts(env.controller)
            time.sleep(1.0)
            sms_validators.clear_sms_and_threads(env.controller)
            time.sleep(0.5)
        except Exception as e:
            logging.warning(f"      ⚠️ Could not clear contacts/SMS: {e}")
        
        # Step 8: Create contacts
        for attendee in attendees:
            try:
                adb_utils.press_home_button(env.controller)
                time.sleep(1.0)
                contacts_utils.add_contact(
                    attendee['name'], attendee['number'],
                    env.controller, ui_delay_sec=2.0
                )
                time.sleep(1.5)
                logging.info(f"      ✅ Contact: {attendee['name']}")
            except Exception as e:
                logging.warning(f"      ⚠️  Failed to add {attendee['name']}: {e}")
        
        time.sleep(1.0)
        adb_utils.press_home_button(env.controller)
        logging.info("      ✅ Task 5 initialization completed")
    
    def _reset_init_task6_shopping(self, subtask, env):
        """
        Task 6 (Shopping):
        Prerequisite: Chrome/Shopping App initialization + login.
        
        Refer to Scenario B Task 7 implementation (lines 2148–2175).
        evaluator.initialize_task() handles Chrome cleanup and WebArena login.
        """
        logging.info("   🔧 Reset Init Task 6: Initializing Shopping (Chrome/WebArena Login)")
        
        from scendroid.env import adb_utils
        import time
        
        # 0. Return to home (clean up previous task's state)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
        except Exception:
            pass
        
        # 1. Initialize Shopping (evaluator handles Chrome and WebArena login)
        try:
            evaluator = subtask.get('evaluator_instance')
            if evaluator:
                evaluator.initialize_task(env)
                logging.info("      ✅ Shopping evaluator initialized (Chrome/WebArena)")
            else:
                logging.warning("      ⚠️  No evaluator instance found for Task 6")
        except Exception as e:
            logging.warning(f"      ⚠️  Shopping initialization failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
        
        # ℹ️ Do not return to home — after Task 6 initialization, remain on the Shopping App homepage
        # evaluator.initialize_task() ends at the Shopping homepage; no additional action needed
        logging.info("      ✅ Task 6 initialization completed (staying on Shopping homepage)")
    
    def _reset_init_task7_music_exercise(self, env):
        """
        Task 7 (Music + OpenTracks):
        Prerequisite: Music library + RetroMusic initialization (skip welcome screen) + OpenTracks clearing and Bluetooth permission dialog handling.
        
        Key point: After _setup_music(), RetroMusic must be initialized separately;
        otherwise, the Agent will encounter the welcome screen when opening RetroMusic.
        Refer to RetroMusicApp.setup() (in apps.py) + implementation in scenario_omnilife.py.
        """
        logging.info("   🔧 Reset Init Task 7: Setting up music library, RetroMusic, and OpenTracks")
        
        from scendroid.task_evals.information_retrieval import activity_app_utils
        from scendroid.env import adb_utils, tools
        import time
        
        # 1. Set up music library files
        self._setup_music(env)
        
        # 2. Initialize the RetroMusic app (handle welcome screen)
        # Refer to RetroMusicApp.setup() in scendroid/env/setup_device/apps.py
        logging.info("      Setting up RetroMusic app (handling welcome screen)...")
        try:
            retro_package = adb_utils.extract_package_name(
                adb_utils.get_adb_activity("retro music")
            )
            
            # Grant necessary permissions (consistent with the official setup)  
            adb_utils.grant_permissions(
                retro_package,
                "android.permission.READ_MEDIA_AUDIO",
                env.controller,
            )
            adb_utils.grant_permissions(
                retro_package,
                "android.permission.POST_NOTIFICATIONS",
                env.controller,
            )
            
            # Launch RetroMusic (the welcome screen will appear)  
            adb_utils.launch_app("retro music", env.controller)
            time.sleep(3.0)  # Wait for the welcome screen to appear and for the app to complete initialization  
            
            # Attempt to tap the Continue/Finish button on the welcome screen (if present)  
            try:
                controller = tools.AndroidToolController(env=env.controller)
                for btn_text in ['GET STARTED', 'Get Started', 'DONE', 'Done', 'NEXT', 'Next',
                                  'FINISH', 'Finish', 'OK', 'Continue', 'START', 'Start']:
                    try:
                        controller.click_element(btn_text)
                        logging.info(f"      ✅ Clicked welcome screen button: '{btn_text}'")
                        time.sleep(1.5)
                    except Exception:
                        pass
            except Exception as e:
                logging.debug(f"      Welcome screen interaction: {e}")
            
            # Close RetroMusic (the app has been initialized and will no longer display the welcome screen)  
            adb_utils.close_app("retro music", env.controller)
            time.sleep(0.5)
            logging.info("      ✅ RetroMusic initialized (welcome screen bypassed)")
            
        except Exception as e:
            logging.warning(f"      ⚠️ RetroMusic setup failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
        
        # 3. Fully set up OpenTracks (handle Bluetooth permission dialog)  
        try:
            logging.info("      Setting up OpenTracks...")
            
            # Clear the database  
            activity_app_utils.clear_db(env)
            logging.info("      ✅ OpenTracks database cleared")
            
            # Grant permissions  
            open_tracks_package = adb_utils.extract_package_name(
                adb_utils.get_adb_activity("open tracks")
            )
            
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
            
            # Launch the app and handle the Bluetooth permission dialog  
            try:
                adb_utils.launch_app("activity tracker", env.controller)
                time.sleep(3.0)
                
                # Tap the Bluetooth permission Allow button  
                try:
                    controller = tools.AndroidToolController(env=env.controller)
                    controller.click_element("Allow")
                    logging.info("      ✅ Clicked bluetooth permission 'Allow' button")
                    time.sleep(1.0)
                except Exception as e:
                    logging.debug(f"      Bluetooth permission already granted or not needed: {e}")
                
                # Close the app  
                adb_utils.close_app("activity tracker", env.controller)
            except Exception as e:
                logging.debug(f"      OpenTracks launch/handling: {e}")
            
            logging.info("      ✅ OpenTracks setup complete")
            
        except Exception as e:
            logging.warning(f"      ⚠️ OpenTracks setup failed: {e}")
        
        # 4. Return to home  
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 7 initialization completed")
    
    def _reset_init_task8_sms_summary(self, env):
        """
        Task 8 (SMS + Markor):
        Prerequisite: Create SMS message + clear Markor.
        
        Refer to the _setup_sms_for_task8 method used in non-reset mode.
        """
        logging.info("   🔧 Reset Init Task 8: Creating SMS messages and clearing Markor")
        
        from scendroid.env import adb_utils, device_constants
        from scendroid.task_evals.common_validators import sms_validators
        import time
        
        # 1. Clear existing SMS (in reset mode, messages from Task 5 need not be retained)  
        try:
            logging.info("      Clearing existing SMS...")
            sms_validators.clear_sms_and_threads(env.controller)
            time.sleep(1.0)
        except Exception as e:
            logging.warning(f"      ⚠️ Could not clear SMS: {e}")
        
        # 2. Create progress-reply SMS and distractors (using the logic from _setup_sms_for_task8)  
        try:
            logging.info("      Creating SMS messages...")
            
            # Get parameters  
            st8 = self.generated_params.get('subtask_8', {})
            shared = self.generated_params.get('shared', {})
            progress_replies = st8.get('progress_replies', [])
            distractor_messages = st8.get('distractor_messages', [])
            seminar_members = shared.get('seminar_members', [])
            
            logging.info(f"      Adding {len(progress_replies)} progress replies + {len(distractor_messages)} distractors...")
            
            # Create phone number mapping  
            name_to_phone = {m['name']: m['phone'] for m in seminar_members}
            
            # Add progress-reply SMS (target message)  
            progress_count = 0
            for reply in progress_replies:
                from_name = reply['from']
                content = reply['content']
                
                # Get phone number  
                phone = name_to_phone.get(from_name)
                if not phone:
                    # Attempt partial matching  
                    for member in seminar_members:
                        if from_name.split()[0] in member['name']:
                            phone = member['phone']
                            break
                
                if phone:
                    try:
                        # Use text_emulator to simulate receiving an SMS  
                        adb_utils.text_emulator(
                            env.controller,
                            phone,  # Sender's phone number  
                            content,  # SMS content  
                        )
                        progress_count += 1
                        logging.info(f"         ✅ Progress SMS from {from_name}: \"{content[:40]}...\"")
                        time.sleep(1.0)
                    except Exception as e:
                        logging.warning(f"         ⚠️ Failed to add SMS from {from_name}: {e}")
                else:
                    logging.warning(f"         ⚠️ No phone found for {from_name}")
            
            logging.info(f"      ✅ Added {progress_count} progress messages")
            
            # Add distractor SMS  
            distractor_count = 0
            for distractor in distractor_messages:
                from_name = distractor['from']
                phone = distractor['phone']
                content = distractor['content']
                
                try:
                    adb_utils.text_emulator(
                        env.controller,
                        phone,
                        content,
                    )
                    distractor_count += 1
                    logging.info(f"         ✅ Distractor SMS from {from_name}: \"{content[:40]}...\"")
                    time.sleep(1.0)
                except Exception as e:
                    logging.warning(f"         ⚠️ Failed to add distractor SMS: {e}")
            
            logging.info(f"      ✅ Added {distractor_count} distractor messages")
            
            # Wait for SMS database synchronization  
            time.sleep(2.0)
            
        except Exception as e:
            logging.warning(f"      ⚠️ SMS creation failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
        
        # 3. Clear Markor  
        try:
            markor_dir = device_constants.MARKOR_DATA
            
            # Close Markor  
            try:
                adb_utils.close_app("markor", env.controller)
                time.sleep(0.5)
            except Exception:
                pass
            
            # Delete directory  
            adb_utils.issue_generic_request(
                ['shell', 'rm', '-rf', markor_dir], env.controller
            )
            time.sleep(0.5)
            
            # Rebuild directory  
            adb_utils.issue_generic_request(
                ['shell', 'mkdir', '-p', markor_dir], env.controller
            )
            time.sleep(0.5)
            
            logging.info("      ✅ Markor cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear Markor: {e}")
        
        # 4. Return to home
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception as e:
            pass
        
        logging.info("      ✅ Task 8 initialization completed")
    
    def _reset_init_task9_daily_summary(self, env):
        """
        Task 9 (Markor Daily Summary):
        Prerequisite: Clear Markor.
        """
        logging.info("   🔧 Reset Init Task 9: Clearing Markor")
        
        from scendroid.env import adb_utils, device_constants
        import time
        
        try:
            markor_dir = device_constants.MARKOR_DATA
            
            # Close Markor
            try:
                adb_utils.close_app("markor", env.controller)
                time.sleep(0.5)
            except Exception:
                pass
            
            # Delete directory
            adb_utils.issue_generic_request(
                ['shell', 'rm', '-rf', markor_dir], env.controller
            )
            time.sleep(0.5)
            
            # Rebuild directory
            adb_utils.issue_generic_request(
                ['shell', 'mkdir', '-p', markor_dir], env.controller
            )
            time.sleep(0.5)
            
            logging.info("      ✅ Markor cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear Markor: {e}")
        
        # Return to home
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception as e:
            pass
        
        logging.info("      ✅ Task 9 initialization completed")

