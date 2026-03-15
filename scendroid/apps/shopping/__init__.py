"""
Shopping App Module

Shopping app-related evaluator (WebArena Shopping task):

Core Shopping evaluator:
1. LayeredShoppingPurchaseProduct - Purchase a product (by SKU)
2. LayeredShoppingStringMatch - String match (information retrieval)
3. LayeredShoppingReorder - Reorder a previously canceled order
4. LayeredShoppingConstrainedPurchase - Constrained purchase
5. LayeredShoppingNewsletter - Subscribe to newsletter
6. LayeredShoppingContactUs - Contact customer support (for refunds)
7. LayeredShoppingUpdateAddress - update address
8. LayeredShoppingAddressAndOrder - Update address and purchase

Note: These evaluators use the Chrome browser and the WebArena framework
"""

from scendroid.apps.registry import AppRegistry

# auto-load evaluators
from . import evaluators

__all__ = ['evaluators']

