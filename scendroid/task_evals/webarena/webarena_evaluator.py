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

"""WebArena evaluator adapter for ScenDroid.

This module adapts WebArena's evaluation logic to work with Android Chrome.
It imports and reuses WebArena's evaluator classes but provides Android-compatible
page access methods.
"""

import sys
import os
import urllib.parse
from typing import Any

from absl import logging
from scendroid.env import interface

# Add webarena-main to Python path to import its modules
webarena_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))),
    "webarena-main"
)
if webarena_path not in sys.path:
    sys.path.insert(0, webarena_path)

# Import WebArena's evaluator classes
try:
    from evaluation_harness.evaluators import StringEvaluator
    from evaluation_harness.helper_functions import llm_fuzzy_match, llm_ua_match
except ImportError as e:
    logging.warning(f"Failed to import WebArena evaluators: {e}")
    logging.warning("String matching evaluation will not be available")
    StringEvaluator = None
    llm_fuzzy_match = None
    llm_ua_match = None


class AndroidPageAdapter:
    """Adapter to make Android Chrome behave like a Playwright Page object.
    
    WebArena's evaluators expect a Playwright Page object with methods like
    page.url, page.content(), etc. This adapter provides these methods but
    extracts data from Android Chrome using ADB commands.
    """
    
    def __init__(self, env: interface.AsyncEnv):
        """Initialize the adapter.
        
        Args:
            env: ScenDroid environment with controller for ADB access
        """
        self.env = env
        self._cached_url = None
        self._cached_content = None
    
    @property
    def url(self) -> str:
        """Get current URL from Android Chrome.
        
        Returns:
            Current URL as string
        """
        if self._cached_url:
            return self._cached_url
        
        try:
            # Method 1: Try to get URL from Chrome's UI hierarchy
            # This requires dumping the UI and parsing for the URL bar
            ui_dump = self.env.controller.get_screenshot_as_string()  # Simplified
            
            # TODO: Implement proper URL extraction from Android Chrome
            # Options:
            # 1. Parse UI hierarchy dump to find URL bar text
            # 2. Use Chrome DevTools Protocol (if available on Android)
            # 3. Use accessibility service to read URL bar
            # 4. Inject JavaScript via ADB to get window.location
            
            # For now, return a placeholder (use dynamic URL based on env)
            logging.warning("URL extraction from Android Chrome not yet implemented")
            from scendroid.task_evals.webarena import port_utils
            return port_utils.get_shopping_base_url(env)  # Dynamic shopping URL
            
        except Exception as e:
            logging.error(f"Error extracting URL from Android Chrome: {e}")
            return ""
    
    def goto(self, url: str) -> None:
        """Navigate to a URL in Android Chrome.
        
        Args:
            url: URL to navigate to
        """
        try:
            # Use ADB to open URL in Chrome
            cmd = f'adb shell am start -a android.intent.action.VIEW -d "{url}"'
            self.env.controller.execute_adb_call(cmd)
            
            # Wait for page to load
            import time
            time.sleep(2)
            
            self._cached_url = url
            self._cached_content = None  # Invalidate content cache
            
        except Exception as e:
            logging.error(f"Error navigating to {url}: {e}")
    
    def content(self) -> str:
        """Get page content from Android Chrome.
        
        Returns:
            HTML content as string
        """
        if self._cached_content:
            return self._cached_content
        
        try:
            # TODO: Implement proper HTML content extraction from Android Chrome
            # Options:
            # 1. Use Chrome DevTools Protocol to get page HTML
            # 2. Save page to file and read it
            # 3. Use accessibility service to get page content
            # 4. Inject JavaScript to extract document.documentElement.outerHTML
            
            logging.warning("HTML content extraction from Android Chrome not yet implemented")
            return ""
            
        except Exception as e:
            logging.error(f"Error extracting content from Android Chrome: {e}")
            return ""
    
    def evaluate(self, script: str) -> Any:
        """Evaluate JavaScript in Android Chrome.
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Result of JavaScript evaluation
        """
        try:
            # TODO: Implement JavaScript injection into Android Chrome
            # This is needed for HTMLContentEvaluator
            
            logging.warning("JavaScript evaluation in Android Chrome not yet implemented")
            return None
            
        except Exception as e:
            logging.error(f"Error evaluating JavaScript: {e}")
            return None


