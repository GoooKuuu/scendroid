"""
Scenario Utility Functions

Provides common helper functions for the Scenario scenario.
"""

from datetime import datetime, timedelta
from absl import logging


def parse_time(time_str: str) -> tuple:
    """
    Parse a time string.
    
    Args:
        time_str: Time string in format "HH:MM".
        
    Returns:
        tuple: (hour, minute)
    """
    try:
        hour, minute = map(int, time_str.split(':'))
        return hour, minute
    except Exception as e:
        logging.error(f"Failed to parse time '{time_str}': {e}")
        return 0, 0


def combine_datetime(base_date: str, time_str: str) -> datetime:
    """
    Combine date and time.
    
    Args:
        base_date: Base date in format "YYYY-MM-DD".
        time_str: Time string in format "HH:MM".
        
    Returns:
        datetime: Combined date-time object.
    """
    try:
        # Parse date.
        date = datetime.strptime(base_date, "%Y-%m-%d")
        
        # Parse time.
        hour, minute = parse_time(time_str)
        
        # Combine.
        return date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
    except Exception as e:
        logging.error(f"Failed to combine datetime '{base_date}' + '{time_str}': {e}")
        return datetime.now()


def set_device_time(env, base_date: str, time_str: str):
    """
    Set up device time.
    
    Args:
        env: ScenDroid environment
        base_date: Base date in format "YYYY-MM-DD" or None (use default date).
        time_str: Time string in format "HH:MM".
    """
    try:
        from scendroid.env import adb_utils
        
        # If no base_date is provided, use the default date (refer to the old architecture).
        if not base_date:
            base_date = "2025-12-26"  # Default date: Friday, December 26, 2025.
            logging.info(f"   ℹ️  No base_date specified, using default: {base_date}")
        
        # Combine date and time (do NOT use timestamp()!).
        target_dt = combine_datetime(base_date, time_str)
        
        logging.info(f"⏰ Setting device time to: {target_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Set up root permission (required).
        adb_utils.set_root_if_needed(env.controller)
        
        # Format as ADB date command format: MMDDHHMMyy.SS.
        # Reference old architecture: scenario_env_setup.py line 88.
        time_str_adb = target_dt.strftime('%m%d%H%M%y.%S')
        
        adb_utils.issue_generic_request(
            ['shell', 'date', time_str_adb],
            env.controller
        )
        
        import time
        time.sleep(1.0)  # e.g., wait for time setup to take effect.
        
        logging.info(f"   ✅ Device time set successfully")
        
    except Exception as e:
        logging.warning(f"   ⚠️  Failed to set device time: {e}")
        import traceback
        logging.warning(traceback.format_exc())
        logging.warning(f"   Continuing without time adjustment...")


def calculate_weighted_score(
    scores: list, 
    weights: list = None
) -> float:
    """
    Calculate weighted score.
    
    Args:
        scores: List of scores.
        weights: List of weights (if None, use uniform weights).
        
    Returns:
        float: Weighted average score (0.0 - 1.0).
    """
    if not scores:
        return 0.0
    
    if weights is None:
        weights = [1.0] * len(scores)
    
    if len(scores) != len(weights):
        logging.warning(
            f"Scores and weights length mismatch: {len(scores)} vs {len(weights)}"
        )
        return sum(scores) / len(scores)
    
    total_score = sum(s * w for s, w in zip(scores, weights))
    total_weight = sum(weights)
    
    return total_score / total_weight if total_weight > 0 else 0.0


def format_subtask_summary(subtask_id: int, name: str, score: float, max_score: float = 1.0) -> str:
    """
    Format subtask summary.
    
    Args:
        subtask_id: Subtask ID.
        name: Subtask name.
        score: Score achieved.
        max_score: Maximum possible score.
        
    Returns:
        str: Formatted summary.
    """
    percentage = (score / max_score * 100) if max_score > 0 else 0
    status = "✅" if score >= 0.99 * max_score else "❌"
    
    return f"{status} Subtask {subtask_id}: {name} - {score:.2f}/{max_score:.2f} ({percentage:.0f}%)"


def check_success_criteria(
    passed_count: int,
    total_count: int,
    min_subtasks_pass: int = None,
    all_subtasks_pass: bool = False
) -> bool:
    """
    Check success criteria.
    
    Args:
        passed_count: Number of passed subtasks.
        total_count: Total number of subtasks.
        min_subtasks_pass: Minimum number of subtasks required to pass.
        all_subtasks_pass: Whether all subtasks must pass.
        
    Returns:
        bool: Whether success criteria are satisfied.
    """
    if all_subtasks_pass:
        return passed_count == total_count
    
    if min_subtasks_pass is not None:
        return passed_count >= min_subtasks_pass
    
    # Default: All must pass.
    return passed_count == total_count

