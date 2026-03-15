"""
SMS App Evaluators

Provides evaluators related to the Simple SMS Messenger app (5 in total):

1. LayeredSmsSendMessage - Send an SMS message to a contact
2. LayeredSmsReplyMostRecent - Reply to the most recent SMS message
3. LayeredSmsDeleteMessagesFromSender - Delete all messages from a specific sender
4. LayeredSMSBatchNotify - Send notification messages in batch to multiple contacts
5. LayeredSMSProgressSummary - Track SMS reply progress for meetings/events (QA task)

Note: All scendroid.env imports are performed inside functions to avoid circular dependencies during module loading
"""

import time
import random
from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.base import BaseAppEvaluator


# ============================================================================
# 1. LayeredSmsSendMessage - Send an SMS message to a contact
# ============================================================================

@AppRegistry.register_evaluator("LayeredSmsSendMessage")
class SmsSendMessageEvaluator(BaseAppEvaluator):
    """
    Evaluate the SMS sending task
    
    supported scenarios:
    - L0: "Open the Messages app and text Alex Zhang: 'I'm here.'"
    - L1: "Text Alex Zhang: 'I'm here.'"
    - L2: "Send a text saying 'I'm here.'"
    - L3: "I want to let someone know that I've arrived."
    
    evaluation content:
    - Check whether the SMS message was successfully sent to the specified contact
    - Check whether the message content is correct
    """
    
    # ScenDroid standard attributes
    app_names = ("simple sms messenger",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # required parameters
        self.contact_name = params.get('contact_name')
        self.number = params.get('number')
        self.message = params.get('message')
        
        # set complexity
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether the SMS message was successfully sent
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        try:
            # import on demand
            from scendroid.task_evals.common_validators import sms_validators
            
            # Use the evaluation logic of SimpleSMSSendSms
            # Create an instance to call get_sent_messages
            temp_validator = sms_validators.SimpleSMSSendSms({})
            sent_messages = temp_validator.get_sent_messages(env.controller)
            
            logging.warning("📊 SMS Send Evaluation:")
            logging.warning(f"   Target: {self.contact_name} ({self.number})")
            logging.warning(f"   Expected message: '{self.message}'")
            logging.warning(f"   Found {len(sent_messages)} sent message(s)")
            
            # Check whether there is a message sent to the target phone number
            for msg_str in sent_messages:
                try:
                    msg = sms_validators.parse_message(msg_str)
                    
                    # Normalize the phone number (remove spaces, hyphens, and plus signs)
                    sent_number = msg.get("address", "").replace("+", "").replace("-", "").replace(" ", "")
                    target_number = self.number.replace("+", "").replace("-", "").replace(" ", "")
                    
                    logging.warning(f"   Checking: sent='{sent_number}' vs target='{target_number}'")
                    
                    if sent_number == target_number:
                        # Check the message content (loose match: one side must contain the other)
                        sent_body = msg.get("body", "").lower().strip()
                        expected_body = self.message.lower().strip()
                        
                        logging.warning(f"   ✅ Number matched! Checking content:")
                        logging.warning(f"      Expected: '{expected_body}'")
                        logging.warning(f"      Sent: '{sent_body}'")
                        
                        if expected_body in sent_body or sent_body in expected_body or sent_body == expected_body:
                            logging.warning("✅ PASSED - Message sent successfully:")
                            logging.warning(f"   To: {msg.get('address')}")
                            logging.warning(f"   Body: {msg.get('body')}")
                            return 1.0
                        else:
                            logging.warning(f"   ❌ Content doesn't match")
                except Exception as e:
                    logging.warning(f"Failed to parse message: {e}")
                    continue
            
            logging.warning("❌ FAILED - No matching sent message found")
            return 0.0
            
        except Exception as e:
            logging.error(f"❌ error occurred during evaluation: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize task: Add a contact
        """
        from scendroid.env import adb_utils
        from scendroid.task_evals.single import contacts_utils, sms_validators
        
        super().initialize_task(env)
        
        # disablednotification
        adb_utils.disable_headsup_notifications(env.controller)
        
        # Clear existing SMS messages
        sms_validators.clear_sms_and_threads(env.controller)
        
        # Add a contact
        contacts_utils.add_contact(
            self.contact_name,
            self.number,
            env.controller
        )
        time.sleep(3.0)  # e.g., wait for contact addition to complete
        
        adb_utils.enable_headsup_notifications(env.controller)
        logging.info(f"Contact added: {self.contact_name} ({self.number})")
    
    def tear_down(self, env):
        """
        cleanup: deletecontactandSMSmessage
        """
        from scendroid.utils import contacts_utils
        from scendroid.task_evals.common_validators import sms_validators
        
        super().tear_down(env)
        
        try:
            contacts_utils.clear_contacts(env.controller)
            logging.info("Contacts cleared")
        except Exception as e:
            logging.warning(f"Failed to clear contacts: {e}")
        
        try:
            sms_validators.clear_sms_and_threads(env.controller)
            logging.info("SMS messages cleared")
        except Exception as e:
            logging.warning(f"Failed to clear SMS: {e}")


# ============================================================================
# 2. LayeredSmsReplyMostRecent - Reply to the most recent SMS message
# ============================================================================

@AppRegistry.register_evaluator("LayeredSmsReplyMostRecent")
class SmsReplyMostRecentEvaluator(BaseAppEvaluator):
    """
    Evaluate the task of replying to the most recent SMS message
    
    supported scenarios:
    - L0: "Open Simple SMS Messenger and reply to the most recent message with: 'Sounds good, see you then.'"
    - L1: "Reply to my latest text: 'Sounds good, see you then.'"
    - L2: "Respond to the last message I got."
    
    evaluation content:
    - Check whether a correct reply was sent to the sender of the most recent message
    """
    
    # ScenDroid standard attributes
    app_names = ("simple sms messenger",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # required parameters
        self.contact_name = params.get('contact_name', 'Recent Contact')
        self.number = params.get('number')
        self.message = params.get('message')
        
        # Internal state (set up during initialization)
        self._target_sender_number = None
        
        # set complexity
        self.complexity = 1.8
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: Check whether the most recent SMS message was correctly replied to
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        try:
            # import on demand
            from scendroid.task_evals.common_validators import sms_validators
            
            # Get the sent messages
            temp_validator = sms_validators.SimpleSMSSendSms({})
            sent_messages = temp_validator.get_sent_messages(env.controller)
            
            logging.warning("📊 SMS Reply Evaluation:")
            logging.warning(f"   Target number: {self._target_sender_number}")
            logging.warning(f"   Expected message: '{self.message}'")
            logging.warning(f"   Found {len(sent_messages)} sent message(s)")
            
            # Check whether there is a reply message sent to the target phone number
            for msg_str in sent_messages:
                try:
                    msg = sms_validators.parse_message(msg_str)
                    # Normalize the phone number
                    sent_number = msg.get("address", "").replace("-", "").replace(" ", "")
                    target_number = self._target_sender_number.replace("-", "").replace(" ", "")
                    
                    if sent_number == target_number:
                        # Check the message content
                        sent_body = msg.get("body", "").lower()
                        expected_body = self.message.lower()
                        
                        if expected_body in sent_body or sent_body in expected_body:
                            logging.warning("✅ PASSED - Reply sent successfully:")
                            logging.warning(f"   To: {msg.get('address')}")
                            logging.warning(f"   Body: {msg.get('body')}")
                            return 1.0
                except Exception as e:
                    logging.warning(f"Failed to parse message: {e}")
                    continue
            
            logging.warning("❌ FAILED - No matching reply found")
            return 0.0
            
        except Exception as e:
            logging.error(f"❌ error occurred during evaluation: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize task: Send multiple SMS messages, with the latest one coming from the target phone number
        """
        from scendroid.env import adb_utils
        from scendroid.task_evals.common_validators import sms_validators
        from scendroid.utils import user_data_generation
        
        super().initialize_task(env)
        
        # disablednotification
        adb_utils.disable_headsup_notifications(env.controller)
        
        # Clear existing SMS messages
        sms_validators.clear_sms_and_threads(env.controller)
        
        # Send 2–3 noise messages (from different phone numbers)
        num_noise_messages = random.randint(2, 3)
        logging.info(f"Sending {num_noise_messages} noise messages...")
        
        for i in range(num_noise_messages):
            noise_number = user_data_generation.generate_random_number()
            noise_message = self._generate_non_goal_message()
            adb_utils.text_emulator(
                env.controller,
                noise_number,
                noise_message,
            )
            logging.info(f"  Noise message {i+1}: from {noise_number}")
        
        # SMS messages may not arrive in the order they were sent, so pause briefly
        time.sleep(5)
        
        # Send the latest message (from the target contact)
        most_recent_message = self._generate_non_goal_message()
        logging.warning(f"📱 Most recent message: from {self.number}")
        logging.warning(f"   Content: '{most_recent_message}'")
        logging.warning(f"   Expected reply: '{self.message}'")
        
        adb_utils.text_emulator(
            env.controller,
            self.number,
            most_recent_message,
        )
        
        # Save the target phone number for evaluation
        self._target_sender_number = self.number
        
        # Pause to ensure the message is received before enabling notifications
        time.sleep(5)
        adb_utils.enable_headsup_notifications(env.controller)
        
        # Verify whether the latest message is correct
        received_messages = sms_validators.SimpleSMSSendSms._get_received_messages(env.controller)
        if received_messages:
            most_recent = sms_validators.parse_message(received_messages[0])
            if most_recent["address"] != self.number:
                logging.warning(
                    f"⚠️  Most recent message is from {most_recent['address']}, "
                    f"expected {self.number}"
                )
            else:
                logging.info(f"✅ Most recent message verified from {self.number}")
    
    def _generate_non_goal_message(self):
        """Generate a random message different from the target message"""
        from scendroid.task_evals.common_validators import sms_validators
        
        message = random.choice(sms_validators.SimpleSMSSendSms.messages)
        while message == self.message:
            message = random.choice(sms_validators.SimpleSMSSendSms.messages)
        return message


# ============================================================================
# 3. LayeredSmsDeleteMessagesFromSender - Delete all messages from a specific sender
# ============================================================================

@AppRegistry.register_evaluator("LayeredSmsDeleteMessagesFromSender")
class SmsDeleteMessagesFromSenderEvaluator(BaseAppEvaluator):
    """
    evaluation: delete all messages from a specific sender task
    
    supported scenarios:
    - L0: "Delete all messages from 'BankAlert'"
    - L1: "Clear BankAlert messages"
    
    evaluation content:
    - Check whether all messages from the target sender have been deleted
    - Messages from other senders should remain
    """
    
    # ScenDroid standard attributes
    app_names = ("simple sms messenger",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # required parameters
        self.sender_name = params.get('sender_name')
        self.sender_number = params.get('sender_number')
        self.num_target_messages = params.get('num_target_messages', 3)
        self.num_noise_messages = params.get('num_noise_messages', 2)
        
        # internal state (set up during initialization)
        self._target_sender_number = None
        self._noise_sender_numbers = []
        
        # set complexity
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """
        execute evaluation: check whether all messages from the target sender have been deleted and whether other messages have been retained
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        try:
            # import on demand
            from scendroid.task_evals.common_validators import sms_validators
            
            # get all currently received messages
            current_messages = sms_validators.SimpleSMSSendSms._get_received_messages(env.controller)
            
            # parse messages and categorize them by sender
            messages_from_target = []
            messages_from_others = []
            
            for msg_str in current_messages:
                try:
                    msg = sms_validators.parse_message(msg_str)
                    sender = msg.get("address", "").replace("-", "").replace(" ", "")
                    
                    # normalize the target phone number
                    target_normalized = self._target_sender_number.replace("-", "").replace(" ", "")
                    
                    if sender == target_normalized:
                        messages_from_target.append(msg)
                    else:
                        messages_from_others.append(msg)
                except Exception as e:
                    logging.warning(f"Failed to parse message: {msg_str}, error: {e}")
                    continue
            
            logging.warning("📊 Evaluation Results:")
            logging.warning(f"   Messages from target sender ({self._target_sender_number}): {len(messages_from_target)}")
            logging.warning(f"   Messages from other senders: {len(messages_from_others)}")
            
            # check 1: all messages from the target sender should be deleted
            if len(messages_from_target) > 0:
                logging.warning(f"   ❌ FAILED: {len(messages_from_target)} messages from target sender still exist")
                logging.warning(f"   Expected: 0, Found: {len(messages_from_target)}")
                for msg in messages_from_target:
                    logging.info(f"      Remaining: {msg.get('body', 'N/A')}")
                return 0.0
            
            # check 2: noise messages should still exist
            expected_noise = self.num_noise_messages
            if len(messages_from_others) < expected_noise:
                logging.warning(f"   ❌ FAILED: Some noise messages were deleted")
                logging.warning(f"   Expected: {expected_noise}, Found: {len(messages_from_others)}")
                return 0.0
            
            logging.warning("   ✅ PASSED: All target messages deleted, noise messages intact")
            return 1.0
            
        except Exception as e:
            logging.error(f"❌ error occurred during evaluation: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """
        initialize task: send messages from the target sender and other senders
        """
        from scendroid.env import adb_utils
        from scendroid.task_evals.common_validators import sms_validators
        from scendroid.utils import user_data_generation
        
        super().initialize_task(env)
        
        # disablednotification
        adb_utils.disable_headsup_notifications(env.controller)
        
        # clear existing SMS messages
        sms_validators.clear_sms_and_threads(env.controller)
        time.sleep(2)
        
        # target message template
        target_messages = [
            "Your account balance is $1,234.56",
            "Transaction alert: $50.00 spent at Store X",
            "Security notice: Login from new device",
            "Your payment of $100 is due tomorrow",
        ]
        
        logging.warning(f"📱 Sending {self.num_target_messages} messages from target sender:")
        logging.warning(f"   Sender: {self.sender_name} ({self.sender_number})")
        
        # send target messages (which should be deleted)
        for i in range(self.num_target_messages):
            message = target_messages[i % len(target_messages)]
            adb_utils.text_emulator(
                env.controller,
                self.sender_number,
                message,
            )
            logging.info(f"   ✉️  Message {i+1}: '{message}'")
            time.sleep(1)
        
        time.sleep(3)
        
        # send noise messages (which should be retained)
        logging.warning(f"📱 Sending {self.num_noise_messages} noise messages (should remain):")
        
        noise_senders = []
        for i in range(self.num_noise_messages):
            noise_number = user_data_generation.generate_random_number()
            noise_message = random.choice([
                "Hey, how are you?",
                "See you tomorrow!",
                "Thanks for the help!",
                "Can we meet this weekend?",
            ])
            adb_utils.text_emulator(
                env.controller,
                noise_number,
                noise_message,
            )
            noise_senders.append(noise_number)
            logging.info(f"   ✉️  From {noise_number}: '{noise_message}'")
            time.sleep(1)
        
        time.sleep(3)
        adb_utils.enable_headsup_notifications(env.controller)
        
        # save status for evaluation
        self._target_sender_number = self.sender_number
        self._noise_sender_numbers = noise_senders
        
        logging.warning("✅ Environment initialized:")
        logging.warning(f"   - {self.num_target_messages} messages from {self.sender_name} ({self.sender_number})")
        logging.warning(f"   - {self.num_noise_messages} messages from other senders (should remain)")
        logging.warning(f"   💡 TIP: Delete ONLY messages from {self.sender_name}, keep others!")
    
    def tear_down(self, env):
        """
        cleanup: delete all messages
        """
        from scendroid.task_evals.common_validators import sms_validators
        
        super().tear_down(env)
        
        try:
            sms_validators.clear_sms_and_threads(env.controller)
            logging.info("SMS messages cleared")
        except Exception as e:
            logging.warning(f"Failed to clear SMS: {e}")


# ============================================================================
# 4. LayeredSMSBatchNotify - batch send notification messages to multiple contacts
# ============================================================================

@AppRegistry.register_evaluator("LayeredSMSBatchNotify")
class SMSBatchNotifyEvaluator(BaseAppEvaluator):
    """
    evaluation: batch send notification message task
    
    Application scenarios:
    - Send reminders to multiple meeting attendees
    - Send notifications to team members
    - Mass-send invitations or important information
    
    evaluation content:
    - Check whether messages have been sent to all required recipients
    - Check whether message content includes the required time and location
    - Check whether messages have been sent to forbidden recipients (if specified)
    - Check whether the number of sent messages meets the minimum requirement
    """
    
    # ScenDroid standard attributes
    app_names = ("simple sms messenger",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # required parameters
        # required_recipients: list of recipients (names) to whom messages must be sent
        self.required_recipients = params.get('required_recipients', [])
        
        # message content requirements
        self.message_must_contain_time = params.get('message_must_contain_time')
        self.message_must_contain_location = params.get('message_must_contain_location', [])
        
        # optional parameter
        # forbidden_recipients: list of recipients (names) who should not receive messages
        self.forbidden_recipients = params.get('forbidden_recipients', [])
        
        # min_messages_sent: minimum number of messages to be sent
        self.min_messages_sent = params.get('min_messages_sent', len(self.required_recipients))
        
        # internal state (set up during initialization or passed in via params)
        self._contacts_map = params.get('contacts_map', {})  # name -> phone number mapping
        
        # set complexity
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """
        execute evaluation: check whether batch notification succeeded
        
        Returns:
            float: 1.0 indicates success, 0.0 indicates failure
        """
        try:
            # import on demand
            from scendroid.task_evals.common_validators import sms_validators
            from scendroid.apps.sms import utils as sms_utils
            from scendroid.env import adb_utils
            
            # get sent messages (query directly using ADB)
            response = adb_utils.issue_generic_request(
                "shell content query --uri content://sms/sent".split(), env.controller
            )
            sent_messages = sms_validators._decode_messages_from_response(response)
            
            logging.warning("=" * 60)
            logging.warning("📊 SMS Batch Notify Evaluation:")
            logging.warning("=" * 60)
            logging.warning(f"   Required recipients: {', '.join(self.required_recipients)}")
            if self.forbidden_recipients:
                logging.warning(f"   Forbidden recipients: {', '.join(self.forbidden_recipients)}")
            if self.message_must_contain_time:
                logging.warning(f"   Must contain time: {self.message_must_contain_time}")
            if self.message_must_contain_location:
                logging.warning(f"   Must contain location: {', '.join(self.message_must_contain_location)}")
            logging.warning(f"   Min messages to send: {self.min_messages_sent}")
            logging.warning(f"   Found {len(sent_messages)} sent message(s)")
            logging.warning("=" * 60)
            
            if len(sent_messages) == 0:
                logging.warning("❌ FAILED - No messages sent")
                return 0.0
            
            # parse all sent messages
            parsed_messages = []
            for msg_str in sent_messages:
                try:
                    msg = sms_validators.parse_message(msg_str)
                    parsed_messages.append(msg)
                except Exception as e:
                    logging.warning(f"Failed to parse message: {e}")
                    continue
            
            # count messages sent to each recipient
            messages_to_recipients = {}
            for msg in parsed_messages:
                address = msg.get("address", "")
                recipient_number = sms_utils._clean_phone_number(address)
                body = msg.get("body", "")
                
                # find the contact name corresponding to this phone number
                # refer to the old architecture: layered_tasks.py lines 5298–5301
                # Use partial matching (because phone number formats may differ)
                recipient_name = None
                for name, number in self._contacts_map.items():
                    clean_number = sms_utils._clean_phone_number(number)
                    # Use partial matching: address in number or number in address
                    if recipient_number in clean_number or clean_number in recipient_number:
                        recipient_name = name
                        break
                
                if recipient_name:
                    if recipient_name not in messages_to_recipients:
                        messages_to_recipients[recipient_name] = []
                    messages_to_recipients[recipient_name].append(body)
            
            logging.warning(f"📬 Messages sent to:")
            for name, messages in messages_to_recipients.items():
                logging.warning(f"   - {name}: {len(messages)} message(s)")
                for body in messages:
                    logging.warning(f"      '{body[:60]}...'")
            
            logging.warning("=" * 60)
            
            # Check 1: Whether all required recipients have received the message
            # Reference the legacy architecture: lines 5307–5309 in layered_tasks.py
            # Use partial matching (e.g., "John Smith" in "John Smith")
            missing_recipients = []
            recipients_found = set()
            
            for req in self.required_recipients:
                found = False
                for recipient_name in messages_to_recipients.keys():
                    # Use partial matching (case-insensitive)
                    if req.lower() in recipient_name.lower() or recipient_name.lower() in req.lower():
                        recipients_found.add(req)
                        found = True
                        break
                
                if not found:
                    missing_recipients.append(req)
            
            if missing_recipients:
                logging.warning("=" * 60)
                logging.warning(f"❌ FAILED - Missing recipients: {', '.join(missing_recipients)}")
                return 0.0
            
            # Check 2: Whether any messages were sent to prohibited recipients
            # Reference the legacy architecture: lines 5326–5329 in layered_tasks.py
            if self.forbidden_recipients:
                forbidden_sent = []
                for forbidden in self.forbidden_recipients:
                    for recipient_name in messages_to_recipients.keys():
                        # Use partial matching (case-insensitive)
                        if forbidden.lower() in recipient_name.lower() or recipient_name.lower() in forbidden.lower():
                            forbidden_sent.append(recipient_name)
                            break
                
                if forbidden_sent:
                    logging.warning("=" * 60)
                    logging.warning(f"❌ FAILED - Sent to forbidden recipients: {', '.join(forbidden_sent)}")
                    return 0.0
            
            # Checks 3 and 4: Whether the message content includes the required time and location
            # Reference the legacy architecture: lines 5312–5321 in layered_tasks.py
            messages_with_correct_content = 0
            
            for req in recipients_found:
                # Find the message for this recipient
                recipient_messages = []
                for recipient_name in messages_to_recipients.keys():
                    if req.lower() in recipient_name.lower() or recipient_name.lower() in req.lower():
                        recipient_messages = messages_to_recipients[recipient_name]
                        break
                
                # Check message content
                has_valid_message = False
                for body in recipient_messages:
                    body_lower = body.lower()
                    
                    # Check time
                    has_time = True
                    if self.message_must_contain_time:
                        has_time = self.message_must_contain_time.lower() in body_lower
                    
                    # Check location
                    has_location = True
                    if self.message_must_contain_location:
                        has_location = any(loc.lower() in body_lower for loc in self.message_must_contain_location)
                    
                    if has_time and has_location:
                        has_valid_message = True
                        break
                
                if has_valid_message:
                    messages_with_correct_content += 1
            
            # If message content requirements exist, check whether they are satisfied
            if self.message_must_contain_time or self.message_must_contain_location:
                if messages_with_correct_content < self.min_messages_sent:
                    logging.warning("=" * 60)
                    logging.warning(f"❌ FAILED - Only {messages_with_correct_content}/{self.min_messages_sent} messages contain required content")
                    if self.message_must_contain_time:
                        logging.warning(f"   Required time: {self.message_must_contain_time}")
                    if self.message_must_contain_location:
                        logging.warning(f"   Required location (any of): {', '.join(self.message_must_contain_location)}")
                    return 0.0
            
            # Check 5: Whether the number of sent messages meets the minimum requirement
            total_sent = len(messages_to_recipients)
            if total_sent < self.min_messages_sent:
                logging.warning("=" * 60)
                logging.warning(f"❌ FAILED - Not enough messages sent")
                logging.warning(f"   Expected: {self.min_messages_sent}, Found: {total_sent}")
                return 0.0
            
            logging.warning("=" * 60)
            logging.warning("✅ PASSED - Batch notification successful:")
            logging.warning(f"   ✅ All required recipients received messages")
            if self.forbidden_recipients:
                logging.warning(f"   ✅ No forbidden recipients received messages")
            if self.message_must_contain_time:
                logging.warning(f"   ✅ Messages contain time: {self.message_must_contain_time}")
            if self.message_must_contain_location:
                logging.warning(f"   ✅ Messages contain location info")
            logging.warning(f"   ✅ Total messages sent: {total_sent} (min: {self.min_messages_sent})")
            logging.warning("=" * 60)
            
            return 1.0
            
        except Exception as e:
            logging.error(f"❌ error occurred during evaluation: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """
        Initialize task: Add all contacts (required and prohibited)
        """
        from scendroid.env import adb_utils
        from scendroid.task_evals.single import contacts_utils, sms_validators
        
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info("🔧 Initializing SMS Batch Notify task:")
        logging.info("=" * 60)
        
        # disablednotification
        adb_utils.disable_headsup_notifications(env.controller)
        
        # Clear existing SMS messages and contacts
        sms_validators.clear_sms_and_threads(env.controller)
        contacts_utils.clear_contacts(env.controller)
        time.sleep(2)
        
        # Generate a phone number for each recipient and add the contact
        # Note: This assumes that required_recipients already contains full names
        # e.g.:["John Smith", "Bob Johnson", ...]
        
        logging.info(f"📱 Adding {len(self.required_recipients)} required recipient(s):")
        for recipient_name in self.required_recipients:
            # Generate a unique phone number
            # Use a simple format: 555-01XX
            idx = self.required_recipients.index(recipient_name)
            phone_number = f"555-{1000 + idx:04d}"
            
            contacts_utils.add_contact(
                recipient_name,
                phone_number,
                env.controller
            )
            
            self._contacts_map[recipient_name] = phone_number
            logging.info(f"   ✅ {recipient_name} ({phone_number})")
            time.sleep(0.5)
        
        # Add prohibited recipients (as distractors)
        if self.forbidden_recipients:
            logging.info(f"📱 Adding {len(self.forbidden_recipients)} forbidden recipient(s) (distractors):")
            for recipient_name in self.forbidden_recipients:
                idx = len(self.required_recipients) + self.forbidden_recipients.index(recipient_name)
                phone_number = f"555-{2000 + idx:04d}"
                
                contacts_utils.add_contact(
                    recipient_name,
                    phone_number,
                    env.controller
                )
                
                self._contacts_map[recipient_name] = phone_number
                logging.info(f"   ⚠️  {recipient_name} ({phone_number}) - should NOT receive message")
                time.sleep(0.5)
        
        time.sleep(3)
        adb_utils.enable_headsup_notifications(env.controller)
        
        logging.info("=" * 60)
        logging.info("✅ Environment initialized:")
        logging.info(f"   - {len(self.required_recipients)} required recipient(s) added")
        if self.forbidden_recipients:
            logging.info(f"   - {len(self.forbidden_recipients)} forbidden recipient(s) added (distractors)")
        logging.info(f"   💡 TIP: Send notification to ALL required recipients!")
        if self.message_must_contain_time:
            logging.info(f"   💡 TIP: Include time: {self.message_must_contain_time}")
        if self.message_must_contain_location:
            logging.info(f"   💡 TIP: Include location: {', '.join(self.message_must_contain_location)}")
        logging.info("=" * 60)
    
    def tear_down(self, env):
        """
        Cleanup: Delete all contacts and messages
        """
        from scendroid.utils import contacts_utils
        from scendroid.task_evals.common_validators import sms_validators
        
        super().tear_down(env)
        
        try:
            contacts_utils.clear_contacts(env.controller)
            logging.info("Contacts cleared")
        except Exception as e:
            logging.warning(f"Failed to clear contacts: {e}")
        
        try:
            sms_validators.clear_sms_and_threads(env.controller)
            logging.info("SMS messages cleared")
        except Exception as e:
            logging.warning(f"Failed to clear SMS: {e}")


# ============================================================================
# 5. LayeredSMSProgressSummary - Track SMS reply progress for meetings/events (QA task)
# ============================================================================

@AppRegistry.register_evaluator("LayeredSMSProgressSummary")
class SMSProgressSummaryEvaluator(BaseAppEvaluator):
    """
    Evaluate SMS reply progress summary for meetings/events (QA task)
    
    Used to track specific meeting attendees' reply status across days in a 7-day scenario.
    The agent must:
    1. Identify the target meeting (possibly via references: ).replace(u201d, yesterday's meeting", ).replace(u201d, Monday's weekly meeting", etc.)
    2. Review SMS replies from relevant contacts
    3. Summarize who has replied and who has not yet replied
    4. Exclude SMS messages related to other meetings (trap: meetings with similar names)
    
    This is a QA task requiring an agent answer (requires_answer=True).
    """
    
    app_names = ("simple sms messenger",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.target_meeting = params.get('target_meeting', '')
        self.expected_attendees = params.get('expected_attendees', [])
        self.min_reply_count = params.get('min_reply_count', 1)
        self.exclude_events = params.get('exclude_events', [])
        self.agent_answer = ""
        self.complexity = 3.0
    
    def evaluate(self, env) -> float:
        """Evaluate the agent's reply progress summary"""
        # ✅ Retrieve the agent's answer from env.interaction_cache (refer to calendar's get_agent_answer)
        from scendroid.apps.calendar.utils import get_agent_answer
        
        agent_answer = get_agent_answer(env)
        self.agent_answer = agent_answer.lower().strip()
        
        if not self.agent_answer:
            logging.warning("❌ FAILED - No answer provided")
            logging.warning("   Make sure the agent provided an answer using the answer action")
            return 0.0
        
        logging.warning("=" * 70)
        logging.warning("📊 SMS Progress Summary Evaluation:")
        logging.warning(f"   Target Meeting: {self.target_meeting}")
        logging.warning(f"   Agent Answer: {self.agent_answer}")
        logging.warning("=" * 70)
        
        score = 0.0
        max_score = 3.0
        
        # Check whether attendees are mentioned (supporting full name, first name, or last name)
        mentioned_attendees = []
        for name in self.expected_attendees:
            name_lower = name.lower()
            # Attempt full-name matching
            if name_lower in self.agent_answer:
                mentioned_attendees.append(name)
                continue
            # attemptmatchfirst nameorlast name
            name_parts = name_lower.split()
            if any(part in self.agent_answer for part in name_parts if len(part) > 2):
                mentioned_attendees.append(name)
        
        attendee_count = len(mentioned_attendees)
        if attendee_count >= self.min_reply_count:
            score += 1.5
            logging.warning(f"   ✅ Mentioned {attendee_count} attendee(s): {', '.join(mentioned_attendees)}")
        else:
            logging.warning(f"   ❌ Only mentioned {attendee_count} attendee(s), need {self.min_reply_count}")
        
        # Check whether reply status is mentioned (add more keywords: not replied, haven't replied, etc.)
        reply_keywords = ['replied', 'confirmed', 'replied', 'responded', 'answered', 'confirm',
                          'not replied', "haven't replied", "hasn't replied", "didn't reply",
                          'no reply', 'unreplied']
        if any(kw in self.agent_answer for kw in reply_keywords):
            score += 1.0
            logging.warning("   ✅ Mentioned reply status")
        
        # Trap detection: whether the error mentions an excluded event
        wrong_event = False
        for excluded_event in self.exclude_events:
            if any(kw in self.agent_answer for kw in excluded_event.lower().split() if len(kw) > 3):
                wrong_event = True
                score -= 1.0
                break
        
        if not wrong_event and self.exclude_events:
            score += 0.5
        
        final_score = max(0.0, min(1.0, score / max_score))
        logging.warning(f"{'✅ PASSED' if final_score >= 0.8 else '❌ FAILED'} - Score: {final_score:.2f}")
        logging.warning("=" * 70)
        
        return final_score
