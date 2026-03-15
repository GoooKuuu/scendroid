"""
Base Classes for App Layer

Provides the base class for all app evaluators to ensure a unified interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from absl import logging


class BaseAppEvaluator(ABC):
    """
    Base class for all app evaluators
    
    This base class provides:
    1. A unified initialize interface
    2. A unified evaluation interface (compatible with ScenDroid TaskEval)
    3. Complexity management (used to dynamically set max_steps)
    4. Lifecycle management (initialize_task, evaluate, tear_down)
    
    Subclasses must implement:
    - evaluate(env) -> float: return a score between 0.0 and 1.0
    
    Subclasses may optionally implement:
    - initialize_task(env): initialize taskenvironment
    - tear_down(env): cleanuptaskenvironment
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        initializeevaluator
        
        Args:
            params: evaluation parameter dictionary, typically containing:
                - expected_state: the expected system status
                - complexity: task complexity (used to set max_steps)
                - other task-specific parameters
        """
        self.params = params
        self._params = params  # compatibility: some legacy code may use _params
        self.initialized = False
        
        # Extract common properties from params
        # complexity is used to dynamically set max_steps = 10 * complexity
        # Default complexity is 2.0, i.e., default max_steps = 20
        self.complexity = params.get('complexity', 2.0)
        
        # Subclasses can override complexity in __init__
        # e.g.: self.complexity = 1.5  # simple task
        #      self.complexity = 3.0  # complex task
        
        # name property (compatible with ScenDroid TaskEval)
        # Subclasses can set app_names at the class level or set name in __init__
        if not hasattr(self, 'name'):
            # Auto-generate name from class name (remove "Evaluator" suffix)
            class_name = self.__class__.__name__
            if class_name.endswith('Evaluator'):
                self.name = class_name[:-9]  # remove "Evaluator"
            else:
                self.name = class_name
    
    @abstractmethod
    def evaluate(self, env) -> float:
        """
        Execute evaluation (must be implemented by subclasses)
        
        Args:
            env: ScenDroid environment (interface.AsyncEnv)
        
        Returns:
            float: score, between 0.0 and 1.0
                  - 1.0 indicates complete success
                  - 0.0 indicates complete failure
                  - Values between 0.0 and 1.0 indicate partial success (if applicable)
        
        Note:
            - This method should be idempotent (multiple calls return the same result)
            - It should only check status and must not modify the system
            - It should produce detailed log output (using logging)
        """
        pass
    
    def is_successful(self, env) -> float:
        """
        Unified evaluation entry point (compatible with ScenDroid TaskEval interface)
        
        This method is called by run_layered_tui_test.py.
        It invokes the evaluate() method implemented by subclasses and handles exceptions.
        
        Args:
            env: ScenDroid environment
        
        Returns:
            float: score (0.0–1.0)
        """
        try:
            logging.info(f"startevaluation: {self.name}")
            score = self.evaluate(env)
            logging.info(f"Evaluation completed, score: {score}")
            
            # Ensure the return value is within a reasonable range
            if score < 0.0:
                logging.warning(f"Evaluator returned negative score: {score}, clamping to 0.0")
                score = 0.0
            elif score > 1.0:
                logging.warning(f"Evaluator returned score > 1.0: {score}, clamping to 1.0")
                score = 1.0
            
            return score
        except Exception as e:
            logging.error(f"Evaluation failed: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """
        Task initialization (optional implementation by subclasses)
        
        Called before task execution, used for:
        1. cleanupenvironment(cleardatabase, close appetc.)
        2. Set up the initial status (e.g., create test data, etc.)
        3. Open required applications
        
        Args:
            env: ScenDroid environment
        
        Note:
            - In Scenario mode, this method may not be called
              to avoid disrupting the environment status (multiple subtasks share the environment)
            - The default implementation simply sets initialized = True
            - Subclasses can override this method to implement custom initialization logic
        """
        self.initialized = True
        logging.debug(f"{self.__class__.__name__}: initialized")
    
    def tear_down(self, env):
        """
        cleanup_environment (optional implementation by subclasses)
        
        Called after task evaluation to:
        1. close app
        2. Clean up temporary data
        3. Restore the system status
        
        Args:
            env: ScenDroid environment
        
        Note:
            - The default implementation performs no action
            - Subclasses can override this method to implement custom cleanup logic
            - May not be called in Scenario mode (to avoid affecting subsequent subtasks)
        """
        logging.debug(f"{self.__class__.__name__}: tear_down")
    
    def __repr__(self):
        """Return a string representation of the evaluator"""
        return f"{self.__class__.__name__}(complexity={self.complexity})"


class BaseSetupFunction:
    """
    Base class for initialize functions (optional to use)
    
    Although an initialize function can be a regular function, wrapping it in a class provides:
    1. Better status management
    2. Reusable helper methods
    3. Clearer error handling
    
    This is an optional utility class, not mandatory.
    """
    
    def __init__(self, env):
        """
        initialize
        
        Args:
            env: ScenDroid environment
        """
        self.env = env
    
    @abstractmethod
    def setup(self, **kwargs) -> bool:
        """
        executeinitialize
        
        Args:
            **kwargs: initializeparameter
        
        Returns:
            bool: Whether the operation succeeded
        """
        pass
    
    def __call__(self, **kwargs) -> bool:
        """
        Enables the instance to be called like a function
        
        Example:
            setup_func = ClockSetupFunction(env)
            success = setup_func(hour=8, minute=0)
        """
        return self.setup(**kwargs)


# ============================================================================
# Helper functions
# ============================================================================

def validate_evaluator_params(params: Dict[str, Any], required_keys: list) -> bool:
    """
    Verify whether the evaluator parameter contains all required keys
    
    Args:
        params: parameterdictionary
        required_keys: List of required keys
    
    Returns:
        bool: Whether verification passed
    
    Example:
        if not validate_evaluator_params(params, ['alarm_time_hour', 'alarm_time_minute']):
            raise ValueError("Missing required parameters")
    """
    missing_keys = [key for key in required_keys if key not in params]
    
    if missing_keys:
        logging.error(f"❌ Missing required parameters: {missing_keys}")
        logging.error(f"   Provided params: {list(params.keys())}")
        return False
    
    return True


def log_evaluation_start(evaluator_name: str, expected_state: Dict[str, Any]):
    """
    Log a standard message indicating the start of evaluation
    
    Args:
        evaluator_name: evaluatorname
        expected_state: Expected status
    """
    logging.info(f"{'='*60}")
    logging.info(f"🔍 Evaluation Start: {evaluator_name}")
    logging.info(f"{'='*60}")
    logging.info(f"Expected State:")
    for key, value in expected_state.items():
        logging.info(f"   - {key}: {value}")


def log_evaluation_result(success: bool, score: float, details: str = ""):
    """
    Log a standard message indicating the evaluation result
    
    Args:
        success: Whether the operation succeeded (score >= 0.99)
        score: Evaluation score
        details: Detailed information
    """
    if success:
        logging.info(f"✅ Evaluation PASSED")
    else:
        logging.warning(f"❌ Evaluation FAILED")
    
    logging.info(f"   Score: {score:.2f}")
    
    if details:
        logging.info(f"   Details: {details}")
    
    logging.info(f"{'='*60}")

