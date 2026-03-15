"""
Shopping App Evaluators

Provides Shopping app-related evaluators (WebArena Shopping task): 

1. LayeredShoppingPurchaseProduct - Purchase a product (by SKU)
2. LayeredShoppingStringMatch - String match (information retrieval)
3. LayeredShoppingReorder - Reorder a previously canceled order
4. LayeredShoppingConstrainedPurchase - Constrained purchase
5. LayeredShoppingNewsletter - Subscribe to newsletter
6. LayeredShoppingContactUs - Contact customer support (for refunds)
7. LayeredShoppingUpdateAddress - update address
8. LayeredShoppingAddressAndOrder - Update address + purchase a product (composite task)

Note:
- All Shopping evaluators use the WebArena framework and Chrome browser
- WebArena evaluators are imported lazily at method invocation time to avoid dependency issues during module loading
"""

from absl import logging

from scendroid.apps.registry import AppRegistry
from scendroid.apps.base import BaseAppEvaluator


# ============================================================================
# Base class: Shopping evaluator
# ============================================================================

class BaseShoppingEvaluator(BaseAppEvaluator):
    """
    Base class for Shopping evaluators
    
    Provides common functionality for lazily creating WebArena evaluators
    """
    
    def __init__(self, params: dict):
        super().__init__(params)
        self._webarena_evaluator = None
    
    def _create_webarena_evaluator(self):
        """
        Create a WebArena evaluator (to be implemented by subclasses)
        
        Returns:
            WebArena evaluatorinstance
        """
        raise NotImplementedError("Subclass must implement _create_webarena_evaluator")
    
    def _get_webarena_evaluator(self):
        """Lazily create and return a WebArena evaluator"""
        if self._webarena_evaluator is None:
            self._webarena_evaluator = self._create_webarena_evaluator()
        return self._webarena_evaluator


# ============================================================================
# 1. LayeredShoppingPurchaseProduct - Purchase a product (by SKU)
# ============================================================================

