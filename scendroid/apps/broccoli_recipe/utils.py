"""
Utility functions for Broccoli Recipe app.
"""
import logging
from typing import Optional


def get_agent_answer(env) -> str:
    """
    Get the agent's answer from the environment's interaction_cache
    
    Args:
        env: ScenDroid environment
        
    Returns:
        The agent's answer string; return an empty string if none exists
    """
    agent_answer = ""
    
    if hasattr(env, 'interaction_cache'):
        # handledictandstringtype
        if isinstance(env.interaction_cache, dict):
            agent_answer = env.interaction_cache.get('agent_response', '')
            if not agent_answer:
                agent_answer = env.interaction_cache.get('user_response', '')
        elif isinstance(env.interaction_cache, str):
            agent_answer = env.interaction_cache
        else:
            logging.warning(f"Unexpected interaction_cache type: {type(env.interaction_cache)}")
    
    return agent_answer.strip() if agent_answer else ""


def check_keywords_in_text(text: str, required_keywords: list, min_required: int = None) -> tuple:
    """
    Check whether the text contains the required keywords
    
    Args:
        text: The text to check
        required_keywords: A list of required keywords
        min_required: The minimum number of keywords that must be found (None means all)
        
    Returns:
        (found_keywords, missing_keywords, score)
        - found_keywords: A list of found keywords
        - missing_keywords: A list of missing keywords  
        - score: The score (1.0 or 0.0)
    """
    if min_required is None:
        min_required = len(required_keywords)
    
    text_lower = text.lower()
    keywords_found = []
    keywords_missing = []
    
    for keyword in required_keywords:
        keyword_lower = keyword.lower()
        
        # Support OR mode (e.g., "recipe|formula|method")
        if '|' in keyword_lower:
            keyword_variants = [k.strip() for k in keyword_lower.split('|')]
            if any(k in text_lower for k in keyword_variants):
                keywords_found.append(keyword)
            else:
                keywords_missing.append(keyword)
        else:
            # Single keyword match
            if keyword_lower in text_lower:
                keywords_found.append(keyword)
            else:
                keywords_missing.append(keyword)
    
    # Calculate the score
    if len(keywords_found) >= min_required:
        score = 1.0
    else:
        score = 0.0
    
    return keywords_found, keywords_missing, score


def check_recipe_info_in_answer(
    agent_answer: str,
    recipe_keywords: list = None,
    ingredient_keywords: list = None,
    min_recipe_keywords: int = 1,
    min_ingredient_keywords: int = 2
) -> tuple:
    """
    Check whether the answer contains recipe name and ingredient information
    
    Args:
        agent_answer: The agent's answer
        recipe_keywords: Keywords related to the recipe name
        ingredient_keywords: Keywords related to ingredients
        min_recipe_keywords: The minimum number of recipe-related keywords required
        min_ingredient_keywords: The minimum number of ingredient-related keywords required
        
    Returns:
        (has_recipe, has_ingredients, score)
        - has_recipe: Whether the recipe name is included
        - has_ingredients: Whether sufficient ingredients are included
        - score: 0.0-1.0
    """
    score = 0.0
    has_recipe = False
    has_ingredients = False
    
    # checkrecipename(50%)
    if recipe_keywords:
        found_recipe, _, _ = check_keywords_in_text(
            agent_answer, recipe_keywords, min_recipe_keywords
        )
        if len(found_recipe) >= min_recipe_keywords:
            has_recipe = True
            score += 0.5
            logging.info(f"   ✅ Recipe name found: {found_recipe}")
        else:
            logging.warning(f"   ❌ Recipe name not found (expected: {recipe_keywords})")
    
    # Check ingredients (50%)
    if ingredient_keywords:
        found_ingredients, missing_ingredients, _ = check_keywords_in_text(
            agent_answer, ingredient_keywords, min_ingredient_keywords
        )
        if len(found_ingredients) >= min_ingredient_keywords:
            has_ingredients = True
            score += 0.5
            logging.info(f"   ✅ Ingredients found: {found_ingredients}")
        else:
            logging.warning(f"   ⚠️  Ingredients partial: found {len(found_ingredients)}/{min_ingredient_keywords}")
            logging.warning(f"   Found: {found_ingredients}, Missing: {missing_ingredients}")
    
    return has_recipe, has_ingredients, score

