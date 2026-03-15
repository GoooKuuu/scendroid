"""
CrossApp Base Classes

Provides the base class and common functionality for the CrossApp evaluator.
"""

from absl import logging
from typing import List, Tuple

from scendroid.apps.base import BaseAppEvaluator


class BaseCrossAppEvaluator(BaseAppEvaluator):
    """
    Base class for the CrossApp evaluator
    
    core features:
    1. Manages multiple sub-evaluators
    2. Coordinates the initialization order
    3. Aggregates evaluation results
    4. Supports weighted scoring
    
    usage:
    - Composite type: Directly adds existing app evaluators as sub-evaluators
    - Collaborative type: Overrides the initialize_task and evaluate methods, reusing app utilities
    - Question-answering type: Overrides the evaluate method to check the agent's answer
    """
    
    def __init__(self, params: dict):
        super().__init__(params)
        # List of sub-evaluators: [(evaluator_instance, weight), ...]
        self.sub_evaluators: List[Tuple[BaseAppEvaluator, float]] = []
    
    def add_sub_evaluator(
        self, 
        evaluator_class, 
        params: dict, 
        weight: float = 1.0
    ):
        """
        Adds a sub-evaluator
        
        Args:
            evaluator_class: Evaluator class (from the App Layer)
            params: evaluatorparameter
            weight: Weight (used for weighted averaging)
        """
        evaluator = evaluator_class(params)
        self.sub_evaluators.append((evaluator, weight))
        logging.info(f"Added sub-evaluator: {evaluator.name} (weight: {weight})")
    
    def initialize_task(self, env):
        """
        Initializes all sub-evaluators in order
        
        Subclasses can override this method to implement custom initialization logic
        """
        super().initialize_task(env)
        
        if self.sub_evaluators:
            logging.info(f"Initializing {len(self.sub_evaluators)} sub-evaluators...")
            for evaluator, _ in self.sub_evaluators:
                logging.info(f"  → Initializing {evaluator.name}...")
                evaluator.initialize_task(env)
    
    def evaluate(self, env) -> float:
        """
        Aggregates evaluation results from all sub-evaluators
        
        Returns 0.0 if there are no sub-evaluators (subclasses should override this method)
        
        Returns:
            Weighted average score (0.0–1.0)
        """
        if not self.sub_evaluators:
            logging.warning("No sub-evaluators found, returning 0.0")
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        logging.warning("=" * 60)
        logging.warning(f"📊 Evaluating CrossApp Task: {self.name}")
        logging.warning("=" * 60)
        
        for evaluator, weight in self.sub_evaluators:
            logging.info(f"  → Evaluating {evaluator.name} (weight: {weight})...")
            score = evaluator.evaluate(env)
            weighted_score = score * weight
            total_score += weighted_score
            total_weight += weight
            
            logging.warning(f"  {evaluator.name}: {score:.2f} × {weight} = {weighted_score:.2f}")
        
        final_score = total_score / total_weight if total_weight > 0 else 0.0
        
        logging.warning("=" * 60)
        logging.warning(f"📊 Final Score: {final_score:.2f}")
        logging.warning("=" * 60)
        
        return final_score
    
    def tear_down(self, env):
        """
        Cleans up all sub-evaluators in order
        
        Subclasses can override this method to implement custom cleanup logic
        """
        if self.sub_evaluators:
            logging.info(f"Tearing down {len(self.sub_evaluators)} sub-evaluators...")
            for evaluator, _ in self.sub_evaluators:
                logging.info(f"  → Tearing down {evaluator.name}...")
                evaluator.tear_down(env)
        
        super().tear_down(env)

