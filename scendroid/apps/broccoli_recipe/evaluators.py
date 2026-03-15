"""
Evaluators for Broccoli Recipe app tasks.
"""
import logging
from scendroid.apps.base import BaseAppEvaluator
from scendroid.apps.registry import AppRegistry


@AppRegistry.register_evaluator("LayeredBroccoliRecipeSearchQA")
class BroccoliRecipeSearchQAEvaluator(BaseAppEvaluator):
    """
    evaluation recipe search QA task (information retrieval) - Enhanced version
    
    supported scenarios:
    - Scenario C Task 2: "Open Broccoli Recipe and find a quick breakfast recipe 
                          that uses eggs AND takes 15 minutes or less to prepare."
    
    initialization:
    - No initialization required (query task)
    
    evaluation content (Enhanced version): 
    - Check whether the agent's answer contains the recipe name
    - Check whether the agent's answer contains key ingredients
    - 🆕 Check whether the agent's answer contains cooking time
    - 🆕 Check whether cooking time is ≤ max_prep_time_minutes
    
    parameters:
    - query_keywords: List of query keywords
    - recipe_keywords: Recipe name keywords
    - ingredient_keywords: Ingredient keywords
    - min_ingredient_keywords: Minimum required count of ingredient keywords
    - max_prep_time_minutes: 🆕 Maximum cooking time (minutes)
    - must_contain_prep_time: 🆕 Whether cooking time must be included
    - correct_recipe_title: 🆕 Correct answer's recipe title (for exact match)
    """
    
    # ScenDroid standard attributes
    app_names = ("broccoli_recipe",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Query parameter
        self.query_keywords = params.get('query_keywords', [])
        
        # evaluationparameter
        self.recipe_keywords = params.get('recipe_keywords', [])
        self.ingredient_keywords = params.get('ingredient_keywords', [])
        self.min_recipe_keywords = params.get('min_recipe_keywords', 1)
        self.min_ingredient_keywords = params.get('min_ingredient_keywords', 2)
        
        # 🆕 Cooking time constraint
        self.max_prep_time_minutes = params.get('max_prep_time_minutes', None)
        self.must_contain_prep_time = params.get('must_contain_prep_time', False)
        
        # 🆕 Correct answer (optional, for exact match)
        self.correct_recipe_title = params.get('correct_recipe_title', None)
        
        # set complexity
        self.complexity = 2.0  # Complexity increases after adding cooking time constraint
    
    def evaluate(self, env) -> float:
        """
        execute evaluation: check agent's answer (Enhanced version)
        
        Scoring criteria: 
        1. Must contain the recipe name (including the keyword "eggs")
        2. Must contain key ingredients
        3. If a time constraint is set, cooking time must be included and must be ≤ max_prep_time_minutes
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        from .utils import get_agent_answer, check_recipe_info_in_answer
        import re
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating Broccoli Recipe QA Answer (Enhanced):")
        logging.warning("=" * 60)
        
        try:
            # get agent's answer
            agent_answer = get_agent_answer(env)
            
            if not agent_answer:
                logging.error("   ❌ No answer found in env.interaction_cache")
                return 0.0
            
            logging.warning(f"   Agent's answer: {agent_answer[:300]}...")
            logging.warning(f"   Expected recipe keywords: {self.recipe_keywords}")
            logging.warning(f"   Expected ingredient keywords: {self.ingredient_keywords}")
            if self.max_prep_time_minutes:
                logging.warning(f"   Max prep time: {self.max_prep_time_minutes} minutes")
            if self.correct_recipe_title:
                logging.warning(f"   Correct recipe: {self.correct_recipe_title}")
            
            answer_lower = agent_answer.lower()
            
            # 1. checkrecipename
            has_recipe, has_ingredients, _ = check_recipe_info_in_answer(
                agent_answer=agent_answer,
                recipe_keywords=self.recipe_keywords,
                ingredient_keywords=self.ingredient_keywords,
                min_recipe_keywords=self.min_recipe_keywords,
                min_ingredient_keywords=self.min_ingredient_keywords
            )
            
            # 2. 🆕 Check correct recipe title (if specified)
            has_correct_recipe = True
            if self.correct_recipe_title:
                correct_title_lower = self.correct_recipe_title.lower()
                # Check whether title keywords appear in the answer
                title_words = [w for w in correct_title_lower.split() if len(w) > 2]
                title_matches = sum(1 for w in title_words if w in answer_lower)
                has_correct_recipe = title_matches >= len(title_words) * 0.5  # At least 50% word match
                if has_correct_recipe:
                    logging.warning(f"   ✅ Correct recipe title found: {self.correct_recipe_title}")
                else:
                    logging.warning(f"   ⚠️ Correct recipe title not found (matched {title_matches}/{len(title_words)} words)")
            
            # 3. 🆕 checkcooking time
            has_valid_prep_time = True
            found_prep_time = None
            
            if self.must_contain_prep_time or self.max_prep_time_minutes:
                # findcooking time
                prep_time_patterns = [
                    r'(\d+)\s*minutes?',
                    r'(\d+)\s*mins?',
                    r'prep(?:aration)?\s*(?:time)?[:\s]+(\d+)',
                    r'takes?\s*(\d+)\s*min',
                    r'(\d+)\s*minute',
                ]
                
                for pattern in prep_time_patterns:
                    match = re.search(pattern, answer_lower)
                    if match:
                        found_prep_time = int(match.group(1))
                        break
                
                if found_prep_time is not None:
                    logging.warning(f"   Found prep time: {found_prep_time} minutes")
                    
                    # Check whether it falls within the allowed range
                    if self.max_prep_time_minutes and found_prep_time > self.max_prep_time_minutes:
                        logging.warning(f"   ❌ Prep time {found_prep_time}min > max {self.max_prep_time_minutes}min")
                        has_valid_prep_time = False
                    else:
                        logging.warning(f"   ✅ Prep time {found_prep_time}min ≤ {self.max_prep_time_minutes}min")
                else:
                    if self.must_contain_prep_time:
                        logging.warning("   ❌ No prep time found in answer")
                        has_valid_prep_time = False
                    else:
                        logging.warning("   ⚠️ No prep time found (not required)")
            
            # outputevaluation result
            logging.warning("-" * 60)
            logging.warning("📊 Evaluation Results:")
            logging.warning(f"   Recipe name: {'✅ Found' if has_recipe else '❌ Missing'}")
            logging.warning(f"   Key ingredients: {'✅ Found' if has_ingredients else '❌ Missing'}")
            if self.correct_recipe_title:
                logging.warning(f"   Correct recipe: {'✅ Matched' if has_correct_recipe else '❌ Not matched'}")
            if self.must_contain_prep_time or self.max_prep_time_minutes:
                logging.warning(f"   Valid prep time: {'✅ Yes' if has_valid_prep_time else '❌ No'}")
            
            # Binary rating: All conditions must be satisfied
            all_pass = has_recipe and has_ingredients and has_correct_recipe and has_valid_prep_time
            
            if all_pass:
                logging.warning("   ✅ SUCCESS: Complete answer with all required information")
                logging.warning("=" * 60)
                return 1.0
            else:
                logging.warning("   ❌ FAIL: Missing or invalid information")
                logging.warning("=" * 60)
                return 0.0
        
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """
        initialize task: No special initialization required (query task)
        """
        super().initialize_task(env)
        logging.info("=" * 60)
        logging.info("🔧 Initializing Broccoli Recipe QA Task (Enhanced):")
        logging.info(f"   Query keywords: {self.query_keywords}")
        if self.max_prep_time_minutes:
            logging.info(f"   Max prep time: {self.max_prep_time_minutes} minutes")
        if self.correct_recipe_title:
            logging.info(f"   Correct recipe: {self.correct_recipe_title}")
        logging.info("=" * 60)
    
    def tear_down(self, env):
        """
        cleanup environment: No special cleanup required
        """
        super().tear_down(env)
        logging.info("✅ Broccoli Recipe QA task cleanup complete")


@AppRegistry.register_evaluator("LayeredBroccoliRecipeSearch")
class BroccoliRecipeSearchEvaluator(BaseAppEvaluator):
    """
    evaluation recipe search task (for 7-day scenario)
    
    supported scenarios:
    - W2-06: "Find me a simple light dinner recipe in Broccoli app"
    - W4-07: "Find a simple light dinner recipe for tomorrow"
    - W6-02: "Find a batch-cooking friendly light recipe"
    
    evaluation content:
    - Check whether the agent found a recipe matching requirements in Broccoli
    - Check whether the answer contains the recipe name
    """
    
    app_names = ("broccoli_recipe",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Diet type: light, vegetarian, etc.
        self.diet_type = params.get('diet_type', 'light')
        
        # Forbidden ingredients
        self.forbidden_ingredients = params.get('forbidden_ingredients', [])
        
        # Expected recipe keywords (for verifying the answer)
        self.expected_recipe_keywords = params.get('expected_recipe_keywords', [])
        
        # Keywords expected to appear in the answer
        self.answer_must_contain = params.get('answer_must_contain', [])
        
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """
        execute evaluation: check whether the agent found a suitable recipe
        
        Returns:
            float: 1.0 indicates recipe found, 0.0 indicates not found
        """
        logging.info("=" * 60)
        logging.info("📊 Evaluating Broccoli Recipe Search:")
        logging.info("=" * 60)
        logging.info(f"   Diet type: {self.diet_type}")
        logging.info(f"   Forbidden: {self.forbidden_ingredients}")
        
        try:
            # get agent's answer
            agent_answer = ""
            if hasattr(env, 'interaction_cache') and env.interaction_cache:
                agent_answer = str(env.interaction_cache)
            
            if not agent_answer:
                logging.error("   ❌ No answer found in env.interaction_cache")
                return 0.0
            
            logging.info(f"   Agent's answer: {agent_answer}")
            
            answer_lower = agent_answer.lower()
            
            # Check whether the recipe name was mentioned
            recipe_indicators = ['recipe', 'dish', 'meal', 'salad', 'soup', 'stir', 'steam', 
                                'grilled', 'baked', 'roasted', 'chicken', 'fish', 'vegetable',
                                'healthy', 'light', 'simple', 'quick']
            has_recipe = any(ind in answer_lower for ind in recipe_indicators)
            
            # Check whether prohibited ingredients are included (if prohibited ingredients are mentioned, deduct points)
            forbidden_found = [ing for ing in self.forbidden_ingredients if ing.lower() in answer_lower]
            if forbidden_found:
                logging.warning(f"   ⚠️ Found forbidden ingredients in answer: {forbidden_found}")
                # Do not fail directly, but record a warning
            
            # Check required keywords
            if self.answer_must_contain:
                keywords_found = sum(1 for kw in self.answer_must_contain if kw.lower() in answer_lower)
                if keywords_found == 0:
                    logging.warning(f"   ❌ Missing expected keywords: {self.answer_must_contain}")
                    return 0.0
            
            # Check expected recipe keywords
            if self.expected_recipe_keywords:
                recipe_found = any(kw.lower() in answer_lower for kw in self.expected_recipe_keywords)
                if recipe_found:
                    logging.info("   ✅ Found expected recipe in answer")
                    return 1.0
                else:
                    logging.warning(f"   ⚠️ Expected recipes not found: {self.expected_recipe_keywords}")
                    # If other recipe indicator terms are present, it is also considered passed
                    if has_recipe:
                        logging.info("   ✅ Found some recipe information")
                        return 1.0
                    return 0.0
            
            if has_recipe:
                logging.info("   ✅ SUCCESS: Recipe found")
                return 1.0
            else:
                logging.warning("   ❌ FAIL: No recipe found in answer")
                return 0.0
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """initialize task: handled by scenario evaluator in scenario mode"""
        super().initialize_task(env)
        logging.info("=" * 60)
        logging.info("🔧 Initializing Broccoli Recipe Search:")
        logging.info(f"   Diet type: {self.diet_type}")
        logging.info(f"   Forbidden ingredients: {self.forbidden_ingredients}")
        logging.info("=" * 60)



# ============================================================================
# ❌ DUPLICATE REGISTRATION - COMMENTED OUT
# ============================================================================
# The correct evaluator is registered at line 207
# This duplicate was causing: WARNING:absl:⚠️  Evaluator 'LayeredBroccoliRecipeSearch' already registered, overwriting

# @AppRegistry.register_evaluator("LayeredBroccoliRecipeSearch")
# class BroccoliRecipeSearchEvaluatorDuplicate(BaseAppEvaluator):
#     """searchrecipe (with dietary constraints)"""
#     
#     app_names = ("broccoli recipe",)
#     
#     def __init__(self, params: dict):
#         super().__init__(params)
#         self.query_keywords = params.get('query_keywords', [])
#         self.constraint_diet = params.get('constraint_diet', '')
#         self.constraint_forbidden = params.get('constraint_forbidden', [])
#         self.max_prep_time = params.get('max_prep_time', 30)
#         self.complexity = 2.0
#     
#     def evaluate(self, env, agent_answer: str = "") -> float:
#         """Check whether the answer satisfies the constraints"""
#         if not agent_answer:
#             return 0.0
#         answer_lower = agent_answer.lower()
#         # Check prohibited terms
#         for forbidden in self.constraint_forbidden:
#             if forbidden in answer_lower:
#                 logging.warning(f"❌ FAILED - Answer contains forbidden: {forbidden}")
#                 return 0.0
#         logging.warning(f"✅ PASSED - Recipe matches diet constraints")
#         return 1.0
