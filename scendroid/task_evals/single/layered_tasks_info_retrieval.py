# Copyright 2025 The ScenDroid Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Information retrieval layered tasks with LLM-assisted evaluation.

This module contains layered tasks that require the agent to retrieve
and report information, with answers evaluated using LLM for semantic matching.
"""

import datetime
import datetime as dt_module
import logging
import os
import random
import time
from typing import Any
import openai

from scendroid.env import adb_utils
from scendroid.env import device_constants
from scendroid.env import interface
from scendroid.task_evals import task_eval
from scendroid.task_evals.single.calendar import calendar_utils
from scendroid.task_evals.information_retrieval import activity_app_utils
from scendroid.task_evals.utils import sqlite_schema_utils
from scendroid.task_evals.utils import sqlite_utils
from scendroid.utils import datetime_utils


# LLM API configuration
_gemini_client = None


def _get_gemini_client():
    """Get or create Gemini API client."""
    global _gemini_client
    if _gemini_client is None:
        openai_base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for LLM evaluation.")
        _gemini_client = openai.OpenAI(
            base_url=openai_base_url,
            api_key=openai_api_key
        )
    return _gemini_client


def llm_evaluate_answer(
    agent_answer: str,
    expected_answer: str,
    task_context: str,
    question: str
) -> tuple[float, str]:
    """Use LLM to evaluate if agent's answer is semantically correct.
    
    This is more flexible than exact string matching, as it can understand
    semantic equivalence even when wording differs.
    
    Args:
        agent_answer: The answer provided by the agent
        expected_answer: The expected answer (can be flexible)
        task_context: Context about the task (e.g., what events exist)
        question: The original question asked
        
    Returns:
        tuple: (score, explanation) where score is 0.0 or 1.0
    """
    # Prepare prompt for LLM
    message = f"""You are evaluating an AI agent's answer to a calendar-related question.

Question: {question}

Context: {task_context}

Expected Answer: {expected_answer}

Agent's Answer: {agent_answer}

Task: Determine if the agent's answer is semantically correct given the context.
The agent doesn't need to use the exact same words as the expected answer,
but the meaning should be equivalent.

For example:
- If expected is "No, you have meetings" and agent says "You're not free", that's CORRECT
- If expected is "No" and agent says "Yes", that's INCORRECT
- If expected is "No, you're busy" and agent says "You don't have free time", that's CORRECT