class AndroidStringEvaluator:
    """String matching evaluator for Android.
    
    This directly uses WebArena's StringEvaluator logic.
    """
    
    def __init__(self):
        if StringEvaluator is None:
            raise ImportError("WebArena's StringEvaluator not available")
        self.evaluator = StringEvaluator()
    
    @staticmethod
    def clean_answer(answer: str) -> str:
        """Clean answer string (reuse WebArena's logic)."""
        if StringEvaluator:
            return StringEvaluator.clean_answer(answer)
        answer = answer.strip().lower()
        if (answer.startswith("'") and answer.endswith("'")) or \
           (answer.startswith('"') and answer.endswith('"')):
            answer = answer[1:-1]
        return answer
    
    @staticmethod
    def exact_match(ref: str, pred: str) -> float:
        """Check exact match (reuse WebArena's logic)."""
        if StringEvaluator:
            return StringEvaluator.exact_match(ref, pred)
        return float(AndroidStringEvaluator.clean_answer(ref) == 
                    AndroidStringEvaluator.clean_answer(pred))
    
    @staticmethod
    def must_include(ref: str, pred: str, tokenize: bool = False) -> float:
        """Check if reference is included with intelligent fallback.
        
        This method tries multiple strategies:
        1. WebArena's original must_include (if available)
        2. Simple normalization (remove common separators)
        3. LLM-assisted semantic matching (as last resort)
        """
        # Try WebArena's original implementation first
        if StringEvaluator:
            original_result = StringEvaluator.must_include(ref, pred, tokenize)
            if original_result == 1.0:
                return 1.0
            # Continue to fallback strategies if original fails
        
        # Fallback implementation
        clean_ref = AndroidStringEvaluator.clean_answer(ref)
        clean_pred = AndroidStringEvaluator.clean_answer(pred)
        
        # Tokenize to avoid false positives (e.g., "0" matching "10")
        if tokenize and len(clean_ref) == 1:
            try:
                from nltk.tokenize import word_tokenize
                if len(word_tokenize(clean_ref)) == 1:
                    tok_pred = word_tokenize(clean_pred)
                    if clean_ref in tok_pred:
                        return 1.0
            except ImportError:
                logging.warning("NLTK not available, using simple containment")
        
        # Simple containment check
        if clean_ref in clean_pred:
            return 1.0
        
        # Try normalization: remove common separators and spaces
        import re
        ref_normalized = re.sub(r'[*x×X\s\-]', '', clean_ref.lower())
        pred_normalized = re.sub(r'[*x×X\s\-]', '', clean_pred.lower())
        
        if ref_normalized and pred_normalized and ref_normalized in pred_normalized:
            logging.info(f"must_include matched after normalization: '{ref}' vs '{pred}'")
            return 1.0
        
        # Last resort: try LLM for semantic matching
        # Only for non-trivial cases (length > 2 chars)
        if len(clean_ref) > 2 and llm_fuzzy_match:
            try:
                llm_score, _ = llm_fuzzy_match(
                    pred=clean_pred,
                    ref=clean_ref,
                    question=f"Check if '{pred}' contains or is equivalent to '{ref}'"
                )
                if llm_score == 1.0:
                    logging.info(f"must_include matched via LLM: '{ref}' vs '{pred}'")
                    return 1.0
            except Exception as e:
                logging.warning(f"LLM assist failed for must_include: {e}")
        
        return 0.0
    
    @staticmethod
    def fuzzy_match(ref: str, pred: str, intent: str) -> tuple[float, str]:
        """Fuzzy match using LLM (reuse WebArena's logic).
        
        Returns:
            tuple: (score, explanation)
        """
        if llm_fuzzy_match:
            return llm_fuzzy_match(pred, ref, intent)
        # Fallback to exact match if LLM not available
        logging.warning("LLM fuzzy match not available, using exact match")
        score = AndroidStringEvaluator.exact_match(ref, pred)
        if score == 1.0:
            explanation = "⚠️ LLM unavailable, using exact match - match"
        else:
            explanation = f"⚠️ LLM unavailable, using exact match - no match (prediction '{pred}' ≠ reference '{ref}')"
        return score, explanation
    
    @staticmethod
    def ua_match(ref: str, pred: str, intent: str) -> tuple[float, str]:
        """Unachievable match using LLM (reuse WebArena's logic).
        
        Check if the prediction explains why the task is unachievable.
        Used when reference answer is "N/A" but prediction is not exactly "N/A".
        
        Returns:
            tuple: (score, explanation)
        """
        if llm_ua_match:
            return llm_ua_match(pred, ref, intent)
        # Fallback: check if pred contains the explanation
        logging.warning("LLM ua_match not available, using simple containment check")
        clean_ref = AndroidStringEvaluator.clean_answer(ref)
        clean_pred = AndroidStringEvaluator.clean_answer(pred)
        score = float(clean_ref in clean_pred)
        if score == 1.0:
            explanation = "⚠️ LLM unavailable, using containment check - contains"
        else:
            explanation = f"⚠️ LLM unavailable, using containment check - does not contain ('{ref}' not found in prediction '{pred}')"
        return score, explanation
    
    @staticmethod
    def _get_match_type(ref: str, pred: str) -> str:
        """Determine how the match was achieved.
        
        Returns a string indicating the match type for explanation purposes.
        """
        clean_ref = AndroidStringEvaluator.clean_answer(ref).lower()
        clean_pred = AndroidStringEvaluator.clean_answer(pred).lower()
        
        # Check if it's a direct substring match
        if clean_ref in clean_pred:
            return "(exact containment)"
        
        # Check if it's a normalized match
        import re
        ref_normalized = re.sub(r'[*x×X\s\-]', '', clean_ref)
        pred_normalized = re.sub(r'[*x×X\s\-]', '', clean_pred)
        if ref_normalized and pred_normalized and ref_normalized in pred_normalized:
            return "(normalized match, ignoring delimiter differences)"
        
        # Otherwise it must be LLM match
        return "(🤖 LLM semantic match)"
    
    def evaluate(self, agent_answer: str, eval_config: dict[str, Any], 
                 intent: str) -> tuple[float, str]:
        """Evaluate agent's answer against reference answers.
        
        Args:
            agent_answer: Answer provided by the agent
            eval_config: Evaluation configuration from task config
            intent: Task intent/goal
            
        Returns:
            tuple: (score, explanation) where score is between 0.0 and 1.0
        """
        reference_answers = eval_config.get("reference_answers", {})
        score = 1.0
        explanations = []
        
        for approach, value in reference_answers.items():
            if approach == "exact_match":
                step_score = self.exact_match(ref=value, pred=agent_answer)
                score *= step_score
                if step_score == 1.0:
                    explanations.append(f"✅ Exact match: '{agent_answer}' = '{value}'")
                else:
                    explanations.append(f"❌ Exact match failed: '{agent_answer}' ≠ '{value}'")
            
            elif approach == "must_include":
                if isinstance(value, list):
                    # Use tokenize when there's only one value to avoid false positives
                    tokenize = (len(value) == 1)
                    for must_value in value:
                        step_score = self.must_include(
                            ref=must_value, 
                            pred=agent_answer,
                            tokenize=tokenize
                        )
                        score *= step_score
                        if step_score == 1.0:
                            # Determine how the match was achieved
                            match_type = self._get_match_type(must_value, agent_answer)
                            explanations.append(f"✅ Must contain: '{must_value}' in '{agent_answer}' {match_type}")
                        else:
                            explanations.append(f"❌ Must contain failed: '{must_value}' not in '{agent_answer}'")
                else:
                    step_score = self.must_include(ref=value, pred=agent_answer)
                    score *= step_score
                    if step_score == 1.0:
                        match_type = self._get_match_type(value, agent_answer)
                        explanations.append(f"✅ Must contain: '{value}' in '{agent_answer}' {match_type}")
                    else:
                        explanations.append(f"❌ Must contain failed: '{value}' not in '{agent_answer}'")
            
            elif approach == "fuzzy_match":
                if value == "N/A":
                    # Special handling for N/A (unachievable tasks)
                    # First try exact match with "N/A"
                    exact_score = self.exact_match(ref=value, pred=agent_answer)
                    score *= exact_score
                    
                    if exact_score == 1.0:
                        explanations.append(f"✅ N/A exact match: '{agent_answer}' = 'N/A'")
                    else:
                        # If exact match fails, try ua_match with string_note
                        string_note = eval_config.get("string_note", "")
                        if string_note:
                            ua_score, ua_explanation = self.ua_match(
                                ref=string_note,
                                pred=agent_answer,
                                intent=intent
                            )
                            # Override the 0 score from exact_match
                            score = 1.0 * ua_score
                            explanations.append(ua_explanation)
                        else:
                            explanations.append("❌ N/A exact match failed, and no string_note available for ua_match")
                            logging.warning("N/A reference but no string_note provided")
                else:
                    if isinstance(value, list):
                        for reference in value:
                            step_score, step_explanation = self.fuzzy_match(
                                ref=reference, 
                                pred=agent_answer, 
                                intent=intent
                            )
                            score *= step_score
                            explanations.append(step_explanation)
                    else:
                        step_score, step_explanation = self.fuzzy_match(
                            ref=value, 
                            pred=agent_answer, 
                            intent=intent
                        )
                        score *= step_score
                        explanations.append(step_explanation)
        
        # Combine all explanations
        full_explanation = "\n".join(explanations) if explanations else "No evaluation step"
        return score, full_explanation


