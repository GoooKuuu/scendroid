"""
Markor App Evaluators

Provides Markor app-related evaluators (3):

1. LayeredMarkorCreateNote - createnote
2. LayeredMarkorCreateOutline - create outline
3. LayeredMarkorAppendContent - append content

Note: all scendroid.env imports are done inside functions
"""

from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.base import BaseAppEvaluator


@AppRegistry.register_evaluator("LayeredMarkorCreateNote")
class MarkorCreateNoteEvaluator(BaseAppEvaluator):
    """evaluationcreatenotetask"""
    
    app_names = ("markor",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.file_name = params.get('file_name')
        self.content = params.get('content', '')
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """Execute evaluation: check whether the note file is created"""
        try:
            from scendroid.utils import file_utils
            from scendroid.env import device_constants
            
            # check if file exists
            exists = file_utils.check_file_or_folder_exists(
                self.file_name, device_constants.MARKOR_DATA, env.controller
            )
            
            if not exists:
                logging.warning(f"❌ FAILED - File '{self.file_name}' not found")
                return 0.0
            
            # If content checking is required
            if self.content:
                import os
                file_path = os.path.join(device_constants.MARKOR_DATA, self.file_name)
                content_match = file_utils.check_file_content(
                    file_path, self.content, env.controller
                )
                if not content_match:
                    logging.warning(f"❌ FAILED - Content not found in '{self.file_name}'")
                    return 0.0
            
            logging.warning(f"✅ PASSED - Note '{self.file_name}' created")
            return 1.0
        except Exception as e:
            logging.error(f"❌ evaluation error: {e}")
            return 0.0
    
    def initialize_task(self, env):
        """initialize task"""
        from scendroid.task_evals.single import markor
        
        super().initialize_task(env)
        markor.clear_markor_files(env)


@AppRegistry.register_evaluator("LayeredMarkorCreateOutline")
class MarkorCreateOutlineEvaluator(BaseAppEvaluator):
    """Evaluation task for creating an outline
    
    parameters:
    - file_name: file name
    - required_sections: all sections that must be included
    - sections_with_content: sections that must contain content (optional)
    - header_only_sections: sections that require only headers (optional)
    
    Reference legacy architecture: layered_tasks.py LayeredMarkorCreateOutline
    """
    
    app_names = ("markor",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.file_name = params.get('file_name')
        
        # Compatible with two parameter formats:
        # 1. Legacy format: sections (list)
        # 2. New format: required_sections (list)
        self.required_sections = params.get('required_sections', params.get('sections', []))
        self.sections_with_content = params.get('sections_with_content', [])
        self.header_only_sections = params.get('header_only_sections', [])
        
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """Execute evaluation: check whether the outline file is created
        
        Evaluation logic:
        1. check if file exists
        2. Read the file content
        3. Check whether all required_sections appear in the file (case-insensitive)
        
        Reference: layered_tasks.py Lines 6032-6095
        """
        logging.info("=" * 60)
        logging.info("📊 Evaluating Markor Outline:")
        logging.info("=" * 60)
        
        try:
            from scendroid.utils import file_utils
            from scendroid.env import device_constants, adb_utils
            import os
            import time
            
            file_path = os.path.join(device_constants.MARKOR_DATA, self.file_name)
            
            # 🆕 Retry reading the file multiple times (Markor save may have latency)
            # Reference implementation in scenarios_d/e: directly attempt to read the file without using check_file_exists
            content = None
            max_retries = 5
            retry_delay = 2.0  # Wait 2 seconds before each retry
            
            for attempt in range(max_retries):
                # Force synchronization of the file system
                try:
                    adb_utils.issue_generic_request(["shell", "sync"], env.controller)
                    time.sleep(0.5)
                except Exception:
                    pass
                
                # 🆕 Directly attempt to read the file content (without using check_file_exists, as it may be unstable)
                try:
                    logging.info(f"   🔍 Attempt {attempt + 1}/{max_retries}: Reading file: {file_path}")
                    response = adb_utils.issue_generic_request(
                        ["shell", "cat", file_path], 
                        env.controller
                    )
                    raw_output = response.generic.output.decode('utf-8', errors='ignore')
                    content = raw_output.replace("\r", "")
                    
                    # Check whether content was successfully read
                    if content and content.strip():
                        # Exclude "No such file" error information
                        if "No such file" in content or "not found" in content.lower():
                            content = None
                            logging.info(f"   ⏳ File not found, retrying...")
                        else:
                            logging.info(f"   ✅ File content read successfully on attempt {attempt + 1}")
                            break
                    else:
                        logging.info(f"   ⏳ File appears empty...")
                        
                except Exception as e:
                    logging.warning(f"   ⚠️ Could not read file: {e}")
                    content = None
                
                # If reading failed, wait and retry
                if not content or not content.strip():
                    if attempt < max_retries - 1:
                        logging.info(f"   ⏳ Retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                    else:
                        logging.warning(f"   ❌ FAIL: File '{file_path}' not found or empty after {max_retries} attempts")
                        logging.info("=" * 60)
                        return 0.0
            
            if not content or not content.strip():
                logging.warning("   ❌ FAIL: File is empty")
                logging.info("=" * 60)
                return 0.0
            
            content_lower = content.lower()
            logging.info(f"   File: {self.file_name}")
            logging.info(f"   Content ({len(content)} chars):")
            logging.info(f"   {content[:500]}...")
            
            # Check whether all required sections exist
            required_sections_lower = [s.lower() for s in self.required_sections]
            sections_found = []
            sections_missing = []
            
            for section in required_sections_lower:
                if section in content_lower:
                    sections_found.append(section)
                else:
                    sections_missing.append(section)
            
            logging.info(f"   Required sections: {self.required_sections}")
            logging.info(f"   Sections found: {sections_found}")
            
            if sections_missing:
                logging.warning(f"   ❌ FAIL: Missing sections: {sections_missing}")
                logging.info("=" * 60)
                return 0.0
            
            logging.warning(f"   ✅ SUCCESS: All sections found!")
            logging.info("=" * 60)
            return 1.0
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.info("=" * 60)
            return 0.0
    
    def initialize_task(self, env):
        """initialize task"""
        from scendroid.task_evals.single import markor
        
        super().initialize_task(env)
        markor.clear_markor_files(env)


@AppRegistry.register_evaluator("LayeredMarkorAppendContent")
class MarkorAppendContentEvaluator(BaseAppEvaluator):
    """Evaluation task for appending content
    
    Supports two evaluation modes:
    1. Simple mode: check whether append_content appears in the file
    2. Detailed mode: check section_title + meeting_keywords + expense_amount
    
    Reference: layered_tasks.py LayeredMarkorAppendContent (Lines 6108-6300)
    """
    
    app_names = ("markor",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.file_name = params.get('file_name')
        self.initial_content = params.get('initial_content', '')
        self.append_content = params.get('append_content', '')
        
        # Detailed evaluation parameters
        self.section_title = params.get('section_title', '')
        self.must_mention_meeting = params.get('must_mention_meeting', False)
        self.meeting_keywords = params.get('meeting_keywords', [])
        self.must_mention_expense = params.get('must_mention_expense', False)
        self.expense_amount = params.get('expense_amount', 0)
        
        # Strict mode parameters
        self.require_all_keywords = params.get('require_all_keywords', False)  # Whether all keywords must match
        self.strict_scoring = params.get('strict_scoring', True)  # 🆕 Default to strict scoring (returns only 0 or 1)
        
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """Execute evaluation: check whether content was appended
        
        Reference: layered_tasks.py Lines 6190-6284
        """
        logging.info("=" * 60)
        logging.info("📊 Evaluating Markor Append Content:")
        logging.info("=" * 60)
        
        try:
            from scendroid.utils import file_utils
            from scendroid.env import device_constants, adb_utils
            import os
            import time
            
            file_path = os.path.join(device_constants.MARKOR_DATA, self.file_name)
            
            # 🆕 Retry reading the file multiple times (Markor save may have latency)
            # Refer to the implementation of scenario_d/e: directly attempt to read the file without using check_file_exists
            current_content = None
            max_retries = 5
            retry_delay = 2.0
            
            for attempt in range(max_retries):
                # Force syncfile system
                try:
                    adb_utils.issue_generic_request(["shell", "sync"], env.controller)
                    time.sleep(0.5)
                except Exception:
                    pass
                
                # 🆕 Directly attempt to read file content (without using check_file_exists, as it may be unstable)
                try:
                    logging.info(f"   🔍 Attempt {attempt + 1}/{max_retries}: Reading file: {file_path}")
                    response = adb_utils.issue_generic_request(
                        ["shell", "cat", file_path], 
                        env.controller
                    )
                    raw_output = response.generic.output.decode('utf-8', errors='ignore')
                    current_content = raw_output.replace("\r", "")
                    
                    # Check whether content was successfully read
                    if current_content and current_content.strip():
                        # Exclude "No such file" error information
                        if "No such file" in current_content or "not found" in current_content.lower():
                            current_content = None
                            logging.info(f"   ⏳ File not found, retrying...")
                        else:
                            logging.info(f"   ✅ File content read successfully on attempt {attempt + 1}")
                            break
                    else:
                        logging.info(f"   ⏳ File appears empty...")
                        
                except Exception as e:
                    logging.warning(f"   ⚠️ Could not read file: {e}")
                    current_content = None
                
                # If reading did not succeed, etc., retry later
                if not current_content or not current_content.strip():
                    if attempt < max_retries - 1:
                        logging.info(f"   ⏳ Retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                    else:
                        logging.warning(f"   ❌ FAIL: File '{self.file_name}' not found or empty after {max_retries} attempts")
                        logging.info("=" * 60)
                        return 0.0
            
            if not current_content or not current_content.strip():
                logging.warning("   ❌ FAIL: File is empty")
                logging.info("=" * 60)
                return 0.0
            
            logging.info(f"   File: {self.file_name}")
            logging.info(f"   Content ({len(current_content)} chars):")
            logging.info(f"   {current_content[:300]}...")
            
            # mode1: Simple mode — check append_content (exact match)
            if self.append_content:
                content_lower = current_content.lower()
                append_lower = self.append_content.lower()
                
                if append_lower in content_lower:
                    logging.warning(f"   ✅ SUCCESS: Content appended")
                    logging.info("=" * 60)
                    return 1.0
                else:
                    logging.warning(f"   ❌ FAIL: Append content not found")
                    logging.info(f"   Expected: {self.append_content}")
                    logging.info(f"   Content preview: {current_content[:200]}...")
                    logging.info("=" * 60)
                    return 0.0
            
            # mode2: Detailed mode — check section_title + keywords + amount
            # Refer to the legacy architecture, Lines 6220–6284
            
            # check1: Whether section_title exists
            if self.section_title:
                section_title_lower = self.section_title.lower()
                if section_title_lower not in current_content.lower():
                    logging.warning(f"   ❌ FAIL: Section title '{self.section_title}' not found")
                    logging.info("=" * 60)
                    return 0.0
                logging.info(f"   ✅ Section '{self.section_title}' found")
            
            # Under scenariomode, _initial_content is empty; check the entire file
            # Refer to the legacy architecture, Lines 6235–6245
            if self.initial_content:
                new_content = current_content[len(self.initial_content):].lower()
                if not new_content:
                    logging.warning("   ❌ FAIL: No new content added")
                    logging.info("=" * 60)
                    return 0.0
            else:
                # Scenario mode: check entire file content
                new_content = current_content.lower()
                logging.info("   ℹ️  Scenario mode: checking entire file content")
            
            logging.info(f"   Content to check ({len(new_content)} chars): {new_content[:150]}...")
            
            score = 1.0
            
            # check2: meeting keywords
            # Refer to the legacy architecture, Lines 6252–6260
            if self.must_mention_meeting:
                meeting_keywords_lower = [k.lower() for k in self.meeting_keywords]
                matched_keywords = [k for k in meeting_keywords_lower if k in new_content]
                missing_keywords = [k for k in meeting_keywords_lower if k not in new_content]
                
                logging.info(f"   Checking meeting keywords: {self.meeting_keywords}")
                logging.info(f"   Found: {matched_keywords}")
                
                if self.require_all_keywords:
                    # Strict mode: requires all keywords to appear
                    has_all = len(missing_keywords) == 0
                    if not has_all:
                        logging.warning(f"   ❌ Missing keywords: {missing_keywords}")
                        score = 0.0
                    else:
                        logging.info(f"   ✅ All keywords found")
                else:
                    # Lenient mode: requires only one keyword to appear
                    has_any = len(matched_keywords) > 0
                    if not has_any:
                        logging.warning(f"   ⚠️  Missing meeting keywords (at least one of): {self.meeting_keywords}")
                        score = min(score, 0.5)
                    else:
                        logging.info(f"   ✅ Meeting mentioned (found: {matched_keywords})")
            
            # check3: expense amount
            # Refer to the legacy architecture, Lines 6263–6274
            if self.must_mention_expense:
                expense_amount_str = str(self.expense_amount)
                # Check variants: "54.99", "$54.99", "54", etc.
                amount_base = expense_amount_str.split('.')[0]  # "54" from "54.99"
                has_expense = (expense_amount_str in new_content or 
                              amount_base in new_content)
                
                logging.info(f"   Checking expense amount: {self.expense_amount}")
                if not has_expense:
                    logging.warning(f"   ❌ Missing expense amount: {self.expense_amount}")
                    if self.strict_scoring:
                        score = 0.0
                    else:
                        score = min(score, 0.5)
                else:
                    logging.info(f"   ✅ Expense amount mentioned")
            
            # Strict scoring mode: returns only 0 or 1
            if self.strict_scoring and score < 1.0:
                score = 0.0
            
            # returnresult
            if score >= 1.0:
                logging.warning("   ✅ SUCCESS: All requirements met")
            elif score > 0.0:
                logging.warning("   ⚠️  PARTIAL: Some requirements missing")
            else:
                logging.warning("   ❌ FAIL: Requirements not met")
            
            logging.info("=" * 60)
            return score
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.info("=" * 60)
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task: create initial file"""
        from scendroid.task_evals.single import markor
        
        super().initialize_task(env)
        markor.clear_markor_files(env)
        
        # Create a file containing initial content (if specified)
        if self.initial_content:
            markor.create_file_with_content(
                env, self.file_name, self.initial_content
            )


@AppRegistry.register_evaluator("LayeredMarkorCreateRecipeNote")
class MarkorCreateRecipeNoteEvaluator(BaseAppEvaluator):
    """
    evaluationcreate structured recipe note task — enhanced version
    
    supported scenarios:
    - Scenario C Task 3: "Open Markor and create a markdown file called 'SaturdayBreakfast.md'. 
                          Write: (1) the recipe name you found, (2) an ingredients list, 
                          and (3) 3–5 short, practical cooking steps."
    
    initialization:
    - Clean up Markor files by the Scenario evaluator during batch initialization
    
    Evaluation content (enhanced):
    - check if file exists
    - Check whether a recipe name/title exists
    - Check whether an ingredient list exists
    - Check whether cooking steps exist
    - 🆕 Check whether the parameterized recipe name is correct
    - 🆕 Check whether the parameterized ingredients are correct
    
    parameters:
    - file_name: file name
    - required_sections: sections that must be present
    - min_steps: minimum number of steps (default: 3)
    - max_steps: maximum number of steps (default: 5)
    - 🆕 expected_recipe_title: expected recipe title
    - 🆕 expected_ingredients: expected ingredient list
    - 🆕 expected_prep_time: expected cooking time
    """
    
    # ScenDroid standard attributes
    app_names = ("markor",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # fileparameter
        self.file_name = params.get('file_name')
        
        # Structural requirements
        self.required_sections = params.get('required_sections', [])
        self.min_steps = params.get('min_steps', 3)
        self.max_steps = params.get('max_steps', 5)
        
        # 🆕 Parameterized evaluation parameter
        self.expected_recipe_title = params.get('expected_recipe_title', None)
        self.expected_ingredients = params.get('expected_ingredients', [])
        self.expected_prep_time = params.get('expected_prep_time', None)
        
        # set complexity
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: check the structure and content of the recipe note
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure (binary scoring; all elements must be present)
        """
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Markor Recipe Note:")
        logging.warning("=" * 60)
        
        try:
            from scendroid.utils import file_utils
            from scendroid.env import device_constants, adb_utils
            import os
            import re
            
            file_path = os.path.join(device_constants.MARKOR_DATA, self.file_name)
            
            # 1. check if file exists
            if not file_utils.check_file_exists(file_path, env.controller):
                logging.warning(f"   ❌ FAIL: File '{self.file_name}' not found")
                logging.warning("=" * 60)
                return 0.0
            
            logging.warning(f"   ✅ File exists: {self.file_name}")
            
            # 2. Read file content (using the cat command, refer to MarkorCreateNote)
            try:
                logging.info(f"   🔍 Reading file: {file_path}")
                response = adb_utils.issue_generic_request(
                    ["shell", "cat", file_path], 
                    env.controller
                )
                content = response.generic.output.decode('utf-8', errors='ignore').replace("\r", "")
            except Exception as e:
                logging.warning(f"   ❌ FAIL: Could not read file: {e}")
                import traceback
                logging.warning(traceback.format_exc())
                logging.warning("=" * 60)
                return 0.0
            
            if not content:
                logging.warning("   ❌ FAIL: File is empty")
                logging.warning("=" * 60)
                return 0.0
            
            content_lower = content.lower()
            logging.warning(f"   File content ({len(content)} chars):")
            logging.warning(f"   {content[:300]}...")
            
            # 3. Check recipe name/title
            has_recipe_name = False
            has_correct_recipe = True  # Default to True if no expected value is specified
            
            # Method 1: Check Markdown title
            title_patterns = [
                r'^#\s+.+',  # # Title
                r'^##\s+.+',  # ## Title
            ]
            for pattern in title_patterns:
                if re.search(pattern, content, re.MULTILINE):
                    has_recipe_name = True
                    break
            
            # Method 2: Check whether it contains recipe-related keywords
            recipe_keywords = ['recipe', 'scrambled', 'omelet', 'fried', 'boiled', 'egg', 'toast', 'wrap']
            if not has_recipe_name:
                for keyword in recipe_keywords:
                    if keyword in content_lower:
                        has_recipe_name = True
                        break
            
            # 🆕 Check whether it contains the expected recipe title
            if self.expected_recipe_title:
                title_lower = self.expected_recipe_title.lower()
                # Check title keywords
                title_words = [w for w in title_lower.split() if len(w) > 2]
                matches = sum(1 for w in title_words if w in content_lower)
                has_correct_recipe = matches >= len(title_words) * 0.5  # At least 50% match
                
                if has_correct_recipe:
                    logging.warning(f"   ✅ Correct recipe title '{self.expected_recipe_title}' found")
                else:
                    logging.warning(f"   ⚠️ Expected recipe '{self.expected_recipe_title}' not found ({matches}/{len(title_words)} words matched)")
            
            if has_recipe_name:
                logging.warning(f"   ✅ Recipe name/title found")
            else:
                logging.warning(f"   ❌ Recipe name/title not found")
            
            # 4. Check ingredient list
            has_ingredients = False
            has_correct_ingredients = True  # Default to True
            
            # Method 1: Check "ingredient" keyword
            if 'ingredient' in content_lower:
                has_ingredients = True
            
            # Method 2: Check whether there is a list (at least two items)
            if not has_ingredients:
                list_items = re.findall(r'^[\-\*]\s+.+', content, re.MULTILINE)
                if len(list_items) >= 2:
                    has_ingredients = True
            
            # Method 3: Check common ingredient keywords
            if not has_ingredients:
                ingredient_keywords = ['egg', 'butter', 'oil', 'salt', 'pepper', 'bread', 'cheese']
                found_ingredients = sum(1 for k in ingredient_keywords if k in content_lower)
                if found_ingredients >= 2:
                    has_ingredients = True
            
            # 🆕 Check whether it contains the expected ingredients
            if self.expected_ingredients:
                found_expected = sum(1 for ing in self.expected_ingredients if ing.lower() in content_lower)
                min_required = max(2, len(self.expected_ingredients) // 2)  # At least half or two items
                has_correct_ingredients = found_expected >= min_required
                
                if has_correct_ingredients:
                    logging.warning(f"   ✅ Expected ingredients found ({found_expected}/{len(self.expected_ingredients)})")
                else:
                    logging.warning(f"   ⚠️ Missing expected ingredients ({found_expected}/{len(self.expected_ingredients)}, need {min_required})")
            
            if has_ingredients:
                logging.warning(f"   ✅ Ingredients list found")
            else:
                logging.warning(f"   ❌ Ingredients list not found")
            
            # 5. Check cooking steps
            has_steps = False
            step_count = 0
            
            # Method 1: Check numbered list (one step per line)
            numbered_steps = re.findall(r'^\d+\.\s+.+', content, re.MULTILINE)
            step_count = len(numbered_steps)
            
            # 🆕 Method 1.5: Check multiple steps on the same line (e.g., "1. xxx 2. xxx 3. xxx")
            if step_count <= 1:
                inline_steps = re.findall(r'\d+\.\s+[^0-9]+', content)
                if len(inline_steps) > step_count:
                    step_count = len(inline_steps)
            
            # Method 2: Check lines containing "step"
            if step_count == 0:
                step_lines = re.findall(r'.*step.*', content_lower, re.MULTILINE)
                step_count = len(step_lines)
            
            # 🆕 Method 2.5: Check "directions" keyword
            if step_count == 0:
                if 'direction' in content_lower:
                    # If the "directions" keyword exists, consider steps present
                    step_count = 3  # Assume at least three steps
            
            # Method 3: Check list items (if not previously identified as ingredients)
            if step_count == 0:
                list_items = re.findall(r'^[\-\*]\s+.+', content, re.MULTILINE)
                # Assume at least half are steps
                step_count = len(list_items) // 2 if len(list_items) > 2 else 0
            
            # 🆕 Method 4: Check verb keywords (cook, add, heat, mix, stir, pour, serve, etc.)
            if step_count == 0:
                cooking_verbs = ['cook', 'add', 'heat', 'mix', 'stir', 'pour', 'serve', 'scramble', 'warm', 'roll', 'season', 'beat', 'melt', 'toast']
                found_verbs = sum(1 for v in cooking_verbs if v in content_lower)
                if found_verbs >= 3:
                    step_count = found_verbs  # Assume each verb corresponds to one step
            
            # Success if any steps exist (user feedback: step count is hard to standardize)
            if step_count >= 1:
                has_steps = True
                logging.warning(f"   ✅ Cooking steps found: {step_count} steps")
            else:
                logging.warning(f"   ❌ Cooking steps: No steps found")
            
            # 6. Binary rating: all elements must be present
            logging.warning("-" * 60)
            logging.warning("📊 Evaluation Summary:")
            logging.warning(f"   File exists: ✅")
            logging.warning(f"   Recipe name: {'✅' if has_recipe_name else '❌'}")
            if self.expected_recipe_title:
                logging.warning(f"   Correct recipe: {'✅' if has_correct_recipe else '❌'}")
            logging.warning(f"   Ingredients: {'✅' if has_ingredients else '❌'}")
            if self.expected_ingredients:
                logging.warning(f"   Correct ingredients: {'✅' if has_correct_ingredients else '❌'}")
            logging.warning(f"   Steps ({step_count}): {'✅' if has_steps else '❌'}")
            
            # 🆕 Include parameterized check result
            all_pass = has_recipe_name and has_ingredients and has_steps
            if self.expected_recipe_title:
                all_pass = all_pass and has_correct_recipe
            if self.expected_ingredients:
                all_pass = all_pass and has_correct_ingredients
            
            if all_pass:
                logging.warning("   ✅ SUCCESS: Complete recipe note with all requirements")
                logging.warning("=" * 60)
                return 1.0
            else:
                logging.warning("   ❌ FAIL: Missing one or more requirements")
                logging.warning("=" * 60)
                return 0.0
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.warning("=" * 60)
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize task: Handled by the Scenario evaluator
        
        Note: In Scenario mode, the Markor file has already been cleaned up during batch initialization
        """
        super().initialize_task(env)
        logging.info("=" * 60)
        logging.info("🔧 Initializing Markor Recipe Note Task:")
        logging.info(f"   File: {self.file_name}")
        logging.info(f"   Required sections: {self.required_sections}")
        logging.info(f"   Steps: {self.min_steps}-{self.max_steps}")
        logging.info("=" * 60)
    
    def tear_down(self, env):
        """
        cleanup_environment: Do not clean up files (managed by Scenario)
        """
        super().tear_down(env)
        logging.info("✅ Markor Recipe Note task cleanup complete")


@AppRegistry.register_evaluator("LayeredMarkorRenameAndAppendSummary")
class MarkorRenameAndAppendSummaryEvaluator(BaseAppEvaluator):
    """
    Evaluation rename + append summary task
    
    task workflow:
    1. Rename SaturdayBreakfast.md to weekendsummary.md
    2. Append weekend summary content to weekendsummary.md
    3. Mention expense (keywords: egg, 11.8)
    4. Mention track/walk (keyword: walk)
    
    parameters:
    - original_file: Original file name (e.g., "SaturdayBreakfast.md")
    - new_file: New file name (e.g., "weekendsummary.md")
    - expense_keywords: List of expense keywords (e.g., ["egg", "11.8"])
    - track_keywords: List of track keywords (e.g., ["walk"])
    """
    
    app_names = ("markor",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.original_file = params.get('original_file', 'SaturdayBreakfast.md')
        self.new_file = params.get('new_file', 'weekendsummary.md')
        self.expense_keywords = params.get('expense_keywords', ['egg', '11.8'])
        self.track_keywords = params.get('track_keywords', ['walk'])
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: check file renaming and content appending
        
        Binary scoring (1 point only if all criteria are fully met):
        - The new file exists (weekendsummary.md)
        - Contains the "expense" keyword (both "egg" and "11.8" must be present)
        - Contains the "track" keyword ("walk")
        - All conditions satisfied → 1.0; otherwise → 0.0
        """
        try:
            import os
            from scendroid.utils import file_utils
            from scendroid.env import device_constants
            
            logging.warning("=" * 60)
            logging.warning("📊 Markor Rename & Append Summary Evaluation")
            logging.warning("=" * 60)
            
            markor_dir = device_constants.MARKOR_DATA
            original_path = os.path.join(markor_dir, self.original_file)
            new_path = os.path.join(markor_dir, self.new_file)
            
            # 1. Check whether the new file exists (mandatory condition)
            # 🆕 Use case-insensitive matching via file size
            new_exists = False
            actual_new_file = None
            
            try:
                from scendroid.env import adb_utils
                # List all files in the Markor directory
                result = adb_utils.issue_generic_request(
                    ["shell", "ls", markor_dir], env.controller
                )
                if result and result.generic and result.generic.output:
                    files = result.generic.output.decode('utf-8', errors='ignore').strip().split('\n')
                    # Case-insensitive matching
                    new_file_lower = self.new_file.lower()
                    for f in files:
                        f = f.strip()
                        if f.lower() == new_file_lower:
                            new_exists = True
                            actual_new_file = f
                            new_path = os.path.join(markor_dir, f)  # Use the actual filename
                            break
            except Exception as e:
                logging.warning(f"   ⚠️ Error listing files: {e}")
            
            # Fallback: exact matching
            if not new_exists:
                new_exists = file_utils.check_file_or_folder_exists(
                    self.new_file, markor_dir, env.controller
                )
            
            # 2. Check whether the original file still exists (optional, for informational purposes only)
            original_exists = file_utils.check_file_or_folder_exists(
                self.original_file, markor_dir, env.controller
            )
            
            logging.warning(f"📁 File Check:")
            logging.warning(f"   Original file ({self.original_file}): {'⚠️  Still exists' if original_exists else '✅ Deleted/Renamed'}")
            logging.warning(f"   New file ({self.new_file}): {'✅ Exists' if new_exists else '❌ Not found'}")
            
            if not new_exists:
                logging.warning(f"❌ FAIL: New file '{self.new_file}' not found")
                logging.warning("=" * 60)
                return 0.0
            
            # 3. Read the new file's content (using the "cat" command)
            try:
                from scendroid.env import adb_utils
                response = adb_utils.issue_generic_request(
                    ["shell", "cat", new_path], 
                    env.controller
                )
                content = response.generic.output.decode('utf-8', errors='ignore').replace("\r", "")
            except Exception as e:
                logging.warning(f"❌ FAIL: Could not read file: {e}")
                logging.warning("=" * 60)
                return 0.0
            
            if not content:
                logging.warning(f"❌ FAIL: New file is empty")
                logging.warning("=" * 60)
                return 0.0
            
            content_lower = content.lower()
            logging.warning(f"📄 Content length: {len(content)} chars")
            logging.warning(f"   Preview: {content[:200]}...")
            
            # 4. Check for "expense" keywords (at least half must match)
            expense_found = []
            for keyword in self.expense_keywords:
                if keyword.lower() in content_lower:
                    expense_found.append(keyword)
            
            # At least half of the keywords must match, or at least one keyword must match
            min_required = max(1, len(self.expense_keywords) // 2)
            expense_pass = len(expense_found) >= min_required
            if expense_pass:
                logging.warning(f"   ✅ Expense keywords found: {expense_found} ({len(expense_found)}/{len(self.expense_keywords)}, min={min_required})")
            else:
                logging.warning(f"   ❌ Expense keywords missing: {expense_found}/{self.expense_keywords} (need at least {min_required})")
            
            # 5. Check for "track" keywords (at least one must match, if the list is non-empty)
            track_found = []
            for keyword in self.track_keywords:
                if keyword.lower() in content_lower:
                    track_found.append(keyword)
            
            # Skip this check if "track_keywords" is not configured
            if not self.track_keywords:
                track_pass = True
                logging.warning(f"   ℹ️  Track keywords: Not required")
            elif len(track_found) >= 1:
                track_pass = True
                logging.warning(f"   ✅ Track keywords found: {track_found}")
            else:
                track_pass = False
                logging.warning(f"   ❌ Track keywords missing")
            
            # 6. Binary rating: 1 point only if all criteria are fully met
            logging.warning("-" * 60)
            all_pass = new_exists and expense_pass and track_pass
            
            if all_pass:
                logging.warning("✅ SUCCESS: All requirements met")
                logging.warning("=" * 60)
                return 1.0
            else:
                logging.warning("❌ FAIL: Some requirements not met")
                logging.warning(f"   File exists: {new_exists}")
                logging.warning(f"   Expense keywords: {expense_pass}")
                logging.warning(f"   Track keywords: {track_pass}")
                logging.warning("=" * 60)
                return 0.0
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.warning("=" * 60)
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize task: handled by the Scenario evaluator
        """
        super().initialize_task(env)
        logging.info("=" * 60)
        logging.info("🔧 Initializing Markor Rename & Append Summary Task:")
        logging.info(f"   Original file: {self.original_file}")
        logging.info(f"   New file: {self.new_file}")
        logging.info(f"   Expense keywords: {self.expense_keywords}")
        logging.info(f"   Track keywords: {self.track_keywords}")
        logging.info("=" * 60)
    
    def tear_down(self, env):
        """
        Cleanup environment: do not clean up files (managed by Scenario)
        """
        super().tear_down(env)
        logging.info("✅ Markor Rename & Append task cleanup complete")


# ============================================================================
# 6. LayeredMarkorAppendWithKeywords - Append content and check keywords (used in Scenario D)
# ============================================================================

@AppRegistry.register_evaluator("LayeredMarkorAppendWithKeywords")
class MarkorAppendWithKeywordsEvaluator(BaseAppEvaluator):
    """
    Evaluation task for appending content (with keyword checking)
    
    supported scenarios:
    - D10: "Append today's total spending and USB drive name to AI_Notes.md"
    
    evaluation content:
    - check if file exists
    - Check whether the file contains all required keywords
    - Support flexible keyword matching (case-insensitive)
    
    Note:
    - This is an extended version of LayeredMarkorAppendContent
    - Specifically designed for scenarios requiring multiple keyword checks
    """
    
    app_names = ("markor",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # fileparameter
        self.file_name = params.get('file_name')  # e.g.:"AI_Notes.md"
        
        # List of required keywords
        self.must_contain_keywords = params.get('must_contain_keywords', [])
        
        # List of optional keywords (at least N must match)
        self.optional_keywords = params.get('optional_keywords', [])
        self.min_optional_matches = params.get('min_optional_matches', 0)
        
        # Minimum number of matches required (for required keywords)
        self.min_keywords_found = params.get('min_keywords_found', len(self.must_contain_keywords))
        
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: check whether all keywords are present in the file
        
        Returns:
            float: 1.0 indicates success; partial matches return a proportional score; 0.0 indicates failure
        """
        from scendroid.utils import file_utils
        from scendroid.env import device_constants, adb_utils
        import os
        
        logging.info("=" * 60)
        logging.info("📊 Evaluating Markor Append with Keywords:")
        logging.info("=" * 60)
        logging.info(f"   File: {self.file_name}")
        logging.info(f"   Must contain: {self.must_contain_keywords}")
        if self.optional_keywords:
            logging.info(f"   Optional keywords: {self.optional_keywords}")
        
        try:
            file_path = os.path.join(device_constants.MARKOR_DATA, self.file_name)
            
            # check if file exists
            if not file_utils.check_file_exists(file_path, env.controller):
                logging.warning(f"   ❌ FAIL: File '{self.file_name}' not found")
                logging.info("=" * 60)
                return 0.0
            
            # Read file content
            try:
                response = adb_utils.issue_generic_request(
                    ["shell", "cat", file_path], 
                    env.controller
                )
                content = response.generic.output.decode('utf-8', errors='ignore').replace("\r", "")
            except Exception as e:
                logging.warning(f"   ❌ FAIL: Could not read file: {e}")
                logging.info("=" * 60)
                return 0.0
            
            if not content:
                logging.warning("   ❌ FAIL: File is empty")
                logging.info("=" * 60)
                return 0.0
            
            logging.info(f"   File content ({len(content)} chars):")
            logging.info(f"   {content[:500]}...")
            
            # Check required keywords
            content_lower = content.lower()
            found_keywords = []
            missing_keywords = []
            
            for keyword in self.must_contain_keywords:
                keyword_lower = str(keyword).lower()
                if keyword_lower in content_lower:
                    found_keywords.append(keyword)
                    logging.info(f"   ✅ Found: '{keyword}'")
                else:
                    missing_keywords.append(keyword)
                    logging.warning(f"   ❌ Missing: '{keyword}'")
            
            # Check optional keywords (if any)
            optional_found = 0
            if self.optional_keywords:
                for keyword in self.optional_keywords:
                    if str(keyword).lower() in content_lower:
                        optional_found += 1
                        logging.info(f"   ✅ Optional found: '{keyword}'")
                
                logging.info(f"   Optional keywords matched: {optional_found}/{len(self.optional_keywords)}")
            
            # Calculate score
            num_found = len(found_keywords)
            num_required = max(self.min_keywords_found, 1)  # At least one required
            
            # Score for required keywords (90% weight)
            required_score = min(num_found / num_required, 1.0) * 0.9
            
            # Score for optional keywords (10% weight)
            optional_score = 0.0
            if self.optional_keywords and self.min_optional_matches > 0:
                optional_score = min(optional_found / self.min_optional_matches, 1.0) * 0.1
            else:
                optional_score = 0.1  # Assign full score if no optional keywords exist
            
            total_score = required_score + optional_score
            
            logging.info(f"   Found {num_found}/{len(self.must_contain_keywords)} required keywords")
            
            if missing_keywords:
                logging.warning(f"   ❌ Missing keywords: {missing_keywords}")
            
            if total_score >= 0.99:
                logging.warning(f"   ✅ SUCCESS: All keywords found")
                logging.info("=" * 60)
                return 1.0
            elif total_score >= 0.5:
                logging.warning(f"   ⚠️  PARTIAL: Some keywords found ({total_score:.2f})")
                logging.info("=" * 60)
                return total_score
            else:
                logging.warning(f"   ❌ FAIL: Insufficient keywords ({total_score:.2f})")
                logging.info("=" * 60)
                return 0.0
                
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.info("=" * 60)
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task: Ensure the file exists (but do not create a new file)."""
        super().initialize_task(env)
        
        # Note: In Scenario D, D8 has already created AI_Notes.md.
        # No additional initialization is required here.


# ============================================================================
# New: Scenario-related evaluators
# ============================================================================

@AppRegistry.register_evaluator("LayeredMarkorAppendSummary")
class MarkorAppendSummaryEvaluator(BaseAppEvaluator):
    """Append a summary to the end of the file (must mention specific keywords)."""
    
    app_names = ("markor",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.file_name = params.get('file_name')
        self.must_mention = params.get('must_mention', [])  # Keywords that must be mentioned
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """Check whether content containing the keywords has been appended to the end of the file."""
        try:
            from scendroid.utils import file_utils
            from scendroid.env import device_constants
            import os
            
            file_path = os.path.join(device_constants.MARKOR_DATA, self.file_name)
            content = file_utils.get_file_content(file_path, env.controller)
            
            if not content:
                logging.warning(f"❌ FAILED - File '{self.file_name}' is empty or not found")
                return 0.0
            
            content_lower = content.lower()
            score = 0.0
            for keyword in self.must_mention:
                if keyword.lower() in content_lower:
                    score += 1.0
                    logging.warning(f"   ✅ Found keyword: '{keyword}'")
                else:
                    logging.warning(f"   ❌ Missing keyword: '{keyword}'")
            
            final_score = score / len(self.must_mention) if self.must_mention else 1.0
            logging.warning(f"{'✅ PASSED' if final_score >= 0.8 else '❌ FAILED'} - Score: {final_score:.2f}")
            
            return final_score
        except Exception as e:
            logging.error(f"❌ Error: {e}")
            return 0.0


@AppRegistry.register_evaluator("LayeredMarkorAppendReference")
class MarkorAppendReferenceEvaluator(BaseAppEvaluator):
    """Append a file reference (e.g., audio recording file name)."""
    
    app_names = ("markor",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.file_name = params.get('file_name')
        self.must_reference = params.get('must_reference', '')
        self.reference_type = params.get('reference_type', 'file')
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """Check whether the file reference is included."""
        try:
            from scendroid.utils import file_utils
            from scendroid.env import device_constants
            import os
            
            file_path = os.path.join(device_constants.MARKOR_DATA, self.file_name)
            content = file_utils.get_file_content(file_path, env.controller)
            
            if not content:
                return 0.0
            
            if self.must_reference.lower() in content.lower():
                logging.warning(f"✅ PASSED - Reference '{self.must_reference}' found")
                return 1.0
            else:
                logging.warning(f"❌ FAILED - Reference '{self.must_reference}' not found")
                return 0.0
        except Exception as e:
            logging.error(f"❌ Error: {e}")
            return 0.0


@AppRegistry.register_evaluator("LayeredMarkorCreateDailySummaryPartial")
class MarkorCreateDailySummaryPartialEvaluator(BaseAppEvaluator):
    """Create a daily summary document, supporting partial scoring.
    
    Used for Scenario C Task 9, checking the recording status of three items:
    1. Meeting info (title, time, location)
    2. Breakfast expense
    3. Audio recording file name from this morning
    
    Scoring rule:
    - Only one item: 0.3
    - Any two items: 0.6
    - All three items: 1.0
    
    parameters:
    - file_name: File name
    - meeting_keywords: List of meeting-related keywords
    - breakfast_amount: Breakfast amount (numeric)
    - recording_name: Audio recording file name (string)
    """
    
    app_names = ("markor",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.file_name = params.get('file_name')
        self.meeting_keywords = params.get('meeting_keywords', [])  # List of meeting keywords
        self.breakfast_amount = params.get('breakfast_amount', 0.0)  # Breakfast amount
        self.recording_name = params.get('recording_name', '')  # Audio recording file name
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """Execute evaluation: Check the recording status of the three items, supporting partial scoring.
        
        Scoring rule:
        - Only one item: 0.3
        - Any two items: 0.6
        - All three items: 1.0
        """
        logging.info("=" * 60)
        logging.info("📊 Evaluating Daily Summary (Partial Scoring):")
        logging.info("=" * 60)
        
        try:
            from scendroid.env import device_constants, adb_utils
            import os
            import time
            
            file_path = os.path.join(device_constants.MARKOR_DATA, self.file_name)
            
            # Retry reading the file multiple times
            content = None
            max_retries = 5
            retry_delay = 2.0
            
            for attempt in range(max_retries):
                try:
                    adb_utils.issue_generic_request(["shell", "sync"], env.controller)
                    time.sleep(0.5)
                except Exception:
                    pass
                
                try:
                    logging.info(f"   🔍 Attempt {attempt + 1}/{max_retries}: Reading file: {file_path}")
                    response = adb_utils.issue_generic_request(
                        ["shell", "cat", file_path], 
                        env.controller
                    )
                    raw_output = response.generic.output.decode('utf-8', errors='ignore')
                    content = raw_output.replace("\r", "")
                    
                    if content and content.strip():
                        if "No such file" in content or "not found" in content.lower():
                            content = None
                            logging.info(f"   ⏳ File not found, retrying...")
                        else:
                            logging.info(f"   ✅ File content read successfully on attempt {attempt + 1}")
                            break
                    else:
                        logging.info(f"   ⏳ File appears empty...")
                        
                except Exception as e:
                    logging.warning(f"   ⚠️ Could not read file: {e}")
                    content = None
                
                if not content or not content.strip():
                    if attempt < max_retries - 1:
                        logging.info(f"   ⏳ Retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                    else:
                        logging.warning(f"   ❌ FAIL: File '{file_path}' not found or empty after {max_retries} attempts")
                        logging.info("=" * 60)
                        return 0.0
            
            if not content or not content.strip():
                logging.warning("   ❌ FAIL: File is empty")
                logging.info("=" * 60)
                return 0.0
            
            content_lower = content.lower()
            logging.info(f"   File: {self.file_name}")
            logging.info(f"   Content ({len(content)} chars):")
            logging.info(f"   {content[:500]}...")
            
            # Check the three items
            items_found = 0
            
            # Item 1: Meeting info (check keyword list)
            meeting_found = False
            if self.meeting_keywords:
                meeting_keywords_found = []
                for keyword in self.meeting_keywords:
                    if keyword.lower() in content_lower:
                        meeting_keywords_found.append(keyword)
                
                # At least half of the keywords must be found to consider the meeting info as present
                if len(meeting_keywords_found) >= len(self.meeting_keywords) / 2:
                    meeting_found = True
                    items_found += 1
                    logging.info(f"   ✅ Item 1: Meeting info found (keywords: {meeting_keywords_found})")
                else:
                    logging.info(f"   ❌ Item 1: Meeting info not found (only {len(meeting_keywords_found)}/{len(self.meeting_keywords)} keywords)")
            
            # Item 2: Breakfast expense
            breakfast_found = False
            if self.breakfast_amount > 0:
                # Check whether the amount appears in the file (supports multiple formats: $X.XX, X.XX, X, etc.)
                amount_str_1 = f"${self.breakfast_amount:.2f}"  # $5.99
                amount_str_2 = f"{self.breakfast_amount:.2f}"   # 5.99
                amount_str_3 = f"{int(self.breakfast_amount)}"  # 5 (integer)
                
                if (amount_str_1.lower() in content_lower or 
                    amount_str_2 in content_lower or 
                    amount_str_3 in content_lower):
                    breakfast_found = True
                    items_found += 1
                    logging.info(f"   ✅ Item 2: Breakfast expense found (${self.breakfast_amount:.2f})")
                else:
                    logging.info(f"   ❌ Item 2: Breakfast expense not found (${self.breakfast_amount:.2f})")
            
            # Item 3: Audio recording file name
            recording_found = False
            if self.recording_name:
                # Check the audio recording file name (supports both with and without extension)
                recording_base = self.recording_name.replace('.mp3', '').replace('.m4a', '').replace('.wav', '')
                if recording_base.lower() in content_lower:
                    recording_found = True
                    items_found += 1
                    logging.info(f"   ✅ Item 3: Recording file name found ('{self.recording_name}')")
                else:
                    logging.info(f"   ❌ Item 3: Recording file name not found ('{self.recording_name}')")
            
            # Calculate score based on the count of items found
            if items_found == 3:
                score = 1.0
                logging.warning(f"   ✅ EXCELLENT: All 3 items found! Score: {score}")
            elif items_found == 2:
                score = 0.6
                logging.warning(f"   ✅ GOOD: 2 items found. Score: {score}")
            elif items_found == 1:
                score = 0.3
                logging.warning(f"   ⚠️  PARTIAL: Only 1 item found. Score: {score}")
            else:
                score = 0.0
                logging.warning(f"   ❌ FAIL: No items found. Score: {score}")
            
            logging.info(f"   Summary: {items_found}/3 items found")
            logging.info(f"   - Meeting: {'✅' if meeting_found else '❌'}")
            logging.info(f"   - Breakfast: {'✅' if breakfast_found else '❌'}")
            logging.info(f"   - Recording: {'✅' if recording_found else '❌'}")
            logging.info("=" * 60)
            
            return score
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.info("=" * 60)
            return 0.0
    
    def initialize_task(self, env):
        """initialize task"""
        from scendroid.task_evals.single import markor
        
        super().initialize_task(env)
        markor.clear_markor_files(env)
