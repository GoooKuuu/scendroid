# Copyright 2024 The ScenDroid Authors.
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

"""
Qwen3-VL Single Model Agent for ScenDroid

Supports two modes:  
1. API mode: Invoke Qwen3-VL via the Dashscope API  
2. Local mode: Load the local Qwen3-VL model  
"""

import base64
import json
import logging
import os
import time
from io import BytesIO
from PIL import Image
from typing import Optional

# API mode
from openai import OpenAI

# local model mode
try:
    import torch
    from transformers import AutoModelForImageTextToText, AutoProcessor
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available. Local model mode disabled.")

from scendroid.agents import base_agent
from scendroid.env import interface
from scendroid.env import json_action


# System Prompt (basic version, does not support ask_user)  
# Note: Fixed resolution of 999x999 is used, which is Qwen3-VL's training resolution  
SYSTEM_PROMPT = """

# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{"type": "function", "function": {"name": "mobile_use", "description": "Use a touchscreen to interact with a mobile device, and take screenshots.\\n* This is an interface to a mobile device with touchscreen. You can perform actions like clicking, typing, swiping, etc.\\n* Some applications may take time to start or process actions, so you may need to wait and take successive screenshots to see the results of your actions.\\n* The screen's resolution is 999x999.\\n* Make sure to click any buttons, links, icons, etc with the cursor tip in the center of the element. Don't click boxes on their edges unless asked.", "parameters": {"properties": {"action": {"description": "The action to perform. The available actions are:\\n* `click`: Click the point on the screen with coordinate (x, y).\\n* `long_press`: Press the point on the screen with coordinate (x, y) for specified seconds.\\n* `swipe`: Swipe from the starting point with coordinate (x, y) to the end point with coordinates2 (x2, y2).\\n* `type`: Input the specified text into the activated input box.\\n* `answer`: Output the answer.\\n* `system_button`: Press the system button.\\n* `wait`: Wait specified seconds for the change to happen.\\n* `terminate`: Terminate the current task and report its completion status.", "enum": ["click", "long_press", "swipe", "type", "answer", "system_button", "wait", "terminate"], "type": "string"}, "coordinate": {"description": "(x, y): The x (pixels from the left edge) and y (pixels from the top edge) coordinates to move the mouse to. Required only by `action=click`, `action=long_press`, and `action=swipe`.", "type": "array"}, "coordinate2": {"description": "(x, y): The x (pixels from the left edge) and y (pixels from the top edge) coordinates to move the mouse to. Required only by `action=swipe`.", "type": "array"}, "text": {"description": "Required only by `action=type` and `action=answer`.", "type": "string"}, "time": {"description": "The seconds to wait. Required only by `action=long_press` and `action=wait`.", "type": "number"}, "button": {"description": "Back means returning to the previous interface, Home means returning to the desktop, Menu means opening the application background menu, and Enter means pressing the enter. Required only by `action=system_button`", "enum": ["Back", "Home", "Menu", "Enter"], "type": "string"}, "status": {"description": "The status of the task. Required only by `action=terminate`.", "type": "string", "enum": ["success", "failure"]}}, "required": ["action"], "type": "object"}}}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>

# Response format

Response format for every step:
1) Thought: one concise sentence explaining the next move (no multi-step reasoning).
2) Action: a short imperative describing what to do in the UI.
3) A single <tool_call>...</tool_call> block containing only the JSON: {"name": <function-name>, "arguments": <args-json-object>}.

Rules:
- Output exactly in the order: Thought, Action, <tool_call>.
- Be brief: one sentence for Thought, one for Action.
- Do not output anything else outside those three parts.
- If finishing, use action=terminate in the tool call."""


