"""
Scenario Context

scenariocontext: Manages status and data sharing across tasks. 
"""

import time
from typing import Any, Dict, List, Optional
from absl import logging


class ScenarioContext:
    """
    scenariocontext: Manages status and data across tasks
    
    Features: 
    1. Stores data shared across tasks (e.g., created meetings, contacts, etc.)
    2. Records task execution history
    3. Provides a parameter passing mechanism
    4. Supports condition evaluation and branching logic
    
    usage example:
        context = ScenarioContext()
        context.set('meeting_title', 'Team Meeting')
        title = context.get('meeting_title')
        
        context.add_subtask_result(1, 1.0, {'details': 'success'})
        result = context.get_previous_result(1)
    """
    
    def __init__(self):
        # Shared status storage
        self.shared_data: Dict[str, Any] = {}
        
        # taskexecutehistory
        self.subtask_history: List[Dict[str, Any]] = []
        
        # Current task index
        self.current_subtask_idx: int = 0
        
        # Scenario metadata
        self.scenario_id: Optional[str] = None
        self.scenario_name: Optional[str] = None
        self.base_date: Optional[str] = None
        
        # Scenario start time
        self.start_time: float = time.time()
    
    def set(self, key: str, value: Any):
        """
        Setup shared data
        
        Args:
            key: Data key
            value: Data value
        """
        self.shared_data[key] = value
        logging.info(f"Context: Set '{key}' = {value}")
    
    def get(self, key: str, default=None) -> Any:
        """
        Get shared data
        
        Args:
            key: Data key
            default: default value
            
        Returns:
            Data value; returns the default value if it does not exist
        """
        return self.shared_data.get(key, default)
    
    def has(self, key: str) -> bool:
        """
        Check whether data exists
        
        Args:
            key: Data key
            
        Returns:
            bool: Whether the data exists
        """
        return key in self.shared_data
    
    def add_subtask_result(self, subtask_id: int, score: float, details: Dict[str, Any]):
        """
        Record subtask result
        
        Args:
            subtask_id: Subtask ID
            score: Evaluation score (0.0 - 1.0)
            details: Detailed information
        """
        result = {
            'subtask_id': subtask_id,
            'score': score,
            'details': details,
            'timestamp': time.time(),
            'elapsed_time': time.time() - self.start_time,
        }
        self.subtask_history.append(result)
        
        logging.info(f"Context: Recorded result for subtask {subtask_id}: score={score:.2f}")
    
    def get_previous_result(self, subtask_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get the previous task's result
        
        Args:
            subtask_id: Subtask ID; if None, return the most recent result
            
        Returns:
            Task result dictionary; returns None if it does not exist
        """
        if not self.subtask_history:
            return None
        
        if subtask_id is None:
            # Return the most recent result
            return self.subtask_history[-1]
        
        # Find the result with the specified ID (search backward, return the most recent one)
        for result in reversed(self.subtask_history):
            if result['subtask_id'] == subtask_id:
                return result
        
        return None
    
    def get_all_results(self) -> List[Dict[str, Any]]:
        """
        Get all subtask results
        
        Returns:
            List of all subtask results
        """
        return self.subtask_history.copy()
    
    def get_passed_count(self, threshold: float = 0.99) -> int:
        """
        Get the count of passed subtasks
        
        Args:
            threshold: Passing score threshold, default is 0.99
            
        Returns:
            int: Count of passed subtasks
        """
        return sum(1 for result in self.subtask_history if result['score'] >= threshold)
    
    def get_average_score(self) -> float:
        """
        Get the average score
        
        Returns:
            float: Average score (0.0 - 1.0)
        """
        if not self.subtask_history:
            return 0.0
        
        total = sum(result['score'] for result in self.subtask_history)
        return total / len(self.subtask_history)
    
    def clear(self):
        """Clear all data"""
        self.shared_data.clear()
        self.subtask_history.clear()
        self.current_subtask_idx = 0
        logging.info("Context: Cleared all data")
    
    def __repr__(self) -> str:
        return (
            f"ScenarioContext("
            f"scenario='{self.scenario_name}', "
            f"subtasks={len(self.subtask_history)}, "
            f"passed={self.get_passed_count()}"
            f")"
        )

