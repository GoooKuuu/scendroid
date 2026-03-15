"""
Scenario C: Relaxed Saturday

Weekend relaxation scenario, containing 11 subtasks:
1. Disable Weekend Alarm (Clock)
2. Search Breakfast Recipe (Broccoli Recipe - QA) - Enhanced version: ingredients + cooking time constraint
3. Write Recipe to Markor - Enhanced version: parameterized evaluation
4. Set Cooking Timer (Clock) - Enhanced version: synchronized with recipe cooking time
5. Photo and Organize (Camera + Files)
6. Text Friend for Meetup (SMS)
7. Order Eggs Online (Shopping)
8. Record Expense
9. Check Walk Stats with Friend (OpenTracks QA) - Improved version: view data for walking with a friend
10. Text Friend Got Home Safe (SMS) - 🆕 Send a safety message to a friend after walking
11. Weekend Summary (Markor)

features:
- Spans two days (Friday evening -> Saturday all day)
- Relaxed pace, tasks distributed
- Includes QA tasks and cross-application collaboration
- Life-like scenario
- Tasks 2->4 interlinked (recipe cooking time)
- Tasks 6->9->10 interlinked (schedule walk with friend -> check statistics -> send safety message)
"""

from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.scenario.base import BaseScenarioEvaluator


