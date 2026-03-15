"""
Contacts App Evaluators

Provides one evaluator related to the Contacts app:

1. LayeredContactsAddContact - Add a contact (including name, phone number, and label)

Note: All scendroid.env imports are performed inside functions to avoid circular dependencies during module loading.
"""

from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.base import BaseAppEvaluator


# ============================================================================
# 1. LayeredContactsAddContact - Add a contact
# ============================================================================

@AppRegistry.register_evaluator("LayeredContactsAddContact")
class ContactsAddContactEvaluator(BaseAppEvaluator):
    """
    Perform evaluation: add contact task
    
    supported scenarios:
    - L0: "Open the Contacts app and create a new contact named William Wang 
           with phone number +1 (415) 555-0138, labeled 'Work.'"
    - L1: "Save a new contact: William Wang, +1 (415) 555-0138 (Work)."
    - L2: "Add a new contact for me."
    - L3: "I met a new colleague—help me save their contact information."
    
    evaluation content:
    - Check whether the contact was successfully added
    - Verify that the name and phone number are correct
    
    Note: The phone_label parameter (Work/Home/Mobile) is used for instruction generation but is not checked during evaluation.
    """
    
    # ScenDroid standard attributes
    app_names = ("contacts",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # required parameters
        self.contact_name = params.get('name')
        self.contact_number = params.get('number')
        self.phone_label = params.get('phone_label', '')
        
        # set complexity
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether the contact was successfully added
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        try:
            # import on demand
            from scendroid.utils import contacts_utils
            from .utils import has_contact, clean_phone_number
            
            # Get all contacts
            contacts = contacts_utils.list_contacts(env.controller)
            
            logging.warning("📊 Contacts Evaluation:")
            logging.warning(f"   Looking for: {self.contact_name}")
            logging.warning(f"   Phone: {self.contact_number}")
            logging.warning(f"   Label: {self.phone_label}")
            logging.warning(f"   Found {len(contacts)} contact(s) in total")
            
            # Check whether the target contact exists
            contact_found = has_contact(contacts, self.contact_name, self.contact_number)
            
            if contact_found:
                logging.warning("✅ PASSED - Contact added successfully:")
                logging.warning(f"   Name: {self.contact_name}")
                logging.warning(f"   Number: {clean_phone_number(self.contact_number)}")
                return 1.0
            else:
                logging.warning("❌ FAILED - Contact not found")
                logging.warning("   Existing contacts:")
                for contact in contacts:
                    logging.warning(f"     - {contact.name}: {contact.number}")
                return 0.0
            
        except Exception as e:
            logging.error(f"❌ error occurred during evaluation: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize task: Clear all existing contacts
        """
        from scendroid.utils import contacts_utils
        
        super().initialize_task(env)
        contacts_utils.clear_contacts(env.controller)
        logging.info("Contacts cleared")
    
    def tear_down(self, env):
        """
        Cleanup: Remove the added contact
        """
        from scendroid.utils import contacts_utils
        
        super().tear_down(env)
        contacts_utils.clear_contacts(env.controller)
        logging.info("Contacts cleared after task")

