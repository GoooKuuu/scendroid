"""
Extended Scenario Context for 7-Day Scenarios

Extended scenario context, supporting:
1. Cross-day status persistence
2. User preference storage and retrieval
3. Event chain tracing (e.g., purchase-return-exchange workflow)
4. Daily status snapshots
"""

import time
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from absl import logging

from scendroid.apps.scenario.context import ScenarioContext


@dataclass
class DayState:
    """
    Single-day status snapshot
    
    Records all entities created or modified within a given day
    """
    day_idx: int
    date: str
    day_name: str  # "Monday", "Tuesday", etc.
    
    # List of subtasks for the complete task
    completed_subtasks: List[int] = field(default_factory=list)
    
    # Created files {logical name: {path, type, created_by_task}}
    created_files: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # calendarevent [{title, time, location, attendees, ...}]
    created_events: List[Dict[str, Any]] = field(default_factory=list)
    
    # contact [{name, phone, ...}]
    created_contacts: List[Dict[str, Any]] = field(default_factory=list)
    
    # Tasks task [{title, due_date, priority, ...}]
    created_tasks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Shopping orders [{sku, name, price, order_id, ...}]
    shopping_orders: List[Dict[str, Any]] = field(default_factory=list)
    
    # Expense records [{name, amount, category, ...}]
    expense_records: List[Dict[str, Any]] = field(default_factory=list)
    
    # audio recordingfile [{filename, path, duration, ...}]
    audio_recordings: List[Dict[str, Any]] = field(default_factory=list)
    
    # Exercise records [{type, distance, duration, ...}]
    exercise_records: List[Dict[str, Any]] = field(default_factory=list)
    
    # Recipe records [{name, ingredients, steps, ...}]
    recipes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Meeting attendees {event_title: [attendee_names]}
    meeting_attendees: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class UserPreference:
    """User preference entry"""
    value: Any
    source_task: str  # Source task ID, e.g., "W1-03"
    set_at_day: int   # Day index when set up
    category: str     # Preference category
    key: str          # Preference key
    
    # Confirmation rule (optional)
    requires_confirmation: bool = False
    confirmation_message: str = ""


@dataclass 
class EventChainEntry:
    """Event chain entry"""
    action: str       # "purchase", "return_request", "refund", "repurchase"
    day_idx: int      # Day index when the event occurred
    task_id: str      # Task ID, e.g., "W1-09"
    timestamp: float  # Timestamp
    data: Dict[str, Any] = field(default_factory=dict)  # Specific data


