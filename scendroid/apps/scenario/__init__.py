"""
Scenario Module

Scenario module, responsible for orchestrating and managing multi-task sequences. 

Implemented scenarios: 

=== 1-day scenarios (5) ===
A. ScenarioA_BusyMonday - Busy Monday (10 subtasks) - Workday scenario
B. ScenarioB_RelaxedSaturday - Relaxed Saturday (10 subtasks) - Weekend relaxation scenario
C. ScenarioC_StudentResearchDay - Student Research Day (10 subtasks) - Student seminar day scenario
D. ScenarioD_TechConferenceTrip - Tech Conference Trip (10 subtasks) - Business trip scenario
E. ScenarioE_WeekendHiking - Weekend Hiking & Photography (10 subtasks) - Outdoor hiking scenario

=== 7-day scenarios (2) ===
W. ScenarioW_WeeklyWork - Weekly Work (70 subtasks) - 7-day workweek scenario
   - Core test capabilities: coreference resolution [REF], causal consistency [CAU], preference alignment [PRE], 
                   proactive alignment [ALT], spatiotemporal contradictions [CON], data aggregation [AGG], structured extraction [STR]

OmniLife. ScenarioOmniLife_7Day - OmniLife 7-Day Complete Life (72 subtasks)
   - Solution designed based on OmniLife-7D.md
   - Integrates scenarios a/b/c/d/e and enhances preference constraints and multi-meeting tracking
   - Core capabilities: cross-day referencing [REF], preference learning [PRE], conflict detection [CON], budget constraints [PRE]

Design principles: 
- Reuse evaluators from the App Layer and Cross-App Layer
- Provide temporal orchestration and status-sharing capabilities
- Support weighted scoring and result aggregation
- Simulate realistic usage scenarios
- Each scenario resides in an independent file, facilitating maintenance and extension
- 7-day scenarios support cross-day status persistence and preference acquisition
"""

from scendroid.apps.registry import AppRegistry

# Automatically load 1-day scenario evaluators
from . import scenario_a
from . import scenario_b
from . import scenario_c
from . import scenario_d
from . import scenario_e

# Automatically load 7-day scenario evaluators
from . import scenario_w
from . import scenario_omnilife

# Export 7-day scenario base components
from .extended_context import ExtendedScenarioContext
from .preference_store import PreferenceStore
from .reference_resolver import ReferenceResolver
from .seven_day_base import SevenDayScenarioEvaluator

__all__ = [
    # 1 daysscenario
    'scenario_a', 'scenario_b', 'scenario_c', 'scenario_d', 'scenario_e',
    # 7 daysscenario
    'scenario_w', 'scenario_omnilife',
    # Base components
    'base', 'context', 'utils',
    # 7-day scenario components
    'extended_context', 'preference_store', 'reference_resolver', 'seven_day_base',
    # Class exports
    'ExtendedScenarioContext', 'PreferenceStore', 'ReferenceResolver', 'SevenDayScenarioEvaluator',
]
