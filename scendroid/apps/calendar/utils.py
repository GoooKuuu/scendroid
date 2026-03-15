"""
Calendar App Utility Functions

Provides helper functions related to the Simple Calendar Pro app for initialization and evaluation.  
These functions primarily wrap ScenDroid's native calendar_utils and datetime_utils.  
"""

from absl import logging


def get_device_time_ms(env) -> int:
    """
    Get the current device time (in milliseconds)  
    
    Args:
        env: ScenDroid environment
        
    Returns:
        Current device time (in milliseconds)  
    """
    from scendroid.env import adb_utils
    
    adb_output = adb_utils.issue_generic_request(
        ["shell", "date", "+%s"], env.controller
    )
    return int(adb_output.generic.output.strip()) * 1000


def get_agent_answer(env) -> str:
    """
    Retrieve the agent's answer from the environment's interaction_cache  
    
    Args:
        env: ScenDroid environment
        
    Returns:
        The agent's answer string; returns an empty string if none exists  
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
            # Attempt to convert to string  
            agent_answer = str(env.interaction_cache)
    
    return agent_answer


def check_keywords_in_text(text: str, required_keywords: list, min_required: int = None) -> tuple:
    """
    Check whether the text contains the required keywords  
    
    Args:
        text: Text to check  
        required_keywords: List of required keywords  
        min_required: Minimum number of keywords that must be found (None means all)  
        
    Returns:
        (found_keywords, missing_keywords, score)
        - found_keywords: List of found keywords  
        - missing_keywords: List of missing keywords  
        - score: Score (1.0 or 0.0)  
    """
    if min_required is None:
        min_required = len(required_keywords)
    
    text_lower = text.lower()
    keywords_found = []
    keywords_missing = []
    
    for keyword in required_keywords:
        keyword_lower = keyword.lower()
        
        # Support OR mode (e.g., "out of office|business trip|disable notification")
        if '|' in keyword_lower:
            keyword_variants = [k.strip() for k in keyword_lower.split('|')]
            if any(k in text_lower for k in keyword_variants):
                keywords_found.append(keyword)
            else:
                keywords_missing.append(keyword)
        else:
            if keyword_lower in text_lower:
                keywords_found.append(keyword)
            else:
                keywords_missing.append(keyword)
    
    score = 1.0 if len(keywords_found) >= min_required else 0.0
    
    return keywords_found, keywords_missing, score

