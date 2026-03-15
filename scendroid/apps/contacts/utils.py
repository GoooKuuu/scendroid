"""
Contacts App Utility Functions

Provides helper functions related to the Contacts app for initialization and evaluation. 
"""

from absl import logging


def list_contacts(controller):
    """
    Lists all contacts on the device.
    
    Args:
        controller: ADB controller
        
    Returns:
        list[Contact]: contactlist
    """
    from scendroid.utils import contacts_utils
    
    return contacts_utils.list_contacts(controller)


def add_contact(name: str, number: str, controller):
    """
    Adds a contact.
    
    Args:
        name: Contact name.
        number: Phone number.
        controller: ADB controller
    """
    from scendroid.utils import contacts_utils
    
    contacts_utils.add_contact(name, number, controller)
    logging.info(f"Contact added: {name} ({number})")


def clear_contacts(controller):
    """
    Clears all contacts.
    
    Args:
        controller: ADB controller
    """
    from scendroid.utils import contacts_utils
    
    contacts_utils.clear_contacts(controller)
    logging.info("All contacts cleared")


def clean_phone_number(number: str) -> str:
    """
    Normalizes a phone number (removes spaces, hyphens, etc.).
    
    Args:
        number: Original phone number.
        
    Returns:
        str: Normalized phone number.
    """
    from scendroid.utils import contacts_utils
    
    return contacts_utils.clean_phone_number(number)


def has_contact(contacts, name: str, number: str) -> bool:
    """
    Checks whether a specified contact exists in the contact list.
    
    Args:
        contacts: contactlist
        name: Contact name.
        number: Phone number (will be normalized).
        
    Returns:
        bool: Whether the contact exists.
    """
    from scendroid.utils import contacts_utils
    
    target_contact = contacts_utils.Contact(
        name,
        clean_phone_number(number)
    )
    return target_contact in contacts