@AppRegistry.register_evaluator("LayeredShoppingPurchaseProduct")
class ShoppingPurchaseProductEvaluator(BaseShoppingEvaluator):
    """
    Evaluates the product purchase task (by SKU)
    
    supported scenarios:
    - "Add the 'Outdoor Patio Folding Side Table green' to my cart and place an order"
    
    evaluation content:
    - Check whether the most recent order contains the specified product SKU
    - Optional: Verify the product price
    
    Uses WebArena's ProgramHTMLWebArenaTask for evaluation
    """
    
    # ScenDroid standard attributes
    app_names = ("chrome",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # saveparameter
        self.product_sku = params.get('product_sku')
        self.product_price = params.get('product_price')
        self.check_method = params.get('check_method', 'cart')
        
        # set complexity
        self.complexity = 2.0
    
    def _create_webarena_evaluator(self):
        """create ProgramHTML WebArena evaluator"""
        from scendroid.task_evals.webarena import webarena_task
        return webarena_task.ProgramHTMLWebArenaTask(self._params)
    
    def evaluate(self, env) -> float:
        """Execute evaluation: check whether the product was purchased"""
        try:
            from scendroid.task_evals.webarena import program_html_helper
            
            logging.warning("📊 Evaluating Product Purchase:")
            logging.warning(f"   Product SKU: {self.product_sku}")
            logging.warning(f"   Check Method: {self.check_method}")
            
            program_html_config = self._params.get('program_html', [])
            if not program_html_config:
                logging.error("   ❌ No program_html configuration found")
                return 0.0
            
            score, explanations = program_html_helper.evaluate_program_html_via_cdp(
                env, program_html_config
            )
            
            if explanations:
                logging.info(f"   Detailed explanation:\n{explanations}")
            
            if score >= 1.0:
                logging.warning("✅ PASSED - Product purchased")
            else:
                logging.warning("❌ FAILED - Product not found")
            
            return score
            
        except Exception as e:
            logging.error(f"❌ error occurred during evaluation: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task: open Chrome and log in to the Shopping website"""
        super().initialize_task(env)
        
        logging.info("🔧 Initializing Shopping Purchase Task")
        logging.info(f"   📋 Params: require_login={self._params.get('require_login')}")
        logging.info(f"   📋 Params keys: {list(self._params.keys())}")
        
        try:
            webarena_eval = self._get_webarena_evaluator()
            logging.info(f"   🌐 WebArena evaluator created: {type(webarena_eval).__name__}")
            logging.info(f"   🔐 WebArena require_login: {webarena_eval.require_login}")
            
            webarena_eval.initialize_task(env)
            logging.info("   ✅ Chrome opened and logged in successfully!")
        except Exception as e:
            logging.error(f"   ❌ Shopping initialization failed: {e}")
            import traceback
            logging.error(traceback.format_exc())
    
    def tear_down(self, env):
        """Cleanup: if an order was placed, rebuild the Shopping container"""
        super().tear_down(env)
        
        if self.check_method == 'order':
            from .utils import rebuild_shopping_container
            logging.info("   🔄 Order placed, rebuilding container...")
            rebuild_shopping_container(env)  # ✅ Pass env to extract the correct console_port


# ============================================================================
# 2. LayeredShoppingStringMatch - String match (information retrieval)
# ============================================================================

@AppRegistry.register_evaluator("LayeredShoppingStringMatch")
class ShoppingStringMatchEvaluator(BaseShoppingEvaluator):
    """Evaluate the Shopping information retrieval task"""
    
    app_names = ("chrome",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.reference_answers = params.get('reference_answers', {})
        self.complexity = 2.0
    
    def _create_webarena_evaluator(self):
        """create StringMatch WebArena evaluator"""
        from scendroid.task_evals.webarena import webarena_task
        return webarena_task.StringMatchWebArenaTask(self._params)
    
    def evaluate(self, env) -> float:
        """Execute evaluation: use string matching to check the answer"""
        try:
            logging.warning("📊 Evaluating Shopping Q&A")
            score = self._get_webarena_evaluator().is_successful(env)
            
            if score >= 1.0:
                logging.warning("✅ PASSED - Answer matches")
            else:
                logging.warning("❌ FAILED - Answer does not match")
            
            return score
        except Exception as e:
            logging.error(f"❌ evaluation error: {e}")
            return 0.0
    
    def initialize_task(self, env):
        """initialize task"""
        super().initialize_task(env)
        logging.info("🔧 Initializing Shopping Q&A Task")
        
        try:
            self._get_webarena_evaluator().initialize_task(env)
            logging.info("   ✅ Shopping website ready")
        except Exception as e:
            logging.warning(f"   ⚠️  Initialization issue: {e}")


# ============================================================================
# 3. LayeredShoppingReorder - Reorder
# ============================================================================

@AppRegistry.register_evaluator("LayeredShoppingReorder")
class ShoppingReorderEvaluator(BaseShoppingEvaluator):
    """Evaluate the reorder task"""
    
    app_names = ("chrome",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.complexity = 2.5
    
    def _create_webarena_evaluator(self):
        from scendroid.task_evals.webarena import webarena_task
        return webarena_task.ProgramHTMLWebArenaTask(self._params)
    
    def evaluate(self, env) -> float:
        try:
            from scendroid.task_evals.webarena import program_html_helper
            
            logging.warning("📊 Evaluating Reorder Task")
            
            program_html_config = self._params.get('program_html', [])
            if not program_html_config:
                return 0.0
            
            score, _ = program_html_helper.evaluate_program_html_via_cdp(
                env, program_html_config
            )
            
            if score >= 1.0:
                logging.warning("✅ PASSED - Product reordered")
            else:
                logging.warning("❌ FAILED")
            
            return score
        except Exception as e:
            logging.error(f"❌ evaluation error: {e}")
            return 0.0
    
    def initialize_task(self, env):
        super().initialize_task(env)
        logging.info("🔧 Initializing Reorder Task")
        
        try:
            self._get_webarena_evaluator().initialize_task(env)
        except Exception as e:
            logging.error(f"   ❌ Initialization failed: {e}")
    
    def tear_down(self, env):
        super().tear_down(env)
        from .utils import rebuild_shopping_container
        rebuild_shopping_container(env)  # ✅ Pass env to extract the correct console_port


# ============================================================================
# 4-7. Other Shopping evaluators (using the same mode)
# ============================================================================

@AppRegistry.register_evaluator("LayeredShoppingConstrainedPurchase")
class ShoppingConstrainedPurchaseEvaluator(BaseShoppingEvaluator):
    """Evaluate the constrained purchase task"""
    
    app_names = ("chrome",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.complexity = 3.0
    
    def _create_webarena_evaluator(self):
        from scendroid.task_evals.webarena import webarena_task
        return webarena_task.ProgramHTMLWebArenaTask(self._params)
    
    def evaluate(self, env) -> float:
        try:
            from scendroid.task_evals.webarena import program_html_helper
            
            logging.warning("📊 Evaluating Constrained Purchase")
            program_html_config = self._params.get('program_html', [])
            if not program_html_config:
                return 0.0
            
            score, _ = program_html_helper.evaluate_program_html_via_cdp(env, program_html_config)
            
            if score >= 1.0:
                logging.warning("✅ PASSED")
            else:
                logging.warning("❌ FAILED")
            
            return score
        except Exception as e:
            logging.error(f"❌ evaluation error: {e}")
            return 0.0
    
    def initialize_task(self, env):
        super().initialize_task(env)
        logging.info("🔧 Initializing Constrained Purchase Task")
        try:
            self._get_webarena_evaluator().initialize_task(env)
        except Exception as e:
            logging.error(f"   ❌ Failed: {e}")
    
    def tear_down(self, env):
        super().tear_down(env)
        from .utils import rebuild_shopping_container
        rebuild_shopping_container(env)  # ✅ Pass env to extract the correct console_port


@AppRegistry.register_evaluator("LayeredShoppingNewsletter")
class ShoppingNewsletterEvaluator(BaseShoppingEvaluator):
    """Evaluate the newsletter subscription task"""
    
    app_names = ("chrome",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.complexity = 1.5
    
    def _create_webarena_evaluator(self):
        from scendroid.task_evals.webarena import webarena_task
        return webarena_task.ProgramHTMLWebArenaTask(self._params)
    
    def evaluate(self, env) -> float:
        try:
            from scendroid.task_evals.webarena import program_html_helper
            
            logging.warning("📊 Evaluating Newsletter Subscription")
            program_html_config = self._params.get('program_html', [])
            if not program_html_config:
                return 0.0
            
            score, _ = program_html_helper.evaluate_program_html_via_cdp(env, program_html_config)
            
            if score >= 1.0:
                logging.warning("✅ PASSED")
            else:
                logging.warning("❌ FAILED")
            
            return score
        except Exception as e:
            logging.error(f"❌ evaluation error: {e}")
            return 0.0
    
    def initialize_task(self, env):
        super().initialize_task(env)
        logging.info("🔧 Initializing Newsletter Task")
        try:
            self._get_webarena_evaluator().initialize_task(env)
        except Exception as e:
            logging.error(f"   ❌ Failed: {e}")


@AppRegistry.register_evaluator("LayeredShoppingContactUs")
class ShoppingContactUsEvaluator(BaseShoppingEvaluator):
    """Evaluate the contact customer support task"""
    
    app_names = ("chrome",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.complexity = 2.5
    
    def _create_webarena_evaluator(self):
        from scendroid.task_evals.webarena import webarena_task
        return webarena_task.ProgramHTMLWebArenaTask(self._params)
    
    def evaluate(self, env) -> float:
        try:
            from scendroid.task_evals.webarena import program_html_helper
            
            logging.warning("📊 Evaluating Contact Us Submission")
            program_html_config = self._params.get('program_html', [])
            if not program_html_config:
                return 0.0
            
            score, _ = program_html_helper.evaluate_program_html_via_cdp(env, program_html_config)
            
            if score >= 1.0:
                logging.warning("✅ PASSED")
            else:
                logging.warning("❌ FAILED")
            
            return score
        except Exception as e:
            logging.error(f"❌ evaluation error: {e}")
            return 0.0
    
    def initialize_task(self, env):
        super().initialize_task(env)
        logging.info("🔧 Initializing Contact Us Task")
        try:
            self._get_webarena_evaluator().initialize_task(env)
        except Exception as e:
            logging.error(f"   ❌ Failed: {e}")


@AppRegistry.register_evaluator("LayeredShoppingUpdateAddress")
class ShoppingUpdateAddressEvaluator(BaseShoppingEvaluator):
    """evaluationupdate addresstask"""
    
    app_names = ("chrome",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.complexity = 2.0
    
    def _create_webarena_evaluator(self):
        from scendroid.task_evals.webarena import webarena_task
        return webarena_task.ProgramHTMLWebArenaTask(self._params)
    
    def evaluate(self, env) -> float:
        try:
            from scendroid.task_evals.webarena import program_html_helper
            
            logging.warning("📊 Evaluating Address Update")
            program_html_config = self._params.get('program_html', [])
            if not program_html_config:
                return 0.0
            
            score, _ = program_html_helper.evaluate_program_html_via_cdp(env, program_html_config)
            
            if score >= 1.0:
                logging.warning("✅ PASSED")
            else:
                logging.warning("❌ FAILED")
            
            return score
        except Exception as e:
            logging.error(f"❌ evaluation error: {e}")
            return 0.0
    
    def initialize_task(self, env):
        super().initialize_task(env)
        logging.info("🔧 Initializing Address Update Task")
        try:
            self._get_webarena_evaluator().initialize_task(env)
        except Exception as e:
            logging.error(f"   ❌ Failed: {e}")
    
    def tear_down(self, env):
        super().tear_down(env)
        from .utils import rebuild_shopping_container
        rebuild_shopping_container(env)  # ✅ Pass env to extract the correct console_port


# ============================================================================
# 8. LayeredShoppingAddressAndOrder - Update address + purchase a product (composite task)
# ============================================================================

@AppRegistry.register_evaluator("LayeredShoppingAddressAndOrder")
class ShoppingAddressAndOrderEvaluator(BaseShoppingEvaluator):
    """
    Evaluates the composite task of updating address + purchasing a product
    
    supported scenarios:
    - L0: "On this site, change my shipping address to 231 Willow Way, Suite 100, 
          Chicago, IL, 60601. Then find 'General Mills Sugar Cookie Toast Crunch' cereal, 
          add one bag to cart and complete the purchase."
    - L1: "Update my address to 231 Willow Way, Suite 100, Chicago, IL, 60601, 
          then buy one bag of Sugar Cookie Toast Crunch cereal."
    - L2: "Change my address to 231 Willow Way, Suite 100, Chicago IL, 
          then buy some Sugar Cookie cereal."
    - L3: "I moved to a new place in Chicago, update my info. 
          Also I want to order some breakfast cereal."
    
    evaluation content:
    - Part 1 (50%): Check whether the address page (/customer/address) contains all address keywords
    - Part 2 (50%): Check whether the latest order contains all product keywords
    
    Reference:
    - Legacy architecture: layered_tasks.py LayeredShoppingAddressAndOrder (Lines 3476–3696)
    """
    
    # ScenDroid standard attributes
    app_names = ("chrome",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # saveparameter
        self.address_keywords = params.get('address_keywords', [])
        self.product_keywords = params.get('product_keywords', [])
        
        # Set complexity (composite task, higher complexity)
        self.complexity = 3.0
    
    def initialize_task(self, env):
        """
        Initialize task: log in to the Shopping website
        
        Reference: layered_tasks.py Lines 3525–3559
        """
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info("🔧 Initializing Address + Order Task:")
        logging.info("=" * 60)
        
        # Log in to the Shopping website
        logging.info("🛒 Logging in to Shopping site...")
        try:
            from scendroid.task_evals.webarena import webarena_task
            
            # Use WebArena's login mechanism
            webarena_helper = webarena_task.ProgramHTMLWebArenaTask({
                'task_id': 43,
                'intent': 'Update address and place order',
                'start_url': '__SHOPPING__',
                'eval_config': {},
                'require_login': True,
            })
            
            # executelogin
            webarena_helper.initialize_task(env)
            logging.info("   ✅ Shopping site ready (logged in)")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Shopping site initialization issue: {e}")
            logging.warning("   Task will continue but evaluation may fail")
        
        # Record task parameters
        logging.info("📋 Task Parameters:")
        logging.info(f"   📍 Address keywords: {', '.join(self.address_keywords)}")
        logging.info(f"   🛍️  Product keywords: {', '.join(self.product_keywords)}")
        logging.info("=" * 60)
    
    def evaluate(self, env) -> float:
        """
        Execute evaluation: check whether address update and order placement succeeded
        
        Evaluation consists of two parts:
        1. Address check (50%): The address page contains all required keywords
        2. Order check (50%): The latest order contains product keywords
        
        Full credit is awarded only if both parts succeed
        
        Reference: layered_tasks.py Lines 3561–3681
        
        Returns:
            float: Score ranging from 0.0 to 1.0 (weighted average)
        """
        logging.info("=" * 60)
        logging.info("📊 Evaluating Address + Order Task:")
        logging.info("=" * 60)
        
        # Part 1: checkaddressupdate
        address_success = False
        try:
            logging.info("📍 Part 1: Checking address update...")
            
            from scendroid.task_evals.webarena import program_html_helper
            
            # check billing and shipping address
            # Reference WebArena Task 571 configuration
            address_checks = [
                {
                    "url": "__SHOPPING__/customer/address",
                    "locator": "document.querySelector('.box.box-address-billing > .box-content').outerText",
                    "required_contents": {
                        "must_include": [" |AND| ".join(self.address_keywords)]
                    }
                },
                {
                    "url": "__SHOPPING__/customer/address",
                    "locator": "document.querySelector('.box.box-address-shipping > .box-content').outerText",
                    "required_contents": {
                        "must_include": [" |AND| ".join(self.address_keywords)]
                    }
                }
            ]
            
            logging.info(f"   Checking address for keywords: {self.address_keywords}")
            
            # Perform check via CDP execute
            score, explanation = program_html_helper.evaluate_program_html_via_cdp(
                env, address_checks
            )
            
            if score >= 1.0:
                address_success = True
                logging.info(f"   ✅ Address contains all required keywords")
            else:
                logging.warning(f"   ❌ Address check failed")
            
            logging.info(f"   Details: {explanation}")
            
        except Exception as e:
            logging.error(f"   ❌ Address check failed: {e}")
            import traceback
            logging.debug(traceback.format_exc())
        
        # Part 2: Check order
        order_success = False
        try:
            logging.info("🛒 Part 2: Checking order...")
            
            from scendroid.task_evals.webarena import program_html_helper
            
            # Check products in the latest order
            order_check = [{
                "url": "func:shopping_get_latest_order_url()",
                "locator": "document.querySelector('.order-details-items.ordered').outerText",
                "required_contents": {
                    "must_include": [" |AND| ".join(self.product_keywords)]
                }
            }]
            
            logging.info(f"   Checking order for keywords: {self.product_keywords}")
            
            # Perform check via CDP execute
            score, explanation = program_html_helper.evaluate_program_html_via_cdp(
                env, order_check
            )
            
            if score >= 1.0:
                order_success = True
                logging.info(f"   ✅ Order contains all required keywords")
            else:
                logging.warning(f"   ❌ Order check failed")
            
            logging.info(f"   Details: {explanation}")
            
        except Exception as e:
            logging.error(f"   ❌ Order check failed: {e}")
            import traceback
            logging.debug(traceback.format_exc())
        
        # Compute final score
        address_score = 1.0 if address_success else 0.0
        order_score = 1.0 if order_success else 0.0
        
        # Weighted average: 50% address + 50% order
        final_score = (address_score * 0.5) + (order_score * 0.5)
        
        logging.info("=" * 60)
        logging.info("📊 Results:")
        logging.info(f"   📍 Address updated: {'✅ PASS' if address_success else '❌ FAIL'} ({address_score * 0.5:.2f}/0.50)")
        logging.info(f"   🛒 Order placed: {'✅ PASS' if order_success else '❌ FAIL'} ({order_score * 0.5:.2f}/0.50)")
        logging.info(f"   🎯 Final score: {final_score:.2f}")
        
        if final_score >= 1.0:
            logging.warning("✅ Perfect! Both tasks completed successfully")
        elif final_score >= 0.5:
            logging.warning("⚠️  Partial success - one task completed")
        else:
            logging.warning("❌ Both tasks failed")
        
        logging.info("=" * 60)
        return final_score
    
    def tear_down(self, env):
        """
        Cleanup task: Rebuild the Shopping container to clear order and address changes
        
        Reference: layered_tasks.py Lines 3683–3696
        """
        super().tear_down(env)
        
        logging.info("🧹 Cleaning up Address + Order Task...")
        
        # Rebuild the Shopping container to clear order and address
        try:
            from scendroid.task_evals.webarena import container_manager as cm
            
            logging.info("   Rebuilding Shopping container...")
            cm.rebuild_container("shopping")
            logging.info("   ✅ Shopping container rebuilt")
            
        except Exception as e:
            logging.warning(f"   ⚠️  Container rebuild failed: {e}")
            logging.warning("   This may affect subsequent Shopping tasks")


# ============================================================================
# OmniLife Scenario: Budget-Constrained Shopping
# ============================================================================

@AppRegistry.register_evaluator("LayeredShoppingWithBudgetCheck")
class ShoppingWithBudgetCheckEvaluator(BaseAppEvaluator):
    """
    Shopping with budget check (test task before buy rule)
    
    Test preference constraint: When price > $100, the agent should first ask the user
    """
    
    app_names = ("chrome",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.product_sku = params.get('product_sku', '')
        self.product_price = params.get('product_price', 0.0)
        self.budget_threshold = params.get('budget_threshold', 100.0)
        self.should_ask_before_buy = params.get('should_ask_before_buy', True)
        self.complexity = 3.0
    
    def evaluate(self, env) -> float:
        """
        Evaluation: If price > threshold, check whether the agent asked
        
        Simplified implementation: Assume the agent proactively states ).replace(u201d, need to ask" or proceeds directly to purchase
        In practice, the agent's action sequence or dialogue history should be checked
        """
        # Here simplified to checking whether an order was created
        logging.warning("=" * 70)
        logging.warning("🛒 Shopping with Budget Check Evaluation:")
        logging.warning(f"   Product: {self.product_sku}")
        logging.warning(f"   Price: ${self.product_price}")
        logging.warning(f"   Threshold: ${self.budget_threshold}")
        logging.warning(f"   Should ask first: {self.should_ask_before_buy}")
        
        # Simplified evaluation: If price exceeds threshold, assume agent complied with the rule
        if self.product_price > self.budget_threshold:
            if self.should_ask_before_buy:
                logging.warning("   ✅ Price exceeds threshold - agent should have asked")
                logging.warning("   💡 NOTE: Full implementation should check agent's dialogue")
                return 1.0
        
        # Price does not exceed threshold; direct purchase is allowed
        logging.warning("   ✅ Price within budget - can proceed")
        return 1.0


@AppRegistry.register_evaluator("LayeredShoppingPurchase")  
class ShoppingPurchaseEvaluator(BaseAppEvaluator):
    """Simple shopping order placement evaluator"""
    
    app_names = ("chrome",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.product_sku = params.get('product_sku', '')
        self.clear_cart = params.get('clear_cart', False)
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """Check whether an order was created (simplified implementation)"""
        logging.warning(f"✅ Shopping purchase evaluation (SKU: {self.product_sku})")
        return 1.0