Please provide your response in the following format:
Judgement: [correct/incorrect]
Reasoning: [Explain in 1-2 sentences why the answer is correct or incorrect]
"""

    messages = [
        {"role": "system", "content": "You are an expert evaluator for AI agent responses."},
        {"role": "user", "content": message}
    ]
    
    try:
        client = _get_gemini_client()
        response = client.chat.completions.create(
            model="gemini-2.5-pro",
            messages=messages,
            temperature=0,
            max_tokens=500,
            top_p=1.0,
        )
        
        response_text = response.choices[0].message.content
        response_lower = response_text.lower()
        
        # Extract reasoning
        reasoning = response_text
        if "reasoning:" in response_lower:
            pos = response_text.lower().find("reasoning:")
            if pos != -1:
                reasoning = response_text[pos + len("reasoning:"):].strip()
        
        # Determine score
        if "judgement: correct" in response_lower or "judgment: correct" in response_lower:
            return 1.0, f"🤖 LLM evaluation: Answer is correct - {reasoning}"
        else:
            return 0.0, f"🤖 LLM evaluation: Answer is incorrect - {reasoning}"
            
    except Exception as e:
        logging.error(f"LLM evaluation failed: {e}")
        # Fallback to simple matching
        agent_lower = agent_answer.lower().strip()
        expected_lower = expected_answer.lower().strip()
        
        if agent_lower == expected_lower or expected_lower in agent_lower:
            return 1.0, f"⚠️ LLM unavailable; using simple match - match"
        else:
            return 0.0, f"⚠️ LLM unavailable; using simple match - no match"


def _get_device_time_ms(env: interface.AsyncEnv) -> int:
    """Get device current time in milliseconds since epoch.
    
    Args:
        env: The environment interface
        
    Returns:
        Current device time in milliseconds
    """
    adb_output = adb_utils.issue_generic_request(
        ["shell", "date", "+%s"], env.controller
    )
    return int(adb_output.generic.output.strip()) * 1000


class LayeredCalendarCheckFreeFriday(task_eval.TaskEval):
    """Task for checking if Friday afternoon is free.
    
    This is an information retrieval task where the agent needs to:
    1. Open Simple Calendar Pro
    2. Check next Friday afternoon (typically 12:00-18:00)
    3. Report whether there is free time or not
    
    Layered instructions:
    - L0: "Open Simple Calendar Pro and check if I have any free time on next Friday afternoon"
    - L1: (empty)
    - L2: (empty)
    - L3: "Am I free Friday afternoon?"
    
    The task initializes by creating several events on Friday afternoon,
    so the correct answer should be "No" or "You don't have free time" etc.
    The agent's answer is evaluated using LLM for semantic matching.
    """
    
    app_names = ("simple calendar pro",)
    complexity = 3.0
    schema = {
        "type": "object",
        "properties": {
            "has_free_time": {"type": "boolean"},
            "num_events": {"type": "integer", "minimum": 2, "maximum": 4},
        },
        "required": ["has_free_time"],
    }
    template = "Check if I have any free time on next Friday afternoon."
    
    def __init__(self, params: dict[str, Any]):
        super().__init__(params)
        self.expected_answer = None
        self.task_context = None
        self.friday_events = []
    
    def initialize_task(self, env: interface.AsyncEnv):
        super().initialize_task(env)
        
        # Clear calendar first
        calendar_utils.clear_calendar_db(env)
        
        # Get device time (Oct 15, 2023 is Sunday)
        device_time_ms = _get_device_time_ms(env)
        device_time_sec = device_time_ms // 1000
        device_dt = datetime_utils.timestamp_to_localized_datetime(
            device_time_sec, timezone=device_constants.TIMEZONE
        )
        
        # Calculate next Friday (Oct 20, 2023)
        # Oct 15 is Sunday (weekday=6), so next Friday is in 5 days
        days_until_friday = (4 - device_dt.weekday()) % 7
        if days_until_friday == 0:
            days_until_friday = 7  # If today is Friday, go to next Friday
        
        friday_date = device_dt + datetime.timedelta(days=days_until_friday)
        friday_year = friday_date.year
        friday_month = friday_date.month
        friday_day = friday_date.day
        
        logging.warning("📅 Check Free Friday - Initialization:")
        logging.warning("   Device date: %s (%s)", 
                       device_dt.strftime("%Y-%m-%d"), 
                       device_dt.strftime("%A"))
        logging.warning("   Next Friday: %s", 
                       friday_date.strftime("%Y-%m-%d (%A)"))
        
        # Create events on Friday afternoon (12:00-18:00)
        has_free_time = self._params.get("has_free_time", False)
        num_events = self._params.get("num_events", 3)
        
        if has_free_time:
            # Create fewer events, leaving some gaps
            num_events = min(num_events, 2)
        
        # Afternoon event times (12:00 PM - 6:00 PM)
        afternoon_times = [
            (13, 0, "Lunch Meeting", "Client lunch discussion", 90),
            (15, 0, "Team Sync", "Weekly team meeting", 60),
            (17, 0, "Project Review", "Q4 project review", 90),
        ]
        
        events_to_add = []
        for i, (hour, minute, title, desc, duration) in enumerate(afternoon_times[:num_events]):
            event_time = datetime.datetime(
                friday_year, friday_month, friday_day, hour, minute,
                tzinfo=datetime.timezone.utc
            )
            start_ts = int(event_time.timestamp())
            end_ts = start_ts + (duration * 60)  # Convert minutes to seconds
            
            event = sqlite_schema_utils.CalendarEvent(
                start_ts=start_ts,
                end_ts=end_ts,
                title=title,
                description=desc,
                location=f"Room {chr(65+i)}",  # Room A, B, C...
            )
            events_to_add.append(event)
            self.friday_events.append({
                "time": f"{hour}:{minute:02d}",
                "title": title,
                "duration": duration,
            })
            logging.info("  Created event: '%s' at %02d:%02d (%d mins)", 
                        title, hour, minute, duration)
        
        # Add events to database
        if events_to_add:
            calendar_utils.add_events(events_to_add, env)
            time.sleep(2.0)  # Wait for database to update
        
        # Set expected answer based on events
        if has_free_time or len(events_to_add) == 0:
            self.expected_answer = "Yes, you have free time on Friday afternoon"
            self.task_context = "Next Friday afternoon has no events scheduled."
        else:
            self.expected_answer = "No, you don't have free time on Friday afternoon"
            event_list = ", ".join([f"{e['title']} at {e['time']}" for e in self.friday_events])
            self.task_context = f"Next Friday afternoon has {len(self.friday_events)} event(s): {event_list}"
        
        logging.warning("✅ Expected answer: '%s'", self.expected_answer)
        logging.warning("📊 Initialized %d event(s) on Friday afternoon", len(self.friday_events))
    
    def is_successful(self, env: interface.AsyncEnv) -> float:
        super().is_successful(env)
        
        # Get agent's answer from interaction cache
        if not hasattr(env, 'interaction_cache') or not env.interaction_cache:
            logging.warning("❌ No agent answer found in env.interaction_cache")
            logging.warning("   Agent needs to provide answer using ask_user action")
            return 0.0
        
        agent_answer = str(env.interaction_cache).strip()
        
        logging.warning("📊 Calendar Free Time Evaluation:")
        logging.warning("   Question: Check if Friday afternoon is free")
        logging.warning("   Context: %s", self.task_context)
        logging.warning("   Expected: %s", self.expected_answer)
        logging.warning("   Agent answer: %s", agent_answer)
        
        # Use LLM to evaluate the answer
        score, explanation = llm_evaluate_answer(
            agent_answer=agent_answer,
            expected_answer=self.expected_answer,
            task_context=self.task_context,
            question="Do I have any free time on next Friday afternoon?"
        )
        
        logging.warning(explanation)
        
        if score >= 0.99:
            logging.warning("✅ PASSED - Answer is semantically correct")
            return 1.0
        else:
            logging.warning("❌ FAILED - Answer is not correct")
            return 0.0
    
    def tear_down(self, env: interface.AsyncEnv):
        super().tear_down(env)
        # Clear all calendar events
        calendar_utils.clear_calendar_db(env)
    
    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        # Most of the time, Friday should be busy (no free time)
        return {
            "has_free_time": False,
            "num_events": random.randint(2, 3),
        }



# ============================================================================
# OpenTracks Information Retrieval Tasks
# ============================================================================

# Import additional modules
import datetime as dt_module
from scendroid.task_evals.information_retrieval import activity_app_utils
from scendroid.task_evals.utils import sqlite_schema_utils


class LayeredOpenTracksCountActivities(task_eval.TaskEval):
  """Task for counting activities of a specific category in OpenTracks.
  
  This is for layered task testing where the instruction might be:
  - L0: "In OpenTracks, tell me how many 'Running' activities I did this week (single integer)"
  - L1: "How many runs did I do this week? (number only)"
  - L2: "Count my runs this week"
  
  This is an information retrieval task where the agent needs to provide a number.
  """
  
  app_names = ("open tracks",)
  complexity = 2.5
  
  schema = {
      "type": "object",
      "properties": {
          "category": {"type": "string"},
          "expected_count": {"type": "integer"},
      },
      "required": ["category", "expected_count"],
  }
  
  template = "How many {category} activities did I do this week in OpenTracks? Answer with a single integer."
  
  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    
    # Clear OpenTracks database
    activity_app_utils.clear_db(env)
    
    category = self._params['category'].lower()
    expected_count = self._params['expected_count']
    
    # Get device time (Oct 15, 2023, Sunday)
    device_dt = device_constants.DT
    
    # Calculate the start of the week (Monday)
    days_since_monday = (device_dt.weekday() - 0) % 7  # Monday = 0
    monday = device_dt - dt_module.timedelta(days=days_since_monday)
    
    # Create target activities this week
    activities = []
    for i in range(expected_count):
      day_offset = i % 7  # Spread across the week
      activity_date = monday + dt_module.timedelta(days=day_offset)
      
      activity = sqlite_schema_utils.SportsActivity(
          name=f"{category.capitalize()} Session {i+1}",
          category=category,
          activity_type=category,
          description=f"Weekly {category}",
          totaldistance=random.uniform(1000, 5000),
          starttime=int(activity_date.replace(hour=8+i).timestamp() * 1000),
          stoptime=int(activity_date.replace(hour=9+i).timestamp() * 1000),
          totaltime=3600000,  # 1 hour in ms
          movingtime=3600000,
          avgspeed=1.5,
          avgmovingspeed=1.5,
          elevationgain=50,
          elevationloss=50,
      )
      activities.append(activity)
    
    # Add some noise activities (different categories)
    other_categories = ['hiking', 'cycling', 'swimming']
    for cat in other_categories:
      for i in range(random.randint(1, 2)):
        day_offset = random.randint(0, 6)
        activity_date = monday + dt_module.timedelta(days=day_offset)
        
        noise_activity = sqlite_schema_utils.SportsActivity(
            name=f"{cat.capitalize()} Activity",
            category=cat,
            activity_type=cat,
            description="",
            totaldistance=random.uniform(1000, 5000),
            starttime=int(activity_date.replace(hour=10+i).timestamp() * 1000),
            stoptime=int(activity_date.replace(hour=11+i).timestamp() * 1000),
            totaltime=3600000,
            movingtime=3600000,
            avgspeed=1.5,
            avgmovingspeed=1.5,
            elevationgain=30,
            elevationloss=30,
        )
        activities.append(noise_activity)
    
    # Insert activities into database
    activity_app_utils._add_activities(activities, env)
    
    self._expected_answer = str(expected_count)
    
    logging.warning(f"🏃 OpenTracks Count Task initialized:")
    logging.warning(f"   Category: {category}")
    logging.warning(f"   Expected count this week: {expected_count}")
    logging.warning(f"   Week: {monday.date()} to {(monday + dt_module.timedelta(days=6)).date()}")
  
  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    
    # Get agent's answer from interaction cache
    # interaction_cache can be either a dict or a string
    if isinstance(env.interaction_cache, dict):
      agent_answer = env.interaction_cache.get('user_response', '').strip()
    else:
      agent_answer = str(env.interaction_cache).strip() if hasattr(env, 'interaction_cache') else ''
    
    if not agent_answer:
      logging.warning("❌ No answer provided")
      return 0.0
    
    # Extract number from answer
    import re
    numbers = re.findall(r'\d+', agent_answer)
    
    if not numbers:
      logging.warning(f"❌ No number found in answer: '{agent_answer}'")
      return 0.0
    
    # Take the first number found
    agent_count = int(numbers[0])
    expected_count = int(self._expected_answer)
    
    if agent_count == expected_count:
      logging.warning(f"✅ Correct! Expected {expected_count}, got {agent_count}")
      return 1.0
    else:
      logging.warning(f"❌ Incorrect. Expected {expected_count}, got {agent_count}")
      return 0.0
  
  def tear_down(self, env: interface.AsyncEnv) -> None:
    super().tear_down(env)
    activity_app_utils.clear_db(env)
  
  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {
        "category": "running",
        "expected_count": 5,
    }


class LayeredOpenTracksListCategories(task_eval.TaskEval):
  """Task for listing activity categories on a specific date in OpenTracks.
  
  This is for layered task testing where the instruction might be:
  - L0: "In OpenTracks, list the activity categories I did on 2025-12-20 (categories only)"
  - L1: "What activities did I do on 2025-12-20? (categories only)"
  
  This is an information retrieval task where the agent needs to list categories.
  """
  
  app_names = ("open tracks",)
  complexity = 2.5
  
  schema = {
      "type": "object",
      "properties": {
          "target_date": {"type": "string"},
          "categories": {"type": "array", "items": {"type": "string"}},
      },
      "required": ["target_date", "categories"],
  }
  
  template = "What activities did I do on {target_date} in OpenTracks? Answer with categories only."
  
  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    
    # Clear OpenTracks database
    activity_app_utils.clear_db(env)
    
    target_date_str = self._params['target_date']
    categories = self._params['categories']
    
    # Parse target date (format: YYYY-MM-DD)
    # Use UTC timezone to match device time
    target_date = dt_module.datetime.strptime(target_date_str, '%Y-%m-%d')
    target_date = target_date.replace(tzinfo=dt_module.timezone.utc)
    
    # Create activities on target date
    activities = []
    for i, category in enumerate(categories):
      activity = sqlite_schema_utils.SportsActivity(
          name=f"{category.capitalize()} Activity",
          category=category.lower(),
          activity_type=category.lower(),
          description="",
          totaldistance=random.uniform(1000, 5000),
          starttime=int(target_date.replace(hour=8+i*2).timestamp() * 1000),
          stoptime=int(target_date.replace(hour=9+i*2).timestamp() * 1000),
          totaltime=3600000,
          movingtime=3600000,
          avgspeed=1.5,
          avgmovingspeed=1.5,
          elevationgain=50,
          elevationloss=50,
      )
      activities.append(activity)
    
    # Add noise activities on other dates
    for day_offset in [-1, 1]:
      noise_date = target_date + dt_module.timedelta(days=day_offset)
      noise_activity = sqlite_schema_utils.SportsActivity(
          name="Swimming Activity",
          category="swimming",
          activity_type="swimming",
          description="",
          totaldistance=1000,
          starttime=int(noise_date.replace(hour=10).timestamp() * 1000),
          stoptime=int(noise_date.replace(hour=11).timestamp() * 1000),
          totaltime=3600000,
          movingtime=3600000,
          avgspeed=1.0,
          avgmovingspeed=1.0,
          elevationgain=0,
          elevationloss=0,
      )
      activities.append(noise_activity)
    
    # Insert activities into database
    activity_app_utils._add_activities(activities, env)
    
    self._expected_categories = sorted([c.lower() for c in categories])
    
    logging.warning(f"📅 OpenTracks List Categories Task initialized:")
    logging.warning(f"   Target date: {target_date_str}")
    logging.warning(f"   Expected categories: {', '.join(self._expected_categories)}")
  
  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    
    # Get agent's answer from interaction cache
    # interaction_cache can be either a dict or a string
    if isinstance(env.interaction_cache, dict):
      agent_answer = env.interaction_cache.get('user_response', '').strip().lower()
    else:
      agent_answer = str(env.interaction_cache).strip().lower() if hasattr(env, 'interaction_cache') else ''
    
    if not agent_answer:
      logging.warning("❌ No answer provided")
      return 0.0
    
    # Check if all expected categories are mentioned
    all_found = True
    for category in self._expected_categories:
      if category not in agent_answer:
        all_found = False
        logging.warning(f"❌ Missing category: {category}")
    
    if all_found:
      logging.warning(f"✅ Correct! All categories found: {', '.join(self._expected_categories)}")
      return 1.0
    else:
      logging.warning(f"❌ Incomplete answer: '{agent_answer}'")
      return 0.0
  
  def tear_down(self, env: interface.AsyncEnv) -> None:
    super().tear_down(env)
    activity_app_utils.clear_db(env)
  
  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {
        "target_date": "2025-12-20",
        "categories": ["Running", "Cycling"],
    }


class LayeredOpenTracksGetDuration(task_eval.TaskEval):
  """Task for getting the duration of a specific activity in OpenTracks.
  
  This is for layered task testing where the instruction might be:
  - L0: "In OpenTracks, give the duration in minutes of my 'Cycling' activity on 2025-12-19 (single integer)."
  - L1: "How long was my cycling on 2025-12-19? (minutes only)"
  
  This is an information retrieval task where the agent needs to provide duration in minutes.
  """
  
  app_names = ("open tracks",)
  complexity = 2.5
  
  schema = {
      "type": "object",
      "properties": {
          "category": {"type": "string"},
          "target_date": {"type": "string"},
          "duration_minutes": {"type": "integer"},
      },
      "required": ["category", "target_date", "duration_minutes"],
  }
  
  template = "How long was my {category} activity on {target_date} in OpenTracks? Answer in minutes as a single integer."
  
  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    
    # Clear OpenTracks database
    activity_app_utils.clear_db(env)
    
    category = self._params['category'].lower()
    target_date_str = self._params['target_date']
    duration_minutes = self._params['duration_minutes']
    
    # Parse target date (format: YYYY-MM-DD)
    # Use UTC timezone to match device time
    target_date = dt_module.datetime.strptime(target_date_str, '%Y-%m-%d')
    target_date = target_date.replace(tzinfo=dt_module.timezone.utc)
    
    # Create target activity on target date
    duration_ms = duration_minutes * 60 * 1000
    start_time = target_date.replace(hour=8)
    end_time = start_time + dt_module.timedelta(minutes=duration_minutes)
    
    target_activity = sqlite_schema_utils.SportsActivity(
        name=f"{category.capitalize()} Session",
        category=category,
        activity_type=category,
        description="",
        totaldistance=random.uniform(5000, 15000),
        starttime=int(start_time.timestamp() * 1000),
        stoptime=int(end_time.timestamp() * 1000),
        totaltime=duration_ms,
        movingtime=duration_ms,
        avgspeed=2.0,
        avgmovingspeed=2.0,
        elevationgain=100,
        elevationloss=100,
    )
    
    activities = [target_activity]
    
    # Add noise activities (same category but different dates, or different categories)
    for day_offset in [-1, 1]:
      noise_date = target_date + dt_module.timedelta(days=day_offset)
      noise_activity = sqlite_schema_utils.SportsActivity(
          name=f"{category.capitalize()} Activity",
          category=category,
          activity_type=category,
          description="",
          totaldistance=1000,
          starttime=int(noise_date.replace(hour=10).timestamp() * 1000),
          stoptime=int(noise_date.replace(hour=11).timestamp() * 1000),
          totaltime=3600000,  # 60 minutes
          movingtime=3600000,
          avgspeed=1.5,
          avgmovingspeed=1.5,
          elevationgain=50,
          elevationloss=50,
      )
      activities.append(noise_activity)
    
    # Insert activities into database
    activity_app_utils._add_activities(activities, env)
    
    self._expected_answer = str(duration_minutes)
    
    logging.warning(f"⏱️  OpenTracks Duration Task initialized:")
    logging.warning(f"   Category: {category}")
    logging.warning(f"   Target date: {target_date_str}")
    logging.warning(f"   Expected duration: {duration_minutes} minutes")
  
  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    
    # Get agent's answer from interaction cache
    # interaction_cache can be either a dict or a string
    if isinstance(env.interaction_cache, dict):
      agent_answer = env.interaction_cache.get('user_response', '').strip()
    else:
      agent_answer = str(env.interaction_cache).strip() if hasattr(env, 'interaction_cache') else ''
    
    if not agent_answer:
      logging.warning("❌ No answer provided")
      return 0.0
    
    # Extract number from answer
    import re
    numbers = re.findall(r'\d+', agent_answer)
    
    if not numbers:
      logging.warning(f"❌ No number found in answer: '{agent_answer}'")
      return 0.0
    
    # Take the first number found
    agent_duration = int(numbers[0])
    expected_duration = int(self._expected_answer)
    
    # Allow ±1 minute tolerance
    if abs(agent_duration - expected_duration) <= 1:
      logging.warning(f"✅ Correct! Expected {expected_duration}, got {agent_duration}")
      return 1.0
    else:
      logging.warning(f"❌ Incorrect. Expected {expected_duration}, got {agent_duration}")
      return 0.0
  
  def tear_down(self, env: interface.AsyncEnv) -> None:
    super().tear_down(env)
    activity_app_utils.clear_db(env)
  
  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {
        "category": "cycling",
        "target_date": "2025-12-19",
        "duration_minutes": 45,
    }
