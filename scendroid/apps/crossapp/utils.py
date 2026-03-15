"""
CrossApp Utility Functions

Provides helper functions commonly used for CrossApp tasks.
"""

from absl import logging


def get_device_time_ms(env) -> int:
    """
    Gets the device time (in milliseconds).
    
    Args:
        env: ScenDroid environment
        
    Returns:
        int: Device timestamp (in milliseconds).
    """
    from scendroid.env import adb_utils
    
    adb_output = adb_utils.issue_generic_request(
        ["shell", "date", "+%s"], env.controller
    )
    
    if adb_output and adb_output.generic and adb_output.generic.output:
        timestamp_str = adb_output.generic.output.decode().strip()
        timestamp_sec = int(timestamp_str)
        timestamp_ms = timestamp_sec * 1000
        return timestamp_ms
    else:
        raise ValueError("Failed to get device time")


def check_keywords_in_text(text: str, keywords: list, match_all: bool = True) -> bool:
    """
    Checks whether the text contains keywords.
    
    Args:
        text: Text to check.
        keywords: List of keywords.
        match_all: True = must match all keywords; False = match any keyword.
        
    Returns:
        bool: Whether a match occurred.
    """
    text_lower = text.lower()
    
    if match_all:
        return all(kw.lower() in text_lower for kw in keywords)
    else:
        return any(kw.lower() in text_lower for kw in keywords)


def calculate_weighted_score(scores: list, weights: list = None) -> float:
    """
    Computes the weighted score.
    
    Args:
        scores: List of scores.
        weights: List of weights (if None, uses uniform weighting).
        
    Returns:
        float: Weighted average score (0.0–1.0).
    """
    if not scores:
        return 0.0
    
    if weights is None:
        weights = [1.0] * len(scores)
    
    if len(scores) != len(weights):
        logging.warning(f"Scores and weights length mismatch: {len(scores)} vs {len(weights)}")
        return sum(scores) / len(scores)
    
    total_score = sum(s * w for s, w in zip(scores, weights))
    total_weight = sum(weights)
    
    return total_score / total_weight if total_weight > 0 else 0.0

