"""
Preference Store for 7-Day Scenarios

User preference storage and management, supporting:
1. Parsing preferences from user instructions
2. Preference storage and querying
3. Violation detection
4. Confirmation rule management
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from absl import logging


@dataclass
class BudgetLimit:
    """Budget limit"""
    category: str           # Category, e.g., "dining", "total"
    limit: float            # Limit amount
    period: str             # Period, e.g., "weekly", "daily"
    currency: str = "USD"
    requires_confirmation: bool = True
    confirmation_message: str = ""


@dataclass
class DietRestriction:
    """Dietary restriction"""
    restriction_type: str   # "Light", "Low-fat", "Vegetarian", etc.
    forbidden: List[str] = field(default_factory=list)    # Forbidden foods
    preferred: List[str] = field(default_factory=list)    # Preferred foods
    description: str = ""


@dataclass
class ScheduleHabit:
    """Schedule habit"""
    activity: str           # Activity name, e.g., "exercise", "lunch"
    time: str               # Time, e.g., "18:30"
    duration_minutes: int   # Duration (in minutes)
    frequency: str          # Frequency, e.g., "daily", "weekday"
    requires_confirmation: bool = True  # Whether confirmation is required upon conflict
    confirmation_message: str = ""


@dataclass
class ConfirmationRule:
    """confirmrule"""
    rule_type: str          # "budget", "schedule", "diet"
    condition: str          # Trigger condition description
    trigger_check: str      # Check method name
    message_template: str   # Message template


class PreferenceStore:
    """
    User preference storage and management
    
    Supported preference types:
    1. Budget limit (budget): Amount upper bound, categorized budget
    2. Dietary preference (diet): Light, low-fat, forbidden foods, etc.
    3. Schedule habit (schedule): Activities at fixed time slots
    4. Confirmation rule (confirmation): Conditions requiring confirmation
    
    usage example:
        store = PreferenceStore()
        
        # Parse and store preferences
        store.parse_and_store(
            "During fat-loss period, eat only light food and avoid fried food; dining budget within 120 knife",
            task_id="W1-03"
        )
        
        # Check budget
        result = store.check_budget("dining", 50.0, 80.0)
        # result = {'allowed': True, ...}
        
        # Check diet
        result = store.check_diet("fried chicken")
        # result = {'allowed': False, 'reason': 'Fried food is in the forbidden list'}
    """
    
    def __init__(self):
        # Budget limit
        self.budgets: Dict[str, BudgetLimit] = {}
        
        # Dietary restriction
        self.diet: Optional[DietRestriction] = None
        
        # Schedule habit
        self.schedules: Dict[str, ScheduleHabit] = {}
        
        # confirmrule
        self.confirmation_rules: List[ConfirmationRule] = []
        
        # Original preference text (for reference)
        self.raw_preferences: List[Dict[str, str]] = []
    
    # ==================== parsemethod ====================
    
    def parse_and_store(self, instruction: str, task_id: str):
        """
        Parse and store preferences from user instructions
        
        Supported format examples:
        - "Weight loss period: eat only light meals, no fried food"
        - "Dining budget within 120 knife (confirmation required if exceeded)"
        - "Exercise starts daily at 18:30 and lasts for half an hour (confirmation required if other activities are scheduled)"
        
        Args:
            instruction: User instruction text
            task_id: Source task ID
        """
        # Save original text
        self.raw_preferences.append({
            'text': instruction,
            'task_id': task_id,
        })
        
        # Parse dietary preferences
        self._parse_diet(instruction, task_id)
        
        # Parse budget
        self._parse_budget(instruction, task_id)
        
        # Parse schedule habits
        self._parse_schedule(instruction, task_id)
        
        logging.info(f"📝 Parsed preferences from {task_id}")
    
    def _parse_diet(self, instruction: str, task_id: str):
        """Parse dietary preferences"""
        # Detect keywords related to weight loss/light meals (Chinese → English type, list of prohibited foods in English)
        diet_keywords = {
            # Chinese keyword -> (type, forbidden_foods in English)
            'weight_loss': ('weight_loss', ['high_fat', 'fried', 'sweets']),
            'light': ('light', ['fried', 'heavy_flavor', 'spicy']),
            'low_fat': ('low_fat', ['fried', 'fatty_meat', 'cream']),
            'vegetarian': ('vegetarian', ['meat', 'fish', 'seafood']),
            'low_sugar': ('low_sugar', ['sweets', 'candy', 'cake']),
        }
        
        # Map Chinese keywords to English types
        chinese_to_type = {
            'weight loss': 'weight_loss',
            'light': 'light',
            'low-fat': 'low_fat',
            'vegetarian': 'vegetarian',
            'low-sugar': 'low_sugar',
        }
        
        restriction_type = None
        forbidden = []
        
        # Detect Chinese keywords
        for cn_keyword, en_type in chinese_to_type.items():
            if cn_keyword in instruction:
                restriction_type = en_type
                if en_type in diet_keywords:
                    forbidden.extend(diet_keywords[en_type][1])
        
        # Also detect English keywords
        for en_keyword, (rtype, default_forbidden) in diet_keywords.items():
            if en_keyword in instruction.lower():
                restriction_type = rtype
                forbidden.extend(default_forbidden)
        
        # Parse "do not eat XX" / "do not want XX" (Chinese: do not eat XX)
        not_eat_pattern = r'not eat|do not eat|avoid|forbidden|no\s+|avoid|forbidden'
        if re.search(not_eat_pattern, instruction, re.IGNORECASE):
            # Extract subsequent food terms
            food_pattern = r'(?:not eat|do not eat|avoid|forbidden|no\s+|avoid|forbidden)\s*([^.,;,\s]+)'
            matches = re.findall(food_pattern, instruction, re.IGNORECASE)
            for match in matches:
                foods = re.split(r'[,&\s]+', match.strip())
                forbidden.extend([f.strip() for f in foods if f.strip()])
        
        # Remove duplicates
        forbidden = list(set(forbidden))
        
        if restriction_type or forbidden:
            self.diet = DietRestriction(
                restriction_type=restriction_type or 'custom',
                forbidden=forbidden,
                preferred=[],
                description=instruction[:100],
            )
            logging.info(f"   Diet: {restriction_type}, forbidden: {forbidden}")
    
    def _parse_budget(self, instruction: str, task_id: str):
        """Parse budget constraints"""
        # Match budget amount: supports formats such as "120 knife", "$120", "120 USD", etc.
        budget_patterns = [
            r'budget\s*(\d+(?:\.\d+)?)\s*(?:dollars?|USD|\$)',
            r'\$\s*(\d+(?:\.\d+)?)\s*(?:limit|within)?',
            r'(\d+(?:\.\d+)?)\s*(?:dollars?|USD)\s*(?:limit|budget)?',
            # Chinese patterns
            r'budget\s*(\d+(?:\.\d+)?)\s*(?:knife|USD|\$)',
            r'\$?\s*(\d+(?:\.\d+)?)\s*(?:knife|USD)?\s*(?:within|maximum)',
            r'(\d+(?:\.\d+)?)\s*(?:knife|USD)\s*(?:within|budget|limit)',
        ]
        
        amount = None
        for pattern in budget_patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                amount = float(match.group(1))
                break
        
        if amount is None:
            return
        
        # Determine budget category
        category = 'total'  # Default
        # Check both Chinese and English keywords
        if 'dining' in instruction or 'dining' in instruction.lower():
            category = 'dining'
        elif 'shopping' in instruction or 'shopping' in instruction.lower():
            category = 'shopping'
        elif 'food' in instruction or 'food' in instruction.lower():
            category = 'food'
        
        # Detect whether confirmation is required (Chinese and English keywords)
        requires_confirmation = any(
            kw in instruction.lower() for kw in ['confirm', 'reminder', 'ask', 'confirm', 'ask', 'check']
        )
        
        confirmation_message = ""
        if requires_confirmation:
            confirmation_message = f"Current {category} spending will exceed budget ${amount}. Continue?"
        
        self.budgets[category] = BudgetLimit(
            category=category,
            limit=amount,
            period='weekly',
            requires_confirmation=requires_confirmation,
            confirmation_message=confirmation_message,
        )
        
        # Add confirmation rule
        if requires_confirmation:
            self.confirmation_rules.append(ConfirmationRule(
                rule_type='budget',
                condition=f'{category} > {amount}',
                trigger_check='check_budget_exceeded',
                message_template=confirmation_message,
            ))
        
        logging.info(f"   💰 Budget: {category} <= ${amount} "
                     f"(confirm: {requires_confirmation})")
    
    def _parse_schedule(self, instruction: str, task_id: str):
        """Parse schedule habits"""
        # Match time: supports formats such as "18:30", "6:30 PM", "6:30 p.m.", etc.
        time_patterns = [
            r'(\d{1,2}):(\d{2})',  # 18:30
            r'(\d{1,2}) o\'clock (\d{2})?',  # Chinese: 6:30
            r'(?:morning|afternoon|evening|am|pm)?(\d{1,2})[::]?(\d{2})?',
        ]
        
        time_str = None
        for pattern in time_patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2) or 0)
                
                # handle morning/afternoon/evening (Chinese: afternoon/evening or English pm)
                if 'afternoon' in instruction or 'evening' in instruction or 'pm' in instruction.lower():
                    if hour < 12:
                        hour += 12
                
                time_str = f"{hour:02d}:{minute:02d}"
                break
        
        if time_str is None:
            return
        
        # Determine activity type
        activity = 'activity'
        if 'exercise' in instruction or 'exercise' in instruction.lower():
            activity = 'exercise'
        elif 'lunch' in instruction or 'lunch' in instruction.lower():
            activity = 'lunch'
        elif 'dinner' in instruction or 'dinner' in instruction.lower():
            activity = 'dinner'
        
        # Parse duration
        duration = 30  # Default 30 minutes
        duration_patterns = [
            (r'(\d+)\s*(?:minutes?|mins?|minutes|minutes)', 'minutes'),
            (r'half hours|half\s*(?:an\s*)?hour', 'half_hour'),
            (r'one hours|one\s*hour|1\s*hour', 'one_hour'),
            (r'(\d+(?:\.\d+)?)\s*(?:hours?|hours)', 'hours'),
        ]
        
        for pattern, pattern_type in duration_patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                if pattern_type == 'half_hour':
                    duration = 30
                elif pattern_type == 'one_hour':
                    duration = 60
                elif pattern_type == 'hours':
                    duration = int(float(match.group(1)) * 60)
                else:  # minutes
                    duration = int(match.group(1))
                break
        
        # Detect whether confirmation is required (Chinese and English keywords)
        requires_confirmation = any(
            kw in instruction.lower() for kw in ['confirm', 'reminder', 'conflict', 'conflict', 'confirm', 'reminder']
        )
        
        confirmation_message = ""
        if requires_confirmation:
            confirmation_message = f"Conflict with {activity} at {time_str}. Continue?"
        
        self.schedules[activity] = ScheduleHabit(
            activity=activity,
            time=time_str,
            duration_minutes=duration,
            frequency='daily',
            requires_confirmation=requires_confirmation,
            confirmation_message=confirmation_message,
        )
        
        # Add confirm rule
        if requires_confirmation:
            self.confirmation_rules.append(ConfirmationRule(
                rule_type='schedule',
                condition=f'conflict with {activity} at {time_str}',
                trigger_check='check_schedule_conflict',
                message_template=confirmation_message,
            ))
        
        logging.info(f"   📅 Schedule: {activity} at {time_str} for {duration}min "
                     f"(confirm: {requires_confirmation})")
    
    # ==================== checkmethod ====================
    
    def check_budget(self, category: str, amount: float, 
                     current_total: float = 0.0) -> Dict[str, Any]:
        """
        Check budget
        
        Args:
            category: expense category
            amount: amount of this expense
            current_total: current cumulative amount
            
        Returns:
            {
                'allowed': bool,          # Whether allowed
                'requires_confirmation': bool,  # Whether confirmation is required
                'limit': float,           # Budget limit
                'current': float,         # Current cumulative amount
                'proposed': float,        # Total amount after adding this expense
                'message': str,           # Prompt message
            }
        """
        budget = self.budgets.get(category) or self.budgets.get('total')
        
        if budget is None:
            return {
                'allowed': True,
                'requires_confirmation': False,
                'limit': None,
                'current': current_total,
                'proposed': current_total + amount,
                'message': 'No budget limit',
            }
        
        proposed = current_total + amount
        exceeded = proposed > budget.limit
        
        return {
            'allowed': not exceeded or not budget.requires_confirmation,
            'requires_confirmation': exceeded and budget.requires_confirmation,
            'limit': budget.limit,
            'current': current_total,
            'proposed': proposed,
            'message': budget.confirmation_message if exceeded else 'Within budget',
            'exceeded': exceeded,
        }
    
    def check_diet(self, food_item: str) -> Dict[str, Any]:
        """
        Check dietary restrictions
        
        Args:
            food_item: food name
            
        Returns:
            {
                'allowed': bool,
                'reason': str,
                'restriction_type': str,
            }
        """
        if self.diet is None:
            return {
                'allowed': True,
                'reason': 'No diet restriction',
                'restriction_type': None,
            }
        
        # Check whether in prohibited list
        food_lower = food_item.lower()
        for forbidden in self.diet.forbidden:
            if forbidden.lower() in food_lower or food_lower in forbidden.lower():
                return {
                    'allowed': False,
                    'reason': f'"{food_item}" contains forbidden "{forbidden}"',
                    'restriction_type': self.diet.restriction_type,
                    'forbidden_match': forbidden,
                }
        
        return {
            'allowed': True,
            'reason': 'Meets diet requirements',
            'restriction_type': self.diet.restriction_type,
        }
    
    def check_schedule_conflict(self, proposed_time: str, 
                                 duration_minutes: int = 60) -> Dict[str, Any]:
        """
        Check schedule conflict
        
        Args:
            proposed_time: proposed time (HH:MM format)
            duration_minutes: duration (minutes)
            
        Returns:
            {
                'has_conflict': bool,
                'conflicting_activity': str,
                'conflicting_time': str,
                'requires_confirmation': bool,
                'message': str,
            }
        """
        if not self.schedules:
            return {
                'has_conflict': False,
                'conflicting_activity': None,
                'conflicting_time': None,
                'requires_confirmation': False,
                'message': 'No schedule conflict',
            }
        
        # Parse proposed time
        try:
            p_hour, p_minute = map(int, proposed_time.split(':'))
            p_start = p_hour * 60 + p_minute
            p_end = p_start + duration_minutes
        except ValueError:
            return {
                'has_conflict': False,
                'message': f'Cannot parse time: {proposed_time}',
            }
        
        # Check each schedule habit
        for activity, habit in self.schedules.items():
            try:
                h_hour, h_minute = map(int, habit.time.split(':'))
                h_start = h_hour * 60 + h_minute
                h_end = h_start + habit.duration_minutes
            except ValueError:
                continue
            
            # Check time overlap
            if p_start < h_end and p_end > h_start:
                return {
                    'has_conflict': True,
                    'conflicting_activity': activity,
                    'conflicting_time': habit.time,
                    'requires_confirmation': habit.requires_confirmation,
                    'message': habit.confirmation_message or 
                               f'Conflict with {activity} ({habit.time})',
                }
        
        return {
            'has_conflict': False,
            'conflicting_activity': None,
            'conflicting_time': None,
            'requires_confirmation': False,
            'message': 'No schedule conflict',
        }
    
    def get_diet_requirements(self) -> Dict[str, Any]:
        """
        Get dietary requirements (for recipe recommendation)
        
        Returns:
            {
                'restriction_type': str,
                'forbidden': List[str],
                'preferred': List[str],
                'description': str,
            }
        """
        if self.diet is None:
            return {
                'restriction_type': None,
                'forbidden': [],
                'preferred': [],
                'description': 'No diet restriction',
            }
        
        return {
            'restriction_type': self.diet.restriction_type,
            'forbidden': self.diet.forbidden,
            'preferred': self.diet.preferred,
            'description': self.diet.description,
        }
    
    def get_budget_limit(self, category: str = 'total') -> Optional[float]:
        """Get budget limit"""
        budget = self.budgets.get(category) or self.budgets.get('total')
        return budget.limit if budget else None
    
    def get_schedule_habit(self, activity: str) -> Optional[ScheduleHabit]:
        """Get schedule habit"""
        return self.schedules.get(activity)
    
    # ==================== Direct setup method ====================
    
    def set_budget(self, category: str, limit: float, 
                   requires_confirmation: bool = True,
                   confirmation_message: str = ""):
        """Directly set up budget limit"""
        self.budgets[category] = BudgetLimit(
            category=category,
            limit=limit,
            period='weekly',
            requires_confirmation=requires_confirmation,
            confirmation_message=confirmation_message or 
                                 f"Budget exceeded ${limit}. Continue?",
        )
    
    def set_diet_restriction(self, restriction_type: str,
                              forbidden: List[str] = None,
                              preferred: List[str] = None):
        """Directly set up dietary restrictions"""
        self.diet = DietRestriction(
            restriction_type=restriction_type,
            forbidden=forbidden or [],
            preferred=preferred or [],
        )
    
    def set_schedule_habit(self, activity: str, time: str, 
                           duration_minutes: int,
                           requires_confirmation: bool = True):
        """Directly set up the schedule habit"""
        self.schedules[activity] = ScheduleHabit(
            activity=activity,
            time=time,
            duration_minutes=duration_minutes,
            frequency='daily',
            requires_confirmation=requires_confirmation,
        )
    
    # ==================== Serialization ====================
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a dictionary"""
        return {
            'budgets': {
                k: {
                    'category': v.category,
                    'limit': v.limit,
                    'period': v.period,
                    'requires_confirmation': v.requires_confirmation,
                }
                for k, v in self.budgets.items()
            },
            'diet': {
                'restriction_type': self.diet.restriction_type,
                'forbidden': self.diet.forbidden,
                'preferred': self.diet.preferred,
            } if self.diet else None,
            'schedules': {
                k: {
                    'activity': v.activity,
                    'time': v.time,
                    'duration_minutes': v.duration_minutes,
                    'requires_confirmation': v.requires_confirmation,
                }
                for k, v in self.schedules.items()
            },
            'raw_preferences': self.raw_preferences,
        }
    
    def __repr__(self) -> str:
        return (
            f"PreferenceStore("
            f"budgets={len(self.budgets)}, "
            f"diet={self.diet.restriction_type if self.diet else None}, "
            f"schedules={len(self.schedules)}"
            f")"
        )