class ExtendedScenarioContext(ScenarioContext):
    """
    Extended scenario context, supporting 7-day cross-day status management
    
    core features:
    1. Daily status snapshots (day_states)
    2. User preference management (preferences)
    3. Event chain tracing (event_chains)
    4. Cross-day reference parsing support
    5. Conflict detection support
    
    usage example:
        context = ExtendedScenarioContext()
        
        # initializedays
        context.init_day(0, "2026-01-19", "Monday")
        
        # Store preferences
        context.set_preference("diet", "restriction", "light", "W1-03")
        
        # Record purchase
        context.start_event_chain("table_purchase", {
            'action': 'purchase',
            'sku': 'B07FM3WKJ8',
            'price': 54.99,
        })
        
        # Cross-day references
        attendees = context.get_meeting_attendees_by_day(0, "Sprint Kickoff")
    """
    
    # Weekday name mapping
    DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                 "Friday", "Saturday", "Sunday"]
    
    def __init__(self):
        super().__init__()
        
        # Status snapshot for each day
        self.day_states: Dict[int, DayState] = {}
        
        # current dayindex
        self.current_day_idx: int = 0
        
        # User preference storage
        self.preferences: Dict[str, Dict[str, UserPreference]] = {
            'diet': {},        # Dietary preferences
            'budget': {},      # Budget constraints
            'schedule': {},    # schedule preferences
            'habits': {},      # habits
        }
        
        # event chain (e.g., buy-return-exchange workflow)
        self.event_chains: Dict[str, List[EventChainEntry]] = {}
        
        # pending confirmation items (used for ALT-type tasks)
        self.pending_confirmations: List[Dict[str, Any]] = []
        
        # global cumulative data (aggregated across days)
        self.global_totals: Dict[str, float] = {
            'dining_expense': 0.0,
            'total_expense': 0.0,
            'exercise_distance': 0.0,
            'exercise_duration': 0.0,
        }
    
    # ==================== day management ====================
    
    def init_day(self, day_idx: int, date: str, day_name: str = None):
        """
        initialize the status of a specific day
        
        Args:
            day_idx: day index (0-6)
            date: date string, e.g., "2026-01-19"
            day_name: weekday name; if not provided, automatically computed
        """
        if day_name is None:
            day_name = self.DAY_NAMES[day_idx % 7]
        
        self.day_states[day_idx] = DayState(
            day_idx=day_idx,
            date=date,
            day_name=day_name,
        )
        
        self.current_day_idx = day_idx
        logging.info(f"📅 Initialized Day {day_idx + 1} ({day_name}): {date}")
    
    def get_day_state(self, day_idx: int) -> Optional[DayState]:
        """get a status snapshot for a specific day"""
        return self.day_states.get(day_idx)
    
    def get_current_day_state(self) -> Optional[DayState]:
        """get the current day's status snapshot"""
        return self.day_states.get(self.current_day_idx)
    
    def advance_day(self, new_day_idx: int):
        """
        advance to a new day
        
        Args:
            new_day_idx: index of the new day number
        """
        self.current_day_idx = new_day_idx
        logging.info(f"📅 Advanced to Day {new_day_idx + 1}")
    
    # ==================== preference management ====================
    
    def set_preference(self, category: str, key: str, value: Any, 
                       source_task: str = None,
                       requires_confirmation: bool = False,
                       confirmation_message: str = ""):
        """
        setup user preferences
        
        Args:
            category: preference category ("diet", "budget", "schedule", "habits")
            key: preference key
            value: preference value
            source_task: source task ID
            requires_confirmation: whether confirmation is required upon violation
            confirmation_message: confirmation message template
        """
        if category not in self.preferences:
            self.preferences[category] = {}
        
        pref = UserPreference(
            value=value,
            source_task=source_task or f"W{self.current_day_idx + 1}-??",
            set_at_day=self.current_day_idx,
            category=category,
            key=key,
            requires_confirmation=requires_confirmation,
            confirmation_message=confirmation_message,
        )
        
        self.preferences[category][key] = pref
        
        logging.info(f"📝 Preference set: {category}.{key} = {value} "
                     f"(from {pref.source_task})")
    
    def get_preference(self, category: str, key: str, default=None) -> Any:
        """
        get user preference value
        
        Args:
            category: preference category
            key: preference key
            default: default value
            
        Returns:
            preference value; if it does not exist, return the default value
        """
        pref = self.preferences.get(category, {}).get(key)
        if pref is None:
            return default
        return pref.value
    
    def get_preference_full(self, category: str, key: str) -> Optional[UserPreference]:
        """get the complete preference object"""
        return self.preferences.get(category, {}).get(key)
    
    def check_preference_violation(self, category: str, key: str, 
                                    proposed_value: Any) -> Optional[Dict[str, Any]]:
        """
        check whether a preference is violated
        
        Args:
            category: preference category
            key: preference key
            proposed_value: proposed value
            
        Returns:
            if violated, return {violated: True, pref: ..., message: ...}
            if not violated, return None
        """
        pref = self.get_preference_full(category, key)
        if pref is None:
            return None
        
        violation = None
        
        # budget check
        if category == "budget" and isinstance(pref.value, (int, float)):
            if proposed_value > pref.value:
                violation = {
                    'violated': True,
                    'type': 'budget_exceeded',
                    'limit': pref.value,
                    'proposed': proposed_value,
                    'requires_confirmation': pref.requires_confirmation,
                    'message': pref.confirmation_message or 
                               f"Budget exceeded: limit {pref.value}, proposed {proposed_value}",
                }
        
        # diet check
        elif category == "diet" and key == "forbidden":
            if isinstance(pref.value, list) and proposed_value in pref.value:
                violation = {
                    'violated': True,
                    'type': 'diet_forbidden',
                    'forbidden_items': pref.value,
                    'proposed': proposed_value,
                    'requires_confirmation': pref.requires_confirmation,
                    'message': f"Diet violation: {proposed_value} is in forbidden list",
                }
        
        # schedule conflict check
        elif category == "schedule":
            # specific logic implemented by the caller
            pass
        
        if violation:
            logging.warning(f"⚠️ Preference violation: {violation['message']}")
        
        return violation
    
    def get_all_preferences(self) -> Dict[str, Dict[str, Any]]:
        """get all preferences (simplified format)"""
        result = {}
        for category, prefs in self.preferences.items():
            result[category] = {}
            for key, pref in prefs.items():
                result[category][key] = {
                    'value': pref.value,
                    'source': pref.source_task,
                }
        return result
    
    # ==================== event chain management ====================
    
    def start_event_chain(self, chain_id: str, initial_data: Dict[str, Any]):
        """
        start an event chain
        
        Args:
            chain_id: event chain ID, e.g., "table_purchase"
            initial_data: Initial event data, must contain the 'action' field
        """
        entry = EventChainEntry(
            action=initial_data.get('action', 'start'),
            day_idx=self.current_day_idx,
            task_id=initial_data.get('task_id', f"W{self.current_day_idx + 1}-??"),
            timestamp=time.time(),
            data=initial_data,
        )
        
        self.event_chains[chain_id] = [entry]
        
        logging.info(f"🔗 Started event chain '{chain_id}': {entry.action}")
    
    def append_to_chain(self, chain_id: str, event_data: Dict[str, Any]):
        """
        Append an event to the event chain
        
        Args:
            chain_id: Event chain ID
            event_data: eventdata
        """
        if chain_id not in self.event_chains:
            logging.warning(f"⚠️ Event chain '{chain_id}' not found, creating new")
            self.start_event_chain(chain_id, event_data)
            return
        
        entry = EventChainEntry(
            action=event_data.get('action', 'update'),
            day_idx=self.current_day_idx,
            task_id=event_data.get('task_id', f"W{self.current_day_idx + 1}-??"),
            timestamp=time.time(),
            data=event_data,
        )
        
        self.event_chains[chain_id].append(entry)
        
        logging.info(f"🔗 Appended to chain '{chain_id}': {entry.action}")
    
    def get_event_chain(self, chain_id: str) -> List[EventChainEntry]:
        """Get the event chain"""
        return self.event_chains.get(chain_id, [])
    
    def get_chain_first_entry(self, chain_id: str) -> Optional[EventChainEntry]:
        """Get the first entry of the event chain"""
        chain = self.event_chains.get(chain_id, [])
        return chain[0] if chain else None
    
    def get_chain_last_entry(self, chain_id: str) -> Optional[EventChainEntry]:
        """Get the last entry of the event chain"""
        chain = self.event_chains.get(chain_id, [])
        return chain[-1] if chain else None
    
    # ==================== Cross-day data recording ====================
    
    def record_file(self, logical_name: str, path: str, file_type: str,
                    task_id: str = None, extra: Dict[str, Any] = None):
        """
        Record a created file
        
        Args:
            logical_name: Logical name, e.g., "SprintKickoff_Mon"
            path: filepath
            file_type: File type, e.g., "audio", "document", "image"
            task_id: createtask ID
            extra: Additional information
        """
        day_state = self.get_current_day_state()
        if day_state is None:
            logging.warning("⚠️ Current day not initialized")
            return
        
        file_info = {
            'path': path,
            'type': file_type,
            'created_by_task': task_id or f"W{self.current_day_idx + 1}-??",
            'day_idx': self.current_day_idx,
            **(extra or {}),
        }
        
        day_state.created_files[logical_name] = file_info
        
        # Also store in global shared data for convenient reference during parsing
        self.set(f"file:{logical_name}", file_info)
        
        logging.info(f"📁 Recorded file: {logical_name} -> {path}")
    
    def record_audio(self, filename: str, path: str, task_id: str = None,
                     duration: float = None, extra: Dict[str, Any] = None):
        """Record an audio recording file"""
        day_state = self.get_current_day_state()
        if day_state is None:
            return
        
        audio_info = {
            'filename': filename,
            'path': path,
            'duration': duration,
            'created_by_task': task_id or f"W{self.current_day_idx + 1}-??",
            'day_idx': self.current_day_idx,
            **(extra or {}),
        }
        
        day_state.audio_recordings.append(audio_info)
        self.set(f"audio:{filename}", audio_info)
        
        logging.info(f"🎙️ Recorded audio: {filename}")
    
    def record_meeting_attendees(self, event_title: str, attendees: List[str],
                                  location: str = None, time: str = None):
        """
        Record meeting attendees
        
        Args:
            event_title: Meeting title
            attendees: List of attendees
            location: Meeting location
            time: Meeting time
        """
        day_state = self.get_current_day_state()
        if day_state is None:
            return
        
        day_state.meeting_attendees[event_title] = attendees
        
        # Store in global shared data
        meeting_key = f"meeting:{event_title}"
        self.set(meeting_key, {
            'title': event_title,
            'attendees': attendees,
            'location': location,
            'time': time,
            'day_idx': self.current_day_idx,
        })
        
        # Also store a normalized key (lowercase, spaces removed)
        normalized_key = f"meeting:{event_title.lower().replace(' ', '_')}"
        self.set(normalized_key, self.get(meeting_key))
        
        logging.info(f"👥 Recorded meeting attendees: {event_title} -> {attendees}")
    
    def record_shopping_order(self, sku: str, name: str, price: float,
                               order_id: str = None, task_id: str = None,
                               extra: Dict[str, Any] = None):
        """Record a shopping order"""
        day_state = self.get_current_day_state()
        if day_state is None:
            return
        
        order_info = {
            'sku': sku,
            'name': name,
            'price': price,
            'order_id': order_id,
            'created_by_task': task_id or f"W{self.current_day_idx + 1}-??",
            'day_idx': self.current_day_idx,
            **(extra or {}),
        }
        
        day_state.shopping_orders.append(order_info)
        self.set(f"order:{sku}", order_info)
        
        logging.info(f"🛒 Recorded order: {name} (SKU: {sku}, ${price})")
    
    def record_expense(self, name: str, amount: float, category: str,
                       task_id: str = None, extra: Dict[str, Any] = None):
        """Record an expense"""
        day_state = self.get_current_day_state()
        if day_state is None:
            return
        
        expense_info = {
            'name': name,
            'amount': amount,
            'category': category,
            'created_by_task': task_id or f"W{self.current_day_idx + 1}-??",
            'day_idx': self.current_day_idx,
            **(extra or {}),
        }
        
        day_state.expense_records.append(expense_info)
        
        # Update global cumulative data
        self.global_totals['total_expense'] += amount
        if category.lower() == 'dining' or category.lower() == 'food':
            self.global_totals['dining_expense'] += amount
        
        logging.info(f"💰 Recorded expense: {name} ${amount} ({category})")
    
    def record_exercise(self, activity_type: str, distance: float = None,
                        duration: float = None, task_id: str = None,
                        extra: Dict[str, Any] = None):
        """Record exercise"""
        day_state = self.get_current_day_state()
        if day_state is None:
            return
        
        exercise_info = {
            'type': activity_type,
            'distance': distance,  # km
            'duration': duration,  # minutes
            'created_by_task': task_id or f"W{self.current_day_idx + 1}-??",
            'day_idx': self.current_day_idx,
            **(extra or {}),
        }
        
        day_state.exercise_records.append(exercise_info)
        
        # Update global cumulative data
        if distance:
            self.global_totals['exercise_distance'] += distance
        if duration:
            self.global_totals['exercise_duration'] += duration
        
        logging.info(f"🏃 Recorded exercise: {activity_type} "
                     f"({distance or 0}km, {duration or 0}min)")
    
    def record_recipe(self, name: str, ingredients: List[str] = None,
                      steps: List[str] = None, task_id: str = None,
                      extra: Dict[str, Any] = None):
        """Record a recipe"""
        day_state = self.get_current_day_state()
        if day_state is None:
            return
        
        recipe_info = {
            'name': name,
            'ingredients': ingredients or [],
            'steps': steps or [],
            'created_by_task': task_id or f"W{self.current_day_idx + 1}-??",
            'day_idx': self.current_day_idx,
            **(extra or {}),
        }
        
        day_state.recipes.append(recipe_info)
        self.set(f"recipe:{name.lower().replace(' ', '_')}", recipe_info)
        self.set("latest_recipe", recipe_info)  # For "latest recipe" / "previous recipe" reference
        
        logging.info(f"🍳 Recorded recipe: {name}")
    
    # ==================== Cross-day queries ====================
    
    def get_file_by_day(self, day_idx: int, logical_name: str = None,
                        file_type: str = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a file from the specified day
        
        Args:
            day_idx: Day index
            logical_name: Logical name (optional)
            file_type: File type filter (optional)
            
        Returns:
            File info dictionary; returns None if not found
        """
        day_state = self.get_day_state(day_idx)
        if day_state is None:
            return None
        
        if logical_name:
            return day_state.created_files.get(logical_name)
        
        if file_type:
            for name, info in day_state.created_files.items():
                if info.get('type') == file_type:
                    return info
        
        # Return the first file
        if day_state.created_files:
            return next(iter(day_state.created_files.values()))
        
        return None
    
    def get_audio_by_day(self, day_idx: int, 
                          filename_contains: str = None) -> Optional[Dict[str, Any]]:
        """Retrieve an audio recording file from the specified day"""
        day_state = self.get_day_state(day_idx)
        if day_state is None:
            return None
        
        for audio in day_state.audio_recordings:
            if filename_contains is None:
                return audio
            if filename_contains.lower() in audio.get('filename', '').lower():
                return audio
        
        return None
    
    def get_meeting_attendees_by_day(self, day_idx: int, 
                                      event_title: str = None) -> List[str]:
        """
        Retrieve meeting attendees from the specified day
        
        Args:
            day_idx: Day index
            event_title: Meeting title (optional; if not provided, returns attendees of the first meeting)
            
        Returns:
            List of attendees
        """
        day_state = self.get_day_state(day_idx)
        if day_state is None:
            return []
        
        if event_title:
            # Attempt exact match
            if event_title in day_state.meeting_attendees:
                return day_state.meeting_attendees[event_title]
            
            # Attempt fuzzy match
            event_title_lower = event_title.lower()
            for title, attendees in day_state.meeting_attendees.items():
                if event_title_lower in title.lower():
                    return attendees
        
        # Return attendees of the first meeting
        if day_state.meeting_attendees:
            return next(iter(day_state.meeting_attendees.values()))
        
        return []
    
    def get_orders_by_day(self, day_idx: int) -> List[Dict[str, Any]]:
        """Get all orders for the specified number of days"""
        day_state = self.get_day_state(day_idx)
        if day_state is None:
            return []
        return day_state.shopping_orders
    
    def get_expenses_by_day(self, day_idx: int, 
                            category: str = None) -> List[Dict[str, Any]]:
        """Get expense records for the specified number of days"""
        day_state = self.get_day_state(day_idx)
        if day_state is None:
            return []
        
        if category:
            return [e for e in day_state.expense_records 
                    if e.get('category', '').lower() == category.lower()]
        
        return day_state.expense_records
    
    # ==================== Global Statistics ====================
    
    def get_total_expense(self, category: str = None) -> float:
        """
        Get total expenses
        
        Args:
            category: Expense category (optional), e.g., "dining", "food", etc.
            
        Returns:
            Total amount
        """
        if category:
            total = 0.0
            for day_state in self.day_states.values():
                for expense in day_state.expense_records:
                    if expense.get('category', '').lower() == category.lower():
                        total += expense.get('amount', 0.0)
            return total
        
        return self.global_totals.get('total_expense', 0.0)
    
    def get_total_exercise(self, metric: str = "distance") -> float:
        """
        Get total exercise volume
        
        Args:
            metric: "distance" (km) or "duration" (minutes)
            
        Returns:
            Total exercise volume
        """
        if metric == "distance":
            return self.global_totals.get('exercise_distance', 0.0)
        elif metric == "duration":
            return self.global_totals.get('exercise_duration', 0.0)
        return 0.0
    
    def get_weekly_summary(self) -> Dict[str, Any]:
        """
        Get weekly summary
        
        Returns:
            Dictionary containing various statistics
        """
        return {
            'total_days': len(self.day_states),
            'total_subtasks': sum(
                len(ds.completed_subtasks) for ds in self.day_states.values()
            ),
            'total_expense': self.global_totals.get('total_expense', 0.0),
            'dining_expense': self.global_totals.get('dining_expense', 0.0),
            'exercise_distance': self.global_totals.get('exercise_distance', 0.0),
            'exercise_duration': self.global_totals.get('exercise_duration', 0.0),
            'event_chains': list(self.event_chains.keys()),
            'preferences_set': sum(
                len(prefs) for prefs in self.preferences.values()
            ),
        }
    
    # ==================== Serialization ====================
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the context into a dictionary (for save/restore)"""
        return {
            'scenario_id': self.scenario_id,
            'scenario_name': self.scenario_name,
            'base_date': self.base_date,
            'current_day_idx': self.current_day_idx,
            'shared_data': self.shared_data,
            'subtask_history': self.subtask_history,
            'global_totals': self.global_totals,
            'preferences': {
                cat: {
                    key: {
                        'value': pref.value,
                        'source_task': pref.source_task,
                        'set_at_day': pref.set_at_day,
                        'requires_confirmation': pref.requires_confirmation,
                    }
                    for key, pref in prefs.items()
                }
                for cat, prefs in self.preferences.items()
            },
            'event_chains': {
                chain_id: [
                    {
                        'action': entry.action,
                        'day_idx': entry.day_idx,
                        'task_id': entry.task_id,
                        'data': entry.data,
                    }
                    for entry in entries
                ]
                for chain_id, entries in self.event_chains.items()
            },
            # day_states contains a large amount of data; serialize on demand
        }
    
    def __repr__(self) -> str:
        return (
            f"ExtendedScenarioContext("
            f"scenario='{self.scenario_name}', "
            f"day={self.current_day_idx + 1}/7, "
            f"subtasks={len(self.subtask_history)}, "
            f"preferences={sum(len(p) for p in self.preferences.values())}, "
            f"chains={len(self.event_chains)}"
            f")"
        )
