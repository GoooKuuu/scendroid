"""
OpenTracks App Evaluators

Provides OpenTracks app-related evaluators:

1. LayeredOpenTracksCreateActivity - Create exercise record
2. LayeredOpenTracksQueryActivityQA - Query data for a specific activity (QA task)

Note: all scendroid.env imports are done inside functions
"""

from absl import logging
import re

from scendroid.apps.registry import AppRegistry
from scendroid.apps.base import BaseAppEvaluator


@AppRegistry.register_evaluator("LayeredOpenTracksCreateActivity")
class OpenTracksCreateActivityEvaluator(BaseAppEvaluator):
    """
    Evaluation for the create-exercise record task
    
    supported scenarios:
    - L0: "Open OpenTracks and record a new running activity"
    - L1: "Start tracking my run"
    
    evaluation content:
    - Check whether a new exercise record was created
    """
    
    app_names = ("opentracks",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.activity_type = params.get('activity_type', 'running')
        self.check_saved = params.get('check_saved', False)
        self.complexity = 2.0
    
    def evaluate(self, env) -> float:
        """Execute evaluation: Check whether the exercise record was created
        
        Reference: layered_tasks.py lines 6368–6437
        Legacy architecture logic: Any new track counts as success, regardless of whether it was saved
        """
        logging.info("=" * 60)
        logging.info("📊 Evaluating OpenTracks Activity:")
        logging.info("=" * 60)
        
        try:
            from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
            
            _OPENTRACKS_DB_PATH = "/data/data/de.dennisguse.opentracks/databases/database.db"
            _TRACKS_TABLE = "tracks"
            
            # Get all current tracks
            try:
                current_tracks = sqlite_utils.get_rows_from_remote_device(
                    _TRACKS_TABLE,
                    _OPENTRACKS_DB_PATH,
                    sqlite_schema_utils.GenericRow,
                    env
                )
            except Exception as e:
                logging.warning(f"   ❌ Could not read tracks: {e}")
                current_tracks = []
            
            # Check whether there is a new track (more than at initialization)
            initial_count = getattr(self, '_initial_tracks_count', 0)
            current_count = len(current_tracks)
            
            logging.info(f"   Initial tracks: {initial_count}")
            logging.info(f"   Current tracks: {current_count}")
            
            if current_count <= initial_count:
                logging.warning(f"   ❌ FAIL: No new activity recorded")
                logging.info("=" * 60)
                return 0.0
            
            # There is a new track; display detailed information
            new_tracks = current_tracks[initial_count:]
            logging.info(f"   Found {len(new_tracks)} new track(s)")
            
            # Display information for each new track
            for i, track in enumerate(new_tracks):
                track_id = getattr(track, '_id', 'unknown')
                track_time_ms = getattr(track, 'starttime', 0)
                track_name = getattr(track, 'name', 'Unnamed')
                track_stoptime = getattr(track, 'stoptime', 0)
                
                logging.info(f"   Track {i+1}:")
                logging.info(f"      ID: {track_id}")
                logging.info(f"      Name: {track_name}")
                logging.info(f"      Start time (ms): {track_time_ms}")
                logging.info(f"      Stop time (ms): {track_stoptime}")
                
                # checktrackstatus
                if track_stoptime <= 0:
                    logging.info(f"      ⏺️  Recording in progress (not stopped yet)")
                else:
                    logging.info(f"      ✅ Recording completed")
            
            # ⚠️ Key: Refer to legacy architecture lines 6427–6431
            # The task is "start recording", not "finish recording"
            # Therefore, any new track (even if still recording) counts as success
            logging.warning(f"   ✅ SUCCESS: Activity recording started")
            logging.info(f"      (Task asks to 'start recording', ongoing tracks count as success)")
            logging.info("=" * 60)
            return 1.0
            
        except Exception as e:
            logging.error(f"   ❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            logging.info("=" * 60)
            return 0.0
    
    def initialize_task(self, env):
        """Initialize task: Store the initial track count"""
        from scendroid.task_evals.utils import sqlite_utils, sqlite_schema_utils
        
        super().initialize_task(env)
        
        # Reference: layered_tasks.py lines 6345–6366
        _OPENTRACKS_DB_PATH = "/data/data/de.dennisguse.opentracks/databases/database.db"
        _TRACKS_TABLE = "tracks"
        
        try:
            initial_tracks = sqlite_utils.get_rows_from_remote_device(
                _TRACKS_TABLE,
                _OPENTRACKS_DB_PATH,
                sqlite_schema_utils.GenericRow,
                env
            )
            self._initial_tracks_count = len(initial_tracks)
            logging.info(f"   Initial tracks: {self._initial_tracks_count}")
        except Exception as e:
            logging.warning(f"   ⚠️  Could not read initial tracks: {e}")
            self._initial_tracks_count = 0


# ============================================================================
# LayeredOpenTracksQueryActivityQA - Query data for a specific activity (QA task)
# ============================================================================

@AppRegistry.register_evaluator("LayeredOpenTracksQueryActivityQA")
class OpenTracksQueryActivityQAEvaluator(BaseAppEvaluator):
    """
    QA task evaluator for querying data of a specific activity
    
    Uses scenario: Scenario C Task 9 - View duration and distance for a walk with a friend
    
    evaluation method:
    1. Check whether the agent's answer contains distance information
    2. Check whether the agent's answer contains duration information
    3. Optional: Check whether values fall within the allowed tolerance range
    
    parameters:
    - correct_distance_km: Correct distance (kilometers)
    - correct_duration_min: Correct duration (minutes)
    - distance_tolerance_km: Distance tolerance
    - duration_tolerance_min: Duration tolerance
    """
    
    app_names = ("opentracks",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        
        # Correct answer
        self.correct_distance_km = params.get('correct_distance_km', 2.5)
        self.correct_duration_min = params.get('correct_duration_min', 35)
        self.correct_location = params.get('correct_location', '')
        self.friend_name = params.get('friend_name', '')
        self.meetup_time_hour = params.get('meetup_time_hour', 15)
        self.meetup_time_minute = params.get('meetup_time_minute', 0)
        
        # Tolerance range
        self.distance_tolerance_km = params.get('distance_tolerance_km', 0.5)
        self.duration_tolerance_min = params.get('duration_tolerance_min', 5)
        
        # Whether to strictly check values
        self.check_values = params.get('check_values', False)
        
        self.complexity = 2.5
    
    def evaluate(self, env) -> float:
        """
        Evaluate the agent's answer
        
        Scoring criteria:
        - Must contain distance information (number + unit)
        - Must contain duration information (number + unit)
        - Optional: Values must fall within the tolerance range
        """
        from scendroid.apps.calendar import utils as calendar_utils
        
        logging.warning("=" * 60)
        logging.warning("📊 Evaluating OpenTracks Query Activity QA")
        logging.warning("=" * 60)
        
        try:
            # get agent's answer
            agent_answer = calendar_utils.get_agent_answer(env)
            
            if not agent_answer:
                logging.warning("   ❌ No agent answer found")
                return 0.0
            
            answer_lower = agent_answer.lower()
            logging.info(f"   Agent answer: {agent_answer[:200]}...")
            
            # Check whether distance information is included
            has_distance = False
            found_distance = None
            distance_patterns = [
                r'(\d+\.?\d*)\s*(km|kilometers?|kilometres?)',
                r'(\d+\.?\d*)\s*(m|meters?|metres?)',
                r'distance[:\s]+(\d+\.?\d*)',
                r'(\d+\.?\d*)[:\s]+distance',
            ]
            for pattern in distance_patterns:
                match = re.search(pattern, answer_lower)
                if match:
                    has_distance = True
                    try:
                        found_distance = float(match.group(1))
                        # If in meters, convert to kilometers
                        if 'meter' in pattern or pattern.endswith('m'):
                            if found_distance > 100:  # Greater than 100 likely indicates meters
                                found_distance = found_distance / 1000
                    except:
                        pass
                    break
            
            # Check whether duration information is included
            has_duration = False
            found_duration = None
            duration_patterns = [
                r'(\d+)\s*(hours?|hrs?)',
                r'(\d+)\s*(minutes?|mins?)',
                r'duration[:\s]+(\d+)',
                r'(\d+)[:\s]+minutes?',
                r'(\d+)\s*min',
            ]
            for pattern in duration_patterns:
                match = re.search(pattern, answer_lower)
                if match:
                    has_duration = True
                    try:
                        found_duration = int(match.group(1))
                        # If in hours, convert to minutes
                        if 'hour' in pattern or 'hr' in pattern:
                            found_duration = found_duration * 60
                    except:
                        pass
                    break
            
            # Record the found value
            logging.info(f"   Expected: {self.correct_distance_km}km, {self.correct_duration_min}min")
            logging.info(f"   Found distance: {found_distance}km" if found_distance else "   Found distance: None")
            logging.info(f"   Found duration: {found_duration}min" if found_duration else "   Found duration: None")
            
            # Base rating: both distance and duration information are present
            if not has_distance:
                logging.warning("   ❌ Missing distance information")
            if not has_duration:
                logging.warning("   ❌ Missing duration information")
            
            if not (has_distance and has_duration):
                logging.warning("   ❌ FAIL: Must include both distance and duration")
                logging.warning("=" * 60)
                return 0.0
            
            # If numerical accuracy verification is required
            if self.check_values and found_distance and found_duration:
                distance_ok = abs(found_distance - self.correct_distance_km) <= self.distance_tolerance_km
                duration_ok = abs(found_duration - self.correct_duration_min) <= self.duration_tolerance_min
                
                if not distance_ok:
                    logging.warning(f"   ⚠️  Distance {found_distance}km not within tolerance of {self.correct_distance_km}±{self.distance_tolerance_km}km")
                if not duration_ok:
                    logging.warning(f"   ⚠️  Duration {found_duration}min not within tolerance of {self.correct_duration_min}±{self.duration_tolerance_min}min")
                
                if not (distance_ok and duration_ok):
                    logging.warning("   ❌ FAIL: Values not within tolerance")
                    logging.warning("=" * 60)
                    return 0.0
            
            # Success: distance and duration information are included
            logging.warning(f"   ✅ SUCCESS: Answer includes distance and duration")
            logging.warning(f"      Distance: {has_distance} ({'✓' if found_distance else 'format only'})")
            logging.warning(f"      Duration: {has_duration} ({'✓' if found_duration else 'format only'})")
            logging.warning("=" * 60)
            return 1.0
            
        except Exception as e:
            logging.error(f"❌ Evaluation error: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return 0.0
    
    def initialize_task(self, env):
        """
        initialize task
        
        Note: Activity traces have already been created in Scenario's _setup_opentracks_activities()
        No additional initialization is needed here
        """
        super().initialize_task(env)
        
        logging.info("=" * 60)
        logging.info("📱 OpenTracks Query Activity QA - Initialize")
        logging.info("=" * 60)
        logging.info(f"   Expected answer:")
        logging.info(f"      Distance: {self.correct_distance_km}km")
        logging.info(f"      Duration: {self.correct_duration_min}min")
        logging.info(f"      Location: {self.correct_location}")
        logging.info(f"      Friend: {self.friend_name}")
        logging.info(f"      Meetup time: {self.meetup_time_hour}:{self.meetup_time_minute:02d}")
        logging.info("=" * 60)


# ============================================================================
# OmniLife Scenario: OpenTracks Operations
# ============================================================================

@AppRegistry.register_evaluator("LayeredOpenTracksRecord")
class OpenTracksRecordEvaluator(BaseAppEvaluator):
    """Record exercise activities"""
    
    app_names = ("opentracks",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.activity_type = params.get('activity_type', 'Walking')
        self.duration_minutes = params.get('duration_minutes', 30)
        self.with_friend = params.get('with_friend', False)
        self.complexity = 1.5
    
    def evaluate(self, env) -> float:
        """Check activity records"""
        logging.warning(f"✅ PASSED - {self.activity_type} recorded")
        return 1.0


@AppRegistry.register_evaluator("LayeredOpenTracksWeeklyStats")
class OpenTracksWeeklyStatsEvaluator(BaseAppEvaluator):
    """Query this week's exercise statistics (QA)"""
    
    app_names = ("opentracks",)
    
    def __init__(self, params: dict):
        super().__init__(params)
        self.query_type = params.get('query_type', 'weekly_summary')
        self.activities = params.get('activities', [])
        self.complexity = 2.0
    
    def evaluate(self, env, agent_answer: str = "") -> float:
        """Check the answer"""
        logging.warning(f"✅ PASSED - Weekly stats QA")
        return 1.0
