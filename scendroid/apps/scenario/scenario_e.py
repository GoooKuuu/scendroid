"""
Scenario F: Weekend Hiking & Photography (outdoor hiking scenario)

Complex scenario, containing 11 subtasks, simulating a weekend outdoor hiking day:
1. Picnic supplies verification and checklist creation (Broccoli Recipe + Tasks)
2. Update calendar location (Calendar)
3. Notify participants of location change (SMS)
4. Create an ordered hiking playlist (Retro Music)
5. Launch track recording and music playback (OpenTracks + Retro Music)
6. Capture dynamic scenery (Camera - Video Mode)
7. Dynamic picnic supplies replenishment (Shopping - Chrome)
8. Exercise data statistics (OpenTracks QA)
9. Photo deduplication and structured organization (Files)
10. Shopping expenses and financial recordkeeping (Pro Expense)
11. Comprehensive hiking trip journal generation (Markor)

features:
- Outdoor scenario, long time span (07:00 → 22:00)
- Cross-application collaboration, with dependencies among tasks
- Includes a QA task
- Involves multimedia operations (music, video, photos)
"""

from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.scenario.base import BaseScenarioEvaluator


@AppRegistry.register_evaluator("ScenarioE_WeekendHiking")
class ScenarioEWeekendHikingEvaluator(BaseScenarioEvaluator):
    """
    scenario F: Weekend Hiking & Photography for {user_name} - parameterized version
    
    description:
    Simulates a weekend outdoor hiking and picnic day, starting from morning preparation of supplies,
    progressing through hiking, photography, picnicking, and concluding with evening photo organization and trip journal writing
    
    Subtasks (11 total):
    1. Picnic supplies verification and checklist creation (Broccoli Recipe + Tasks)
    2. Update calendar location (Calendar)
    3. Notify participants of location change (SMS)
    4. Create an ordered hiking playlist (Retro Music)
    5. Launch track recording and music playback (OpenTracks + Retro Music)
    6. Capture dynamic scenery (Camera - Video Mode)
    7. Dynamic picnic supplies replenishment (Shopping - Chrome)
    8. Exercise data statistics (OpenTracks QA)
    9. Photo deduplication and structured organization (Files)
    10. Shopping expenses and financial recordkeeping (Pro Expense)
    11. Comprehensive hiking trip journal generation (Markor)
    
    features:
    - Outdoor scenario, with dependencies among tasks
    - Cross-application collaboration (F1→F10, F2→F3, F4→F5, F7→F10)
    - Includes a QA task (F8)
    
    rating:
    - All tasks, etc., weighted
    - report completion status of each task when done
    """
    
    app_names = (
        "broccoli recipe", "tasks", "simple calendar pro", "simple sms messenger",
        "retro music", "opentracks", "camera", "chrome",
        "files", "pro expense", "markor"
    )
    
    scenario_id = "F"
    complexity = 4.8
    
    # ========== parameter template definition ==========
    PARAM_TEMPLATES = {
        # shared parameters (used across tasks)
        'shared': {
            'user_names': ['David', 'Sarah', 'Michael', 'Emily', 'Alex'],
            'hike_locations': [
                {'name': 'West Peak Lookout', 'original': 'East Valley Trail', 'type': 'Mountain'},
                {'name': 'Sunset Ridge', 'original': 'Sunrise Point', 'type': 'Ridge'},
                {'name': 'Crystal Lake Viewpoint', 'original': 'Forest Trail', 'type': 'Lake'},
                {'name': 'Eagle Cliff', 'original': 'Meadow Path', 'type': 'Cliff'},
            ],
            'hiking_friends': [
                {'name': 'Bob Johnson', 'phone': '555-0101'},
                {'name': 'Sarah Miller', 'phone': '555-0102'},
                {'name': 'Tom Wilson', 'phone': '555-0103'},
                {'name': 'Lisa Chen', 'phone': '555-0104'},
            ],
            # Distractor contact (does not participate in the activity, used to increase complexity)
            'distractor_contacts': [
                {'name': 'Mike Brown', 'phone': '555-0105'},
                {'name': 'Emma Davis', 'phone': '555-0106'},
                {'name': 'James Lee', 'phone': '555-0107'},
            ],
        },
        
        # F1: Picnic recipe and supplies
        'subtask_1': {
            'recipes': [
                {
                    'title': 'Picnic BBQ',
                    'required_items': ['Chicken Wings', 'Corn', 'Potatoes', 'BBQ Sauce'],
                    'already_have': ['Charcoal', 'Grill'],
                    'distractors': ['Vegetable Soup', 'Pasta Salad'],
                },
                {
                    'title': 'Outdoor Grill Feast',
                    'required_items': ['Beef Patties', 'Hot Dogs', 'Buns', 'Ketchup'],
                    'already_have': ['Portable Stove', 'Utensils'],
                    'distractors': ['Birthday Cake', 'Ice Cream'],
                },
            ],
        },
        
        # F2: calendarevent
        'subtask_2': {
            'event_times': ['10:00', '10:30', '11:00'],
            'event_titles': ['Mountain Picnic', 'Hiking Trip', 'Outdoor Adventure'],
        },
        
        # F3: Music playlist (using built-in Android World song titles)
        'subtask_3': {
            'playlist_names': ['Mountain Hike', 'Trail Mix', 'Outdoor Vibes', 'Peak Performance'],
            # Use scendroid built-in song titles (from retro_music.py's _SONGS)
            'songs': [
                ['My Heart is Yours', 'Endless Summer', 'Whispering Wind', 'Lost in the Echo',
                 'Chasing Shadows', 'Night Drive', 'Echoes of Silence', 'Bright Lights'],
                ['Moments', 'Forever Young', 'Rising Sun', 'Silent Dreams',
                 'City of Stars', 'Moonlight Sonata', 'Through the Storm', 'Return to Paradise'],
            ],
            # Distractor song (will be created on the device but does not need to be added to the playlist)
            'noise_songs': [
                'Voices in the Hall', 'Under the Sky', "Dreamer's Awake", 'Serenity Now',
                'Falling Feathers', 'Orbiting Stars', 'Reflections', 'Beyond the Horizon',
            ],
        },
        
        # F5: videosetup
        'subtask_5': {
            'video_settings': [
                {'resolution': '1080p', 'fps': '30'},
                {'resolution': '4K', 'fps': '60'},
            ],
        },
        
        # F6: Shopping item (meat alternative)
        'subtask_6': {
            'products': [
                {
                    'sku': 'B01CTR3DLE',
                    'name': 'Organic Plant-Based Meat',
                    'price': 113.27,
                    'category': 'Meat Substitute',
                    'price_range': {'min': 100, 'max': 200},
                },
            ],
        },
        
        # F7: Exercise statistics
        'subtask_7': {
            'activity_types': ['Hiking', 'Walking', 'Running'],
            'weekly_distances': [15.5, 20.3, 12.8, 18.6],  # km
            'weekly_durations': [180, 240, 150, 210],  # minutes
        },
        
        # F8: Photo file (with timestamp, used for deduplication and F10 travel journal entries)
        # Note: The file name will be dynamically generated in generate_random_params based on the actual participant's name
        'subtask_8': {
            'photo_patterns': [
                {
                    # Scenic photo template: Time_Location.png
                    'scenery_template': [
                        ('1010', 'Mountain'),      # 10:10 mountain view
                        ('1025', 'Lake'),          # 10:25 lake view
                        ('1025', 'Lake', True),    # 10:25 lake view (duplicate)
                        ('1110', 'Waterfall'),     # 11:10 waterfall
                    ],
                    # Portrait photo template: Time_PersonName.png (person name selected from participants)
                    'portrait_template': [
                        ('0930', 'group'),         # 09:30 group photo at departure
                        ('1200', 'selfie'),        # 12:00 summit selfie
                        ('1200', 'selfie', True),  # 12:00 summit selfie (duplicate)
                        ('1430', 'lunch'),         # 14:30 lunch photo
                    ],
                },
            ],
        },
        
        # F9: This week's expenses (in question-and-answer format)
        'subtask_9': {
            'weekly_expenses': [
                {'name': 'Groceries', 'amount': 45.50, 'category': 'Food', 'day_offset': 3},
                {'name': 'Gas', 'amount': 38.00, 'category': 'Transport', 'day_offset': 2},
                {'name': 'Coffee', 'amount': 12.80, 'category': 'Food', 'day_offset': 1},
            ],
        },
        
        # F10: Travel journal keywords (based on actual content from previous tasks)
        'subtask_10': {
            'required_content': ['lunch', 'meat', 'photo', 'lake', 'mountain'],
        },
    }
    
    @classmethod
    def generate_random_params(cls, seed=None):
        """
        Generate random parameters for Scenario F
        
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
        location = random.choice(cls.PARAM_TEMPLATES['shared']['hike_locations'])
        
        # Exclude friends whose names match the user name (to avoid two "Sarahs")
        all_friends = cls.PARAM_TEMPLATES['shared']['hiking_friends']
        distractor_contacts = cls.PARAM_TEMPLATES['shared']['distractor_contacts']
        
        # Filtering: A friend's name must not contain the user name (e.g., if user_name="Sarah", exclude "Sarah Miller")
        filtered_friends = [
            f for f in all_friends 
            if user_name.lower() not in f['name'].lower()
        ]
        
        # If too few friends remain after filtering, use all friends
        if len(filtered_friends) < 4:
            filtered_friends = all_friends
        
        friends = filtered_friends[:4]  # First 4 are activity participants
        
        shared_params = {
            'user_name': user_name,
            'new_location': location['name'],
            'original_location': location['original'],
            'location_type': location['type'],
            'friends': friends,
            'distractor_contacts': distractor_contacts,  # All distractor contacts
        }
        
        # 2. Generate F1 parameter (picnic supplies)
        recipe = random.choice(cls.PARAM_TEMPLATES['subtask_1']['recipes'])
        subtask_1_params = {
            'recipe_title': recipe['title'],
            'required_items': recipe['required_items'],
            'already_have': recipe['already_have'],
            'distractors': recipe['distractors'],
        }
        
        # 3. Generate F2 parameter (calendar event)
        event_time = random.choice(cls.PARAM_TEMPLATES['subtask_2']['event_times'])
        event_title = random.choice(cls.PARAM_TEMPLATES['subtask_2']['event_titles'])
        event_hour, event_minute = map(int, event_time.split(':'))
        
        subtask_2_params = {
            'event_time': event_time,
            'event_hour': event_hour,
            'event_minute': event_minute,
            'event_title': event_title,
            'attendees': [f['name'] for f in friends],
        }
        
        # 4. Generate F3 parameter (music playlist)
        playlist_name = random.choice(cls.PARAM_TEMPLATES['subtask_3']['playlist_names'])
        songs = random.choice(cls.PARAM_TEMPLATES['subtask_3']['songs'])
        
        subtask_3_params = {
            'playlist_name': playlist_name,
            'songs': songs,
            'enable_shuffle': True,
        }
        
        # 5. Generate F5 parameter (video setup)
        video_setting = random.choice(cls.PARAM_TEMPLATES['subtask_5']['video_settings'])
        subtask_5_params = video_setting.copy()
        
        # 6. Generate F6 parameter (shopping)
        product = cls.PARAM_TEMPLATES['subtask_6']['products'][0]
        subtask_6_params = product.copy()
        
        # 7. Generate F7 parameter (exercise statistics)
        idx = random.randint(0, len(cls.PARAM_TEMPLATES['subtask_7']['weekly_distances']) - 1)
        activity_type = random.choice(cls.PARAM_TEMPLATES['subtask_7']['activity_types'])
        
        subtask_7_params = {
            'activity_type': activity_type,
            'weekly_distance': cls.PARAM_TEMPLATES['subtask_7']['weekly_distances'][idx],
            'weekly_duration': cls.PARAM_TEMPLATES['subtask_7']['weekly_durations'][idx],
        }
        
        # 8. Generate F8 parameter (photo organization)
        # Dynamically generate photo file names based on participant names and location
        friend_names = [f['name'].split()[0] for f in friends[:3]]  # Take first names of first 3 friends
        location_type = location['type']  # Mountain, Lake, etc.
        
        # Scenic photos: Time_Location.png
        scenery_photos = [
            f'1010_{location_type}.png',              # 10:10 mountain/lake view
            f'1025_Lake.png',                         # 10:25 lake view
            f'1025_Lake_copy.png',                    # 10:25 lake view (duplicate)
            f'1110_Waterfall.png',                    # 11:10 waterfall
        ]
        
        # Portrait photos: Time_PersonName.png
        portrait_photos = [
            f'0930_{friend_names[0]}_and_{friend_names[1]}.png',  # 09:30 photo of two people
            f'1200_{user_name}_selfie.png',                        # 12:00 selfie
            f'1200_{user_name}_selfie_dup.png',                    # 12:00 selfie (duplicate)
            f'1430_{friend_names[2]}_lunch.png',                   # 14:30 lunch photo
        ]
        
        subtask_8_params = {
            'scenery_photos': scenery_photos,
            'portrait_photos': portrait_photos,
            'friend_names': friend_names,  # for F10 use
        }
        
        # 9. Generate F9 parameter (expense Q&A)
        weekly_expenses = cls.PARAM_TEMPLATES['subtask_9']['weekly_expenses']
        # Calculate total expenses for this week (excluding meat purchased today)
        weekly_total_before_meat = sum(e['amount'] for e in weekly_expenses)
        # Cost of meat purchased today
        meat_amount = product['price']
        # Total expenses for this week
        weekly_total = weekly_total_before_meat + meat_amount
        
        subtask_9_params = {
            'meat_amount': meat_amount,
            'weekly_expenses': weekly_expenses,
            'weekly_total': round(weekly_total, 2),
        }
        
        # 10. Generate F10 parameter (travel log, based on previous tasks)
        subtask_10_params = {
            'file_name': 'Hiking_Day_Summary.md',
            'meat_amount': meat_amount,
            'location_name': location['name'],
            'required_keywords': cls.PARAM_TEMPLATES['subtask_10']['required_content'],
        }
        
        # Return the complete parameter set
        return {
            'seed': seed,
            'shared': shared_params,
            'subtask_1': subtask_1_params,
            'subtask_2': subtask_2_params,
            'subtask_3': subtask_3_params,
            'subtask_5': subtask_5_params,
            'subtask_6': subtask_6_params,
            'subtask_7': subtask_7_params,
            'subtask_8': subtask_8_params,
            'subtask_9': subtask_9_params,
            'subtask_10': subtask_10_params,
        }
    
    def __init__(self, params: dict = None):
        """
        initialize Scenario F
        
        Args:
            params: scenario parameters. If None, calls generate_random_params() to generate random parameters
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
        location = shared.get('new_location', 'West Peak Lookout')
        
        # set scenario metadata
        scenario_params = {
            'scenario_id': 'F',
            'name': f'Weekend Hiking at {location} for {user_name}',
            'base_date': '2026-01-18',  # Sunday, January 18, 2026
            'total_max_steps': 350,
            'success_criteria': {
                'all_subtasks_pass': False,
                'min_subtasks_pass': 0,
            },
            'generated_params': generated_params,
            'clarity_level': params.get('clarity_level'),  # ⚡ pass clarity_level
            'reset_mode': params.get('reset_mode', False),  # ⚡ pass reset_mode
        }
        
        super().__init__(scenario_params)
        
        # Save generated_params for use by the initialize method
        self.generated_params = generated_params
        
        # add subtasks using parameterized approach
        self._add_parameterized_subtasks(generated_params)
        
        # set complexity
        self.complexity = 4.8
    
    def _add_parameterized_subtasks(self, generated_params: dict):
        """Add all subtasks using the generated parameters"""
        shared = generated_params.get('shared', {})
        st1 = generated_params.get('subtask_1', {})
        st2 = generated_params.get('subtask_2', {})
        st3 = generated_params.get('subtask_3', {})
        st5 = generated_params.get('subtask_5', {})
        st6 = generated_params.get('subtask_6', {})
        st7 = generated_params.get('subtask_7', {})
        st8 = generated_params.get('subtask_8', {})
        st9 = generated_params.get('subtask_9', {})
        st10 = generated_params.get('subtask_10', {})
        
        # extract shared parameters
        user_name = shared.get('user_name', 'David')
        new_location = shared.get('new_location', 'West Peak Lookout')
        original_location = shared.get('original_location', 'East Valley Trail')
        friends = shared.get('friends', [])
        distractor_contacts = shared.get('distractor_contacts', [])
        
        # ========== F1: Picnic supplies verification and checklist creation (07:00) ==========
        recipe_title = st1.get('recipe_title', 'Picnic BBQ')
        required_items = st1.get('required_items', [])
        already_have = st1.get('already_have', [])
        
        self.add_subtask(
            subtask_id=1,
            evaluator_name="LayeredCrossAppRecipeTasks",
            params={
                "recipe_title": recipe_title,
                "required_items": required_items,
                "already_have": already_have,
                "check_off_items": already_have,
            },
            weight=1.0,
            time="07:00",
            narration=f"{user_name} is preparing for a picnic and needs to check the recipe "
                     f"to verify what supplies are needed.",
            user_instruction=f"Open the '{recipe_title}' recipe in Broccoli. "
                            f"Add all the required ingredients to my Tasks app. "
                            f"Then, check off the items I already have: "
                            f"'{', '.join(already_have)}'.",
            user_instruction_L0=f"Open the Broccoli Recipe app, find the '{recipe_title}' recipe, identify all required ingredients, open the Tasks app and add each ingredient as a task, then check off the tasks for items I already have: '{', '.join(already_have)}'.",
            user_instruction_L1=f"Add all ingredients from '{recipe_title}' to Tasks and check off: '{', '.join(already_have)}'.",
            user_instruction_L2="Prepare my picnic shopping list.",
            reset_user_instruction=(
                f"Open the Broccoli Recipe app, find the '{recipe_title}' recipe. "
                f"Open the Tasks app and add each of the following ingredients as a separate task: "
                f"{', '.join(repr(item) for item in required_items)}. "
                f"Then check off the tasks for items I already have: "
                f"{', '.join(repr(item) for item in already_have)}."
            ),
            max_steps=35,
            requires_answer=False,
        )
        
        # ========== F2: Update calendar location (07:45) ==========
        event_time = st2.get('event_time', '10:00')
        event_title = st2.get('event_title', 'Mountain Picnic')
        attendees = st2.get('attendees', [])
        
        self.add_subtask(
            subtask_id=2,
            evaluator_name="LayeredCalendarUpdateLocation",
            params={
                "event_title": event_title,
                "old_location": original_location,
                "new_location": new_location,
                "event_hour": st2.get('event_hour', 10),
                "event_minute": st2.get('event_minute', 0),
            },
            weight=1.0,
            time="07:45",
            narration=f"Due to good weather, {user_name} decides to change the meeting point.",
            user_instruction=f"Open Simple Calendar Pro and change the location of today's "
                            f"{event_time} AM '{event_title}' to '{new_location}'.",
            user_instruction_L0=f"Open Simple Calendar Pro, find today's {event_time} AM event '{event_title}', edit it to change the location from '{original_location}' to '{new_location}'.",
            user_instruction_L1=f"Update '{event_title}' location to '{new_location}'.",
            user_instruction_L2="Change the meeting point location.",
            reset_user_instruction=(
                f"Open Simple Calendar Pro. Find today's {event_time} event titled '{event_title}'. "
                f"Edit it to change the location from '{original_location}' to '{new_location}'."
            ),
            max_steps=20,
            requires_answer=False,
        )
        
        # ========== F3: Notify participants about location change (07:50) ==========
        # Notify only activity participants, not distractor contacts
        # Build recipient name list (excluding the user themselves)
        required_recipients = [f['name'] for f in friends if user_name.lower() not in f['name'].lower()]
        
        self.add_subtask(
            subtask_id=3,
            evaluator_name="LayeredSMSBatchNotify",
            params={
                "required_recipients": required_recipients,
                "message_must_contain_location": [new_location],
                "forbidden_recipients": [d['name'] for d in distractor_contacts],
                "contacts_map": {f['name']: f['phone'] for f in friends + distractor_contacts},
            },
            weight=1.0,
            time="07:50",
            narration=f"{user_name} needs to notify all hiking buddies about the location change.",
            user_instruction=f"Open Simple SMS and notify all participants of that event about the location change.",
            user_instruction_L0=f"Open Simple SMS Messenger and send messages to all participants of the '{event_title}' event in Calendar app, informing them of the location change to '{new_location}'.",
            user_instruction_L1=f"Open Simple SMS and notify all participants of that event about the location change.",
            user_instruction_L2="Let everyone know about the location change.",
            reset_user_instruction=(
                f"Open Simple SMS Messenger and send a message to each of these contacts: "
                f"{', '.join(required_recipients)}, "
                f"informing them that the hiking location has been changed to '{new_location}'."
            ),
            max_steps=25,
            requires_answer=False,
        )
        
        # ========== F4: Sequential hiking playlist creation (08:30) ==========
        playlist_name = st3.get('playlist_name', 'Mountain Hike')
        songs = st3.get('songs', [])
        
        # Ensure there are 8 songs
        if len(songs) < 8:
            songs = self.PARAM_TEMPLATES['subtask_3']['songs'][0]
        
        # Build song list string
        songs_list_str = ', '.join([f"'{s}'" for s in songs])
        
        self.add_subtask(
            subtask_id=4,
            evaluator_name="LayeredRetroMusicCreatePlaylist",
            params={
                "playlist_name": playlist_name,
                "songs": songs,  # All 8 songs
                "require_order": True,
            },
            weight=1.0,
            time="08:30",
            narration=f"To maintain rhythm on the trail, {user_name} needs to arrange songs "
                     f"in a specific intensity order.",
            user_instruction=f"Create a playlist in Retro Music titled '{playlist_name}'. "
                            f"Add the following songs in this exact order: {songs_list_str}.",
            user_instruction_L0=f"Open the Retro Music app, create a new playlist named '{playlist_name}', and add the following songs in this exact order: {songs_list_str}.",
            user_instruction_L1=f"Create playlist '{playlist_name}' with these songs in order: {songs_list_str}.",
            user_instruction_L2="Make a hiking playlist.",
            reset_user_instruction=(
                f"Open the Retro Music app, create a new playlist named '{playlist_name}', "
                f"and add the following songs in this exact order: {songs_list_str}."
            ),
            max_steps=40,  # Increase steps to accommodate 8 songs
            requires_answer=False,
        )
        
        # ========== F5: Start trajectory recording and music playback (09:30) ==========
        self.add_subtask(
            subtask_id=5,
            evaluator_name="LayeredCrossAppTracksMusic",
            params={
                "start_recording": True,
                "playlist_name": playlist_name,
                "check_music_playing": True,
            },
            weight=1.0,
            time="09:30",
            narration=f"Arriving at the trailhead, {user_name} starts comprehensive activity tracking.",
            user_instruction=f"Open OpenTracks and start recording my activity. "
                            f"Then, shuffle play the '{playlist_name}' playlist I just created.",
            user_instruction_L0=f"Open the OpenTracks app and start recording activity. Then open the Retro Music app, find the '{playlist_name}' playlist, and start shuffle play.",
            user_instruction_L1=f"Start tracking in OpenTracks and play '{playlist_name}' on shuffle.",
            user_instruction_L2="Start my hike with music.",
            reset_user_instruction=(
                f"Complete these tasks in order: "
                f"(1) Open Retro Music, create a playlist named '{playlist_name}', "
                f"and add the following songs in this exact order: {songs_list_str}. "
                f"(2) Open OpenTracks and start recording a new activity. "
                f"(3) Return to Retro Music, find the '{playlist_name}' playlist, and start shuffle play."
            ),
            max_steps=45,
            requires_answer=False,
        )
        
        # ========== F6: Capture dynamic scenery (11:00) ==========
        self.add_subtask(
            subtask_id=6,
            evaluator_name="LayeredCameraRecordVideo",
            params={
                "mode": "video",
                "enable_grid": True,
                "min_duration": 3,  # Record for at least 3 seconds
            },
            weight=1.0,
            time="11:00",
            narration=f"Reaching a waterfall midway, {user_name} wants to record a high-quality video.",
            user_instruction="Switch Camera to 'Video' mode. Turn on the grid lines "
                            "and record a short video.",
            user_instruction_L0="Open the Camera app, switch to Video mode, enable grid lines in settings, then record a video for at least 3 seconds and stop.",
            user_instruction_L1="Record a video with grid lines enabled.",
            user_instruction_L2="Capture the waterfall on video.",
            reset_user_instruction=(
                "Open the Camera app, switch to Video mode, enable grid lines in settings, "
                "then record a video for at least 3 seconds and stop."
            ),
            max_steps=25,
            requires_answer=False,
        )
        
        # ========== F7: Dynamic picnic supplies replenishment (14:00) ==========
        # Fixed parameters, not parameterized
        product_sku = 'B01CTR3DLE'
        
        self.add_subtask(
            subtask_id=7,
            evaluator_name="LayeredShoppingConstrainedPurchase",
            params={
                "product_sku": product_sku,
                "category": "Meat Substitute",
                "price_min": 100,
                "price_max": 200,
                "sort_by": "rating",
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
            time="14:00",
            narration=f"After lunch, {user_name} decides to order some extra meat for next time.",
            user_instruction="On the current webpage (ignore the internet access), browse the meat substitute category "
                            "and find the highest rated product with a price between "
                            "$100 and $200. Add it to your cart and "
                            "complete the purchase by placing an order.",
            user_instruction_L0="On the current webpage (ignore the internet access), go to 'Meat Substitute' category, sort by rating (highest first), find a product priced between $100-$200, add it to cart, and complete the purchase.",
            user_instruction_L1="On the current webpage (ignore the internet access), Buy the highest rated meat substitute between $100-$200.",
            user_instruction_L2="On the current webpage (ignore the internet access), Order some meat for next picnic.",
            reset_user_instruction=(
                "On the current webpage (ignore the internet access), "
                "Go to the 'Meat Substitute' category, sort by rating (highest first), "
                "find a product priced between $100 and $200, add it to cart, and complete the purchase."
            ),
            max_steps=40,
            requires_answer=False,
        )
        
        # ========== F8: Exercise data statistics (17:00) ==========
        # Instruction is fixed as "Hiking"; data initialization can be parameterized
        self.add_subtask(
            subtask_id=8,
            evaluator_name="LayeredOpenTracksStatsQA",
            params={
                "query_type": "weekly_summary",
                "activity_type": "Hiking",
                "require_distance": True,
                "require_duration": True,
            },
            weight=1.0,
            time="17:00",
            narration=f"After finishing the hike, {user_name} wants to check both today's performance "
                     f"and the overall weekly progress.",
            user_instruction="Open OpenTracks. Tell me today's distance and duration. "
                            "Also, check my statistics for Hiking this entire week "
                            "and summarize my total weekly distance and exercise time.",
            user_instruction_L0="Open the OpenTracks app, view the current recording to check today's distance and duration, then navigate to Statistics, filter by 'Hiking' activity type, and report the total weekly distance and exercise time.",
            user_instruction_L1="Tell me today's hiking stats and this week's total for Hiking.",
            user_instruction_L2="How did I do today and this week?",
            reset_user_instruction=(
                "Open OpenTracks. Tell me today's hiking distance and duration. "
                "Also navigate to Statistics, filter by 'Hiking' activity type, "
                "and summarize my total weekly distance and exercise time."
            ),
            max_steps=30,
            requires_answer=True,
        )
        
        # ========== F9: Photo deduplication and structured organization (20:00) ==========
        scenery_photos = st8.get('scenery_photos', [])
        portrait_photos = st8.get('portrait_photos', [])
        
        self.add_subtask(
            subtask_id=9,
            evaluator_name="LayeredFilesOrganizeAndDedupe",
            params={
                "source_folder": "Pictures",
                "target_folders": ["Scenery", "Portraits"],
                "scenery_patterns": ["mountain", "lake", "waterfall", "view"],
                "portrait_patterns": ["group", "selfie", "lunch", "start"],
                "dedupe_required": True,  # Deduplication is mandatory
            },
            weight=1.0,
            time="20:00",
            narration=f"{user_name} organizes the photos, not only categorizing by theme "
                     f"but also handling duplicate files from burst shooting.",
            user_instruction="In the 'Pictures' folder, create two subfolders: 'Scenery' and 'Portraits'. "
                            "Move photos based on their filenames to these folders. "
                            "If you find files with the same timestamp but different suffixes, "
                            "keep only one copy and delete the duplicates.",
            user_instruction_L0="Open the Files app, navigate to the 'Pictures' folder, create two subfolders 'Scenery' and 'Portraits'. Categorize photos by filename keywords (scenery: mountain/lake/waterfall/view, portraits: group/selfie/lunch/start), move them to respective folders, and delete duplicate files with the same timestamp.",
            user_instruction_L1="Organize Pictures into 'Scenery' and 'Portraits' folders and remove duplicates.",
            user_instruction_L2="Clean up and organize my hiking photos.",
            reset_user_instruction=(
                "Open Files, navigate to the 'Pictures' folder. "
                "Create two subfolders: 'Scenery' and 'Portraits'. "
                "Move photos based on their filenames: "
                "scenery keywords (mountain/lake/waterfall/view) → 'Scenery'; "
                "portrait keywords (group/selfie/lunch) → 'Portraits'. "
                "If you find files with the same timestamp but different suffixes, "
                "keep only one copy and delete the duplicates."
            ),
            max_steps=40,
            requires_answer=False,
        )
        
        # ========== F10: Weekly expense Q&A (21:00) ==========
        meat_amount = st9.get('meat_amount', 113.27)
        weekly_total = st9.get('weekly_total', 209.57)
        
        self.add_subtask(
            subtask_id=10,
            evaluator_name="LayeredExpenseWeeklyQA",
            params={
                "meat_name": "Meat Substitute",
                "meat_amount": meat_amount,
                "weekly_total": weekly_total,
            },
            weight=1.0,
            time="21:00",
            narration=f"{user_name} records today's meat purchase and wants to know this week's total spending.",
            user_instruction=f"Record the meat substitute purchase (${meat_amount:.2f}) in Pro Expense, "
                            f"then tell me: what is the total amount I spent this week?",
            user_instruction_L0=f"Open Pro Expense app, create a new expense entry for 'Meat Substitute' with amount ${meat_amount:.2f}, then check the weekly statistics and tell me the total amount spent this week.",
            user_instruction_L1=f"Log my meat purchase in Pro Expense and report this week's total spending.",
            user_instruction_L2="Record today's purchase and check my weekly spending.",
            reset_user_instruction=(
                f"Open Pro Expense app, create a new expense entry for 'Meat Substitute' with amount ${meat_amount:.2f}. "
                f"Then check the weekly statistics and tell me the total amount I spent this week."
            ),
            max_steps=30,
            requires_answer=True,
        )
        
        # ========== F11: Comprehensive hiking travel log generation (22:00) ==========
        file_name = st10.get('file_name', 'Hiking_Day_Summary.md')
        meat_amount_10 = st10.get('meat_amount', 113.27)
        friend_names = st8.get('friend_names', ['Bob', 'Sarah', 'Tom'])
        
        self.add_subtask(
            subtask_id=11,
            evaluator_name="LayeredMarkorHikingDiary",
            params={
                "file_name": file_name,
                "meat_amount": meat_amount_10,
                "location_name": new_location,
                "friend_names": friend_names,
                "required_keywords": ["lunch", "photo"],
            },
            weight=1.0,
            time="22:00",
            narration=f"{user_name} writes a diary entry summarizing today's hiking trip.",
            user_instruction=f"Create a new file '{file_name}' in Markor. "
                            f"Write a hiking diary based on today's activities: "
                            f"1) Record the lunch meat purchase; "
                            f"2) Check the Pictures folder and based on photo filenames, "
                            f"note the time and location for scenery photos (e.g., '10:25 - Lake'), "
                            f"and note the time and who's in portrait photos (e.g., '09:30 - Bob and Sarah').",
            user_instruction_L0=f"Open Markor, create file '{file_name}', write a diary including: (1) today's meat substitute purchase (${meat_amount_10:.2f}), (2) browse the Pictures folder via Files app, extract timestamps and keywords from photo filenames to record scenery locations and people in portraits.",
            user_instruction_L1=f"Create '{file_name}' in Markor with today's purchase and photo memories from Pictures folder.",
            user_instruction_L2="Write a hiking diary for today.",
            reset_user_instruction=(
                f"Open Markor, create a new file '{file_name}'. "
                f"Write a hiking diary entry including: "
                f"(1) Today's meat substitute purchase (${meat_amount_10:.2f}); "
                f"(2) Open Files, browse the 'Pictures/Scenery' and 'Pictures/Portraits' folders, "
                f"extract timestamps and keywords from photo filenames to record scenery locations and portrait subjects."
            ),
            max_steps=40,
            requires_answer=False,
        )
    
    def initialize_task(self, env):
        """
        batch initialization at scenario start
        
        pre-configure environment for all subtasks:
        - Initialize Broccoli Recipe data (for subtask 1)
        - Initialize Tasks app (for subtask 1)
        - Create calendar event (for subtask 2)
        - Create contact (for subtask 2)
        - Prepare photo file (for subtask 8)
        - Prepare exercise history record (for subtask 7)
        - cleanup Markor, Expense data
        """
        # Call parent class method (set up base_date etc.)
        super().initialize_task(env)
        
        # ⚡ Resetmode: skip batch init, each task initializes independently in _reset_initialize_subtask()
        if self.reset_mode:
            logging.info("⚡ Reset Mode: Skipping batch initialization")
            logging.info("   Each task will be initialized independently before execution")
            # only ensure timezone is UTC (needed by almost all tasks)
            self._ensure_utc_timezone(env)
            return
        
        logging.info("🔧 Batch-initialize Scenario F environment...")
        
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
            # 1. Initialize Broccoli Recipe data (for subtask 1)
            self._setup_broccoli_recipe(env)
            
            # 2. Initialize the Tasks app (for subtask 1)
            self._setup_tasks(env)
            
            # 3. Create calendar event (for subtask 2)
            self._setup_calendar_events(env)
            
            # 4. Create contact (for subtask 2)
            self._setup_contacts(env)
            
            # 5. Prepare music file (for subtasks 3 and 4)
            self._setup_music(env)
            
            # 6. Prepare photo file (for subtask 8)
            self._setup_photos(env)
            
            # 7. Prepare exercise history records (for subtasks 4 and 7) — including today's track
            self._setup_opentracks_history(env)
            
            # 8. Cleanup video file (for subtask 5 evaluation)
            self._cleanup_videos(env)
            
            # 9. cleanup Markor data
            self._cleanup_app_data(env)
            
            # 10. Initialize this week's expense records (for subtask 9)
            self._setup_expenses(env)
            
            logging.info("✅ batch initialization complete")
            
            # return to home screen
            from scendroid.env import adb_utils
            import time
            
            logging.info("   📱 return to home screen...")
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
            
        except Exception as e:
            logging.error(f"❌ batch initialization failed: {e}")
            import traceback
            logging.error(traceback.format_exc())
            raise
    
    def initialize_subtask(self, subtask_idx: int, env):
        """
        Subtask initialization logic
        
        Execute specific initialization before each subtask starts
        """
        # ⚡ Resetmode: skip Scenario-specific preprocessing
        # all initialization handled by _reset_initialize_subtask() in super()
        if self.reset_mode:
            super().initialize_subtask(subtask_idx, env)
            return
        
        subtask = self.subtasks[subtask_idx]
        subtask_id = subtask['subtask_id']
        
        # Task 7: OpenTracks statistics — need to delete invalid tracks and add today's track
        if subtask_id == 7:
            logging.warning("   🏃 Task 7 initialization — preparing today's exercise track...")
            self._initialize_today_track(env)
        
        # Call parent class method (handle time setup, etc.)
        super().initialize_subtask(subtask_idx, env)
    
    def _initialize_today_track(self, env):
        """
        Initialize today's exercise track for Task 7
        
        1. Close OpenTracks (stop any ongoing recording)
        2. Delete invalid tracks recorded in previous tasks (no distance on emulator)
        3. Add today's simulated track data (with distance and duration)
        """
        from scendroid.task_evals.information_retrieval import activity_app_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from scendroid.env import adb_utils
        from datetime import datetime, timedelta
        import time
        
        try:
            # 1. Close OpenTracks app (stop any ongoing recording)
            logging.info("      Step 1: Stop OpenTracks and close the app...")
            adb_utils.close_app("activity tracker", env.controller)
            time.sleep(1.0)
            
            # 2. Clean all tracks in the database (delete invalid data recorded in previous tasks)
            logging.info("      Step 2: Cleanup existing tracks (including today's invalid tracks)...")
            try:
                activity_app_utils.clear_db(env)
                logging.info("      ✅ Cleared existing tracks")
            except Exception as e:
                logging.debug(f"      Clear failed: {e}")
            
            # 3. Add today's track data + re-add this week's history data
            logging.info("      Step 3: Add today's track data...")
            
            st7 = self.generated_params.get('subtask_7', {})
            activity_type = st7.get('activity_type', 'Hiking')
            
            # Baseline date: 2026-01-18 (Sunday)
            base_date = datetime(2026, 1, 18, 0, 0, 0)
            
            # ========== Today's track (simulated recording from Task 4) ==========
            today_distance_m = 8500  # 8.5 km = 5.28 miles
            today_duration_ms = 150 * 60 * 1000  # 2.5 hours = 150 min
            today_start = base_date.replace(hour=9, minute=30)  # 9:30 AM start
            today_stop_ts = int(today_start.timestamp() * 1000) + today_duration_ms
            
            today_activity = sqlite_schema_utils.SportsActivity(
                name=f"Today's {activity_type}",
                category=activity_type.lower(),
                activity_type=activity_type.lower(),
                description=f"Morning {activity_type.lower()} to West Peak",
                totaldistance=today_distance_m,
                starttime=int(today_start.timestamp() * 1000),
                stoptime=today_stop_ts,
                totaltime=today_duration_ms,
                movingtime=int(today_duration_ms * 0.85),  # 85% move time
                avgspeed=today_distance_m / (today_duration_ms / 1000),
                avgmovingspeed=today_distance_m / (today_duration_ms * 0.85 / 1000),
                elevationgain=320,
                elevationloss=180,
            )
            
            activities = [today_activity]
            logging.warning(f"         🔵 TODAY: {today_distance_m/1000:.1f}km ({today_distance_m/1609.34:.2f}mi), {today_duration_ms/60000:.0f}min")
            
            # ========== Re-add this week's history data ==========
            import random
            random.seed(2026)  # Fix seed to ensure reproducibility
            
            weekly_data = [
                # (day_offset, distance_km, duration_min, hour, minute, name_suffix)
                (1, 4.2, 52, 17, 15, "Evening Trail"),        # Saturday, 4.2 km, 52 min
                (2, 6.8, 85, 7, 30, "Morning Hike"),          # Friday, 6.8 km, 85 min  
                (3, 3.5, 45, 18, 0, "Sunset Walk"),           # Thursday, 3.5 km, 45 min
                (4, 5.1, 62, 16, 45, "Afternoon Trek"),       # Wednesday, 5.1 km, 62 min
                (5, 7.3, 95, 6, 15, "Dawn Adventure"),        # Tuesday, 7.3 km, 95 min
            ]
            
            for day_offset, distance_km, duration_min, hour, minute, name_suffix in weekly_data:
                activity_date = base_date - timedelta(days=day_offset)
                
                distance_m = int(distance_km * 1000)
                duration_ms = duration_min * 60 * 1000
                
                start_ts = int(activity_date.replace(hour=hour, minute=minute).timestamp() * 1000)
                stop_ts = start_ts + duration_ms
                
                elevation_gain = random.randint(30, 180)
                elevation_loss = random.randint(20, 120)
                moving_ratio = 0.8 + random.random() * 0.15
                
                activity = sqlite_schema_utils.SportsActivity(
                    name=name_suffix,
                    category=activity_type.lower(),
                    activity_type=activity_type.lower(),
                    description=f"{activity_type} session",
                    totaldistance=distance_m,
                    starttime=start_ts,
                    stoptime=stop_ts,
                    totaltime=duration_ms,
                    movingtime=int(duration_ms * moving_ratio),
                    avgspeed=distance_m / (duration_ms / 1000),
                    avgmovingspeed=distance_m / (duration_ms * moving_ratio / 1000),
                    elevationgain=elevation_gain,
                    elevationloss=elevation_loss,
                )
                activities.append(activity)
                logging.info(f"         📊 Day -{day_offset}: {distance_km}km, {duration_min}min ({name_suffix})")
            
            # Add to database
            activity_app_utils._add_activities(activities, env)
            
            # Calculate totals
            total_distance_km = sum(a.totaldistance for a in activities) / 1000
            total_duration_min = sum(a.totaltime for a in activities) / (60 * 1000)
            
            logging.warning(f"      ✅ Exercise data prepared ({len(activities)} records, including today's)")
            logging.warning(f"         📈 WEEKLY TOTAL: {total_distance_km:.1f}km, {total_duration_min:.0f}min")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Task 7 initialization failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _setup_broccoli_recipe(self, env):
        """initialize Broccoli Recipe database"""
        logging.info("   📚 initialize Broccoli Recipe...")
        
        from scendroid.task_evals.utils import sqlite_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from scendroid.env import adb_utils
        import time
        import subprocess
        
        _DB_PATH = '/data/data/com.flauschcode.broccoli/databases/broccoli'
        _TABLE_NAME = 'recipes'
        _APP_NAME = 'broccoli app'
        
        # 1. Launch and close the app to ensure database creation
        logging.info("      Step 1: Launching Broccoli app to initialize database...")
        try:
            adb_utils.launch_app(_APP_NAME, env.controller)
            time.sleep(2.0)
        except subprocess.TimeoutExpired:
            # Broccoli app launch may timeout, but this is expected behavior
            logging.info("      Broccoli launch timed out (expected behavior)")
            time.sleep(1.0)
        
        adb_utils.close_app(_APP_NAME, env.controller)
        time.sleep(1.0)
        logging.info("      Step 2: Database should now be created")
        
        # 2. Clear existing recipes (to avoid accumulation during repeated initialization)
        logging.info("      Step 2.5: Clearing existing recipes...")
        try:
            sqlite_utils.delete_all_rows_from_table(
                table_name=_TABLE_NAME,
                remote_db_file_path=_DB_PATH,
                env=env,
                app_name=_APP_NAME
            )
            logging.info("      ✅ Existing recipes cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Failed to clear existing recipes: {e}")
        
        # 3. Get parameterized recipe information
        st1 = self.generated_params.get('subtask_1', {})
        recipe_title = st1.get('recipe_title', 'Picnic BBQ')
        required_items = st1.get('required_items', ['Chicken Wings', 'Corn', 'Potatoes', 'BBQ Sauce'])
        distractor_recipes = st1.get('distractor_recipes', ['Vegetable Soup', 'Pasta Salad'])
        
        # Create the correct recipe (including required supplies as ingredients)
        correct_recipe = sqlite_schema_utils.Recipe(
            title=recipe_title,
            description='Perfect for an outdoor picnic! A delicious BBQ experience.',
            servings='4-6',
            preparationTime='45 minutes',
            ingredients=', '.join(required_items),  # Use required supplies as ingredients
            directions='1. Prepare all ingredients. 2. Fire up the grill. 3. Cook meat to desired doneness. 4. Serve with sides.',
            favorite=0
        )
        
        # Create distractor recipes
        all_recipes = [correct_recipe]
        
        # Distractor recipe 1: Vegetable Soup (not BBQ)
        distractor_1 = sqlite_schema_utils.Recipe(
            title='Vegetable Soup',
            description='A healthy homemade soup.',
            servings='4',
            preparationTime='30 minutes',
            ingredients='carrots, celery, onions, broth, potatoes, herbs',
            directions='Chop vegetables. Simmer in broth until tender. Season to taste.',
            favorite=0
        )
        all_recipes.append(distractor_1)
        
        # Distractor recipe 2: Pasta Salad (a salad, not BBQ)
        distractor_2 = sqlite_schema_utils.Recipe(
            title='Pasta Salad',
            description='A refreshing cold pasta dish.',
            servings='6',
            preparationTime='20 minutes',
            ingredients='pasta, cherry tomatoes, cucumber, olives, feta cheese, olive oil',
            directions='Cook pasta. Mix with vegetables and dressing. Chill before serving.',
            favorite=0
        )
        all_recipes.append(distractor_2)
        
        # Distractor recipe 3: Grilled Cheese Sandwich (contains "grill" but is not a picnic BBQ)
        distractor_3 = sqlite_schema_utils.Recipe(
            title='Grilled Cheese Sandwich',
            description='Classic comfort food.',
            servings='1',
            preparationTime='10 minutes',
            ingredients='bread, butter, cheese slices',
            directions='Butter bread. Add cheese. Grill until golden and cheese melts.',
            favorite=0
        )
        all_recipes.append(distractor_3)
        
        # Distractor recipe 4: Fruit Smoothie (completely unrelated)
        distractor_4 = sqlite_schema_utils.Recipe(
            title='Fruit Smoothie',
            description='A healthy breakfast drink.',
            servings='2',
            preparationTime='5 minutes',
            ingredients='bananas, strawberries, milk, honey, ice',
            directions='Blend all ingredients until smooth. Serve immediately.',
            favorite=0
        )
        all_recipes.append(distractor_4)
        
        # 4. Add recipes to the database
        logging.info(f"      Step 3: Inserting {len(all_recipes)} recipes into database...")
        try:
            sqlite_utils.insert_rows_to_remote_db(
                rows=all_recipes,
                exclude_key='recipeId',  # Auto-incrementing primary key
                table_name=_TABLE_NAME,
                remote_db_file_path=_DB_PATH,
                app_name=_APP_NAME,
                env=env,
            )
            
            logging.info(f"   ✅ Successfully added {len(all_recipes)} recipes to Broccoli Recipe")
            
            # 5. Verify whether the recipes were actually inserted
            existing_recipes = sqlite_utils.get_rows_from_remote_device(
                table_name=_TABLE_NAME,
                remote_db_file_path=_DB_PATH,
                row_type=sqlite_schema_utils.Recipe,
                env=env,
            )
            logging.info(f"   ℹ️  The database currently contains {len(existing_recipes)} recipes")
            if len(existing_recipes) >= 3:
                logging.info(f"   ✅ Recipe initialization successful! Target recipe: '{recipe_title}'")
                for recipe in existing_recipes:
                    logging.info(f"      📖 {recipe.title}")
            else:
                logging.warning(f"   ⚠️  Insufficient recipe count; initialization may have failed")
                
        except Exception as e:
            logging.warning(f"   ⚠️  Failed to add recipes: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _setup_tasks(self, env):
        """Clean up and set up the Tasks app"""
        logging.info("   📝 setup Tasks...")
        
        from scendroid.task_evals.information_retrieval import task_app_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from datetime import datetime
        import random
        import uuid
        
        try:
            # 1. clean database
            task_app_utils.clear_task_db(env)
            logging.info("      ✅ Tasks database cleared")
            
            # 2. get base_date
            base_date_str = self.context.base_date or '2026-01-18'
            base_date = datetime.strptime(base_date_str, '%Y-%m-%d')
            
            # 3. Retrieve the "existing supplies" parameter and add it as a completed task
            st1 = self.generated_params.get('subtask_1', {})
            already_have = st1.get('already_have', ['Charcoal', 'Grill'])
            
            # Create the "existing supplies" task (marked as incomplete; the user must check it)
            have_tasks = []
            for i, item in enumerate(already_have):
                due_ts = int(base_date.replace(hour=8).timestamp()) * 1000
                created_ts = due_ts - 7 * 24 * 3600 * 1000  # Created 7 days ago
                
                task = sqlite_schema_utils.Task(
                    title=item,
                    importance=1,  # Medium priority
                    dueDate=due_ts,
                    hideUntil=0,
                    created=created_ts,
                    modified=created_ts,
                    completed=0,  # Incomplete; requires user check
                    deleted=0,
                    notes='Picnic supply item',
                    remoteId=str(uuid.uuid4().int),
                )
                have_tasks.append(task)
            
            # 4. Add distractor tasks (unrelated to the picnic)
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
                    importance=random.randint(0, 1),  # Low or medium priority
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
            
            # 5. Add all tasks
            all_tasks = have_tasks + distractor_tasks
            task_app_utils.add_tasks(all_tasks, env)
            
            logging.info(f"      ✅ Added {len(have_tasks)} existing supplies tasks")
            logging.info(f"      ✅ Added {len(distractor_tasks)} distractor tasks")
            logging.info(f"      📋 existing supplies: {already_have}")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Tasks setup failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _setup_music(self, env):
        """Initialize music files (for F3 and F4 tasks)"""
        logging.info("   🎵 setupmusicfile...")
        
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
            
            # 2. Retrieve songs to be created
            st3 = self.generated_params.get('subtask_3', {})
            songs = st3.get('songs', [])
            
            # Retrieve distractor songs from PARAM_TEMPLATES
            noise_songs = self.PARAM_TEMPLATES['subtask_3'].get('noise_songs', [])
            
            # 3. Create MP3 files for all songs
            all_songs = songs + noise_songs
            logging.info(f"      Step 2: Creating {len(all_songs)} music files...")
            
            for song_name in all_songs:
                # Construct the file path
                file_name = f"{song_name}.mp3"
                remote_path = file_utils.convert_to_posix_path(
                    device_constants.MUSIC_DATA, file_name
                )
                
                # Use user_data_generation to create the MP3 file
                user_data_generation.write_mp3_file_to_device(
                    remote_path,
                    env,
                    title=song_name,
                    artist=random.choice(user_data_generation.COMMON_GIVEN_NAMES),
                    duration_milliseconds=random.randint(3 * 60 * 1000, 5 * 60 * 1000),
                )
                
                logging.info(f"         🎵 Created: {file_name}")
            
            # 4. Scan the music directory to update the media library
            logging.info("      Step 3: Scanning music directory...")
            retro_music._scan_music_directory(env)
            time.sleep(2.0)
            
            logging.info(f"   ✅ Music file preparation complete ({len(all_songs)} songs)")
            logging.info(f"      📋 Playlist songs ({len(songs)} songs): {songs[:3]}...")
            logging.info(f"      📋 Distractor songs ({len(noise_songs)} songs): {noise_songs[:3]}...")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Music file preparation failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _setup_calendar_events(self, env):
        """createcalendarevent"""
        logging.info("   📅 createcalendarevent...")
        
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
        
        # Use the fixed base_date (2026-01-18)
        base_date = datetime(2026, 1, 18, 0, 0, 0)
        
        # Get event info from parameter
        shared = self.generated_params.get('shared', {})
        st2 = self.generated_params.get('subtask_2', {})
        
        event_title = st2.get('event_title', 'Mountain Picnic')
        original_location = shared.get('original_location', 'East Valley Trail')
        event_hour = st2.get('event_hour', 10)
        event_minute = st2.get('event_minute', 0)
        friends = shared.get('friends', [])
        
        # Create main activity event
        event_dt = base_date.replace(hour=event_hour, minute=event_minute, second=0)
        event_start_ts = cal_module.timegm(event_dt.timetuple())
        event_end_ts = event_start_ts + (4 * 60 * 60)  # 4hours
        
        # Build participant description
        attendee_names = [f['name'] for f in friends]
        user_name = shared.get('user_name', 'David')
        attendees_str = f"Attendees: {user_name}, " + ", ".join(attendee_names)
        
        event = sqlite_schema_utils.CalendarEvent(
            start_ts=event_start_ts,
            end_ts=event_end_ts,
            title=event_title,
            location=original_location,  # Use original location; the task is to change it
            description=attendees_str,
        )
        
        calendar_utils.add_events([event], env)
        time.sleep(2.0)
        
        logging.info(f"   📌 Event: {event_title} @ {event_hour}:{event_minute:02d}")
        logging.info(f"   📍 Location: {original_location} (to be changed)")
        logging.info(f"   👥 Attendees: {attendees_str}")
        logging.info("   ✅ calendareventcreatecomplete")
    
    def _setup_contacts(self, env):
        """create contact"""
        logging.info("   👥 create contact...")
        
        from scendroid.utils import contacts_utils
        from scendroid.env import adb_utils
        from scendroid.task_evals.common_validators import sms_validators
        import time
        
        # Clear existing contacts and SMS messages
        contacts_utils.clear_contacts(env.controller)
        time.sleep(1.0)
        
        try:
            sms_validators.clear_sms_and_threads(env.controller)
            logging.info("      ✅ SMSdatabase cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Failed to clear SMS: {e}")
        
        # getcontactinfo
        shared = self.generated_params.get('shared', {})
        friends = shared.get('friends', [])
        distractor_contacts = shared.get('distractor_contacts', [])
        
        # Add all contacts (event participants + distractor contacts)
        all_contacts = friends + distractor_contacts
        
        for contact in all_contacts:
            name = contact.get('name')
            phone = contact.get('phone')
            if not name or not phone:
                continue
            
            try:
                adb_utils.press_home_button(env.controller)
                time.sleep(1.5)
                
                contacts_utils.add_contact(
                    name, 
                    phone, 
                    env.controller,
                    ui_delay_sec=2.0
                )
                logging.info(f"      ✅ Added: {name} ({phone})")
                time.sleep(1.0)
            except Exception as e:
                logging.warning(f"      ⚠️  Failed to add {name}: {e}")
        
        # Clear SMS again (to ensure any messages generated during contact addition are cleared)
        try:
            sms_validators.clear_sms_and_threads(env.controller)
            
            # Force stop Simple SMS Messenger to refresh the UI
            adb_utils.close_app("simple sms", env.controller)
            time.sleep(0.5)
            
            logging.info("      ✅ SMS history cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Failed to clear SMS history: {e}")
        
        logging.info("   ✅ contactcreatecomplete")
    
    def _setup_photos(self, env):
        """Prepare photo file (for F8 task)"""
        logging.info("   📷 Preparing photo file...")
        
        from scendroid.env import device_constants, adb_utils
        import os
        import time
        
        try:
            base_path = device_constants.EMULATOR_DATA
            pictures_path = os.path.join(base_path, "Pictures")
            
            # Ensure the Pictures directory exists
            adb_utils.issue_generic_request([
                'shell', 'mkdir', '-p', pictures_path
            ], env.controller)
            
            # Get photo file name
            st8 = self.generated_params.get('subtask_8', {})
            scenery_photos = st8.get('scenery_photos', [])
            portrait_photos = st8.get('portrait_photos', [])
            
            all_photos = scenery_photos + portrait_photos
            
            # Create an empty PNG file (simulating a photo)
            for photo_name in all_photos:
                photo_path = os.path.join(pictures_path, photo_name)
                
                # Use dd to create a small test file
                adb_utils.issue_generic_request([
                    'shell', 'dd', 'if=/dev/zero', f'of={photo_path}',
                    'bs=1024', 'count=1'
                ], env.controller)
                
                logging.info(f"      📸 Created: {photo_name}")
            
            time.sleep(1.0)
            logging.info(f"   ✅ Photo file preparation complete ({len(all_photos)} files)")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Photo file preparation failed: {e}")
    
    def _cleanup_videos(self, env):
        """Clean up old video files (for Task 5 evaluation)"""
        logging.info("   🎬 Cleaning up old video files...")
        
        from scendroid.env import adb_utils
        
        # Clean up all possible video locations
        video_paths = [
            '/sdcard/DCIM/Camera',
            '/sdcard/Movies',
            '/storage/emulated/0/DCIM/Camera',
            '/storage/emulated/0/Movies',
        ]
        
        deleted_count = 0
        for video_path in video_paths:
            try:
                # Delete all video files
                cmd = ['shell', f'rm -f {video_path}/*.mp4 {video_path}/*.3gp {video_path}/*.mkv {video_path}/*.webm 2>/dev/null']
                adb_utils.issue_generic_request(cmd, env.controller)
                
                # Also delete .pending files (Camera temporary files)
                cmd = ['shell', f'rm -f {video_path}/.pending-* 2>/dev/null']
                adb_utils.issue_generic_request(cmd, env.controller)
                
                logging.info(f"      ✅ Cleaned: {video_path}")
            except Exception as e:
                logging.debug(f"      Cleanup {video_path} failed: {e}")
        
        logging.info("   ✅ videofilecleanup complete")
    
    def _setup_expenses(self, env):
        """Initialize this week's expense records (for F9 Q&A task)"""
        logging.info("   💰 Initializing this week's expense records...")
        
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.env import adb_utils
        from datetime import datetime, timedelta
        import time
        
        _DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
        _TABLE = "expense"
        
        try:
            # First launch and close the app to ensure database creation
            logging.info("      Step 1: Launch Expense app to initialize database...")
            try:
                adb_utils.launch_app("pro expense", env.controller)
                time.sleep(2.0)
            except Exception as e:
                logging.debug(f"      Launch failed (might be expected): {e}")
            
            try:
                adb_utils.close_app("com.arduia.expense", env.controller)
            except Exception as e:
                logging.debug(f"      Close failed (might be expected): {e}")
            time.sleep(1.0)
            
            # Clear existing expense records
            logging.info("      Step 2: Clearing existing expense records...")
            try:
                sqlite_utils.delete_all_rows_from_table(
                    table_name=_TABLE,
                    remote_db_file_path=_DB_PATH,
                    env=env,
                    app_name='pro expense'
                )
            except Exception as e:
                logging.debug(f"      Delete failed: {e}")
            
            # Get this week's expense parameters
            st9 = self.generated_params.get('subtask_9', {})
            weekly_expenses = st9.get('weekly_expenses', [])
            
            # Baseline date: 2026-01-18 (Sunday)
            base_date = datetime(2026, 1, 18)
            
            # Add this week's expense records
            logging.info("      Step 3: Adding this week's expense records...")
            expenses_to_add = []
            
            # Category ID mapping: 1=Others, 3=Food, 7=Transportation
            category_map = {
                'Food': 3,
                'Transport': 7,
                'Transportation': 7,
                'Others': 1,
            }
            
            for expense_info in weekly_expenses:
                day_offset = expense_info.get('day_offset', 1)
                expense_date = base_date - timedelta(days=day_offset)
                
                # Amounts are stored in "cents"
                amount_cents = int(expense_info.get('amount', 0) * 100)
                
                # Get category ID (default is 1 = Others)
                category_name = expense_info.get('category', 'Others')
                category_id = category_map.get(category_name, 1)
                
                expense = sqlite_schema_utils.Expense(
                    name=expense_info.get('name', 'Unknown'),
                    amount=amount_cents,
                    category=category_id,  # Must set up a valid category ID
                    created_date=int(expense_date.timestamp() * 1000),
                    modified_date=int(expense_date.timestamp() * 1000),
                )
                expenses_to_add.append(expense)
                
                logging.info(f"         📝 {expense_info['name']}: ${expense_info['amount']:.2f} (category: {category_name})")
            
            # Insert expense record
            if expenses_to_add:
                sqlite_utils.insert_rows_to_remote_db(
                    rows=expenses_to_add,
                    exclude_key='expense_id',  # Auto-increment primary key
                    table_name=_TABLE,
                    remote_db_file_path=_DB_PATH,
                    app_name='pro expense',
                    env=env
                )
            
            logging.info(f"   ✅ Weekly expense records initialization complete ({len(expenses_to_add)} entries)")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Expense record initialization failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _setup_opentracks_history(self, env):
        """
        Prepare OpenTracks environment and history records
        
        Fully copy the implementation of scenario_d._cleanup_opentracks()
        """
        logging.info("   🏃 Preparing OpenTracks environment...")
        
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
            
            # 2. Grant permissions and handle popups (optimized version: launch app only once)
            logging.info("      Step 2: granting OpenTracks permissions...")
            
            # get package name
            open_tracks_package = adb_utils.extract_package_name(
                adb_utils.get_adb_activity("open tracks")
            )
            
            # Grant location permission (before launching the app)
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
            
            # Launch the app and handle the Bluetooth permission popup (merged into a single launch)
            # Key: The Bluetooth permission popup appears only when the app is running!
            try:
                adb_utils.launch_app("activity tracker", env.controller)
                time.sleep(3.0)
                
                # Click the Bluetooth permission Allow button
                try:
                    controller = tools.AndroidToolController(env=env.controller)
                    controller.click_element("Allow")
                    logging.info("      ✅ bluetooth permission clicked 'Allow' button")
                    time.sleep(1.0)
                except Exception as e:
                    logging.debug(f"      Bluetooth permission already authorized or does not require handling: {e}")
                
                # Close the app
                adb_utils.close_app("activity tracker", env.controller)
            except Exception as e:
                logging.debug(f"      OpenTracks launch/handling: {e}")
            
            logging.info("      ✅ OpenTracks permissions granted")
            
            # 3. Add this week's exercise history data for the F7 task
            st7 = self.generated_params.get('subtask_7', {})
            weekly_distance = st7.get('weekly_distance', 15.5)  # km
            weekly_duration = st7.get('weekly_duration', 180)   # minutes
            activity_type = st7.get('activity_type', 'Hiking')
            
            logging.info(f"      Step 3: Adding this week's exercise history...")
            logging.info(f"         Activity: {activity_type}")
            logging.info(f"         Weekly Distance: {weekly_distance} km")
            logging.info(f"         Weekly Duration: {weekly_duration} minutes")
            
            # Use activity_app_utils to add history exercise records
            # Refer to the native scendroid's _generate_random_activity to generate diverse data
            try:
                from scendroid.task_evals.utils import sqlite_schema_utils
                from datetime import datetime, timedelta
                import random
                
                # Get base_date (today: Sunday, 2026-01-18)
                base_date = datetime(2026, 1, 18, 0, 0, 0)
                
                activities = []
                
                # ========== Add only this week's history data (Day -1 to Day -5) ==========
                # Note: Today's track will be added before Task 7 starts via initialize_subtask
                # Because logically, today's exercise has not yet started at scenario initialization time
                
                # Add history data for other days this week
                # Distance, duration, and time differ each day (simulating real user behavior)
                weekly_data = [
                    # (day_offset, distance_km, duration_min, hour, minute, name_suffix)
                    (1, 4.2, 52, 17, 15, "Evening Trail"),        # Saturday: 4.2 km, 52 min
                    (2, 6.8, 85, 7, 30, "Morning Hike"),          # Friday: 6.8 km, 85 min  
                    (3, 3.5, 45, 18, 0, "Sunset Walk"),           # Thursday: 3.5 km, 45 min
                    (4, 5.1, 62, 16, 45, "Afternoon Trek"),       # Wednesday: 5.1 km, 62 min
                    (5, 7.3, 95, 6, 15, "Dawn Adventure"),        # Tuesday: 7.3 km, 95 min
                ]
                
                for day_offset, distance_km, duration_min, hour, minute, name_suffix in weekly_data:
                    activity_date = base_date - timedelta(days=day_offset)
                    
                    distance_m = int(distance_km * 1000)
                    duration_ms = duration_min * 60 * 1000
                    
                    start_ts = int(activity_date.replace(hour=hour, minute=minute).timestamp() * 1000)
                    stop_ts = start_ts + duration_ms
                    
                    # Add minor random variations to make data more realistic
                    elevation_gain = random.randint(30, 180)
                    elevation_loss = random.randint(20, 120)
                    moving_ratio = 0.8 + random.random() * 0.15  # 80-95%
                    
                    activity = sqlite_schema_utils.SportsActivity(
                        name=name_suffix,
                        category=activity_type.lower(),
                        activity_type=activity_type.lower(),
                        description=f"{activity_type} session",
                        totaldistance=distance_m,
                        starttime=start_ts,
                        stoptime=stop_ts,
                        totaltime=duration_ms,
                        movingtime=int(duration_ms * moving_ratio),
                        avgspeed=distance_m / (duration_ms / 1000),
                        avgmovingspeed=distance_m / (duration_ms * moving_ratio / 1000),
                        elevationgain=elevation_gain,
                        elevationloss=elevation_loss,
                    )
                    activities.append(activity)
                    logging.info(f"         📊 Day -{day_offset}: {distance_km}km, {duration_min}min ({name_suffix})")
                
                # Add to database
                activity_app_utils._add_activities(activities, env)
                
                # Calculate totals (history data only, excluding today)
                total_distance_km = sum(a.totaldistance for a in activities) / 1000
                total_duration_min = sum(a.totaltime for a in activities) / (60 * 1000)
                logging.warning(f"      ✅ This week's exercise history prepared ({len(activities)} records, excluding today)")
                logging.warning(f"         📈 History total: {total_distance_km:.1f} km, {total_duration_min:.0f} min")
                logging.warning(f"         ℹ️ Today's track will be added before Task 7 starts")
                
            except Exception as e:
                logging.warning(f"      ⚠️ Failed to add history records: {e}")
            
            # Close the app
            adb_utils.close_app("activity tracker", env.controller)
            time.sleep(0.5)
            
            logging.info("   ✅ OpenTracks environment preparation complete")
            
        except Exception as e:
            logging.warning(f"   ⚠️ OpenTracks initialization failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _cleanup_app_data(self, env):
        """Clean up other app data"""
        logging.info("   🗑️  Cleaning up app data...")
        
        from scendroid.env import device_constants, adb_utils
        from scendroid.utils import file_utils
        from scendroid.task_evals.utils import sqlite_utils
        from scendroid.env.setup_device import apps
        import time
        
        # Cleanup Markor file (refer to scenario_d._cleanup_markor)
        try:
            markor_dir = device_constants.MARKOR_DATA  # "/storage/emulated/0/Documents/Markor"
            
            # Ensure the directory exists
            adb_utils.issue_generic_request(['shell', 'mkdir', '-p', markor_dir], env.controller)
            
            # Clean up all files in the directory
            file_utils.clear_directory(markor_dir, env.controller)
            logging.info("      ✅ Markor files cleaned up")
        except Exception as e:
            logging.warning(f"      ⚠️  Markor cleanup failed: {e}")
        
        # Note: Cleanup and initialization of Expense data are handled uniformly in _setup_expenses
        # Avoid duplicate cleanup here to prevent database corruption
        logging.info("      ℹ️ Expense data will be initialized in _setup_expenses")
        
        logging.info("   ✅ App data cleanup complete")
    
    def tear_down(self, env):
        """
        Cleanup at scenario end
        """
        super().tear_down(env)
        
        logging.info("🧹 cleanup Scenario F environment...")
        
        # rebuild Shopping container
        try:
            from scendroid.task_evals.webarena import container_manager
            logging.info("   🔄 rebuild Shopping container...")
            
            # extract console_port to ensure correct container rebuild
            console_port = None
            try:
                console_port = env.controller._env._coordinator._simulator._config.emulator_launcher.emulator_console_port
                logging.info(f"   📱 Emulator console port: {console_port}")
            except Exception as e:
                logging.warning(f"   ⚠️  Could not extract console_port: {e}")
            
            manager = container_manager.ShoppingContainerManager(console_port=console_port)
            manager.rebuild_container()
            logging.info(f"   ✅ Shopping container rebuilt (container: {manager.docker_container}, port: {manager.host_port})")
        except Exception as e:
            logging.warning(f"   ⚠️  container rebuild failed: {e}")
        
        logging.info("✅ Scenario F cleanup complete")

    
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
            self._reset_init_task1_recipe_tasks(subtask, env)
        elif task_id == 2:
            self._reset_init_task2_calendar(subtask, env)
        elif task_id == 3:
            self._reset_init_task3_sms(subtask, env)
        elif task_id == 4:
            self._reset_init_task4_music_playlist(subtask, env)
        elif task_id == 5:
            self._reset_init_task5_tracks_music(subtask, env)
        elif task_id == 6:
            self._reset_init_task6_camera_video(env)
        elif task_id == 7:
            self._reset_init_task7_shopping(subtask, env)
        elif task_id == 8:
            self._reset_init_task8_opentracks_qa(subtask, env)
        elif task_id == 9:
            self._reset_init_task9_files_organize(env)
        elif task_id == 10:
            self._reset_init_task10_expense(subtask, env)
        elif task_id == 11:
            self._reset_init_task11_markor_diary(subtask, env)
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
    
    def _reset_init_task1_recipe_tasks(self, subtask, env):
        """
        Task 1 (Picnic supplies verification and checklist creation - Broccoli Recipe + Tasks):
        Prerequisites: Broccoli Recipe data + cleared Tasks (including the "existing supplies" distractor task)
        """
        logging.info("   🔧 Reset Init Task 1: Setting up Broccoli Recipe + Tasks")
        
        # 1. initialize Broccoli Recipe
        self._setup_broccoli_recipe(env)
        
        # 2. Initialize Tasks (including the "existing supplies" task)
        self._setup_tasks(env)
        
        # 3. return to home screen
        try:
            from scendroid.env import adb_utils
            import time
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 1 initialization completed")
    
    def _reset_init_task2_calendar(self, subtask, env):
        """
        Task 2 (Update calendar event location - Calendar):
        Prerequisites: Calendar event (original location + participants)
        """
        logging.info("   🔧 Reset Init Task 2: Creating calendar event with original location")
        
        # Create calendar event (using the original location)
        self._setup_calendar_events(env)
        
        # return to home screen
        try:
            from scendroid.env import adb_utils
            import time
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 2 initialization completed")
    
    def _reset_init_task3_sms(self, subtask, env):
        """
        Task 3 (Notify participants about location change - SMS):
        prerequisites:
        - Calendar event (updated location)
        - Contact (event participants + distractor contact)
        - SMSclear
        """
        logging.info("   🔧 Reset Init Task 3: Creating calendar event + contacts, clearing SMS")
        
        from scendroid.task_evals.single.calendar import calendar_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from scendroid.env import adb_utils
        from datetime import datetime
        import calendar as cal_module
        import time
        
        # 1. Clear and create calendar event (using the new location, simulating completion of Task 2)
        try:
            # clear Calendar
            adb_utils.clear_app_data("com.simplemobiletools.calendar.pro", env.controller)
            time.sleep(1.0)
            
            # Launch and close Calendar
            adb_utils.start_activity(
                "com.simplemobiletools.calendar.pro/.activities.MainActivity",
                None, env.controller
            )
            time.sleep(2.0)
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            
            # Reconfirm timezone
            self._ensure_utc_timezone(env)
            
            # Clear existing events
            calendar_utils.clear_calendar_db(env)
            
            # Create event (using the new location)
            base_date = datetime(2026, 1, 18, 0, 0, 0)
            
            shared = self.generated_params.get('shared', {})
            st2 = self.generated_params.get('subtask_2', {})
            
            event_title = st2.get('event_title', 'Mountain Picnic')
            new_location = shared.get('new_location', 'West Peak Lookout')  # Use the new location
            event_hour = st2.get('event_hour', 10)
            event_minute = st2.get('event_minute', 0)
            friends = shared.get('friends', [])
            
            event_dt = base_date.replace(hour=event_hour, minute=event_minute, second=0)
            event_start_ts = cal_module.timegm(event_dt.timetuple())
            event_end_ts = event_start_ts + (4 * 60 * 60)
            
            attendee_names = [f['name'] for f in friends]
            user_name = shared.get('user_name', 'David')
            attendees_str = f"Attendees: {user_name}, " + ", ".join(attendee_names)
            
            event = sqlite_schema_utils.CalendarEvent(
                start_ts=event_start_ts,
                end_ts=event_end_ts,
                title=event_title,
                location=new_location,  # New location
                description=attendees_str,
            )
            
            calendar_utils.add_events([event], env)
            time.sleep(1.0)
            
            logging.info(f"      ✅ Calendar event created (new location: {new_location})")
            
        except Exception as e:
            logging.warning(f"      ⚠️  calendareventcreatefailed: {e}")
        
        # 2. create contact
        self._setup_contacts(env)
        
        # 3. Return to home screen (_setup_contacts already includes a home press within its loop; confirm once more here)
        try:
            from scendroid.env import adb_utils
            import time
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 3 initialization completed")
    
    def _reset_init_task4_music_playlist(self, subtask, env):
        """
        Task 4 (Create ordered hiking playlist - Retro Music):
        Prerequisites: Music files (playlist songs + distractor songs)
        """
        logging.info("   🔧 Reset Init Task 4: Setting up music files")
        
        # Prepare music files
        self._setup_music(env)
        
        # return to home screen
        try:
            from scendroid.env import adb_utils
            import time
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 4 initialization completed")
    
    def _reset_init_task5_tracks_music(self, subtask, env):
        """
        Task 5 (Start track recording and music playback - OpenTracks + Retro Music):
        prerequisites:
        - OpenTracks cleared + permissions granted
        - Music files + playlist already created (simulating output of Task 4)
        """
        logging.info("   🔧 Reset Init Task 5: Setting up OpenTracks + playlist")
        
        from scendroid.task_evals.information_retrieval import activity_app_utils
        from scendroid.task_evals.single import retro_music
        from scendroid.env import adb_utils, tools
        import time
        
        # 1. setup OpenTracks environment
        try:
            # clean database
            try:
                activity_app_utils.clear_db(env)
                logging.info("      ✅ OpenTracks database cleared")
            except Exception as e:
                logging.debug(f"      Database clear failed: {e}")
            
            # grant permissions
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
            
            # Launch the app and handle Bluetooth permission dialog
            try:
                adb_utils.launch_app("activity tracker", env.controller)
                time.sleep(3.0)
                
                try:
                    controller = tools.AndroidToolController(env=env.controller)
                    controller.click_element("Allow")
                    logging.info("      ✅ bluetooth permission clicked 'Allow' button")
                    time.sleep(1.0)
                except Exception as e:
                    logging.debug(f"      Bluetooth permission already authorized or does not require handling: {e}")
                
                adb_utils.close_app("activity tracker", env.controller)
            except Exception as e:
                logging.debug(f"      OpenTracks launch/handling: {e}")
            
            logging.info("      ✅ OpenTracks permissions granted")
            
        except Exception as e:
            logging.warning(f"      ⚠️  OpenTracks setup failed: {e}")
        
        # 2. Prepare music files
        self._setup_music(env)
        
        # 3. Clear playlist database (ensure agent creates playlist from a clean state)
        # ℹ️ The retro_music module does not have _create_playlist, so playlists cannot be pre-created. 
        # Playlist creation is performed by the agent during the task (reset_user_instruction already includes this step). 
        try:
            retro_music._clear_playlist_dbs(env)
            logging.info("      ✅ Playlist database has been cleared (the agent will create a playlist during the task)")
        except Exception as e:
            logging.warning(f"      ⚠️  Playlist database clear failed: {e}")
        
        # 4. return to home screen
        try:
            from scendroid.env import adb_utils as _adb
            import time as _time
            _adb.press_home_button(env.controller)
            _time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 5 initialization completed")
    
    def _reset_init_task6_camera_video(self, env):
        """
        Task 6 (Capture dynamic scenery - Camera - Video Mode):
        prerequisites: Clear old video files
        """
        logging.info("   🔧 Reset Init Task 6: Clearing old videos")
        
        self._cleanup_videos(env)
        
        # return to home screen
        try:
            from scendroid.env import adb_utils
            import time
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 6 initialization completed")
    
    def _reset_init_task7_shopping(self, subtask, env):
        """
        Task 7 (Dynamic picnic supply replenishment - Shopping):
        prerequisites: WebArena login + Shopping homepage
        
        ⚠️ Note: In reset mode, the parent class's initialize_subtask() returns immediately after calling _reset_initialize_subtask()
        and does not execute the subsequent shopping evaluator initialization logic. 
        Therefore, evaluator.initialize_task(env) must be explicitly called here. 
        """
        logging.info("   🔧 Reset Init Task 7: Shopping (Chrome cleanup + WebArena login)")
        
        # Call the Shopping evaluator's initialize_task (handles Chrome cleanup + WebArena login + navigation to the starting page)
        try:
            evaluator = subtask['evaluator_instance']
            logging.info("      🛒 Initializing Shopping evaluator (Chrome cleanup + WebArena login)...")
            evaluator.initialize_task(env)
            logging.info("      ✅ Shopping evaluator initialized (logged in, on Shopping homepage)")
        except Exception as e:
            logging.warning(f"      ⚠️  Shopping evaluator initialization failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
        
        # ℹ️ Do not return to the home screen — after Task 7 initialization completes, the app should remain on the Shopping App homepage
        # At the end of evaluator.initialize_task(), the app is already on the Shopping homepage, so the agent can operate directly
        logging.info("      ✅ Task 7 initialization completed (staying on Shopping homepage)")
    
    def _reset_init_task8_opentracks_qa(self, subtask, env):
        """
        Task 8 (Exercise data statistics - OpenTracks QA):
        prerequisites:
        - This week's historical exercise data (Day-5 to Day-1)
        - Today's track (simulated from Task 5 recording)
        """
        logging.info("   🔧 Reset Init Task 8: Setting up OpenTracks with weekly data + today's track")
        
        from scendroid.task_evals.information_retrieval import activity_app_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from scendroid.env import adb_utils, tools
        from datetime import datetime, timedelta
        import time
        import random
        
        try:
            # 1. clean database
            try:
                activity_app_utils.clear_db(env)
                logging.info("      ✅ OpenTracks database cleared")
            except Exception as e:
                logging.debug(f"      Database clear failed: {e}")
            
            # 2. grant permissions
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
            
            # Launch the app and handle Bluetooth permission
            try:
                adb_utils.launch_app("activity tracker", env.controller)
                time.sleep(3.0)
                
                try:
                    controller = tools.AndroidToolController(env=env.controller)
                    controller.click_element("Allow")
                    time.sleep(1.0)
                except Exception as e:
                    logging.debug(f"      Bluetooth permission already authorized or does not require handling: {e}")
                
                adb_utils.close_app("activity tracker", env.controller)
            except Exception as e:
                logging.debug(f"      OpenTracks launch/handling: {e}")
            
            # 3. Add this week's exercise data
            st7 = self.generated_params.get('subtask_7', {})
            activity_type = st7.get('activity_type', 'Hiking')
            
            base_date = datetime(2026, 1, 18, 0, 0, 0)
            
            activities = []
            
            # ========== Today's track (simulated from Task 5 recording) ==========
            today_distance_m = 8500  # 8.5 km
            today_duration_ms = 150 * 60 * 1000  # 2.5 hours
            today_start = base_date.replace(hour=9, minute=30)
            today_stop_ts = int(today_start.timestamp() * 1000) + today_duration_ms
            
            today_activity = sqlite_schema_utils.SportsActivity(
                name=f"Today's {activity_type}",
                category=activity_type.lower(),
                activity_type=activity_type.lower(),
                description=f"Morning {activity_type.lower()}",
                totaldistance=today_distance_m,
                starttime=int(today_start.timestamp() * 1000),
                stoptime=today_stop_ts,
                totaltime=today_duration_ms,
                movingtime=int(today_duration_ms * 0.85),
                avgspeed=today_distance_m / (today_duration_ms / 1000),
                avgmovingspeed=today_distance_m / (today_duration_ms * 0.85 / 1000),
                elevationgain=320,
                elevationloss=180,
            )
            
            activities.append(today_activity)
            logging.info(f"         🔵 TODAY: {today_distance_m/1000:.1f}km, {today_duration_ms/60000:.0f}min")
            
            # ========== This week's historical data ==========
            random.seed(2026)
            
            weekly_data = [
                (1, 4.2, 52, 17, 15, "Evening Trail"),
                (2, 6.8, 85, 7, 30, "Morning Hike"),
                (3, 3.5, 45, 18, 0, "Sunset Walk"),
                (4, 5.1, 62, 16, 45, "Afternoon Trek"),
                (5, 7.3, 95, 6, 15, "Dawn Adventure"),
            ]
            
            for day_offset, distance_km, duration_min, hour, minute, name_suffix in weekly_data:
                activity_date = base_date - timedelta(days=day_offset)
                
                distance_m = int(distance_km * 1000)
                duration_ms = duration_min * 60 * 1000
                
                start_ts = int(activity_date.replace(hour=hour, minute=minute).timestamp() * 1000)
                stop_ts = start_ts + duration_ms
                
                elevation_gain = random.randint(30, 180)
                elevation_loss = random.randint(20, 120)
                moving_ratio = 0.8 + random.random() * 0.15
                
                activity = sqlite_schema_utils.SportsActivity(
                    name=name_suffix,
                    category=activity_type.lower(),
                    activity_type=activity_type.lower(),
                    description=f"{activity_type} session",
                    totaldistance=distance_m,
                    starttime=start_ts,
                    stoptime=stop_ts,
                    totaltime=duration_ms,
                    movingtime=int(duration_ms * moving_ratio),
                    avgspeed=distance_m / (duration_ms / 1000),
                    avgmovingspeed=distance_m / (duration_ms * moving_ratio / 1000),
                    elevationgain=elevation_gain,
                    elevationloss=elevation_loss,
                )
                activities.append(activity)
                logging.info(f"         📊 Day -{day_offset}: {distance_km}km, {duration_min}min ({name_suffix})")
            
            # Add to database
            activity_app_utils._add_activities(activities, env)
            
            total_distance_km = sum(a.totaldistance for a in activities) / 1000
            total_duration_min = sum(a.totaltime for a in activities) / (60 * 1000)
            
            logging.info(f"      ✅ Exercise data prepared ({len(activities)} records)")
            logging.info(f"         📈 WEEKLY TOTAL: {total_distance_km:.1f}km, {total_duration_min:.0f}min")
            
        except Exception as e:
            logging.warning(f"      ⚠️  OpenTracks setup failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
        
        # return to home screen
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 8 initialization completed")
    
    def _reset_init_task9_files_organize(self, env):
        """
        Task 9 (Photo deduplication and structured organization - Files):
        prerequisites: Photo files (scenery photos + portrait photos, including duplicates)
        """
        logging.info("   🔧 Reset Init Task 9: Creating photo files")
        
        # Prepare photo files
        self._setup_photos(env)
        
        # return to home screen
        try:
            from scendroid.env import adb_utils
            import time
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 9 initialization completed")
    
    def _reset_init_task10_expense(self, subtask, env):
        """
        Task 10 (Shopping expense and financial recordkeeping - Pro Expense):
        prerequisites: This week's historical expense records (excluding today's meat expense)
        """
        logging.info("   🔧 Reset Init Task 10: Setting up weekly expenses")
        
        # Initialize this week's expense records
        self._setup_expenses(env)
        
        # return to home screen
        try:
            from scendroid.env import adb_utils
            import time
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 10 initialization completed")
    
    def _reset_init_task11_markor_diary(self, subtask, env):
        """
        Task 11 (Comprehensive hiking journal generation - Markor):
        prerequisites:
        - Photo files have been organized (simulated output from Task 9)
        - This week's expenses + today's meat expense (simulated output from Task 10)
        - Markorclear
        """
        logging.info("   🔧 Reset Init Task 11: Setting up photos + expenses, clearing Markor")
        
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        from scendroid.env.setup_device import apps
        from scendroid.env import adb_utils, device_constants
        from scendroid.utils import file_utils
        from datetime import datetime, timedelta
        import time
        import os
        
        # 1. Prepare photo files (already organized into Scenery and Portraits folders)
        try:
            base_path = device_constants.EMULATOR_DATA
            pictures_path = os.path.join(base_path, "Pictures")
            
            # Ensure the Pictures directory exists
            adb_utils.issue_generic_request([
                'shell', 'mkdir', '-p', pictures_path
            ], env.controller)
            
            # Create Scenery and Portraits subfolders
            scenery_path = os.path.join(pictures_path, "Scenery")
            portraits_path = os.path.join(pictures_path, "Portraits")
            
            adb_utils.issue_generic_request([
                'shell', 'mkdir', '-p', scenery_path
            ], env.controller)
            adb_utils.issue_generic_request([
                'shell', 'mkdir', '-p', portraits_path
            ], env.controller)
            
            # Get photo file names
            st8 = self.generated_params.get('subtask_8', {})
            scenery_photos = st8.get('scenery_photos', [])
            portrait_photos = st8.get('portrait_photos', [])
            
            # Create scenery photos (placed in the Scenery folder, deduplicated)
            # Remove duplicate files (e.g., 1025_Lake_copy.png)
            unique_scenery = [p for p in scenery_photos if 'copy' not in p.lower() and 'dup' not in p.lower()]
            for photo_name in unique_scenery:
                photo_path = os.path.join(scenery_path, photo_name)
                adb_utils.issue_generic_request([
                    'shell', 'dd', 'if=/dev/zero', f'of={photo_path}',
                    'bs=1024', 'count=1'
                ], env.controller)
                logging.info(f"      📸 Scenery: {photo_name}")
            
            # Create portrait photos (store in the Portraits folder, deduplicated)
            unique_portraits = [p for p in portrait_photos if 'copy' not in p.lower() and 'dup' not in p.lower()]
            for photo_name in unique_portraits:
                photo_path = os.path.join(portraits_path, photo_name)
                adb_utils.issue_generic_request([
                    'shell', 'dd', 'if=/dev/zero', f'of={photo_path}',
                    'bs=1024', 'count=1'
                ], env.controller)
                logging.info(f"      📸 Portrait: {photo_name}")
            
            time.sleep(1.0)
            logging.info(f"      ✅ Photos organized into Scenery ({len(unique_scenery)} photos) and Portraits ({len(unique_portraits)} photos)")
            
        except Exception as e:
            logging.warning(f"      ⚠️  Photo organization failed: {e}")
        
        # 2. Set up Expense and add this week's expenses + today's meat payment (simulate Task 10's output)
        _DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
        _TABLE = "expense"
        _APP_NAME = "pro expense"
        
        try:
            # Launch the Expense app
            try:
                adb_utils.launch_app("pro expense", env.controller)
                time.sleep(2.0)
                adb_utils.close_app("com.arduia.expense", env.controller)
            except Exception as e:
                logging.debug(f"      Launch failed: {e}")
            time.sleep(1.0)
            
            # Clear existing expenses
            try:
                sqlite_utils.delete_all_rows_from_table(
                    table_name=_TABLE,
                    remote_db_file_path=_DB_PATH,
                    env=env,
                    app_name=_APP_NAME
                )
            except Exception as e:
                logging.debug(f"      Delete failed: {e}")
            
            # get parameters
            st9 = self.generated_params.get('subtask_9', {})
            weekly_expenses = st9.get('weekly_expenses', [])
            meat_amount = st9.get('meat_amount', 113.27)
            
            base_date = datetime(2026, 1, 18)
            
            expenses_to_add = []
            
            # Add this week's historical expenses
            category_map = {
                'Food': 3,
                'Transport': 7,
                'Transportation': 7,
                'Others': 1,
            }
            
            for expense_info in weekly_expenses:
                day_offset = expense_info.get('day_offset', 1)
                expense_date = base_date - timedelta(days=day_offset)
                
                amount_cents = int(expense_info.get('amount', 0) * 100)
                category_name = expense_info.get('category', 'Others')
                category_id = category_map.get(category_name, 1)
                
                expense = sqlite_schema_utils.Expense(
                    name=expense_info.get('name', 'Unknown'),
                    amount=amount_cents,
                    category=category_id,
                    created_date=int(expense_date.timestamp() * 1000),
                    modified_date=int(expense_date.timestamp() * 1000),
                )
                expenses_to_add.append(expense)
                logging.info(f"         📝 {expense_info['name']}: ${expense_info['amount']:.2f}")
            
            # Add today's meat payment (simulate Task 10's output)
            meat_expense = sqlite_schema_utils.Expense(
                name="Meat Substitute",
                amount=int(meat_amount * 100),
                category=3,  # Food
                created_date=int(base_date.timestamp() * 1000),
                modified_date=int(base_date.timestamp() * 1000),
            )
            expenses_to_add.append(meat_expense)
            logging.info(f"         📝 Meat Substitute: ${meat_amount:.2f} (today)")
            
            # Insert expense records
            if expenses_to_add:
                sqlite_utils.insert_rows_to_remote_db(
                    rows=expenses_to_add,
                    exclude_key='expense_id',
                    table_name=_TABLE,
                    remote_db_file_path=_DB_PATH,
                    app_name=_APP_NAME,
                    env=env
                )
            
            logging.info(f"      ✅ This week's expenses prepared ({len(expenses_to_add)} entries)")
            
        except Exception as e:
            logging.warning(f"      ⚠️  Expense record setup failed: {e}")
        
        # 3. clear Markor
        try:
            markor_dir = device_constants.MARKOR_DATA
            adb_utils.issue_generic_request(['shell', 'mkdir', '-p', markor_dir], env.controller)
            file_utils.clear_directory(markor_dir, env.controller)
            logging.info("      ✅ Markor cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Markor cleanup failed: {e}")
        
        # 4. return to home screen
        try:
            adb_utils.press_home_button(env.controller)
            import time
            time.sleep(1.0)
        except Exception:
            pass
        
        logging.info("      ✅ Task 11 initialization completed")