class AndroidURLEvaluator:
    """URL matching evaluator for Android.
    
    This uses WebArena's URL matching logic but gets URL from Android Chrome.
    """
    
    @staticmethod
    def clean_url(url: str) -> str:
        """Clean URL string."""
        url = str(url).rstrip("/")
        return url
    
    @staticmethod
    def parse_url(url: str) -> tuple[str, dict[str, list[str]]]:
        """Parse URL into base path and query parameters."""
        parsed_url = urllib.parse.urlparse(url)
        base_path = parsed_url.netloc + parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)
        return base_path, query
    
    def evaluate(self, current_url: str, eval_config: dict[str, Any]) -> float:
        """Evaluate if current URL matches reference URL.
        
        Args:
            current_url: Current URL from Android Chrome
            eval_config: Evaluation configuration from task config
            
        Returns:
            Score between 0.0 and 1.0
        """
        reference_url = eval_config.get("reference_url", "")
        if not reference_url:
            logging.warning("No reference URL provided for evaluation")
            return 0.0
        
        # Handle multiple possible URLs separated by |OR|
        ref_urls = reference_url.split(" |OR| ")
        ref_urls = [self.clean_url(url) for url in ref_urls]
        
        pred = self.clean_url(current_url)
        
        # Parse URLs
        ref_base_paths = []
        ref_queries = {}
        for ref_url in ref_urls:
            base_path, query = self.parse_url(ref_url)
            ref_base_paths.append(base_path)
            for k, v in query.items():
                if k not in ref_queries:
                    ref_queries[k] = set()
                ref_queries[k].update(v)
        
        pred_base_path, pred_query = self.parse_url(pred)
        
        # Check if any reference base path is in predicted URL
        base_score = float(any(
            ref_base_path in pred_base_path for ref_base_path in ref_base_paths
        ))
        
        # Check query parameters
        query_score = 1.0
        for k, possible_values in ref_queries.items():
            query_score *= float(any(
                possible_ref_value in pred_query.get(k, [])
                for possible_ref_value in possible_values
            ))
        
        score = base_score * query_score
        return score