@AppRegistry.register_evaluator("ScenarioB_RelaxedSaturday")
class ScenarioBRelaxedSaturdayEvaluator(BaseScenarioEvaluator):
    """
    scenario C: Relaxed Saturday for {user_name} - Parameterized version (enhanced)
    
    description:
    Simulate a weekend rest day, from canceling an alarm on Friday evening to reviewing one day on Saturday evening
    Covers life logging, leisure activities, shopping, and fitness
    
    Subtasks (11 total):
    1. Disable Weekend Alarm (Clock)
    2. Search Breakfast Recipe (Broccoli Recipe - QA) - Requires finding an egg-based recipe with cooking time ≤15 minutes
    3. Write Recipe to Markor - Record the found recipe (parameterized evaluation)
    4. Set Cooking Timer (Clock) - Set up the timer based on the recipe's cooking time
    5. Photo and Organize (Camera + Files)
    6. Text Friend for Meetup (SMS) - Text a friend to schedule a walking meetup
    7. Order Eggs Online (Shopping)
    8. Record Expense
    9. Check Walk Stats with Friend (OpenTracks QA) - View duration and distance of the walk with a friend
    10. Text Friend Got Home Safe (SMS) - 🆕 Send an SMS to a friend confirming safe arrival after walking
    11. Weekend Summary (Markor)
    
    features:
    - Spans two days (Friday evening -> Saturday all day)
    - Tasks 2->3->4 interlinked: recipe -> note -> cooking time
    - Tasks 6->9->10 interlinked: schedule walk with friend -> check statistics -> send safety message
    - Includes distractor design
    
    rating:
    - All tasks, etc., weighted
    - report completion status of each task when done
    """
    
    app_names = ("clock", "broccoli recipe", "markor", "camera", "files",
                  "simple sms messenger", "chrome", "pro expense", "opentracks")
    
    scenario_id = "C"
    complexity = 2.5  # Increased interlinking complexity
    
    # ========== parameter template definition ==========
    PARAM_TEMPLATES = {
        # shared parameters (used across tasks)
        'shared': {
            'user_names': ['David', 'Sarah', 'Michael', 'Emily', 'Alex'],
            'friend_info': [
                {'name': 'Bob Johnson', 'phone': '555-0102'},
                {'name': 'Alice Davis', 'phone': '555-0201'},
                {'name': 'Charlie Wilson', 'phone': '555-0301'},
                {'name': 'Diana Smith', 'phone': '555-0401'},
            ],
            'meetup_locations': ['Central Park entrance', 'Downtown Cafe', 'City Library', 'Riverside Park'],
            # Meeting time (used for Task 6 and Task 9 interlinking)
            # Format: (display time, 24-hour format hours, minutes)
            'meetup_times': [
                ('3:00 PM', 15, 0),
                ('2:30 PM', 14, 30),
                ('4:00 PM', 16, 0),
                ('3:30 PM', 15, 30),
            ],
        },
        
        # Subtask 1: cancel alarm
        'subtask_1': {
            'alarm_hours': [7, 8, 9],
            'alarm_minutes': [0, 15, 30],
        },
        
        # Subtasks 2, 3, and 4: breakfast recipe (enhanced version: includes cooking time)
        # 🆕 Correct answer: satisfies ingredient requirements + cooking time ≤15 minutes
        # 🆕 Distractor: satisfies ingredients but cooking time >15 minutes, or satisfies cooking time but incorrect ingredients
        'subtask_2_3_4': {
            # 🆕 Note: recipe name must not contain trigger words such as "quick", "fast", "easy", etc., to avoid directly indicating the answer
            'correct_recipes': [
                {
                    'title': 'Scrambled Eggs with Toast',
                    'prep_time': 10,  # minutes
                    'ingredients': ['eggs', 'butter', 'salt', 'pepper', 'bread'],
                    'directions': '1. Beat eggs with salt and pepper. 2. Melt butter in pan. 3. Pour eggs and scramble. 4. Toast bread. 5. Serve together.',
                },
                {
                    'title': 'Sunny Side Up Eggs',
                    'prep_time': 8,  # minutes
                    'ingredients': ['eggs', 'oil', 'salt', 'pepper'],
                    'directions': '1. Heat oil in pan. 2. Crack eggs carefully. 3. Cook until whites set. 4. Season and serve.',
                },
                {
                    'title': 'Cheese Egg Wrap',  # 🆕 Remove "Quick", change to "Cheese"
                    'prep_time': 12,  # minutes
                    'ingredients': ['eggs', 'butter', 'salt', 'tortilla', 'cheese'],
                    'directions': '1. Scramble eggs with butter. 2. Season with salt. 3. Warm tortilla. 4. Add eggs and cheese. 5. Roll and serve.',
                },
            ],
            # Distractor: satisfies ingredients but cooking time is too long
            'distractor_long_time': [
                {
                    'title': 'Eggs Benedict',
                    'prep_time': 35,  # Too long!
                    'ingredients': ['eggs', 'butter', 'english muffin', 'ham', 'hollandaise'],
                    'directions': '1. Poach eggs (10 min). 2. Make hollandaise (15 min). 3. Toast muffins. 4. Assemble and serve.',
                },
                {
                    'title': 'Shakshuka Eggs',
                    'prep_time': 30,  # Too long!
                    'ingredients': ['eggs', 'tomatoes', 'onion', 'spices', 'oil'],
                    'directions': '1. Saute onions (10 min). 2. Add tomatoes and simmer (15 min). 3. Crack eggs and cook. 4. Serve with bread.',
                },
            ],
            # Distractor: short cooking time but incorrect ingredients (no eggs)
            'distractor_no_eggs': [
                {
                    'title': 'Fresh Avocado Toast',  # 🆕 remove "Quick", change to "Fresh"
                    'prep_time': 5,
                    'ingredients': ['avocado', 'bread', 'lemon', 'salt', 'pepper'],
                    'directions': '1. Toast bread. 2. Mash avocado. 3. Season and spread. 4. Serve immediately.',
                },
                {
                    'title': 'Fruit Yogurt Bowl',
                    'prep_time': 5,
                    'ingredients': ['yogurt', 'berries', 'honey', 'granola'],
                    'directions': '1. Add yogurt to bowl. 2. Top with berries. 3. Drizzle honey. 4. Add granola.',
                },
            ],
        },
        
        # Subtask 5: Photo folder
        'subtask_5': {
            'folder_names': [
                'Weekend/Breakfast',
                'Saturday/Food',
                'Weekend/Cooking',
                'MyPhotos/Breakfast',
            ],
        },
        
        # Subtask 7: Shopping items
        'subtask_7': {
            'products': [
                {'sku': 'B078158XZ4', 'name': 'Egg Organic 12-count', 'price': 11.8, 'keywords': ['Egg', 'Organic', '12']},
                {'sku': 'B07FM3WKJ8', 'name': 'Outdoor Patio Folding Side Table green', 'price': 54.99, 'keywords': ['Outdoor', 'Table', 'Green']},
                {'sku': 'B07KB88W7G', 'name': 'Dentemp Ora-GUARD Bruxism Night Guard (Two Pack)', 'price': 54.99, 'keywords': ['Dentemp', 'Bruxism', 'Two Pack']},
                {'sku': 'B074QVN413', 'name': 'Tide PODS Spring Meadow Scent, 81 Count', 'price': 68.97, 'keywords': ['Tide', 'PODS', '81 Count']},
                {'sku': 'B07ZQT1L6B', 'name': 'Apple iPhone 11 Pro, US Version, 256GB, Silver', 'price': 539.99, 'keywords': ['Apple', 'iPhone', '11 Pro']},
            ],
        },
        
        # Subtask 8: Expense tracking (fixed as "Shopping", linked with Task 7)
        'subtask_8': {
            'expense_name': 'Shopping',
            'expense_note': 'Weekend order',
        },
        
        # 🆕 Subtask 9: View walking data with a friend (linked with Task 6)
        # Correct trajectory: Walking with a friend after the scheduled time (location matches Task 6)
        # Distractor trajectory: Walking at other locations (🆕 distinguished by location, all occurring in the afternoon)
        'subtask_9': {
            # Statistical data for the correct trajectory (matches the scheduled time in Task 6)
            'correct_walk_distance_km': [2.5, 3.0, 2.8, 3.2],  # kilometers
            'correct_walk_duration_min': [35, 40, 38, 45],  # minutes
            # Distractor trajectories (🆕 distinguished by location, all within the afternoon timeframe)
            'distractor_activities': [
                {'name': 'Walk', 'location': 'Riverside Park', 'time_offset_hours': -2, 'distance_km': 5.0, 'duration_min': 30},    # around 1 p.m.
                {'name': 'Walk', 'location': 'Downtown Loop', 'time_offset_hours': -1, 'distance_km': 1.2, 'duration_min': 15},     # around 2 p.m.
                {'name': 'Walk', 'location': 'Lake Trail', 'time_offset_hours': 2, 'distance_km': 4.5, 'duration_min': 25},         # around 4 p.m.
            ],
        },
        
        # 🆕 Subtask 10: Send an SMS message to a friend after walking to report safety (linked with Tasks 6 and 9)
        'subtask_10': {
            'safe_home_messages': [
                "I'm home safe now. Thanks for the lovely walk today!",
                "Just got home safely. Had a great time walking with you!",
                "Made it home! Thanks for joining me for the walk.",
                "Home safe and sound. Really enjoyed our walk today!",
            ],
        },
    }
    
    @classmethod
    def generate_random_params(cls, seed=None):
        """
        Generate random parameters for Scenario C (enhanced version)
        
        🆕 Linked design:
        - Task 2->3->4:recipe -> note -> cooking time
        - Task 6 -> Task 9: Schedule a meeting with a friend -> View walking data
        
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
        friend = random.choice(cls.PARAM_TEMPLATES['shared']['friend_info'])
        meetup_location = random.choice(cls.PARAM_TEMPLATES['shared']['meetup_locations'])
        # 🆕 Meeting time now includes 24-hour format information (used for Task 9 linkage)
        meetup_time_tuple = random.choice(cls.PARAM_TEMPLATES['shared']['meetup_times'])
        meetup_time_display = meetup_time_tuple[0]  # "3:00 PM"
        meetup_time_hour = meetup_time_tuple[1]  # 15
        meetup_time_minute = meetup_time_tuple[2]  # 0
        
        shared_params = {
            'user_name': user_name,
            'friend_name': friend['name'],
            'friend_phone': friend['phone'],
            'meetup_location': meetup_location,
            'meetup_time': meetup_time_display,
            'meetup_time_hour': meetup_time_hour,  # 🆕 24-hour format
            'meetup_time_minute': meetup_time_minute,  # 🆕 minutes
        }
        
        # 2. Generate subtask 1 parameters (alarm)
        alarm_hour = random.choice(cls.PARAM_TEMPLATES['subtask_1']['alarm_hours'])
        alarm_minute = random.choice(cls.PARAM_TEMPLATES['subtask_1']['alarm_minutes'])
        
        subtask_1_params = {
            'alarm_hour': alarm_hour,
            'alarm_minute': alarm_minute,
        }
        
        # 3. 🆕 Generate subtask 2, 3, and 4 parameters (recipe — enhanced version)
        # Select one correct recipe (ingredients include eggs + cooking time ≤ 15 minutes)
        correct_recipe = random.choice(cls.PARAM_TEMPLATES['subtask_2_3_4']['correct_recipes'])
        
        # Generate distractor list
        distractor_long = cls.PARAM_TEMPLATES['subtask_2_3_4']['distractor_long_time']
        distractor_no_eggs = cls.PARAM_TEMPLATES['subtask_2_3_4']['distractor_no_eggs']
        
        subtask_2_3_4_params = {
            'correct_recipe': correct_recipe,
            'recipe_title': correct_recipe['title'],
            'recipe_prep_time': correct_recipe['prep_time'],
            'recipe_ingredients': correct_recipe['ingredients'],
            'recipe_directions': correct_recipe['directions'],
            'distractor_long_time': distractor_long,  # Distractor: cooking time too long
            'distractor_no_eggs': distractor_no_eggs,  # Distractor: no eggs
        }
        
        # 4. 🆕 Subtask 4 parameters (timer — linked with recipe)
        # Use the recipe's cooking time as the timer duration!
        timer_minutes = correct_recipe['prep_time']
        subtask_4_params = {
            'timer_minutes': timer_minutes,
        }
        
        # 5. Generate subtask 5 parameters (photo folder)
        folder_name = random.choice(cls.PARAM_TEMPLATES['subtask_5']['folder_names'])
        subtask_5_params = {
            'folder_name': folder_name,
        }
        
        # 6. Generate subtask 7 parameters (shopping)
        product = random.choice(cls.PARAM_TEMPLATES['subtask_7']['products'])
        subtask_7_params = product.copy()
        
        # 7. Generate subtask 8 parameters (expense tracking, fixed to link with Task 7 shopping)
        subtask_8_params = {
            'expense_name': 'Shopping',  # Fixed as "Shopping", linked with Task 7
            'expense_note': 'Weekend order',
            'expense_amount': product['price'],  # Depends on the item price from subtask 7
        }
        
        # 8. 🆕 Generate subtask 9 parameters (view walking data — linked with Task 6)
        # Correct trajectory: Walking with a friend at the scheduled time
        walk_distance = random.choice(cls.PARAM_TEMPLATES['subtask_9']['correct_walk_distance_km'])
        walk_duration = random.choice(cls.PARAM_TEMPLATES['subtask_9']['correct_walk_duration_min'])
        distractor_activities = cls.PARAM_TEMPLATES['subtask_9']['distractor_activities']
        
        subtask_9_params = {
            # Correct trajectory information (linked with Task 6)
            'correct_walk_distance_km': walk_distance,
            'correct_walk_duration_min': walk_duration,
            'correct_walk_location': meetup_location,  # 🆕 Use the location scheduled in Task 6
            'correct_walk_start_hour': meetup_time_hour,  # 🆕 Use the time scheduled in Task 6
            'correct_walk_start_minute': meetup_time_minute,
            'friend_name': friend['name'],  # 🆕 Who walked together
            # Distractor trajectories
            'distractor_activities': distractor_activities,
        }
        
        # 9. 🆕 Generate subtask 10 parameters (send SMS to report safety — linked with Task 6)
        safe_home_message = random.choice(cls.PARAM_TEMPLATES['subtask_10']['safe_home_messages'])
        subtask_10_params = {
            'safe_home_message': safe_home_message,
            'friend_name': friend['name'],  # Reuse the friend from Task 6
            'friend_phone': friend['phone'],
        }
        
        # 10. Return the complete parameter set
        return {
            'seed': seed,
            'shared': shared_params,
            'subtask_1': subtask_1_params,
            'subtask_2_3_4': subtask_2_3_4_params,  # 🆕 Merged into a single parameter block
            'subtask_5': subtask_5_params,
            'subtask_7': subtask_7_params,
            'subtask_8': subtask_8_params,
            'subtask_9': subtask_9_params,
            'subtask_10': subtask_10_params,  # 🆕 Newly added
        }
    
    def __init__(self, params: dict = None):
        """
        Initialize Scenario C (enhanced version)
        
        Args:
            params: scenario parameters. If None, calls generate_random_params() to generate random parameters
                   If the 'generated_params' key is provided, use the parameterized data within it
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
            'scenario_id': 'C',
            'name': f'Relaxed Saturday for {user_name}',
            'base_date': '2025-12-26',  # Friday, December 26, 2025
            'total_max_steps': 300,  # 🆕 Increased step count (Task 10: send an SMS message to report safety)
            'success_criteria': {
                'all_subtasks_pass': False,
                'min_subtasks_pass': 0,
            },
            'generated_params': generated_params,
            'clarity_level': params.get('clarity_level'),  # ⚡ pass clarity_level
            'reset_mode': params.get('reset_mode', False),  # ⚡ pass reset_mode
        }
        
        super().__init__(scenario_params)
        
        # 🆕 Save generated_params for use by the initialize method
        self.generated_params = generated_params
        
        # add subtasks using parameterized approach
        self._add_parameterized_subtasks(generated_params)
        
        # set complexity
        self.complexity = 2.5  # 🆕 Increased interdependency complexity
    
    def _add_parameterized_subtasks(self, generated_params: dict):
        """Add all subtasks using the generated parameters (enhanced version)"""
        shared = generated_params.get('shared', {})
        st1 = generated_params.get('subtask_1', {})
        st2_3_4 = generated_params.get('subtask_2_3_4', {})  # 🆕 Merged parameter block
        st5 = generated_params.get('subtask_5', {})
        st7 = generated_params.get('subtask_7', {})
        st8 = generated_params.get('subtask_8', {})
        st9 = generated_params.get('subtask_9', {})
        
        # Extract shared parameters (with default values)
        user_name = shared.get('user_name', 'David')
        friend_name = shared.get('friend_name', 'Bob Johnson')
        friend_phone = shared.get('friend_phone', '555-0102')
        meetup_location = shared.get('meetup_location', 'Central Park entrance')
        meetup_time = shared.get('meetup_time', '3:00 PM')
        meetup_time_hour = shared.get('meetup_time_hour', 15)
        meetup_time_minute = shared.get('meetup_time_minute', 0)
        
        # Subtask 1: Cancel the weekend alarm (parameterized)
        alarm_hour = st1.get('alarm_hour', 7)
        alarm_minute = st1.get('alarm_minute', 0)
        
        self.add_subtask(
            subtask_id=1,
            evaluator_name="LayeredClockDisableSpecificAlarm",
            params={
                "day_offset": 1,  # Saturday
                "alarm_time_hour": alarm_hour,
                "alarm_time_minute": alarm_minute,
                "keep_weekday_alarms": True,
            },
            weight=1.0,
            time="22:40",
            narration=f"Friday night, {user_name} plans to sleep in tomorrow and decides to cancel the next morning alarm",
            user_instruction="I'm off tomorrow. Please disable my next morning alarm so it won't ring. Don't change my weekday alarms.",
            user_instruction_L0=f"Open the Clock app and disable the alarm set for tomorrow morning ({alarm_hour}:{alarm_minute:02d} AM). Make sure you only disable this specific alarm and keep all weekday alarms unchanged.",
            user_instruction_L1="Disable my next morning alarm without affecting weekday alarms.",
            user_instruction_L2="I want to sleep in tomorrow without affecting my regular schedule.",
            max_steps=15,
            requires_answer=False,
        )
        
        # 🆕 Subtask 2: Find a breakfast recipe (QA task, enhanced version)
        # Constraint: Ingredients must include eggs + cooking time ≤ 15 minutes
        recipe_title = st2_3_4.get('recipe_title', 'Scrambled Eggs with Toast')
        recipe_prep_time = st2_3_4.get('recipe_prep_time', 10)
        
        self.add_subtask(
            subtask_id=2,
            evaluator_name="LayeredBroccoliRecipeSearchQA",
            params={
                # 🆕 Enhanced evaluation parameters
                "query_keywords": ["egg", "breakfast", "quick"],
                "recipe_keywords": ["egg"],
                "ingredient_keywords": ["egg", "butter|oil", "salt"],
                "min_ingredient_keywords": 2,
                # 🆕 Newly added: cooking time constraint
                "max_prep_time_minutes": 15,
                "must_contain_prep_time": True,
                # 🆕 Keywords of the correct answer (for evaluation)
                "correct_recipe_title": recipe_title,
            },
            weight=1.0,
            time="08:35",
            narration=f"Saturday morning, {user_name} wants a quick breakfast idea without spending too much time",
            # 🆕 Update instruction: explicitly state the cooking time constraint
            user_instruction="Open Broccoli Recipe and find a quick breakfast recipe that uses eggs AND takes 15 minutes or less to prepare. Tell me the recipe name, key ingredients, and the preparation time.",
            user_instruction_L0=f"Open the Broccoli Recipe app, search for egg breakfast recipes, find one that (1) uses eggs as main ingredient, and (2) has preparation time of 15 minutes or less. Tell me: the recipe name, its key ingredients, and the exact preparation time.",
            user_instruction_L1="Search for a quick egg breakfast recipe that takes no more than 15 minutes. Tell me the name, ingredients, and prep time.",
            user_instruction_L2="What can I make for a fast breakfast with eggs?",
            max_steps=25,
            requires_answer=True,
        )
        
        # 🆕 Subtask 3: Write the recipe into a note (parameterized evaluation)
        recipe_ingredients = st2_3_4.get('recipe_ingredients', ['eggs', 'butter', 'salt', 'pepper', 'bread'])
        recipe_directions = st2_3_4.get('recipe_directions', "")
        
        # Construct the cooking steps string (for reset_user_instruction)
        # recipe_directions is a string: "1. Step A. 2. Step B. 3. Step C."
        if recipe_directions:
            # Split by periods and clean up
            steps = [s.strip() for s in recipe_directions.split('.') if s.strip()]
            # Take only the first five steps
            cooking_steps_str = ", ".join(steps[:5])
        else:
            # If no directions exist, use the default step
            cooking_steps_str = "1. Beat eggs with salt and pepper, 2. Melt butter in pan, 3. Pour eggs and scramble, 4. Toast bread, 5. Serve together"
        
        # Construct the ingredients string
        ingredients_str = ", ".join(recipe_ingredients)
        
        self.add_subtask(
            subtask_id=3,
            evaluator_name="LayeredMarkorCreateRecipeNote",
            params={
                "file_name": "SaturdayBreakfast.md",
                "required_sections": ["recipe", "ingredient", "step"],
                "min_steps": 3,
                "max_steps": 5,
                # 🆕 Parameterized evaluation: check the actual recipe content
                "expected_recipe_title": recipe_title,
                "expected_ingredients": recipe_ingredients,
                "expected_prep_time": recipe_prep_time,
            },
            weight=1.0,
            time="08:42",
            narration=f"{user_name} wants a small, actionable note to follow while cooking without switching screens too much",
            user_instruction=f"Open Markor and create a markdown file called 'SaturdayBreakfast.md'. Write: (1) the recipe name you found for my breakfast, (2) an ingredients list, and (3) 3–5 short, practical cooking steps.",
            user_instruction_L0=f"Open the Markor app, create a new markdown file named 'SaturdayBreakfast.md', and write three sections: (1) the recipe name '{recipe_title}', (2) a list of ingredients including {', '.join(recipe_ingredients[:3])}, and (3) 3–5 practical cooking steps.",
            user_instruction_L1="Create a markdown file 'SaturdayBreakfast.md' with the recipe name you found for my breakfast, ingredients, and 3–5 cooking steps.",
            user_instruction_L2="Write down the breakfast recipe you just found for me so I can follow it while cooking.",
            reset_user_instruction=f"Open Markor, create a new file 'SaturdayBreakfast.md' with three sections: (1) Recipe name: {recipe_title}, (2) Ingredients: {ingredients_str}, (3) Cooking steps: {cooking_steps_str}.",
            max_steps=30,
            requires_answer=False,
        )
        
        # 🆕 Subtask 4: Set up a cooking timer (interlinked with the recipe)
        # Use the cooking time from the recipe as the timer duration!
        timer_minutes = st2_3_4.get('recipe_prep_time', 10)
        
        self.add_subtask(
            subtask_id=4,
            evaluator_name="LayeredClockStartTimer",
            params={
                "minutes": timer_minutes,
                "seconds": 0,
            },
            weight=1.0,
            time="08:50",
            narration=f"{user_name} starts cooking and needs a timer based on the recipe's preparation time",
            # 🆕 Update instruction: interlink with the recipe
            user_instruction=f"Set a cooking timer based on the recipe preparation time you found and start it.",
            user_instruction_L0=f"Open the Clock app, navigate to the Timer tab, set a timer for {timer_minutes} minutes (the preparation time from the recipe), and start it.",
            user_instruction_L1=f"Set a timer matching the recipe's prep time and start it.",
            user_instruction_L2="I need a timer matching how long the recipe takes.",
            max_steps=15,
            requires_answer=False,
        )
        
        # Subtask 5: Take a photo and organize it into a file folder (parameterized)
        folder_name = st5.get('folder_name', 'Weekend/Breakfast')
        
        # 🆕 Split folder_name into parent directory and subdirectory (if multi-level path)
        # e.g., "Weekend/Breakfast" -> parent directory "Weekend", subdirectory "Breakfast"
        # e.g., "MyPhotos/Breakfast" -> parent directory "MyPhotos", subdirectory "Breakfast"
        folder_parts = folder_name.split('/')
        if len(folder_parts) == 2:
            parent_folder = folder_parts[0]
            child_folder = folder_parts[1]
            folder_desc = f"a parent folder named '{parent_folder}' containing a subfolder named '{child_folder}'"
            # 🆕 Build a more explicit path description for the reset instruction
            folder_creation_desc = f"create a folder '{parent_folder}' (if it doesn't exist), then create a subfolder '{child_folder}' inside '{parent_folder}'"
        elif len(folder_parts) == 1:
            parent_folder = folder_parts[0]
            child_folder = None
            folder_desc = f"a folder named '{parent_folder}'"
            folder_creation_desc = f"create a folder '{parent_folder}'"
        else:
            # More than two levels (uncommon)
            parent_folder = folder_parts[0]
            child_folder = '/'.join(folder_parts[1:])
            folder_desc = f"a parent folder named '{parent_folder}' containing subfolders '{child_folder}'"
            folder_creation_desc = f"create a folder '{parent_folder}', then create subfolders '{child_folder}' inside it"
        
        self.add_subtask(
            subtask_id=5,
            evaluator_name="LayeredCameraAndFilesOrganize",
            params={
                "photo_type": "camera",
                "target_folder": folder_name,
                "create_folder_if_missing": True,
            },
            weight=1.0,
            time="09:10",
            narration=f"{user_name} wants to keep a small memory of the weekend breakfast",
            user_instruction=f"Take a photo of my breakfast, then open Files and move it into a folder named '{folder_name}'. If the folder doesn't exist, create it.",
            user_instruction_L0=f"Open the Camera app and take a photo. Then open the Files app, find the most recent photo, and move it to '{folder_name}'. Create the folder '{folder_name}' if it doesn't exist.",
            user_instruction_L1=f"Take a photo and organize it into the folder '{folder_name}'.",
            user_instruction_L2="Take a photo of my breakfast and organize it.",
            reset_user_instruction=f"Open the Files app and navigate to the sdk_gphone_x86_64 storage area. Go to the Pictures folder within sdk_gphone_x86_64, find the photo file named 'breakfast_saturday.png'. Then in the root of sdk_gphone_x86_64 storage area, {folder_creation_desc}. Finally, move the file 'breakfast_saturday.png' from the Pictures folder to the '{folder_name}' folder, both within the same sdk_gphone_x86_64 storage area.",
            max_steps=35,
            requires_answer=False,
        )
        
        # Subtask 6: Schedule a meeting with a friend in the afternoon (parameterized)
        self.add_subtask(
            subtask_id=6,
            evaluator_name="LayeredSmsSendMessage",
            params={
                "contact_name": friend_name,
                "number": friend_phone,
                "message": f"Let's meet at {meetup_time} at {meetup_location} for a walk.",
            },
            weight=1.0,
            time="10:30",
            narration=f"{user_name} plans to go out in the afternoon and wants to confirm the meetup details with a friend",
            user_instruction=f"Use Simple SMS Messenger to text {friend_name}: 'Let's meet at {meetup_time} at {meetup_location} for a walk.' Keep it friendly and clear.",
            user_instruction_L0=f"Open Simple SMS Messenger, select the contact {friend_name} ({friend_phone}), and send this message: 'Let's meet at {meetup_time} at {meetup_location} for a walk.'",
            user_instruction_L1=f"Text {friend_name} to meet at {meetup_time} at {meetup_location} for a walk.",
            user_instruction_L2=f"Ask {friend_name} to meet up for a walk this afternoon.",
            max_steps=20,
            requires_answer=False,
        )
        
        # Subtask 7: Place a large grocery order (parameterized)
        product_sku = st7.get('sku', 'B078158XZ4')
        product_name = st7.get('name', 'Egg Organic 12-count')
        product_price = st7.get('price', 11.8)
        product_keywords = st7.get('keywords', ['Egg', 'Organic', '12'])
        
        self.add_subtask(
            subtask_id=7,
            evaluator_name="LayeredShoppingPurchaseProduct",
            params={
                "product_sku": product_sku,
                "product_keywords": product_keywords,
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
            time="11:05",
            narration=f"After cooking, {user_name} realizes needing to restock and wants to quickly order online",
            user_instruction=f"On the current webpage (ignore the internet access), clear my cart, add the '{product_name}' to my cart and place an order.",
            user_instruction_L0=f"On the current webpage (ignore the internet access), clear my cart first, then add the '{product_name}' to my cart and place an order.",
            user_instruction_L1=f"On the current webpage (ignore the internet access), place an order for the '{product_name}'.",
            user_instruction_L2=f"On the current webpage (ignore the internet access), buy one {product_name}.",
            max_steps=40,
            requires_answer=False,
        )
        
        # Subtask 8: Record an expense (parameterized, dependent on the grocery purchase from Subtask 7)
        expense_name = 'Shopping'  # Fixed as 'Shopping', linked to Task 7
        expense_note = 'Weekend order'
        expense_amount = product_price  # Use the product price from Task 7
        
        self.add_subtask(
            subtask_id=8,
            evaluator_name="LayeredExpenseAddSingle",
            params={
                "name": expense_name,
                "amount": expense_amount,
                "note": expense_note,
                "date": "2025-12-27",
            },
            weight=1.0,
            time="11:25",
            narration=f"{user_name} tracks the weekend spending and wants the amount to match the order total",
            user_instruction=f"Record this shopping purchase in Pro Expense app, name it 'Shopping', use the order total from my last order as the amount.",
            user_instruction_L0=f"Open Pro Expense app and record a new expense: name 'Shopping', amount ${expense_amount} (the total from my last order).",
            user_instruction_L1=f"Record my last shopping expense in Pro Expense app.",
            user_instruction_L2="Log what I just spent.",
            max_steps=20,
            requires_answer=False,
        )
        
        # 🆕 Subtask 9: View data about walking with a friend (Q&A task, linked with Task 6)
        walk_distance = st9.get('correct_walk_distance_km', 2.5)
        walk_duration = st9.get('correct_walk_duration_min', 35)
        walk_location = st9.get('correct_walk_location', meetup_location)
        
        self.add_subtask(
            subtask_id=9,
            evaluator_name="LayeredOpenTracksQueryActivityQA",
            params={
                # 🆕 Information about the correct trajectory (for evaluation)
                "correct_distance_km": walk_distance,
                "correct_duration_min": walk_duration,
                "correct_location": walk_location,
                "friend_name": friend_name,
                "meetup_time_hour": meetup_time_hour,
                "meetup_time_minute": meetup_time_minute,
                # Allowed margin of error
                "distance_tolerance_km": 0.5,
                "duration_tolerance_min": 5,
            },
            weight=1.0,
            time="17:30",
            narration=f"After walking with {friend_name}, {user_name} wants to check the walk statistics",
            # 🆕 Task: View data about walking with a friend
            user_instruction=f"Open OpenTracks and find the walk I did with {friend_name} this afternoon. Tell me how long we walked (duration) and how far (distance).",
            user_instruction_L0=f"Open OpenTracks app, find the activity that started around {meetup_time} at {walk_location} (our walk with {friend_name}). Report the total duration in minutes and total distance in kilometers.",
            user_instruction_L1=f"Check OpenTracks for my walk with {friend_name} today and tell me the duration and distance.",
            user_instruction_L2=f"How far and how long did {friend_name} and I walk today?",
            max_steps=25,
            requires_answer=True,  # 🆕 This is a Q&A task
        )
        
        # 🆕 Subtask 10: Send an SMS message to a friend to report safety (parameterized, linked with Task 6)
        st10 = self.generated_params.get('subtask_10', {})
        safe_home_message = st10.get('safe_home_message', "I'm home safe now. Thanks for the lovely walk today!")
        
        self.add_subtask(
            subtask_id=10,
            evaluator_name="LayeredSmsSendMessage",
            params={
                "contact_name": friend_name,
                "number": friend_phone,
                "message": safe_home_message,
            },
            weight=1.0,
            time="18:00",
            narration=f"After arriving home safely, {user_name} wants to let {friend_name} know everything is okay",
            user_instruction=f"Send a message to my friend letting him know I got home safely from our walk.",
            user_instruction_L0=f"Open Simple SMS Messenger, select the contact {friend_name} ({friend_phone}), and send this message: '{safe_home_message}'",
            user_instruction_L1=f"Text {friend_name} to let him know I'm home safe from our walk.",
            user_instruction_L2=f"Let {friend_name} know I got home okay.",
            max_steps=20,
            requires_answer=False,
        )
        
        # Subtask 11: Evening review (parameterized, dependent on subtasks 7, 8, and 9)
        # Extract keywords from the product name for the review
        product_keyword = product_name.split()[0].lower()  # e.g., "egg", "wireless"
        expense_amount_str = f"{expense_amount:.1f}"
        
        self.add_subtask(
            subtask_id=11,
            evaluator_name="LayeredMarkorRenameAndAppendSummary",
            params={
                "original_file": "SaturdayBreakfast.md",
                "new_file": "weekendsummary.md",
                "expense_keywords": [product_keyword, expense_amount_str],
                "track_keywords": ["walk", friend_name.split()[0].lower()],  # 🆕 Updated to be walk-related
            },
            weight=1.0,
            time="21:10",
            narration=f"{user_name} wants to consolidate the weekend notes: rename the breakfast note to a summary and add expense and activity info",
            user_instruction=f"Rename 'SaturdayBreakfast.md' to 'weekendsummary.md' in Markor. Then append a brief summary about today's shopping purchase and the walk with {friend_name}.",
            user_instruction_L0=f"Open Markor, find the file 'SaturdayBreakfast.md', rename it to 'weekendsummary.md', and append a summary section that includes: (1) today's shopping expense ({product_keyword}, ${expense_amount_str}), and (2) the walk with {friend_name} ({walk_distance}km, {walk_duration}min).",
            user_instruction_L1=f"Rename 'SaturdayBreakfast.md' to 'weekendsummary.md' and add a summary of today's shopping and walk with {friend_name}.",
            user_instruction_L2="Update my notes to reflect what I did today.",
            max_steps=30,
            requires_answer=False,
        )
    
    def initialize_task(self, env):
        """
        batch initialization at scenario start
        
        pre-configure environment for all subtasks:
        - Clock: Set up multiple alarms (weekdays + weekends)
        - Contacts: Add Bob Johnson
        - Shopping: Auto-login
        - Markor: Clean up the directory (Task 3 creates SaturdayBreakfast.md)
        - Other apps: Clear data
        
        Note: The device time is set up in each subtask's initialize_subtask()!
        """
        # Call the parent class method (set up base_date etc. + WebArena environment variables)
        super().initialize_task(env)
        
        # ⚡ Resetmode: skip batch init, each task initializes independently in _reset_initialize_subtask()
        if self.reset_mode:
            logging.info("⚡ Reset Mode: Skipping batch initialization")
            logging.info("   Each task will be initialized independently before execution")
            # only ensure timezone is UTC (needed by almost all tasks)
            self._ensure_utc_timezone(env)
            return
        
        logging.info("🔧 Initializing Scenario C environment in batch...")
        
        try:
            # 1. Set up alarms (multiple)
            self._setup_clocks(env)
            
            # 2. initialize Broccoli Recipe data
            self._setup_broccoli_recipe(env)
            
            # 3. Set up contact and SMS
            self._setup_contacts(env)
            
            # 4. setup Markor(cleanupdirectory)
            self._setup_markor(env)
            
            # 5. Clean up other apps
            # Note: Chrome login latency is executed during subtask 7 (more reliable)
            self._cleanup_apps(env)
            
            logging.info("✅ Scenario C batch initialization complete")
            
            # Return to the home screen (refer to Scenario B)
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
    
    def _setup_clocks(self, env):
        """Set up alarms (weekdays + weekends) — parameterized version"""
        logging.info("   ⏰ setupalarm...")
        
        from scendroid.env import adb_utils
        import time
        
        # Clear all alarms and timers
        adb_utils.clear_app_data(
            adb_utils.extract_package_name(adb_utils.get_adb_activity("clock")),
            env.controller
        )
        time.sleep(1.0)
        
        # Get weekend alarm time from parameters
        st1 = self.generated_params.get('subtask_1', {})
        weekend_alarm_hour = st1.get('alarm_hour', 7)
        weekend_alarm_minute = st1.get('alarm_minute', 0)
        
        # Add weekday alarms (Monday–Friday at 6:30 AM) — should be retained
        safe_message = "Weekday"
        cmd = [
            'shell', 'am', 'start',
            '-a', 'android.intent.action.SET_ALARM',
            '--ei', 'android.intent.extra.alarm.HOUR', '6',
            '--ei', 'android.intent.extra.alarm.MINUTES', '30',
            '--es', 'android.intent.extra.alarm.MESSAGE', safe_message,
            '--eia', 'android.intent.extra.alarm.DAYS', '2,3,4,5,6',  # Mon-Fri
        ]
        adb_utils.issue_generic_request(cmd, env.controller)
        time.sleep(3.0)
        adb_utils.press_home_button(env.controller)
        time.sleep(0.5)
        
        logging.info(f"   ✅ Weekday alarm: {safe_message} at 06:30 (Mon-Fri)")
        
        # Add Saturday alarm (parameterized) — to be canceled by the user
        safe_message = "Weekend"
        cmd = [
            'shell', 'am', 'start',
            '-a', 'android.intent.action.SET_ALARM',
            '--ei', 'android.intent.extra.alarm.HOUR', str(weekend_alarm_hour),
            '--ei', 'android.intent.extra.alarm.MINUTES', str(weekend_alarm_minute),
            '--es', 'android.intent.extra.alarm.MESSAGE', safe_message,
            '--eia', 'android.intent.extra.alarm.DAYS', '7',  # Saturday
        ]
        adb_utils.issue_generic_request(cmd, env.controller)
        time.sleep(3.0)
        adb_utils.press_home_button(env.controller)
        time.sleep(0.5)
        
        logging.info(f"   ✅ Saturday alarm: {safe_message} at {weekend_alarm_hour:02d}:{weekend_alarm_minute:02d} (Saturday)")
        
        logging.info("   ✅ alarmcreatecomplete")
    
    def _setup_broccoli_recipe(self, env):
        """
        Initialize Broccoli Recipe database (enhanced version)
        
        🆕 Constraint design:
        - Correct answer: Ingredients include eggs + cooking time ≤15 minutes
        - Distractor 1–2: Ingredients include eggs but cooking time >15 minutes (meets ingredient requirement but not time)
        - Distractor 3–4: Cooking time ≤15 minutes but no eggs (meets time requirement but not ingredients)
        - Correct answer is not in the first position
        """
        logging.info("   📚 Initializing Broccoli Recipe (enhanced version)...")
        
        from scendroid.task_evals.utils import sqlite_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from scendroid.env import adb_utils
        import time
        import subprocess
        import random
        
        _DB_PATH = '/data/data/com.flauschcode.broccoli/databases/broccoli'
        _TABLE_NAME = 'recipes'
        _APP_NAME = 'broccoli app'
        
        # 1. Launch and close the app to ensure database creation
        logging.info("      Step 1: Launching Broccoli app to initialize database...")
        try:
            adb_utils.launch_app(_APP_NAME, env.controller)
            time.sleep(2.0)
        except subprocess.TimeoutExpired:
            # Broccoli app launch may time out, but this is expected behavior
            logging.info("      Broccoli launch timed out (expected behavior)")
            time.sleep(1.0)
        
        adb_utils.close_app(_APP_NAME, env.controller)
        time.sleep(1.0)
        logging.info("      Step 2: Database should now be created")
        
        # 2. Clear the existing recipe (to avoid accumulation during repeated initialization)
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
        
        # 3. Get the parameterized recipe info
        st2_3_4 = self.generated_params.get('subtask_2_3_4', {})
        correct_recipe_info = st2_3_4.get('correct_recipe', {})
        distractor_long_time = st2_3_4.get('distractor_long_time', [])
        distractor_no_eggs = st2_3_4.get('distractor_no_eggs', [])
        
        # ✅ Create the correct answer (ingredients include eggs + cooking time ≤15 minutes)
        correct_recipe = sqlite_schema_utils.Recipe(
            title=correct_recipe_info.get('title', 'Scrambled Eggs with Toast'),
            description='A easy breakfast with eggs.',
            servings='2',
            preparationTime=f"{correct_recipe_info.get('prep_time', 10)} minutes",
            ingredients=', '.join(correct_recipe_info.get('ingredients', ['eggs', 'butter', 'salt', 'pepper', 'bread'])),
            directions=correct_recipe_info.get('directions', 'Beat eggs. Cook in butter. Serve with toast.'),
            favorite=0
        )
        logging.info(f"      ✅ Correct answer: {correct_recipe.title} ({correct_recipe.preparationTime})")
        
        # ❌ Distractor 1: Classic Egg Casserole (contains eggs but cooking time is 45 minutes > 15 minutes)
        # 🆕 Starts with "Classic", alphabetically before "Scrambled"
        distractor_1 = sqlite_schema_utils.Recipe(
            title='Classic Egg Casserole',
            description='A hearty breakfast bake with eggs and cheese.',
            servings='6',
            preparationTime='45 minutes',
            ingredients='eggs, cheese, milk, bread, sausage, onion',
            directions='Layer bread and sausage. Mix eggs with milk. Pour over. Bake for 45 minutes.',
            favorite=0
        )
        logging.info(f"      ❌ Distractor 1 (cooking time too long): {distractor_1.title} ({distractor_1.preparationTime})")
        
        # ❌ Distractor 2: Perfect Poached Eggs (contains eggs but cooking time is 25 minutes > 15 minutes)
        # 🆕 Starts with "Perfect", alphabetically before "Scrambled"
        distractor_2 = sqlite_schema_utils.Recipe(
            title='Perfect Poached Eggs',
            description='Restaurant-style poached eggs with runny yolk.',
            servings='2',
            preparationTime='25 minutes',
            ingredients='eggs, vinegar, water, salt, butter, toast',
            directions='Bring water to simmer. Add vinegar. Create vortex. Gently drop eggs. Cook 3-4 minutes. Repeat for each egg.',
            favorite=0
        )
        logging.info(f"      ❌ Distractor 2 (cooking time too long): {distractor_2.title} ({distractor_2.preparationTime})")
        
        # ❌ Distractor 3: Quick Avocado Toast (cooking time is short—5 minutes—but contains no eggs)
        distractor_3 = sqlite_schema_utils.Recipe(
            title=distractor_no_eggs[0]['title'] if len(distractor_no_eggs) > 0 else 'Quick Avocado Toast',
            description='Healthy and quick breakfast option.',
            servings='1',
            preparationTime=f"{distractor_no_eggs[0]['prep_time'] if len(distractor_no_eggs) > 0 else 5} minutes",
            ingredients=', '.join(distractor_no_eggs[0]['ingredients'] if len(distractor_no_eggs) > 0 else ['avocado', 'bread', 'lemon', 'salt', 'pepper']),
            directions='Toast bread. Mash avocado. Season and spread. Serve immediately.',
            favorite=0
        )
        logging.info(f"      ❌ Distractor 3 (no eggs): {distractor_3.title} ({distractor_3.preparationTime})")
        
        # ❌ Distractor 4: Fruit Yogurt Bowl (cooking time is short—5 minutes—but contains no eggs)
        distractor_4 = sqlite_schema_utils.Recipe(
            title=distractor_no_eggs[1]['title'] if len(distractor_no_eggs) > 1 else 'Fruit Yogurt Bowl',
            description='Refreshing and healthy breakfast.',
            servings='1',
            preparationTime=f"{distractor_no_eggs[1]['prep_time'] if len(distractor_no_eggs) > 1 else 5} minutes",
            ingredients=', '.join(distractor_no_eggs[1]['ingredients'] if len(distractor_no_eggs) > 1 else ['yogurt', 'berries', 'honey', 'granola']),
            directions='Add yogurt to bowl. Top with berries. Drizzle honey. Add granola.',
            favorite=0
        )
        logging.info(f"      ❌ Distractor 4 (no eggs): {distractor_4.title} ({distractor_4.preparationTime})")
        
        # ❌ Distractor 5: Baked Egg Cups (contains eggs but cooking time is 30 minutes > 15 minutes)
        # 🆕 Starts with "Baked", alphabetically before "Scrambled"
        distractor_5 = sqlite_schema_utils.Recipe(
            title='Baked Egg Cups',
            description='Individual egg cups baked in muffin tin.',
            servings='4',
            preparationTime='30 minutes',
            ingredients='eggs, ham, cheese, spinach, salt, pepper',
            directions='Preheat oven to 350F. Line muffin tin with ham. Add spinach. Crack egg into each. Bake 25 minutes.',
            favorite=0
        )
        logging.info(f"      ❌ Distractor 5 (cooking time too long): {distractor_5.title} ({distractor_5.preparationTime})")
        
        # 🆕 Combine all recipes: the correct answer is NOT in the first position!
        # Order: Distractor 1, Distractor 3, Correct Answer, Distractor 2, Distractor 4, Distractor 5
        all_recipes = [distractor_1, distractor_3, correct_recipe, distractor_2, distractor_4, distractor_5]
        
        logging.info("      📋 Recipe order (correct answer is at position 3):")
        for i, recipe in enumerate(all_recipes, 1):
            is_correct = "✅" if recipe.title == correct_recipe.title else "❌"
            logging.info(f"         {i}. {is_correct} {recipe.title} ({recipe.preparationTime})")
        
        # 4. Add recipes to the database
        logging.info(f"      Step 3: Inserting {len(all_recipes)} recipes into database...")
        try:
            sqlite_utils.insert_rows_to_remote_db(
                rows=all_recipes,
                exclude_key='recipeId',
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
            logging.info(f"   ℹ️  There are currently {len(existing_recipes)} recipes in the database")
            
            # Verify the position of the correct answer
            for i, recipe in enumerate(existing_recipes):
                if recipe.title == correct_recipe.title:
                    logging.info(f"   ✅ Correct answer '{recipe.title}' is at position {i+1} (not the first position)")
                    break
                
        except Exception as e:
            logging.warning(f"   ⚠️  Failed to add recipes: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _setup_contacts(self, env):
        """Add contact and clear SMS messages—parameterized version"""
        logging.info("   📱 Setting up contact and SMS messages...")
        
        from scendroid.utils import contacts_utils
        from scendroid.task_evals.common_validators import sms_validators
        from scendroid.env import adb_utils
        import time
        
        # clearcontact
        try:
            contacts_utils.clear_contacts(env.controller)
        except Exception as e:
            logging.warning(f"clearcontactfailed: {e}")
        
        time.sleep(1.0)
        
        # Retrieve friend info from parameters
        shared = self.generated_params.get('shared', {})
        friend_name = shared.get('friend_name', 'Bob Johnson')
        friend_phone = shared.get('friend_phone', '555-0102')
        
        # ⚠️ Important: All possible friend info (from PARAM_TEMPLATES)
        all_friends = [
            {"name": "Bob Johnson", "phone": "555-0102"},
            {"name": "Alice Davis", "phone": "555-0201"},
            {"name": "Charlie Wilson", "phone": "555-0301"},
            {"name": "Diana Smith", "phone": "555-0401"},
        ]
        
        # ✅ Ensure the parameterized friend is added; others serve as distractors
        contacts = []
        
        # 1. First, add the target friend (parameterized)
        contacts.append({"name": friend_name, "phone": friend_phone})
        
        # 2. Add other people as distractors (excluding the target friend)
        for friend in all_friends:
            if friend['name'] != friend_name:  # Avoid duplicate addition of the target friend
                contacts.append(friend)
        
        successfully_added = 0
        for i, contact in enumerate(contacts, 1):
            name = contact['name']
            phone = contact['phone']
            
            # Attempt to add each contact twice
            for attempt in range(2):
                try:
                    if attempt > 0:
                        logging.info(f"      ↻ retry '{name}' (attempt {attempt + 1})")
                    
                    # Press the Home button to ensure stable status
                    adb_utils.press_home_button(env.controller)
                    time.sleep(1.5)
                    
                    # Add the contact
                    contacts_utils.add_contact(
                        name, 
                        phone, 
                        env.controller,
                        ui_delay_sec=2.0
                    )
                    logging.info(f"      ✅ Added {i}/{len(contacts)}: '{name}' ({phone})")
                    successfully_added += 1
                    time.sleep(2.0)
                    break  # Success; proceed to the next one
                    
                except Exception as e:
                    if attempt == 1:  # Last attempt failed
                        logging.error(f"      ❌ Failed to add '{name}' (after 2 attempts): {e}")
                    else:
                        logging.warning(f"      ⚠️  attempt {attempt + 1} failed: '{name}': {e}")
                    time.sleep(1.0)
        
        logging.info("   " + "=" * 50)
        logging.info(f"   📊 Contact addition summary: {successfully_added}/{len(contacts)} successful")
        logging.info("   " + "=" * 50)
        
        # etc. Pending contact sync
        time.sleep(3.0)
        
        # Clear SMS messages
        try:
            sms_validators.clear_sms_and_threads(env.controller)
        except Exception as e:
            logging.warning(f"Failed to clear SMS messages: {e}")
        
        # refresh SMS UI
        try:
            adb_utils.close_app("simple sms", env.controller)
            time.sleep(0.5)
        except:
            pass
        
        logging.info("   ✅ SMS messages cleared")
    
    def _setup_markor(self, env):
        """
        initialize Markor(cleanupdirectory, do_not_create_file)
        
        🆕 Refer to Scenario A's implementation: Use the more reliable approach of deleting the entire directory and then rebuilding it
        """
        logging.info("   📝 initialize Markor...")
        
        from scendroid.env import adb_utils, device_constants
        import time
        
        markor_dir = device_constants.MARKOR_DATA  # "/storage/emulated/0/Documents/Markor"
        
        try:
            # 🆕 Step 0: First, close the Markor app (to release file locks)
            try:
                adb_utils.close_app("markor", env.controller)
                time.sleep(0.5)
            except Exception:
                pass
            
            # 🆕 Step 1: Delete the entire directory (instead of using wildcards)
            # Refer to Scenario A's _cleanup_app_data method
            logging.info("      🗑️  delete Markor directory...")
            adb_utils.issue_generic_request(
                ['shell', 'rm', '-rf', markor_dir], env.controller
            )
            time.sleep(0.5)
            
            # 🆕 Step 2: recreate directory
            logging.info("      📁 Re-creating Markor directory...")
            adb_utils.issue_generic_request(
                ['shell', 'mkdir', '-p', markor_dir], env.controller
            )
            time.sleep(0.5)
            
            # 🆕 Step 3: Verify whether cleanup succeeded
            logging.info("      🔍 verify Markor directorycleanup...")
            check_result = adb_utils.issue_generic_request(
                ['shell', 'ls', '-la', markor_dir], env.controller
            )
            if check_result and check_result.generic and check_result.generic.output:
                output = check_result.generic.output.decode('utf-8', errors='ignore')
                # Check whether the directory is empty (contains only . and .. or has zero total entries)
                lines = [l for l in output.strip().split('\n') if l and not l.startswith('total')]
                if len(lines) <= 2:  # Only . and ..
                    logging.info("      ✅ Markor directory cleared")
                else:
                    logging.warning(f"      ⚠️ Directory may not be fully cleared: {output[:100]}")
            
            logging.info("   ✅ Markor initializecomplete")
            
        except Exception as e:
            logging.warning(f"      ⚠️  Markor directorycleanup failed: {e}")
        
        # Note: Do not create any files
        # Task 3 will create SaturdayBreakfast.md
        # Task 10 will rename it to weekendsummary.md
    
    def _create_breakfast_photo(self, env):
        """
        Create a fake breakfast photo (refer to scenario_d's _create_trip_info_image method)
        
        Use PIL to create a real PNG image file, rather than an empty file
        Create only in the Pictures folder
        """
        logging.info("   📷 Creating fake breakfast photo...")
        
        from scendroid.task_evals.utils import user_data_generation
        from scendroid.utils import file_utils
        from scendroid.env import device_constants, adb_utils
        import os
        import tempfile
        import time
        
        try:
            # Pictures folder path
            pictures_path = f"{device_constants.EMULATOR_DATA}Pictures"
            
            # 1. First, clear the Pictures folder (if it exists)
            logging.info(f"      🧹 Clearing Pictures folder...")
            adb_utils.issue_generic_request(
                ['shell', 'rm', '-rf', pictures_path], env.controller
            )
            time.sleep(0.3)
            
            # 2. Re-create the Pictures directory
            adb_utils.issue_generic_request(
                ['shell', 'mkdir', '-p', pictures_path], env.controller
            )
            time.sleep(0.3)
            logging.info(f"      ✅ Pictures folder cleared and rebuilt")
            
            # get parameters
            st2_3_4 = self.generated_params.get('subtask_2_3_4', {})
            recipe_title = st2_3_4.get('recipe_title', 'Scrambled Eggs with Toast')
            
            # Construct photo content (text description simulating a breakfast photo)
            photo_text = f"""
═══════════════════════════════════
    🍳 SATURDAY BREAKFAST 🍳
═══════════════════════════════════

    {recipe_title}

    📸 Photo taken on Saturday
    
    Delicious homemade breakfast!
    
═══════════════════════════════════
"""
            
            # use _draw_text to generate image
            image = user_data_generation._draw_text(photo_text.strip(), font_size=20)
            
            # save to temp file
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "breakfast_saturday.png")
            image.save(temp_path)
            
            # 3. Copy to Pictures directory
            remote_path = f"{pictures_path}/breakfast_saturday.png"
            file_utils.copy_data_to_device(temp_path, remote_path, env.controller)
            logging.info(f"      ✅ Pictures photo: {remote_path}")
            
            # clean up temp files
            try:
                os.remove(temp_path)
            except:
                pass
            
            # Scan the media library to ensure the photo is recognized
            action = 'android.intent.action.MEDIA_SCANNER_SCAN_FILE'
            data_uri = f'file://{remote_path}'
            adb_utils.send_android_intent(
                command='broadcast', action=action,
                env=env.controller, data_uri=data_uri
            )
            time.sleep(1.0)
            
            logging.info(f"   ✅ Fake breakfast photo created (in Pictures only)")
            
        except Exception as e:
            logging.warning(f"   ⚠️ Failed to create fake photo: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def _cleanup_apps(self, env):
        """
        Clean up other app data (enhanced version)
        
        🆕 Enhanced content:
        1. Clean up all possible target folders (refer to Scenario E)
        2. Initialize OpenTracks activity tracks (correct + distractors)
        """
        logging.info("   🧹 Cleaning up other apps...")
        
        from scendroid.env import adb_utils
        from scendroid.task_evals.information_retrieval import activity_app_utils
        import time
        
        # 1. Camera: Clear photos (cleanup DCIM directory)
        try:
            from scendroid.env import device_constants
            from scendroid.utils import file_utils
            
            file_utils.clear_directory(device_constants.GALLERY_DATA, env.controller)
            logging.info("   ✅ Camera photos cleared")
        except Exception as e:
            logging.warning(f"cleanup Camera failed: {e}")
        
        # 🆕 1.5. Create a fake breakfast photo (refer to the PNG creation method in scenario_d)
        # The simulator cannot capture real photos, so a fake photo is pre-placed
        # Place it in the Pictures folder; the agent must move it to the target folder
        self._create_breakfast_photo(env)
        
        # 🆕 2. Files: Cleanup all possible target folders (refer to Scenario E)
        try:
            from scendroid.env import device_constants
            
            # Get parameterized folder name
            st5 = self.generated_params.get('subtask_5', {})
            folder_name = st5.get('folder_name', 'Weekend/Breakfast')
            
            # All possible target folders (from PARAM_TEMPLATES)
            all_folder_names = [
                'Weekend/Breakfast',
                'Saturday/Food',
                'Weekend/Cooking',
                'MyPhotos/Breakfast',
                'Weekend',  # Parent directory must also be cleaned up
                'Saturday',
                'MyPhotos',
            ]
            
            base_path = device_constants.EMULATOR_DATA  # /storage/emulated/0/
            
            logging.info("      🗑️  Cleaning up target folders...")
            for folder in all_folder_names:
                folder_path = f"{base_path}{folder}"
                try:
                    adb_utils.issue_generic_request(
                        ['shell', 'rm', '-rf', folder_path], env.controller
                    )
                    logging.info(f"         ✅ Cleaned up: {folder}")
                except Exception as e:
                    logging.debug(f"         cleanup {folder} failed: {e}")
            
            logging.info(f"   ✅ Target folders cleaned up")
        except Exception as e:
            logging.warning(f"   ⚠️  Folder cleanup failed: {e}")
        
        # 3. Expense: cleardata
        try:
            from scendroid.task_evals.utils import sqlite_utils
            from scendroid.env.setup_device import apps
            
            _EXPENSE_DB_PATH = "/data/data/com.arduia.expense/databases/accounting.db"
            _EXPENSE_TABLE = "expense"
            _EXPENSE_APP_NAME = "pro expense"
            
            if not sqlite_utils.table_exists(_EXPENSE_TABLE, _EXPENSE_DB_PATH, env):
                logging.info("      Expensedatabase does not exist, initializing...")
                apps.ExpenseApp.setup(env)
            
            sqlite_utils.delete_all_rows_from_table(
                _EXPENSE_TABLE, _EXPENSE_DB_PATH, env, _EXPENSE_APP_NAME
            )
            logging.info("   ✅ Expense data cleared")
        except Exception as e:
            logging.warning(f"clear Expense failed: {e}")
        
        # 4. OpenTracks: Clear data and grant permissions
        try:
            activity_app_utils.clear_db(env)
            logging.info("   ✅ OpenTracks database cleaned up")
            
            logging.info("      🔐 granting OpenTracks permissions...")
            
            try:
                adb_utils.launch_app("open tracks sports tracker", env.controller)
            except Exception as e:
                logging.debug(f"      Launch app timeout (expected): {e}")
            
            time.sleep(3.0)
            adb_utils.close_app("open tracks sports tracker", env.controller)
            
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
            
            time.sleep(2.0)
            
            try:
                from scendroid.env import tools
                controller = tools.AndroidToolController(env=env.controller)
                controller.click_element("Allow")
                logging.info("      ✅ bluetooth permission clicked 'Allow' button")
            except Exception as e:
                logging.debug(f"      'Allow' button not found or already authorized: {e}")
            
            try:
                adb_utils.start_activity(
                    "de.dennisguse.opentracks/.TrackListActivity",
                    None,
                    env.controller
                )
                time.sleep(2.0)
                adb_utils.close_app("activity tracker", env.controller)
            except Exception as e:
                logging.debug(f"      OpenTracks launch/shutdown failed (can be ignored): {e}")
            
            logging.info("   ✅ OpenTracks permission granted")
            
        except Exception as e:
            logging.warning(f"OpenTracks initialization failed: {e}")
        
        # 🆕 5. Initialize OpenTracks activity tracks (correct + distractor)
        self._setup_opentracks_activities(env)
        
        logging.info("   ✅ App cleanup complete")
    
    def _setup_opentracks_activities(self, env):
        """
        🆕 Initialize OpenTracks activity tracks (coordinated with Task 6)
        
        Refer to the implementation of scenario_e._setup_opentracks_history()
        Use the SportsActivity data structure
        
        Correct track: A walk with a friend at the scheduled time and location (only the location is displayed, not the friend's name)
        Distractor track: Activities at other times/locations
        
        🔧 Timezone handling: Use calendar.timegm() to avoid local timezone impact
        """
        logging.info("   🏃 Initializing OpenTracks activity tracks...")
        
        from scendroid.task_evals.information_retrieval import activity_app_utils
        from scendroid.task_evals.utils import sqlite_schema_utils
        from datetime import datetime, timedelta
        import calendar
        import random
        
        try:
            # get parameters
            shared = self.generated_params.get('shared', {})
            st9 = self.generated_params.get('subtask_9', {})
            
            friend_name = shared.get('friend_name', 'Bob Johnson')
            meetup_location = shared.get('meetup_location', 'Central Park entrance')
            meetup_time_hour = shared.get('meetup_time_hour', 15)
            meetup_time_minute = shared.get('meetup_time_minute', 0)
            
            correct_distance_km = st9.get('correct_walk_distance_km', 2.5)
            correct_duration_min = st9.get('correct_walk_duration_min', 35)
            distractor_activities = st9.get('distractor_activities', [])
            
            # Use fixed base_date: 2025-12-27 (Saturday)
            base_date = datetime(2025, 12, 27, 0, 0, 0)
            
            logging.info(f"      📅 Base date: {base_date.strftime('%Y-%m-%d')}")
            logging.info(f"      👥 Scheduled time with {friend_name}: {meetup_time_hour}:{meetup_time_minute:02d}")
            logging.info(f"      📍 Scheduled location: {meetup_location}")
            
            activities = []
            
            # 1. Create the correct walking track (matching the scheduled time and location in Task 6)
            correct_start_dt = base_date.replace(hour=meetup_time_hour, minute=meetup_time_minute)
            # 🔧 Use calendar.timegm() to avoid local timezone impact
            # timegm() treats the struct_time as UTC time and returns a UTC timestamp
            correct_start_ts = int(calendar.timegm(correct_start_dt.timetuple()) * 1000)  # milliseconds
            correct_duration_ms = int(correct_duration_min * 60 * 1000)
            correct_stop_ts = correct_start_ts + correct_duration_ms
            correct_distance_m = int(correct_distance_km * 1000)
            
            # 🆕 Activity name includes only the location, not the friend's name (to reduce difficulty)
            # The agent must infer the correct track based on the location information in Task 6
            correct_activity_name = f"Walk at {meetup_location}"
            
            # Calculate speed (m/s)
            correct_avg_speed = correct_distance_m / (correct_duration_min * 60)
            
            correct_activity = sqlite_schema_utils.SportsActivity(
                name=correct_activity_name,
                description="Afternoon walk",  # 🆕 Does not include the friend's name
                category='walking',
                activity_type='walking',
                starttime=correct_start_ts,
                stoptime=correct_stop_ts,
                numpoints=int(correct_duration_min * 2),  # Approximately one point every 30 seconds
                totaldistance=correct_distance_m,
                totaltime=correct_duration_ms,
                movingtime=int(correct_duration_ms * 0.9),  # 90% move time
                avgspeed=correct_avg_speed,
                avgmovingspeed=correct_avg_speed / 0.9,
                elevationgain=random.randint(10, 50),
                elevationloss=random.randint(10, 50),
            )
            activities.append(correct_activity)
            
            logging.info(f"      ✅ Correct trajectory: '{correct_activity_name}'")
            logging.info(f"         Start time: {correct_start_dt.strftime('%H:%M')}")
            logging.info(f"         duration: {correct_duration_min} minutes")
            logging.info(f"         Distance: {correct_distance_km} km")
            
            # 2. Create distractor trajectory (🆕 Differentiated by location; all times are in the afternoon)
            logging.info("      ❌ Distractor trajectory:")
            for idx, distractor in enumerate(distractor_activities):
                name = distractor.get('name', 'Walk')
                # 🆕 Use the location defined in the parameter
                distractor_location = distractor.get('location', f'Location {idx+1}')
                time_offset_hours = distractor.get('time_offset_hours', -1)
                distance_km = distractor.get('distance_km', 5.0)
                duration_min = distractor.get('duration_min', 30)
                
                # Calculate the start time of the distractor trajectory
                distractor_start_dt = correct_start_dt + timedelta(hours=time_offset_hours)
                # 🔧 Use calendar.timegm() to avoid local timezone effects
                distractor_start_ts = int(calendar.timegm(distractor_start_dt.timetuple()) * 1000)
                distractor_duration_ms = int(duration_min * 60 * 1000)
                distractor_stop_ts = distractor_start_ts + distractor_duration_ms
                distractor_distance_m = int(distance_km * 1000)
                
                # 🆕 Trajectory name: Walk at {location}
                distractor_activity_name = f"{name} at {distractor_location}"
                distractor_avg_speed = distractor_distance_m / (duration_min * 60)
                
                distractor_activity = sqlite_schema_utils.SportsActivity(
                    name=distractor_activity_name,
                    description="Afternoon walk",  # 🆕 Unified description
                    category='walking',
                    activity_type='walking',
                    starttime=distractor_start_ts,
                    stoptime=distractor_stop_ts,
                    numpoints=int(duration_min * 2),
                    totaldistance=distractor_distance_m,
                    totaltime=distractor_duration_ms,
                    movingtime=int(distractor_duration_ms * 0.85),
                    avgspeed=distractor_avg_speed,
                    avgmovingspeed=distractor_avg_speed / 0.85,
                    elevationgain=random.randint(20, 100),
                    elevationloss=random.randint(20, 100),
                )
                activities.append(distractor_activity)
                
                logging.info(f"         '{distractor_activity_name}' at {distractor_start_dt.strftime('%H:%M')}")
                logging.info(f"            Duration: {duration_min} min, Distance: {distance_km} km")
            
            # 3. Add activities to the database
            activity_app_utils._add_activities(activities, env)
            
            logging.info(f"   ✅ Added {len(activities)} activity trajectories (1 correct + {len(activities)-1} distractors)")
            
        except Exception as e:
            logging.warning(f"   ⚠️  OpenTracks activity initialization failed: {e}")
            import traceback
            logging.warning(traceback.format_exc())
    
    def initialize_subtask(self, subtask_idx: int, env):
        """
        Custom subtask initialization logic
        
        🆕 Date-switching logic: 
        - Task 1 (Friday evening at 22:40): Use base_date (2025-12-26 Friday)
        - Tasks 2–10 (Saturday): Use base_date + 1 day (2025-12-27 Saturday)
        
        ⚠️ In Reset mode: Directly call super(), handled by _reset_initialize_subtask()
        📚 In Scenario mode: Execute scenario-specific pre-handling, then call super()
        """
        from datetime import datetime, timedelta
        
        subtask = self.subtasks[subtask_idx]
        
        # ⚡ Resetmode: skip Scenario-specific preprocessing
        # all initialization handled by _reset_initialize_subtask() in super()
        if self.reset_mode:
            super().initialize_subtask(subtask_idx, env)
            return
        
        # ---- Execute the following only in Scenario mode ----
        
        # Save the original base_date (only on first save)
        if not hasattr(self, '_friday_date'):
            self._friday_date = self.context.base_date  # 2025-12-26
            friday = datetime.strptime(self._friday_date, '%Y-%m-%d')
            self._saturday_date = (friday + timedelta(days=1)).strftime('%Y-%m-%d')  # 2025-12-27
        
        # 🆕 Date switching: Task 1 is Friday; Tasks 2+ are Saturday
        if subtask['subtask_id'] == 1:
            # Task 1: Friday evening, use Friday's date
            self.context.base_date = self._friday_date
            logging.info(f"   📅 Using Friday's date: {self.context.base_date}")
        else:
            # Tasks 2–10: Saturday, use Saturday's date
            self.context.base_date = self._saturday_date
            logging.info(f"   📅 Using Saturday's date: {self.context.base_date}")
        
        # Subtask 6: SMS task – requires UI refresh
        if subtask['subtask_id'] == 6:
            logging.info("   💬 SMS task – Preparing environment...")
            
            # 1. Refresh UI and ensure returning to the home screen
            # Although SMS was cleaned up during scenario initialization, UI cache remnants may persist
            # and the UI might remain on a previous conversation screen
            try:
                from scendroid.env import adb_utils
                import time
                
                logging.info("      📱 refreshSMS UI...")
                
                # ⚠️ Critical step 1: First, force stop (to clear UI cache)
                adb_utils.close_app("simple sms", env.controller)
                time.sleep(1.0)
                
                # Step 2: Open the SMS application
                logging.info("      📱 opening SMS app...")
                adb_utils.start_activity(
                    "com.simplemobiletools.smsmessenger/.activities.MainActivity",
                    None,
                    env.controller
                )
                time.sleep(2.0)  # etc., wait for app to fully load
                
                # 🆕 Step 3: Press the Back button to ensure returning to the home screen (not remaining on the conversation page)
                logging.info("      📱 pressing back to return to home screen...")
                for _ in range(3):  # press back button multiple times to ensure return to home screen
                    adb_utils.issue_generic_request(
                        ["shell", "input", "keyevent", "KEYCODE_BACK"],
                        env.controller
                    )
                    time.sleep(0.3)
                
                # Step 4: Press the Home button to exit to the desktop
                logging.info("      📱 pressing Home to exit to desktop...")
                adb_utils.press_home_button(env.controller)
                time.sleep(1.0)
                
                logging.info("      ✅ SMS UI refreshed (force stop + open + Back button + Home button)")
            except Exception as e:
                logging.warning(f"      ⚠️  SMS UIrefreshfailed: {e}")
        
        # Call the parent class method (which sets up device time and creates an evaluator instance)
        super().initialize_subtask(subtask_idx, env)
    
    def tear_down(self, env):
        """
        Cleanup after scenario end
        """
        logging.info("🧹 Scenario B tear down...")
        
        try:
            # cleanup SMS
            from scendroid.task_evals.common_validators import sms_validators
            from scendroid.env import adb_utils
            
            try:
                sms_validators.clear_sms_and_threads(env.controller)
            except:
                pass
            
            # Rebuild Shopping container (because Task 7 places an order)
            logging.info("   🔄 rebuild Shopping container...")
            try:
                from scendroid.apps.shopping.utils import rebuild_shopping_container
                rebuild_shopping_container(env=env)
                logging.info("      ✅ Shopping container rebuilt")
            except Exception as e:
                logging.warning(f"      ⚠️ Shopping container rebuild failed: {e}")
            
            logging.info("✅ Scenario B tear down completed")
            
        except Exception as e:
            logging.error(f"❌ Tear down failed: {e}")
            import traceback
            logging.error(traceback.format_exc())
        
        # Call the parent class's tear_down
        super().tear_down(env)
    
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
            self._reset_init_task2_recipe_qa(env)
        elif task_id == 3:
            self._reset_init_task3_markor_create(subtask, env)
        elif task_id == 4:
            self._reset_init_task4_timer(env)
        elif task_id == 5:
            self._reset_init_task5_photo_organize(env)
        elif task_id == 6:
            self._reset_init_task6_sms(subtask, env)
        elif task_id == 7:
            self._reset_init_task7_shopping(subtask, env)
        elif task_id == 8:
            self._reset_init_task8_expense(subtask, env)
        elif task_id == 9:
            self._reset_init_task9_opentracks_qa(env)
        elif task_id == 10:
            self._reset_init_task10_sms_again(subtask, env)
        elif task_id == 11:
            self._reset_init_task11_markor_summary(subtask, env)
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
    
    def _reset_setup_contacts(self, env):
        """Create contact in Reset mode (used by Tasks 6 and 10)"""
        from scendroid.utils import contacts_utils
        from scendroid.env import adb_utils
        from scendroid.task_evals.common_validators import sms_validators
        import time
        
        contacts_utils.clear_contacts(env.controller)
        time.sleep(1.0)
        
        # clearSMS
        try:
            sms_validators.clear_sms_and_threads(env.controller)
            adb_utils.close_app("simple sms", env.controller)
            time.sleep(1.0)
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear SMS: {e}")
        
        # Get parameterized friend info
        shared = self.generated_params.get('shared', {})
        friend_name = shared.get('friend_name', 'Bob Johnson')
        friend_phone = shared.get('friend_phone', '555-0102')
        
        # All possible friend info (from PARAM_TEMPLATES)
        all_friends = [
            {"name": "Bob Johnson", "phone": "555-0102"},
            {"name": "Alice Davis", "phone": "555-0201"},
            {"name": "Charlie Wilson", "phone": "555-0301"},
            {"name": "Diana Smith", "phone": "555-0401"},
        ]
        
        contacts = []
        # 1. First add the target friend
        contacts.append({"name": friend_name, "phone": friend_phone})
        # 2. Add others as distractors
        for friend in all_friends:
            if friend['name'] != friend_name:
                contacts.append(friend)
        
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
        Task 1 (Disable Weekend Alarm): 
        Prerequisites: Two alarms (weekday + weekend); the agent must cancel the weekend alarm
        """
        logging.info("   🔧 Reset Init Task 1: Creating alarms for disable task")
        
        from scendroid.env import adb_utils
        import time
        
        # 0. return to home (cleanup previous task state)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
        except Exception:
            pass
        
        # 1. Clear Clock data
        try:
            adb_utils.clear_app_data(
                adb_utils.extract_package_name(adb_utils.get_adb_activity("clock")),
                env.controller,
            )
            time.sleep(1.0)
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear clock data: {e}")
        
        # 2. Create two alarms (weekday + weekend)
        st1 = self.generated_params.get('subtask_1', {})
        weekend_hour = st1.get('alarm_hour', 7)
        weekend_minute = st1.get('alarm_minute', 0)
        
        # Weekday alarm (should be retained)
        cmd = [
            'shell', 'am', 'start',
            '-a', 'android.intent.action.SET_ALARM',
            '--ei', 'android.intent.extra.alarm.HOUR', '6',
            '--ei', 'android.intent.extra.alarm.MINUTES', '30',
            '--es', 'android.intent.extra.alarm.MESSAGE', 'Weekday',
            '--eia', 'android.intent.extra.alarm.DAYS', '2,3,4,5,6',
        ]
        adb_utils.issue_generic_request(cmd, env.controller)
        time.sleep(3.0)
        adb_utils.press_home_button(env.controller)
        time.sleep(0.5)
        
        # Weekend alarm (the agent must cancel it)
        cmd = [
            'shell', 'am', 'start',
            '-a', 'android.intent.action.SET_ALARM',
            '--ei', 'android.intent.extra.alarm.HOUR', str(weekend_hour),
            '--ei', 'android.intent.extra.alarm.MINUTES', str(weekend_minute),
            '--es', 'android.intent.extra.alarm.MESSAGE', 'Weekend',
            '--eia', 'android.intent.extra.alarm.DAYS', '7',
        ]
        adb_utils.issue_generic_request(cmd, env.controller)
        time.sleep(3.0)
        adb_utils.press_home_button(env.controller)
        time.sleep(0.5)
        
        logging.info(f"      ✅ 2 alarms created (Weekday@06:30 Mon-Fri, Weekend@{weekend_hour}:{weekend_minute:02d} Sat)")
        
        # 3. return to home (initialization complete)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            logging.info("      ✅ Returned to home screen")
        except Exception:
            pass
    
    def _reset_init_task2_recipe_qa(self, env):
        """
        Task 2 (Search Breakfast Recipe QA):
        Prerequisites: Broccoli Recipe database (containing the correct recipe + distractors)
        """
        logging.info("   🔧 Reset Init Task 2: Initializing Broccoli Recipe database")
        
        from scendroid.env import adb_utils
        import time
        
        # 0. return to home (cleanup previous task state)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
        except Exception:
            pass
        
        # 1. Reuse the batch initialize method
        self._setup_broccoli_recipe(env)
        
        # 2. return to home (initialization complete)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            logging.info("      ✅ Returned to home screen")
        except Exception:
            pass
    
    def _reset_init_task3_markor_create(self, subtask, env):
        """
        Task 3 (Write Recipe to Markor):
        Prerequisites: Markor directory cleared (no SaturdayBreakfast.md) + return-to-home interface
        """
        logging.info("   🔧 Reset Init Task 3: Clearing Markor directory and returning to home")
        
        from scendroid.env import adb_utils, device_constants
        import time
        
        # 0. return to home (cleanup previous task state)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
        except Exception:
            pass
        
        # 1. Clear the Markor directory (using the same reliable method as in scenario a)
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
            
            logging.info("      ✅ Markor cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear Markor: {e}")
        
        # 2. Return to the home interface (complete initialization)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(1.0)
            logging.info("      ✅ Returned to home screen")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not return to home: {e}")
    
    def _reset_init_task4_timer(self, env):
        """
        Task 4 (Set Cooking Timer):
        Prerequisites: Clock timer cleared
        """
        logging.info("   🔧 Reset Init Task 4: Clearing Clock timers")
        
        from scendroid.env import adb_utils
        import time
        
        # 0. return to home (cleanup previous task state)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
        except Exception:
            pass
        
        # 1. Clear Clock data
        try:
            adb_utils.clear_app_data(
                adb_utils.extract_package_name(adb_utils.get_adb_activity("clock")),
                env.controller,
            )
            time.sleep(1.0)
            logging.info("      ✅ Clock data cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear clock data: {e}")
        
        # 2. return to home (initialization complete)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            logging.info("      ✅ Returned to home screen")
        except Exception:
            pass
    
    def _reset_init_task5_photo_organize(self, env):
        """
        Task 5 (Photo and Organize):
        Prerequisites: Pre-created dummy photos + cleanup of target folder
        
        🆕 Optimization: Ensure deletion of all possible target folders (including those created in previous runs)
        """
        logging.info("   🔧 Reset Init Task 5: Creating fake photo and clearing folders")
        
        from scendroid.env import adb_utils, device_constants
        from scendroid.utils import file_utils
        import time
        
        # 0. return to home (cleanup previous task state)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
        except Exception:
            pass
        
        # 1. Clear the DCIM/Camera folder
        try:
            file_utils.clear_directory(device_constants.GALLERY_DATA, env.controller)
            logging.info("      ✅ DCIM cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear DCIM: {e}")
        
        # 2. Create dummy photos
        self._create_breakfast_photo(env)
        
        # 3. 🆕 Cleanup target folder (including all possible parent directories and subdirectories)
        # Ensure deletion of folders possibly created in previous runs
        st5 = self.generated_params.get('subtask_5', {})
        folder_name = st5.get('folder_name', 'Weekend/Breakfast')
        
        # All possible folders (including parent directories and full paths for all parameterized options)
        all_folder_names = [
            # Full path (two levels deep)
            'Weekend/Breakfast',
            'Saturday/Food',
            'Weekend/Cooking',
            'MyPhotos/Breakfast',
            # Parent directory (must be deleted to ensure cleanliness)
            'Weekend',
            'Saturday',
            'MyPhotos',
        ]
        
        base_path = device_constants.EMULATOR_DATA  # /storage/emulated/0/
        
        logging.info("      🗑️  Cleaning up all possible target folders (ensuring deletion of leftovers from previous runs)...")
        for folder in all_folder_names:
            folder_path = f"{base_path}{folder}"
            try:
                # Use 'rm -rf' to ensure thorough deletion
                adb_utils.issue_generic_request(
                    ['shell', 'rm', '-rf', folder_path], env.controller
                )
                logging.info(f"         ✅ Deleted: {folder}")
            except Exception as e:
                logging.debug(f"         Failed to delete {folder} (may not exist): {e}")
        
        # 🆕 Verify cleanup result (check whether the target folder for the current task exists)
        logging.info(f"      🔍 Verifying target folder '{folder_name}' does not exist...")
        target_folder_path = f"{base_path}{folder_name}"
        try:
            check_result = adb_utils.issue_generic_request(
                ['shell', 'test', '-e', target_folder_path, '&&', 'echo', 'EXISTS', '||', 'echo', 'NOT_EXIST'],
                env.controller
            )
            if check_result and check_result.generic and check_result.generic.output:
                output = check_result.generic.output.decode('utf-8', errors='ignore').strip()
                if 'NOT_EXIST' in output:
                    logging.info(f"         ✅ confirm: '{folder_name}' does not exist (already cleaned up)")
                else:
                    logging.warning(f"         ⚠️  warning: '{folder_name}' still exists; attempting deletion again...")
                    # Attempt deletion again
                    adb_utils.issue_generic_request(
                        ['shell', 'rm', '-rf', target_folder_path], env.controller
                    )
                    time.sleep(0.5)
        except Exception as e:
            logging.debug(f"         verification failed (can be ignored): {e}")
        
        logging.info("      ✅ Target folders cleared (including leftovers from previous runs)")
        
        # 4. return to home (initialization complete)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            logging.info("      ✅ Returned to home screen")
        except Exception:
            pass
    
    def _reset_init_task6_sms(self, subtask, env):
        """
        Task 6 (Text Friend for Meetup SMS):
        prerequisites:contact + SMSclear
        """
        logging.info("   🔧 Reset Init Task 6: Creating contacts + clearing SMS")
        
        from scendroid.env import adb_utils
        import time
        
        # 0. return to home (cleanup previous task state)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
        except Exception:
            pass
        
        # 1. Create contact and clear SMS
        self._reset_setup_contacts(env)
        
        # 2. Populate evaluator's _contacts_map (if evaluator has this property)
        evaluator = subtask.get('evaluator_instance')
        if evaluator and hasattr(evaluator, '_contacts_map'):
            shared = self.generated_params.get('shared', {})
            friend_name = shared.get('friend_name', 'Bob Johnson')
            friend_phone = shared.get('friend_phone', '555-0102')
            
            all_friends = [
                {"name": "Bob Johnson", "phone": "555-0102"},
                {"name": "Alice Davis", "phone": "555-0201"},
                {"name": "Charlie Wilson", "phone": "555-0301"},
                {"name": "Diana Smith", "phone": "555-0401"},
            ]
            
            evaluator._contacts_map = {f['name']: f['phone'] for f in all_friends}
            logging.info("      ✅ Contacts map populated for evaluator")
        
        # 3. return to home (initialization complete)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            logging.info("      ✅ Returned to home screen")
        except Exception:
            pass
    
    def _reset_init_task7_shopping(self, subtask, env):
        """
        Task 7 (Order Product - Shopping):
        prerequisites:Chrome/Shopping App initialize+login
        evaluator.initialize_task() is sufficient
        """
        logging.info("   🔧 Reset Init Task 7: Initializing Shopping (Chrome/Login)")
        
        from scendroid.env import adb_utils
        import time
        
        # 0. return to home (cleanup previous task state)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
        except Exception:
            pass
        
        # 1. initializeShopping
        subtask['evaluator_instance'].initialize_task(env)
        
        # 2. return to home (initialization complete)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            logging.info("      ✅ Returned to home screen")
        except Exception:
            pass
    
    def _reset_init_task8_expense(self, subtask, env):
        """
        Task 8 (Record Expense):
        prerequisites:Expensedatabaseclear
        evaluator.initialize_task() is sufficient
        """
        logging.info("   🔧 Reset Init Task 8: Clearing Expense database")
        
        from scendroid.env import adb_utils
        import time
        
        # 0. return to home (cleanup previous task state)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
        except Exception:
            pass
        
        # 1. Clear Expense database
        subtask['evaluator_instance'].initialize_task(env)
        
        # 2. return to home (initialization complete)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            logging.info("      ✅ Returned to home screen")
        except Exception:
            pass
    
    def _reset_init_task9_opentracks_qa(self, env):
        """
        Task 9 (Check Walk Stats with Friend QA):
        Prerequisites: OpenTracks activity track (correct + distractor)
        """
        logging.info("   🔧 Reset Init Task 9: Setting up OpenTracks activities")
        
        from scendroid.task_evals.information_retrieval import activity_app_utils
        from scendroid.env import adb_utils
        import time
        
        # 0. return to home (cleanup previous task state)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
        except Exception:
            pass
        
        # 1. clean database
        try:
            activity_app_utils.clear_db(env)
            logging.info("      ✅ OpenTracks database cleared")
        except Exception as e:
            logging.warning(f"      ⚠️  Could not clear OpenTracks: {e}")
        
        # 2. grant permissions
        try:
            adb_utils.launch_app("open tracks sports tracker", env.controller)
        except Exception as e:
            logging.debug(f"      Launch app timeout (expected): {e}")
        
        time.sleep(3.0)
        adb_utils.close_app("open tracks sports tracker", env.controller)
        
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
        time.sleep(2.0)
        
        try:
            from scendroid.env import tools
            controller = tools.AndroidToolController(env=env.controller)
            controller.click_element("Allow")
            logging.info("      ✅ bluetooth permission clicked 'Allow' button")
        except Exception as e:
            logging.debug(f"      'Allow' button not found or already authorized: {e}")
        
        # 3. Create activity track
        self._setup_opentracks_activities(env)
        
        logging.info("      ✅ OpenTracks setup completed")
        
        # 4. return to home (initialization complete)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            logging.info("      ✅ Returned to home screen")
        except Exception:
            pass
    
    def _reset_init_task10_sms_again(self, subtask, env):
        """
        Task 10 (Text Friend Got Home Safe SMS):
        Prerequisites: contact (reusing friend from Task 6) + SMS cleared
        """
        logging.info("   🔧 Reset Init Task 10: Creating contacts + clearing SMS")
        
        from scendroid.env import adb_utils
        import time
        
        # 0. return to home (cleanup previous task state)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
        except Exception:
            pass
        
        # 1. Create contact and clear SMS
        self._reset_setup_contacts(env)
        
        # 2. Populate evaluator's _contacts_map (if evaluator has this property)
        evaluator = subtask.get('evaluator_instance')
        if evaluator and hasattr(evaluator, '_contacts_map'):
            shared = self.generated_params.get('shared', {})
            friend_name = shared.get('friend_name', 'Bob Johnson')
            friend_phone = shared.get('friend_phone', '555-0102')
            
            all_friends = [
                {"name": "Bob Johnson", "phone": "555-0102"},
                {"name": "Alice Davis", "phone": "555-0201"},
                {"name": "Charlie Wilson", "phone": "555-0301"},
                {"name": "Diana Smith", "phone": "555-0401"},
            ]
            
            evaluator._contacts_map = {f['name']: f['phone'] for f in all_friends}
            logging.info("      ✅ Contacts map populated for evaluator")
        
        # 3. return to home (initialization complete)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            logging.info("      ✅ Returned to home screen")
        except Exception:
            pass
    
    def _reset_init_task11_markor_summary(self, subtask, env):
        """
        Task 11 (Weekend Summary - Markor Append):
        Prerequisites: SaturdayBreakfast.md must already exist (created by Task 3 in Scenario mode)
        In Reset mode, SaturdayBreakfast.md must be pre-created
        """
        logging.info("   🔧 Reset Init Task 11: Creating pre-existing SaturdayBreakfast.md")
        
        from scendroid.env import device_constants, adb_utils
        from scendroid.utils import file_utils
        import tempfile
        import os
        import time
        
        # 0. return to home (cleanup previous task state)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
        except Exception:
            pass
        
        # 1. Clear Markor file (using the correct method)
        try:
            markor_dir = device_constants.MARKOR_DATA
            
            # Close Markor
            try:
                adb_utils.close_app("markor", env.controller)
                time.sleep(0.5)
            except Exception:
                pass
            
            # cleanupdirectory
            file_utils.clear_directory(markor_dir, env.controller)
            logging.info("      ✅ Markor files cleared")
        except Exception as e:
            logging.warning(f"      ⚠️ Markor clear failed: {e}")
        
        # 2. Pre-create SaturdayBreakfast.md (simulating Task 3's output)
        st2_3_4 = self.generated_params.get('subtask_2_3_4', {})
        recipe_title = st2_3_4.get('recipe_title', 'Scrambled Eggs with Toast')
        recipe_ingredients = st2_3_4.get('recipe_ingredients', ['eggs', 'butter', 'salt', 'pepper', 'bread'])
        recipe_prep_time = st2_3_4.get('recipe_prep_time', 10)
        
        # Construct initial file content (simulating content created by Task 3)
        initial_content = f"""# Saturday Breakfast Recipe

## Recipe Name
{recipe_title}

## Ingredients
- {recipe_ingredients[0]}
- {recipe_ingredients[1]}
- {recipe_ingredients[2]}
{f'- {recipe_ingredients[3]}' if len(recipe_ingredients) > 3 else ''}
{f'- {recipe_ingredients[4]}' if len(recipe_ingredients) > 4 else ''}

## Cooking Steps
1. Prepare ingredients
2. Cook for {recipe_prep_time} minutes
3. Serve hot
"""
        
        # Use adb to directly create file
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as tmp_file:
                tmp_file.write(initial_content)
                tmp_path = tmp_file.name
            
            # Push to device
            target_path = f"{device_constants.MARKOR_DATA}/SaturdayBreakfast.md"
            adb_utils.issue_generic_request([
                'push', tmp_path, target_path
            ], env.controller)
            
            # Delete temporary file
            os.remove(tmp_path)
            
            logging.info("      ✅ SaturdayBreakfast.md created with recipe content")
        except Exception as e:
            logging.warning(f"      ⚠️ Could not create SaturdayBreakfast.md: {e}")
        
        # 3. return to home (initialization complete)
        try:
            adb_utils.press_home_button(env.controller)
            time.sleep(0.5)
            logging.info("      ✅ Returned to home screen")
        except Exception:
            pass

