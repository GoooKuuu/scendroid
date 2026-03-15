"""
Contacts App Module

Contacts app-related evaluator (1):
1. LayeredContactsAddContact - Add a contact (including name, phone number, and label)

This evaluator is based on ScenDroid's contacts_validators.AddContact
"""

from scendroid.apps.registry import AppRegistry

# auto-load evaluators
from . import evaluators

__all__ = ['evaluators']