class AndroidHTMLEvaluator:
    """HTML content evaluator for Android.
    
    This checks if required content exists in the page.
    """
    
    def evaluate(self, page_content: str, eval_config: dict[str, Any], 
                 page_adapter: AndroidPageAdapter) -> float:
        """Evaluate if page contains required content.
        
        Args:
            page_content: HTML content from Android Chrome
            eval_config: Evaluation configuration from task config
            page_adapter: Adapter for accessing Chrome
            
        Returns:
            Score between 0.0 and 1.0
        """
        program_html = eval_config.get("program_html", [])
        if not program_html:
            logging.warning("No HTML checks defined for evaluation")
            return 1.0
        
        score = 1.0
        
        for target in program_html:
            target_url = target.get("url", "")
            required_contents = target.get("required_contents", {})
            
            # Navigate to target URL if needed
            if target_url and target_url != "last":
                page_adapter.goto(target_url)
                page_content = page_adapter.content()
            
            # Check required contents
            if "exact_match" in required_contents:
                ref = required_contents["exact_match"]
                score *= AndroidStringEvaluator.exact_match(ref, page_content)
            
            elif "must_include" in required_contents:
                must_include_list = required_contents["must_include"]
                if isinstance(must_include_list, list):
                    for content in must_include_list:
                        # Handle |OR| syntax
                        content_options = content.split(" |OR| ")
                        cur_score = any(
                            AndroidStringEvaluator.must_include(opt, page_content)
                            for opt in content_options
                        )
                        score *= float(cur_score)
        
        return score