# System Prompt 2 for Interactive Clarification
# Supports asking the user for clarification; ask_user is an action within mobile_use  
SYSTEM_PROMPT_WITH_ASK = """

# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{"type": "function", "function": {"name": "mobile_use", "description": "Use a touchscreen to interact with a mobile device, and take screenshots.\\n* This is an interface to a mobile device with touchscreen. You can perform actions like clicking, typing, swiping, etc.\\n* When the instruction is unclear or missing critical information, you can ask the user for clarification.\\n* Some applications may take time to start or process actions, so you may need to wait and take successive screenshots to see the results of your actions.\\n* The screen's resolution is 999x999.\\n* Make sure to click any buttons, links, icons, etc with the cursor tip in the center of the element. Don't click boxes on their edges unless asked.", "parameters": {"properties": {"action": {"description": "The action to perform. The available actions are:\\n* `click`: Click the point on the screen with coordinate (x, y).\\n* `long_press`: Press the point on the screen with coordinate (x, y) for specified seconds.\\n* `swipe`: Swipe from the starting point with coordinate (x, y) to the end point with coordinates2 (x2, y2).\\n* `type`: Input the specified text into the activated input box.\\n* `answer`: Output the answer for QA tasks.\\n* `ask_user`: Ask the user for clarification when the instruction is unclear, ambiguous, or missing critical information. Use this ONLY when you genuinely cannot proceed. Ask ONE specific question at a time.\\n* `system_button`: Press the system button.\\n* `wait`: Wait specified seconds for the change to happen.\\n* `terminate`: Terminate the current task and report its completion status.", "enum": ["click", "long_press", "swipe", "type", "answer", "ask_user", "system_button", "wait", "terminate"], "type": "string"}, "coordinate": {"description": "(x, y): The x (pixels from the left edge) and y (pixels from the top edge) coordinates to move the mouse to. Required only by `action=click`, `action=long_press`, and `action=swipe`.", "type": "array"}, "coordinate2": {"description": "(x, y): The x (pixels from the left edge) and y (pixels from the top edge) coordinates to move the mouse to. Required only by `action=swipe`.", "type": "array"}, "text": {"description": "Required by `action=type`, `action=answer`, and `action=ask_user`. For ask_user, this should be a concise, specific question asking for missing information (e.g., 'What is the contact phone number?' or 'Which alarm time?').", "type": "string"}, "time": {"description": "The seconds to wait. Required only by `action=long_press` and `action=wait`.", "type": "number"}, "button": {"description": "Back means returning to the previous interface, Home means returning to the desktop, Menu means opening the application background menu, and Enter means pressing the enter. Required only by `action=system_button`", "enum": ["Back", "Home", "Menu", "Enter"], "type": "string"}, "status": {"description": "The status of the task. Required only by `action=terminate`.", "type": "string", "enum": ["success", "failure"]}}, "required": ["action"], "type": "object"}}}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{"name": <function-name>, "arguments": <args-json-object>}
</tool_call>

# Response format

Response format for every step:
1) Thought: one concise sentence explaining your next move or why you need clarification.
2) Action: a short imperative describing what to do (operate the UI or ask the user).
3) A single <tool_call>...</tool_call> block containing only the JSON: {"name": "mobile_use", "arguments": <args-json-object>}.

Rules:
- Output exactly in the order: Thought, Action, <tool_call>.
- Be brief: one sentence for Thought, one for Action.
- Do not output anything else outside those three parts.
- When the task instruction is clear enough, proceed with UI actions (click, type, swipe, etc.).
- When critical information is missing or ambiguous, use action=ask_user to get clarification.
- For ask_user, put your question in the "text" field.
- Only ask ONE question at a time, then wait for the user's response (which will appear in the next step).
- After receiving clarification, continue with other actions.
- If finishing, use action=terminate."""


def rescale_coordinates(point, width, height):
    """
    scale model output 999x999 coordinates to actual screen size
    
    Important: Qwen3-VL model was trained at 999x999 resolution,
    regardless of what resolution is specified in the prompt, the model always outputs coordinates in 999x999 range.
    therefore coordinate scaling is required.
    
    Args:
        point: [x, y] model output coordinates (based on 999x999)
        width: actual screen width
        height: actual screen height
    
    Returns:
        scaled coordinates [x, y]
    """
    point = [round(point[0]/999*width), round(point[1]/999*height)]
    return point


