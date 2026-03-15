"""
Reference Resolver for 7-Day Scenarios

Cross-day reference parser, supports:
1. Relative time references: "yesterday", "the day before yesterday", "just now"
2. Absolute time references: "Monday", "Day 3"
3. Event references: "the kickoff meeting's audio recording", "that meeting"
4. Entity references: "those people", "the recipe just now"
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
from absl import logging

if TYPE_CHECKING:
    from scendroid.apps.scenario.extended_context import ExtendedScenarioContext


@dataclass
class ResolvedReference:
    """
    Parsed reference result
    
    Attributes:
        success: Whether parsing succeeded
        day_idx: Parsed day index (0-6)
        entity_type: Entity type (meeting, audio, file, attendees, order, recipe, etc.)
        entity_id: Entity identifier
        resolved_data: Actual parsed data
        confidence: Confidence score (0.0-1.0)
        resolution_path: Parsing path description
    """
    success: bool = False
    day_idx: Optional[int] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    resolved_data: Any = None
    confidence: float = 0.0
    resolution_path: str = ""
    
    def __bool__(self):
        return self.success


class ReferenceResolver:
    """
    Cross-day reference parser
    
    Supported reference modes:
    1. Relative time: "yesterday", "the day before yesterday", "just now", "today"
    2. Absolute time: "Monday", "Tuesday", "Day 3", "Day 1"
    3. Event references: "kickoff meeting", "design review meeting", "that meeting"
    4. Entity references: "those people", "attendees", "audio recording", "recipe"
    
    usage example:
        resolver = ReferenceResolver(context)
        
        # Parse "yesterday's kickoff meeting's audio recording"
        result = resolver.resolve("yesterday's kickoff meeting's audio recording", current_day=1)
        # result.day_idx = 0, result.entity_type = "audio"
        
        # Parse "send info to those people who attended yesterday's meeting"
        result = resolver.resolve("those people who attended yesterday's meeting", current_day=1)
        # result.resolved_data = ["Alice", "Bob", "Charlie"]
    """
    
    # ==================== Mode definitions ====================
    
    # Relative time mode (Chinese patterns included for backward compatibility)
    RELATIVE_TIME_PATTERNS: Dict[str, int] = {
        r'yesterday': -1,
        r'day\s*before\s*yesterday': -2,
        r'just\s*now': 0,  # Same day
        r'today': 0,
        r'last\s*week': -7,
        # Chinese patterns (kept for compatibility with Chinese instructions)
        r'\u6628\u5929|\u6628\u65e5': -1,  # yesterday|yesterday
        r'\u524d\u5929': -2,  # the day before yesterday
        r'\u521a\u624d|\u521a\u521a': 0,  # just now|just now
        r'\u4eca\u5929|\u4eca\u65e5': 0,  # today|today
        r'\u4e0a\u5468': -7,  # last week
    }
    
    # Absolute time mode (weekday)
    WEEKDAY_PATTERNS: Dict[str, int] = {
        r'Monday|Mon': 0,
        r'Tuesday|Tue': 1,
        r'Wednesday|Wed': 2,
        r'Thursday|Thu': 3,
        r'Friday|Fri': 4,
        r'Saturday|Sat': 5,
        r'Sunday|Sun': 6,
        # Chinese patterns
        r'\u5468\u4e00|\u661f\u671f\u4e00': 0,  # Monday|Monday
        r'\u5468\u4e8c|\u661f\u671f\u4e8c': 1,  # Tuesday|Tuesday
        r'\u5468\u4e09|\u661f\u671f\u4e09': 2,  # Wednesday|Wednesday
        r'\u5468\u56db|\u661f\u671f\u56db': 3,  # Thursday|Thursday
        r'\u5468\u4e94|\u661f\u671f\u4e94': 4,  # Friday|Friday
        r'\u5468\u516d|\u661f\u671f\u516d': 5,  # Saturday|Saturday
        r'\u5468\u65e5|\u5468\u5929|\u661f\u671f\u65e5|\u661f\u671f\u5929': 6,  # Sunday|Sunday|Sunday|Sunday
    }
    
    # Ordinal number mode
    ORDINAL_PATTERNS: Dict[str, int] = {
        r'Day\s*1|day\s*one': 0,
        r'Day\s*2|day\s*two': 1,
        r'Day\s*3|day\s*three': 2,
        r'Day\s*4|day\s*four': 3,
        r'Day\s*5|day\s*five': 4,
        r'Day\s*6|day\s*six': 5,
        r'Day\s*7|day\s*seven': 6,
        # Chinese patterns
        r'\u7b2c\u4e00\u5929': 0,  # Day 1
        r'\u7b2c\u4e8c\u5929': 1,  # Second day
        r'\u7b2c\u4e09\u5929': 2,  # Third day
        r'\u7b2c\u56db\u5929': 3,  # Fourth day
        r'\u7b2c\u4e94\u5929': 4,  # Fifth day
        r'\u7b2c\u516d\u5929': 5,  # Sixth day
        r'\u7b2c\u4e03\u5929': 6,  # Seventh day
    }
    
    # event/entity type mode (English patterns with Chinese aliases in Unicode)
    ENTITY_PATTERNS: Dict[str, Tuple[str, Optional[str]]] = {
        # Meeting related
        r'kickoff|kick-off|sprint\s*kickoff|\u542f\u52a8\u4f1a': ('meeting', 'sprint_kickoff'),  # Kickoff meeting
        r'design.*review|\u8bbe\u8ba1.*\u4f1a|\u8bbe\u8ba1\u8bc4\u5ba1': ('meeting', 'design_review'),  # Design review meeting|design review
        r'sync|sprint\s*sync|\u540c\u6b65\u4f1a': ('meeting', 'sprint_sync'),  # Sync meeting
        r'meeting|\u4f1a\u8bae': ('meeting', None),  # Meeting
        
        # People related
        r'attendees?|\u90a3\u51e0\u4e2a\u4eba|\u90a3\u4e9b\u4eba|\u53c2\u4f1a\u4eba|\u4e0e\u4f1a\u4eba|\u8d1f\u8d23\u4eba': ('attendees', None),  # Those people|those people|attendees|participants|responsible person
        r'participants|\u5f00\u4f1a\u7684.*\u4eba|\u53c2\u52a0.*\u7684\u4eba': ('attendees', None),  # People attending the meeting|people participating in...
        
        # File related
        r'recording|audio|\u5f55\u97f3': ('audio', None),  # audio recording
        r'file|document|\u6587\u4ef6': ('file', None),  # file
        r'photo|image|picture|\u7167\u7247|\u56fe\u7247': ('photo', None),  # Photo|image
        
        # Shopping related
        r'table|outdoor.*table|\u684c\u5b50': ('order', 'table'),  # Table
        r'order|bought|\u8ba2\u5355|\u8d2d\u4e70|\u4e70\u7684': ('order', None),  # Order|purchase|purchased
        r'egg|\u9e21\u86cb': ('order', 'egg'),  # Egg
        
        # Recipe related
        r'recipe|\u98df\u8c31|\u505a\u6cd5': ('recipe', None),  # Recipe|cooking method
        r'dish|\u90a3\u9053\u83dc|\u90a3\u4e2a\u83dc': ('recipe', None),  # That dish|that dish
        
        # Expense related
        r'expense|\u652f\u51fa|\u82b1\u8d39|\u5f00\u9500': ('expense', None),  # Expense|expenditure|cost
        
        # Exercise related
        r'exercise|walk|run|\u8fd0\u52a8|\u953b\u70bc|\u6563\u6b65|\u8dd1\u6b65': ('exercise', None),  # Exercise|physical exercise|walking|running
    }
    
    def __init__(self, context: 'ExtendedScenarioContext'):
        """
        initialize parser
        
        Args:
            context: Extended scenario context
        """
        self.context = context
    
    # ==================== Main parse method ====================
    
    def resolve(self, reference: str, current_day: int = None) -> ResolvedReference:
        """
        Parse reference
        
        Args:
            reference: Quoted text, e.g., "yesterday's sprint kickoff audio recording"
            current_day: Current day index (0-6); if not provided, retrieve from context
        
        Returns:
            ResolvedReference object containing the parse result
        """
        if current_day is None:
            current_day = self.context.current_day_idx
        
        result = ResolvedReference()
        
        try:
            # 1. Parse time component
            day_idx = self._resolve_time(reference, current_day)
            result.day_idx = day_idx
            
            # 2. Parse entity type
            entity_type, entity_id = self._resolve_entity_type(reference)
            result.entity_type = entity_type
            result.entity_id = entity_id
            
            # 3. Retrieve actual data from context
            resolved_data = self._fetch_from_context(
                day_idx, entity_type, entity_id, reference
            )
            result.resolved_data = resolved_data
            
            # 4. Compute confidence score and success status
            result.success = resolved_data is not None
            result.confidence = self._calculate_confidence(
                day_idx, entity_type, entity_id, resolved_data
            )
            
            # 5. Generate parse path explanation
            result.resolution_path = (
                f"Day {day_idx} -> {entity_type}"
                f"{f':{entity_id}' if entity_id else ''}"
            )
            
            logging.info(f"🔍 Resolved '{reference[:50]}...' -> {result.resolution_path} "
                         f"(confidence: {result.confidence:.2f})")
            
        except Exception as e:
            logging.warning(f"⚠️ Failed to resolve '{reference}': {e}")
            result.success = False
            result.confidence = 0.0
        
        return result
    
    def resolve_attendees(self, reference: str, 
                           current_day: int = None) -> List[str]:
        """
        Specialized parser for attendee references
        
        Args:
            reference: quoted text
            current_day: current day
            
        Returns:
            List of attendees
        """
        result = self.resolve(reference, current_day)
        
        if result.success and isinstance(result.resolved_data, list):
            return result.resolved_data
        
        return []
    
    def resolve_file(self, reference: str, 
                      current_day: int = None) -> Optional[Dict[str, Any]]:
        """
        Specialized parser for file references
        
        Args:
            reference: quoted text
            current_day: current day
            
        Returns:
            fileinfodictionary
        """
        result = self.resolve(reference, current_day)
        
        if result.success and isinstance(result.resolved_data, dict):
            return result.resolved_data
        
        return None
    
    def resolve_order(self, reference: str, 
                       current_day: int = None) -> Optional[Dict[str, Any]]:
        """
        Specialized parser for order references
        
        Args:
            reference: quoted text
            current_day: current day
            
        Returns:
            Dictionary containing order information
        """
        result = self.resolve(reference, current_day)
        
        if result.success and isinstance(result.resolved_data, dict):
            return result.resolved_data
        
        # Attempt to retrieve from event chain
        if '\u684c\u5b50' in reference or 'table' in reference.lower():  # Table
            chain = self.context.get_event_chain('table_purchase')
            if chain:
                return chain[0].data
        
        return None
    
    # ==================== Internal parse method ====================
    
    def _resolve_time(self, reference: str, current_day: int) -> int:
        """
        Parse time references
        
        Args:
            reference: quoted text
            current_day: current day
            
        Returns:
            Target day index (0-6)
        """
        reference_lower = reference.lower()
        
        # 1. Check relative time
        for pattern, offset in self.RELATIVE_TIME_PATTERNS.items():
            if re.search(pattern, reference, re.IGNORECASE):
                target_day = current_day + offset
                return max(0, min(6, target_day))
        
        # 2. Check absolute weekday
        for pattern, day_idx in self.WEEKDAY_PATTERNS.items():
            if re.search(pattern, reference, re.IGNORECASE):
                return day_idx
        
        # 3. Check ordinal numbers
        for pattern, day_idx in self.ORDINAL_PATTERNS.items():
            if re.search(pattern, reference, re.IGNORECASE):
                return day_idx
        
        # 4. Check task ID in W{N}-XX format
        task_id_match = re.search(r'W(\d)-', reference)
        if task_id_match:
            return int(task_id_match.group(1)) - 1
        
        # 5. Default return current days
        return current_day
    
    def _resolve_entity_type(self, reference: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse entity type
        
        Args:
            reference: quoted text
            
        Returns:
            (entity_type, entity_id) tuple
        """
        for pattern, (entity_type, entity_id) in self.ENTITY_PATTERNS.items():
            if re.search(pattern, reference, re.IGNORECASE):
                return entity_type, entity_id
        
        return None, None
    
    def _fetch_from_context(self, day_idx: int, entity_type: str, 
                            entity_id: str, reference: str) -> Any:
        """
        Retrieve data from context
        
        Args:
            day_idx: target days number
            entity_type: entity type
            entity_id: entity ID
            reference: original quoted text (used for fuzzy matching)
            
        Returns:
            Parsed data
        """
        if entity_type is None:
            return None
        
        # Dispatch based on entity type
        if entity_type == 'meeting':
            return self._fetch_meeting(day_idx, entity_id, reference)
        
        elif entity_type == 'attendees':
            return self._fetch_attendees(day_idx, entity_id, reference)
        
        elif entity_type == 'audio':
            return self._fetch_audio(day_idx, entity_id, reference)
        
        elif entity_type == 'file':
            return self._fetch_file(day_idx, entity_id, reference)
        
        elif entity_type == 'order':
            return self._fetch_order(day_idx, entity_id, reference)
        
        elif entity_type == 'recipe':
            return self._fetch_recipe(day_idx, entity_id, reference)
        
        elif entity_type == 'expense':
            return self._fetch_expense(day_idx, entity_id, reference)
        
        elif entity_type == 'exercise':
            return self._fetch_exercise(day_idx, entity_id, reference)
        
        return None
    
    def _fetch_meeting(self, day_idx: int, entity_id: str, 
                        reference: str) -> Optional[Dict[str, Any]]:
        """Get meeting info"""
        # Attempt to retrieve from shared_data
        if entity_id:
            meeting_key = f"meeting:{entity_id}"
            meeting = self.context.get(meeting_key)
            if meeting:
                return meeting
        
        # Retrieve from day_state
        day_state = self.context.get_day_state(day_idx)
        if day_state and day_state.meeting_attendees:
            # Return the first meeting
            for title, attendees in day_state.meeting_attendees.items():
                return {
                    'title': title,
                    'attendees': attendees,
                    'day_idx': day_idx,
                }
        
        return None
    
    def _fetch_attendees(self, day_idx: int, entity_id: str, 
                          reference: str) -> List[str]:
        """Get attendee list"""
        # 1. Check whether there is a specific meeting reference (English patterns with Chinese Unicode)
        meeting_patterns = [
            (r'kickoff|\u542f\u52a8\u4f1a', 'sprint_kickoff'),  # kickoff meeting
            (r'design.*review|\u8bbe\u8ba1.*\u4f1a', 'design_review'),  # design.*meeting
            (r'sync|\u540c\u6b65\u4f1a', 'sprint_sync'),  # sync meeting
        ]
        
        for pattern, meeting_id in meeting_patterns:
            if re.search(pattern, reference, re.IGNORECASE):
                # Retrieve from shared_data
                meeting = self.context.get(f"meeting:{meeting_id}")
                if meeting and 'attendees' in meeting:
                    return meeting['attendees']
        
        # 2. Retrieve from day_state
        return self.context.get_meeting_attendees_by_day(day_idx)
    
    def _fetch_audio(self, day_idx: int, entity_id: str, 
                      reference: str) -> Optional[Dict[str, Any]]:
        """getaudio recordingfile"""
        # Check whether there is a specific audio recording reference
        filename_hint = None
        
        # Check for specific recording references (English and Chinese patterns)
        if '\u542f\u52a8\u4f1a' in reference or 'kickoff' in reference.lower():  # kickoff meeting
            filename_hint = 'kickoff'
        elif '\u8bbe\u8ba1' in reference or 'design' in reference.lower():  # design
            filename_hint = 'design'
        elif '\u5907\u5fd8' in reference or 'memo' in reference.lower():  # memo
            filename_hint = 'memo'
        
        return self.context.get_audio_by_day(day_idx, filename_hint)
    
    def _fetch_file(self, day_idx: int, entity_id: str, 
                     reference: str) -> Optional[Dict[str, Any]]:
        """getfileinfo"""
        # Infer file type based on quoted text
        file_type = None
        
        # Check file type references (English and Chinese patterns)
        if '\u5f55\u97f3' in reference or 'audio' in reference.lower():  # audio recording
            file_type = 'audio'
        elif '\u7167\u7247' in reference or 'photo' in reference.lower():  # photo
            file_type = 'image'
        elif '\u6587\u6863' in reference or 'document' in reference.lower():  # document
            file_type = 'document'
        
        return self.context.get_file_by_day(day_idx, file_type=file_type)
    
    def _fetch_order(self, day_idx: int, entity_id: str, 
                      reference: str) -> Optional[Dict[str, Any]]:
        """Get order info"""
        # 1. Check event chain (English and Chinese patterns)
        if entity_id == 'table' or '\u684c\u5b50' in reference or 'table' in reference.lower():  # table
            chain = self.context.get_event_chain('table_purchase')
            if chain:
                # Return the first (purchase) entry
                return chain[0].data
        
        if entity_id == 'egg' or '\u9e21\u86cb' in reference or 'egg' in reference.lower():  # egg
            chain = self.context.get_event_chain('egg_purchase')
            if chain:
                return chain[0].data
        
        # 2. Retrieve from day_state
        orders = self.context.get_orders_by_day(day_idx)
        
        # Filter based on quoted text
        for order in orders:
            name = order.get('name', '').lower()
            if ('table' in reference or 'table' in reference.lower()) and 'table' in name:  # table
                return order
            if ('egg' in reference or 'egg' in reference.lower()) and 'egg' in name:  # egg
                return order
        
        # Return the first order
        return orders[0] if orders else None
    
    def _fetch_recipe(self, day_idx: int, entity_id: str, 
                       reference: str) -> Optional[Dict[str, Any]]:
        """getrecipeinfo"""
        # 1. Check for the "just now" / "latest" recipe (just now / latest in Chinese)
        if '\u521a\u624d' in reference or '\u521a\u521a' in reference or 'just' in reference.lower() or 'latest' in reference.lower():
            return self.context.get('latest_recipe')
        
        # 2. Retrieve from day_state
        day_state = self.context.get_day_state(day_idx)
        if day_state and day_state.recipes:
            return day_state.recipes[-1]  # Return the latest one
        
        return None
    
    def _fetch_expense(self, day_idx: int, entity_id: str, 
                        reference: str) -> List[Dict[str, Any]]:
        """Get expense records"""
        # Check whether there is a category filter (English and Chinese patterns)
        category = None
        if ('dining' in reference or 'dining' in reference.lower()):  # dining
            category = 'dining'
        elif ('shopping' in reference or 'shopping' in reference.lower()):  # shopping
            category = 'shopping'
        
        return self.context.get_expenses_by_day(day_idx, category)
    
    def _fetch_exercise(self, day_idx: int, entity_id: str, 
                         reference: str) -> Optional[Dict[str, Any]]:
        """Get exercise records"""
        day_state = self.context.get_day_state(day_idx)
        if day_state and day_state.exercise_records:
            return day_state.exercise_records[-1]
        
        return None
    
    def _calculate_confidence(self, day_idx: int, entity_type: str, 
                               entity_id: str, resolved_data: Any) -> float:
        """
        Calculate parse confidence score
        
        Args:
            day_idx: number of days parsed
            entity_type: entity type
            entity_id: entity ID
            resolved_data: parsed data
            
        Returns:
            Confidence score (0.0–1.0)
        """
        confidence = 0.0
        
        # Base score: data successfully parsed
        if resolved_data is not None:
            confidence += 0.5
        
        # Bonus score: explicit entity type provided
        if entity_type is not None:
            confidence += 0.2
        
        # Bonus score: explicit entity ID provided
        if entity_id is not None:
            confidence += 0.2
        
        # Bonus score: data is non-empty
        if resolved_data:
            if isinstance(resolved_data, list) and len(resolved_data) > 0:
                confidence += 0.1
            elif isinstance(resolved_data, dict) and resolved_data:
                confidence += 0.1
        
        return min(1.0, confidence)
    
    # ==================== Helper methods ====================
    
    def get_supported_patterns(self) -> Dict[str, List[str]]:
        """Get all supported modes (for debugging)"""
        return {
            'relative_time': list(self.RELATIVE_TIME_PATTERNS.keys()),
            'weekday': list(self.WEEKDAY_PATTERNS.keys()),
            'ordinal': list(self.ORDINAL_PATTERNS.keys()),
            'entity': list(self.ENTITY_PATTERNS.keys()),
        }
    
    def test_resolve(self, reference: str, current_day: int = 0) -> str:
        """
        Test parsing (return a human-readable result string)
        
        Args:
            reference: quoted text
            current_day: current day
            
        Returns:
            String description of the parseresult
        """
        result = self.resolve(reference, current_day)
        
        if result.success:
            return (
                f"✅ Resolved: '{reference}'\n"
                f"   Day: {result.day_idx} ({self.context.DAY_NAMES[result.day_idx] if result.day_idx is not None else 'N/A'})\n"
                f"   Type: {result.entity_type}\n"
                f"   ID: {result.entity_id}\n"
                f"   Data: {result.resolved_data}\n"
                f"   Confidence: {result.confidence:.2f}"
            )
        else:
            return (
                f"❌ Failed to resolve: '{reference}'\n"
                f"   Day: {result.day_idx}\n"
                f"   Type: {result.entity_type}\n"
                f"   Confidence: {result.confidence:.2f}"
            )