def evaluate_task(env: interface.AsyncEnv, task_config: dict[str, Any],
                  agent_answer: str = None) -> tuple[float, str]:
    """Evaluate a WebArena task in Android environment.
    
    This is the main evaluation function that routes to appropriate evaluators.
    
    Args:
        env: ScenDroid environment
        task_config: Task configuration dict
        agent_answer: Agent's final answer (for string_match tasks)
        
    Returns:
        tuple: (score, explanation) where score is between 0.0 and 1.0
    """
    eval_config = task_config.get("eval", {})
    eval_types = eval_config.get("eval_types", [])
    intent = task_config.get("intent", "")
    
    # Create page adapter
    page_adapter = AndroidPageAdapter(env)
    
    score = 1.0
    explanations = []
    
    for eval_type in eval_types:
        if eval_type == "string_match":
            if agent_answer is None:
                logging.warning("No agent answer provided for string_match evaluation")
                score *= 0.0
                explanations.append("❌ String match: No answer provided")
            else:
                evaluator = AndroidStringEvaluator()
                step_score, step_explanation = evaluator.evaluate(agent_answer, eval_config, intent)
                score *= step_score
                explanations.append(f"📝 stringmatchevaluation:\n{step_explanation}")
        
        elif eval_type == "url_match":
            current_url = page_adapter.url
            evaluator = AndroidURLEvaluator()
            step_score = evaluator.evaluate(current_url, eval_config)
            score *= step_score
            ref_url = eval_config.get("reference_url", "")
            if step_score == 1.0:
                explanations.append(f"✅ URL match: '{current_url}' matches reference '{ref_url}'")
            else:
                explanations.append(f"❌ URL match failed: '{current_url}' does not match reference '{ref_url}'")
        
        elif eval_type == "program_html":
            page_content = page_adapter.content()
            evaluator = AndroidHTMLEvaluator()
            step_score = evaluator.evaluate(page_content, eval_config, page_adapter)
            score *= step_score
            if step_score == 1.0:
                explanations.append(f"✅ HTML content check: All conditions satisfied")
            else:
                explanations.append(f"❌ HTML content check failed: Some conditions not satisfied")
        
        else:
            logging.warning(f"Unknown evaluation type: {eval_type}")
            score *= 0.0
            explanations.append(f"❌ Unknown evaluation type: {eval_type}")
    
    full_explanation = "\n\n".join(explanations) if explanations else "No evaluation step"
    return score, full_explanation

