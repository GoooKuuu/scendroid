"""
SMS App Utility Functions

Provides helper functions related to the Simple SMS Messenger app for initialization and evaluation. 
"""

from absl import logging


def get_received_messages(controller):
    """
    Retrieves all SMS messages received on the device.
    
    Args:
        controller: ADB controller
        
    Returns:
        list: messagestringlist
    """
    from scendroid.task_evals.single import sms_validators
    
    return sms_validators.SimpleSMSSendSms._get_received_messages(controller)


def parse_message(msg_str: str) -> dict:
    """
    Parses an SMS string.
    
    Args:
        msg_str: The SMS string.
        
    Returns:
        dict: A dictionary containing fields such as address and body.
    """
    from scendroid.task_evals.single import sms_validators
    
    return sms_validators.parse_message(msg_str)


def clear_sms_and_threads(controller):
    """
    Clears all SMS messages and conversation threads.
    
    Args:
        controller: ADB controller
    """
    from scendroid.task_evals.single import sms_validators
    
    sms_validators.clear_sms_and_threads(controller)


def generate_random_message():
    """
    Generates random SMS content.
    
    Returns:
        str: The random SMS content.
    """
    import random
    from scendroid.task_evals.single import sms_validators
    
    return random.choice(sms_validators.SimpleSMSSendSms.messages)


def _clean_phone_number(phone_number: str) -> str:
    """
    Cleans up a phone number (removes all non-digit characters).
    
    This is an internal helper function used to normalize phone numbers for comparison. 
    
    Args:
        phone_number: The original phone number (which may contain spaces, hyphens, etc.).
        
    Returns:
        str: A phone number containing only digits.
        
    Example:
        >>> _clean_phone_number("555-0101")
        "5550101"
        >>> _clean_phone_number("(555) 0101")
        "5550101"
    """
    from scendroid.utils import contacts_utils
    
    return contacts_utils.clean_phone_number(phone_number)