def encode_image(image_path: str) -> str:
    """encode image to base64 format"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


class QwenAgent(base_agent.EnvironmentInteractingAgent):
    """
    Base class for the Qwen3-VL Agent, supporting both API and local model modes  
    
    can create agents with different capabilities through subclassing:
    - QwenAgent: Basic version, does not support ask_user  
    - QwenAgentWithAsk: Supports interactive clarification via ask_user  
    """
    
    # subclasses can override this property to select a different system prompt
    SYSTEM_PROMPT_TEMPLATE = SYSTEM_PROMPT
    
    def __init__(
        self,
        env: interface.AsyncEnv,
        use_local_model: bool = False,
        model_path: Optional[str] = None,
        api_key: str = "",  # Set via DASHSCOPE_API_KEY env var or pass directly
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_id: str = "qwen3-vl-235b-a22b-instruct",
        device: str = "cuda",
        max_new_tokens: int = 2048,
        name: str = 'QwenAgent',
        wait_after_action_seconds: float = 2.0,
        human_simulator = None,
        original_goal: Optional[str] = None,
    ):
        """initialize Qwen Agent
        
        Args:
            env: Android environment
            use_local_model: Whether to use the local model (False = API mode, True = local model mode)  
            model_path: Path to the local model (required only when use_local_model=True)  
            api_key: DashScope API key (only used when use_local_model=False)
            base_url: API base URL (only used when use_local_model=False)
            model_id: Model ID (used in API mode)
            device: Device type (used in local mode, e.g., "cuda" or "cpu")
            max_new_tokens: max generation token count
            name: Agent name
            wait_after_action_seconds: wait time after action
            human_simulator: HumanSimulator instance for auto-answering agent questions (optional)
            original_goal: original clear instruction (L0), for human_simulator use (optional)
        """
        super().__init__(env, name)
        
        self.use_local_model = use_local_model
        self.wait_after_action_seconds = wait_after_action_seconds
        self.max_new_tokens = max_new_tokens
        
        # use system prompt specified by class attribute
        self.system_prompt = self.SYSTEM_PROMPT_TEMPLATE
        supports_ask = "ask_user" in self.system_prompt
        logging.info(f"📝 Using {self.__class__.__name__} {'(with ask_user)' if supports_ask else '(without ask_user)'}")
        
        # Human simulator for automated testing
        self.human_simulator = human_simulator
        self.original_goal = original_goal
        if human_simulator:
            logging.info(f"🤖 HumanSimulator enabled - agent questions will be auto-answered")
        
        if use_local_model:
            # local model mode
            if not TRANSFORMERS_AVAILABLE:
                raise RuntimeError("Transformers library is required for local model mode. Please install it.")
            if not model_path:
                raise ValueError("model_path is required when use_local_model=True")
            
            logging.info(f"🔧 Loading local model from: {model_path}")
            self.device = device
            self.model_path = model_path
            
            # Load the local model (refer to dualmodel_v7.py and qwen3vl_README.md)  
            self.model = AutoModelForImageTextToText.from_pretrained(
                model_path,
                torch_dtype=torch.bfloat16,
                attn_implementation="flash_attention_2",
                device_map="auto",
            )
            self.processor = AutoProcessor.from_pretrained(model_path)
            self.model_id = os.path.basename(model_path)
            
            logging.info(f"✅ Local model loaded successfully")
            logging.info(f"   Device: {device}")
        else:
            # API mode
            logging.info(f"🌐 Using API mode")
            resolved_api_key = api_key or os.environ.get("DASHSCOPE_API_KEY", "")
            if not resolved_api_key:
                raise ValueError(
                    "API key is required for API mode. "
                    "Set DASHSCOPE_API_KEY environment variable or pass api_key parameter."
                )
            self.client = OpenAI(
                api_key=resolved_api_key,
                base_url=base_url,
            )
            self.model_id = model_id
            logging.info(f"   Model ID: {model_id}")
        
        # action history
        self.history_instruction = []
        
        # count proactive question attempts
        self.ask_count = 0  # number of proactive questions by agent in current task
        
        # save current task's goal (for context when asking user)
        self.current_goal = None  # will be set on first step
        
        # get actual screen size (for coordinate scaling)
        self.screen_width, self.screen_height = env.logical_screen_size
        
        # create temp screenshot directory
        self.base_save_dir = "./save/images/qwen_test"
        os.makedirs(self.base_save_dir, exist_ok=True)
        
        logging.info(f"✅ QwenAgent initialization successful")
        logging.info(f"   model: {model_id}")
        logging.info(f"   actual screen size: {self.screen_width}x{self.screen_height}")
        logging.info(f"   Model coordinate space: 999x999 (will be automatically scaled)")  
    
    def _save_screenshot(self, pixels, som=False):
        """save screenshot to temp file"""
        timestamp = int(time.time())
        temp_file = os.path.join(self.base_save_dir, f'scr_{timestamp}.png')
        if som:
            temp_file = os.path.join(self.base_save_dir, f'scr_{timestamp}_som.png')
        try:
            img = Image.fromarray(pixels)
            img.save(temp_file)
            return temp_file
        except Exception as e:
            logging.error(f"Failed to save screenshot: {e}")
            return None
    
    def _call_qwen_api(self, user_query: str, image_path: str):
        """Invoke the Qwen3-VL API (API mode)  
        
        Args:
            user_query: user query text
            image_path: screenshot path
            
        Returns:
            model response text
        """
        try:
            # encode image
            base64_image = encode_image(image_path)
            
            # Build message (refer to test_qwen3vl_cookbook.py)  
            messages = [
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": self.system_prompt},
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_query},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ]
            
            # call API
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=0.3,
                max_tokens=self.max_new_tokens,
            )
            
            output_text = completion.choices[0].message.content
            return output_text
            
        except Exception as e:
            logging.error(f"API call failed: {e}")
            raise
    
    def _call_local_model(self, user_query: str, image_path: str):
        """Invoke the local Qwen3-VL model (local mode)  
        
        Args:
            user_query: user query text
            image_path: screenshot path
            
        Returns:
            model response text
        """
        try:
            # Load image  
            image = Image.open(image_path)
            
            # Build message (refer to qwen3vl_README.md)  
            messages = [
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": self.system_prompt},
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_query},
                        {"type": "image", "image": image},
                    ],
                }
            ]
            
            # Prepare input  
            inputs = self.processor.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_dict=True,
                return_tensors="pt"
            )
            inputs = inputs.to(self.model.device)
            
            # Generate output  
            generated_ids = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            output_text = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[0]
            
            return output_text
            
        except Exception as e:
            logging.error(f"Local model call failed: {e}")
            raise
    
    def _call_model(self, user_query: str, image_path: str):
        """Unified model invocation interface, selecting either API or local model based on mode  
        
        Args:
            user_query: user query text
            image_path: screenshot path
            
        Returns:
            model response text
        """
        if self.use_local_model:
            return self._call_local_model(user_query, image_path)
        else:
            return self._call_qwen_api(user_query, image_path)
    
    def _parse_action_from_output(self, output_text: str):
        """Parse action from model output  
        
        Args:
            output_text: model output text
            
        Returns:
            parsed action dictionary, containing 'thought', 'action_description', 'tool_call'
        """
        try:
            # Extract thought (first line)  
            lines = output_text.strip().split('\n')
            thought = ""
            action_description = ""
            
            for line in lines:
                if line.startswith("Thought:"):
                    thought = line.replace("Thought:", "").strip()
                elif line.startswith("Action:"):
                    action_description = line.replace("Action:", "").strip()
            
            # Extract JSON from tool_call  
            if '<tool_call>' in output_text and '</tool_call>' in output_text:
                tool_call_str = output_text.split('<tool_call>')[1].split('</tool_call>')[0].strip()
                tool_call = json.loads(tool_call_str)
            else:
                raise ValueError("No tool_call found in output")
            
            return {
                'thought': thought,
                'action_description': action_description,
                'tool_call': tool_call
            }
            
        except Exception as e:
            logging.error(f"Failed to parse action: {e}")
            logging.error(f"Output text: {output_text}")
            return None
    
    def _translate_to_json_action(self, tool_call: dict):
        """Translate tool_call into ScenDroid's JSONAction (refer to lines 100–167 in dualmodel_v7.py)  
        
        Args:
            tool_call: Parsed tool_call dictionary  
            
        Returns:
            json_action.JSONAction object
        """
        arguments = tool_call.get('arguments', {})
        action_type = arguments.get('action')
        
        if action_type == 'click':
            # scale coordinates
            coord = arguments['coordinate']
            scaled_coord = rescale_coordinates(coord, self.screen_width, self.screen_height)
            logging.info(f"Click: original coordinates {coord} → after scaling {scaled_coord}")
            
            return json_action.JSONAction(
                action_type='click',
                x=scaled_coord[0],
                y=scaled_coord[1]
            )
        
        elif action_type == 'long_press':
            coord = arguments['coordinate']
            scaled_coord = rescale_coordinates(coord, self.screen_width, self.screen_height)
            duration_s = arguments.get('time', 1.0)
            logging.info(f"Long press: original coordinates {coord} → after scaling {scaled_coord}, duration {duration_s}s")
            
            return json_action.JSONAction(
                action_type='long_press',
                x=scaled_coord[0],
                y=scaled_coord[1]
            )
        
        elif action_type == 'swipe':
            coord1 = arguments['coordinate']
            coord2 = arguments['coordinate2']
            scaled_coord1 = rescale_coordinates(coord1, self.screen_width, self.screen_height)
            scaled_coord2 = rescale_coordinates(coord2, self.screen_width, self.screen_height)
            logging.info(f"Swipe: {coord1} → {coord2} (after scaling: {scaled_coord1} → {scaled_coord2})")
            
            return json_action.JSONAction(
                action_type='swipe',
                start_x=scaled_coord1[0],
                start_y=scaled_coord1[1],
                end_x=scaled_coord2[0],
                end_y=scaled_coord2[1]
            )
        
        elif action_type == 'type':
            text = arguments['text']
            logging.info(f"Type: '{text}'")
            
            return json_action.JSONAction(
                action_type='input_text',
                text=text
            )
        
        elif action_type == 'system_button':
            button = arguments['button']
            logging.info(f"System button: {button}")
            
            # Map button name (refer to lines 139–147 in dualmodel_v7.py)  
            button_map = {
                'Back': 'navigate_back',
                'Home': 'navigate_home',
                'Menu': 'navigate_overview',
                'Enter': 'keyboard_enter'
            }
            
            action_name = button_map.get(button)
            if not action_name:
                raise ValueError(f"Unknown system button: {button}")
            
            return json_action.JSONAction(
                action_type=action_name
            )
        
        elif action_type == 'wait':
            duration_s = arguments.get('time', 1.0)
            logging.info(f"Wait: {duration_s}s")
            
            return json_action.JSONAction(
                action_type='wait',
                text=str(duration_s)
            )
        
        elif action_type == 'terminate':
            status = arguments.get('status', 'success')
            logging.info(f"Terminate: {status}")
            
            # Convert status (refer to lines 154–158 in dualmodel_v7.py)  
            goal_status = status.lower()
            if goal_status not in ['success', 'infeasible']:
                raise ValueError(f"Invalid goal status: {goal_status}")
            
            return json_action.JSONAction(
                action_type='status',
                goal_status=goal_status
            )
        
        elif action_type == 'answer':
            text = arguments.get('text', '')
            logging.info(f"Answer: '{text}'")
            
            return json_action.JSONAction(
                action_type='answer',
                text=text
            )
        
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    def step(self, goal: str = None):
        """execute one step
        
        Args:
            goal: task goal (optional, provided on first call)
            
        Returns:
            base_agent.AgentInteractionResult
        """
        # save or update goal (for context when asking user)
        if goal:
            self.current_goal = goal
        
        step_data = {
            'raw_screenshot': None,
            'action_output': None,
            'action_output_json': None,
            'summary': None,
            'is_ask': False,  # default is not an ask action
        }
        
        step_num = len(self.history_instruction) + 1
        print(f'----------step {step_num}----------')
        
        # wait at step start (critical! avoid gRPC connection issues)
        time.sleep(1)
        
        # get current state
        state = self.get_post_transition_state()
        step_data['raw_screenshot'] = state.pixels.copy()
        
        # save screenshot
        image_path = self._save_screenshot(step_data['raw_screenshot'])
        
        # build action history
        stage2_history = ''
        for idx, his in enumerate(self.history_instruction):
            summary = his.get('summary', '')
            stage2_history += f'Step {idx + 1}: {summary.replace(chr(10), "").replace(chr(34), "")}; '
        
        if not stage2_history:
            stage2_history = 'No actions taken yet.'
        
        # Build user query (refer to test_qwen3vl_cookbook.py)  
        # ✅ Use the provided goal parameter (consistent with dualmodel_v7.py)  
        # The standard ScenDroid invocation pattern passes the same goal to each step() call  
        user_query = f"The user query: {goal}.\nTask progress (You have done the following operation on the current device): {stage2_history}\n"
        
        try:
            # Invoke model (API or local model)  
            output_text = self._call_model(user_query, image_path)
            step_data['action_output'] = output_text
            
            print('modeloutput:\n')
            print(output_text)
            
            # parse action
            parsed = self._parse_action_from_output(output_text)
            if not parsed:
                summary = 'Failed to parse action from model output'
                self.history_instruction.append({'summary': summary})
                return base_agent.AgentInteractionResult(False, step_data)
            
            # ✅ Save parsed thought and action_description to step_data  
            step_data['thought'] = parsed.get('thought', '')
            step_data['action_description'] = parsed.get('action_description', '')
            
            # Check whether it is an ask_user action (currently an action within mobile_use)  
            tool_call = parsed.get('tool_call', {})
            arguments = tool_call.get('arguments', {})
            action_type = arguments.get('action', '')
            
            # 🆕 Save the raw tool_call JSON (including specific action parameters, e.g., click(x,y))  
            step_data['tool_call_raw'] = json.dumps(tool_call, ensure_ascii=False)
            
            if action_type == 'ask_user':
                # Handle ask_user: Ask the user for clarification  
                question = arguments.get('text', '')
                
                # increment ask count
                self.ask_count += 1
                
                print(f'\n❓ Agent needs clarification (attempt {self.ask_count} time): {question}')
                
                # if HumanSimulator available, auto-get answer
                if self.human_simulator and self.original_goal:
                    try:
                        answer = self.human_simulator.answer_question(
                            question=question,
                            original_instruction=self.original_goal,
                            obfuscated_instruction=self.current_goal,
                        )
                        print(f'💬 simulated user answer: {answer}')
                        
                        # Add the question-answer pair to history (so the answer will be visible in the next step)  
                        qa_summary = f"Agent asked: '{question}' → User answered: '{answer}'"
                        step_data['summary'] = qa_summary
                        step_data['action_output_json'] = f"ask_user: {question} | answer: {answer}"
                        step_data['action_type'] = 'ask_user'
                        step_data['is_ask'] = True
                        step_data['ask_question'] = question
                        step_data['ask_answer'] = answer
                        self.history_instruction.append(step_data)
                        
                        # Continue executing the task (the agent will see the answer in the next step)
                        print(f'   ✅ answer provided, agent will see this info in next step and continue')
                        return base_agent.AgentInteractionResult(False, step_data)
                        
                    except Exception as e:
                        logging.error(f"HumanSimulator failed: {e}")
                        print(f'   Warning: simulator failed: {e}, continue without answer')
                        # Fall through to no-answer case
                
                # no simulator or simulator failed
                print(f'   (in actual use, this will wait for user response)')
                
                summary = f"Asked for clarification: {question}"
                step_data['summary'] = summary
                step_data['action_output_json'] = f"ask_user: {question}"
                step_data['action_type'] = 'ask_user'
                step_data['is_ask'] = True  # Mark this as an ask action
                step_data['ask_question'] = question  # Record the question content
                self.history_instruction.append(step_data)
                
                # Note: When no answer is provided, the task continues but may not be completed
                # In ambiguous instruction scenarios, if clarification questions are left unanswered, the task generally cannot be completed
                return base_agent.AgentInteractionResult(False, step_data)
            
            # Translate to JSONAction (only for mobile_use)
            json_action_obj = self._translate_to_json_action(parsed['tool_call'])
            step_data['action_output_json'] = str(json_action_obj)
            
            # ✅ Save action_type and additional information for special actions
            action_type = parsed['tool_call']['arguments'].get('action', '')
            step_data['action_type'] = action_type
            
            # check if terminated
            if json_action_obj.action_type == 'status':
                if json_action_obj.goal_status == 'infeasible':
                    print('Agent considers the task infeasible')
                summary = 'task completed'
                step_data['summary'] = summary
                self.history_instruction.append(step_data)
                return base_agent.AgentInteractionResult(True, step_data)
            
            # execute action
            try:
                self.env.execute_action(json_action_obj)
                print('✅ action executed successfully')
            except Exception as e:
                print(f'❌ action execution failed: {e}')
                summary = f'action execution failed: {str(e)[:100]}'
                step_data['summary'] = summary
                self.history_instruction.append(step_data)
                return base_agent.AgentInteractionResult(False, step_data)
            
            # wait after action
            time.sleep(self.wait_after_action_seconds)
            
            # generate summary
            action_type = parsed['tool_call']['arguments']['action']
            summary = f"{parsed['action_description']} (action: {action_type})"
            step_data['summary'] = summary
            
            # ✅ Check whether this is an answer action and save the answer text
            if action_type == 'answer':
                answer_text = parsed['tool_call']['arguments'].get('text', '')
                step_data['answer_text'] = answer_text
                print(f'✅ task completed (based on answer action): {answer_text}')
                self.history_instruction.append(step_data)
                return base_agent.AgentInteractionResult(True, step_data)
            
            self.history_instruction.append(step_data)
            
            return base_agent.AgentInteractionResult(False, step_data)
            
        except Exception as e:
            logging.error(f"Step execution failed: {e}")
            summary = f'step execution failed: {str(e)[:100]}'
            step_data['summary'] = summary
            self.history_instruction.append(step_data)
            return base_agent.AgentInteractionResult(False, step_data)
    
    def reset(self, go_home_on_reset: bool = False):
        """Reset agent state (refer to lines 485–489 in dualmodel_v7.py)"""
        super().reset(go_home_on_reset)
        self.env.hide_automation_ui()
        self.history_instruction = []
        self.ask_count = 0  # reset ask count
        self.current_goal = None  # reset goal
        logging.info("Agent reset: cleared history and ask count")


class QwenAgentWithAsk(QwenAgent):
    """
    Qwen3-VL Agent supports an interactive clarification version
    
    Compared with the base version, this agent can proactively ask the user clarifying questions when encountering ambiguous instructions.
    Suitable for L1–L2 ambiguous instruction scenarios.
    """
    
    # override parent's system prompt
    SYSTEM_PROMPT_TEMPLATE = SYSTEM_PROMPT_WITH_ASK
    
    def __init__(self, *args, **kwargs):
        """Initialize a Qwen Agent supporting ask_user"""
        # Ensure the name reflects that this is the ask-supported version
        if 'name' not in kwargs:
            kwargs['name'] = 'QwenAgentWithAsk'
        super().__init__(*args, **kwargs)
