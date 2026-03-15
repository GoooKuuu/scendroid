"""
SMS App Module

SMS app-related evaluators (3):
1. LayeredSmsSendMessage - Send an SMS message to a contact.
2. LayeredSmsReplyMostRecent - Reply to the most recent SMS message.
3. LayeredSmsDeleteMessagesFromSender - Delete all messages from a specific sender.

These evaluators are based on ScenDroid's sms_validators.SimpleSMSSendSms.
"""

from scendroid.apps.registry import AppRegistry

# auto-load evaluators
from . import evaluators

__all__ = ['evaluators']

