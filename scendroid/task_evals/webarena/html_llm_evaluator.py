"""LLM-assisted HTML content evaluation for WebArena tasks.

This module provides intelligent evaluation of HTML content using LLM,
which can handle cases where the content is semantically correct but
uses different wording than the exact reference.
"""

import os
import re
import openai
from typing import Any, Optional
from absl import logging


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


def extract_relevant_context(html_content: str, keywords: list[str], 
                            context_chars: int = 200) -> list[str]:
    """Extract relevant context snippets containing keywords from HTML.
    
    Args:
        html_content: Full HTML content
        keywords: List of keywords to search for
        context_chars: Number of characters to include around each keyword
        
    Returns:
        List of context snippets
    """
    html_lower = html_content.lower()
    contexts = []
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Find all occurrences
        start = 0
        found_positions = []
        while True:
            pos = html_lower.find(keyword_lower, start)
            if pos == -1:
                break
            found_positions.append(pos)
            start = pos + 1
        
        # Extract context around each occurrence
        for pos in found_positions[:3]:  # Limit to first 3 occurrences
            context_start = max(0, pos - context_chars)
            context_end = min(len(html_content), pos + len(keyword) + context_chars)
            context = html_content[context_start:context_end]
            
            # Clean HTML tags for readability
            context_clean = re.sub(r'<[^>]+>', ' ', context)
            context_clean = re.sub(r'\s+', ' ', context_clean).strip()
            
            if context_clean and context_clean not in contexts:
                contexts.append(context_clean)
    
    return contexts[:5]  # Return at most 5 contexts


def llm_html_content_match(
    html_content: str,
    required_content: list[str],
    task_intent: str,
    page_url: str = ""
) -> tuple[float, str]:
    """Use LLM to evaluate if HTML content matches required content.
    
    This is more flexible than exact string matching, as it can understand
    semantic equivalence even when wording differs.
    
    Args:
        html_content: Full HTML content from the page
        required_content: List of content that must be present
        task_intent: The task goal/intent
        page_url: URL of the page (for context)
        
    Returns:
        tuple: (score, explanation) where score is 0.0 or 1.0
    """
    # Extract relevant contexts
    all_keywords = []
    for content in required_content:
        all_keywords.extend(content.lower().split())
    
    contexts = extract_relevant_context(html_content, all_keywords, context_chars=300)
    
    if not contexts:
        return 0.0, "❌ LLMjudge: No relevant content found on the page"
    
    # Prepare context for LLM (limit total length)
    context_text = "\n\n".join(contexts[:5])  # Max 5 contexts
    if len(context_text) > 3000:  # Limit to ~3000 chars
        context_text = context_text[:3000] + "..."
    
    # Build prompt
    required_list = "\n".join(f"  - {c}" for c in required_content)
    
    message = f"""Task: {task_intent}

Page URL: {page_url}

Required content on the page:
{required_list}

Relevant excerpts from the page:
{context_text}

Question: Do the page excerpts show that the required content is present on the page?
Consider semantic meaning, not just exact wording. For example:
- "bruxism night guard" and "jaw muscles" together satisfy "jaw bruxism"
- "dental guard" can satisfy "mouth guard"
- "teeth grinding guard" can satisfy "bruxism guard"

Please provide your response in the following format:
Judgement: [yes/no]
Reasoning: [Explain in 1-2 sentences why the required content is or is not present, considering semantic equivalence]
"""

    messages = [
        {"role": "system", "content": "You are a helpful assistant evaluating whether web page content matches requirements."},
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
        if "judgement: yes" in response_lower or "judgment: yes" in response_lower:
            return 1.0, f"🤖 LLMjudge: Content matches - {reasoning}"
        else:
            return 0.0, f"🤖 LLMjudge: Content does not match - {reasoning}"
            
    except Exception as e:
        logging.error(f"LLM HTML evaluation failed: {e}")
        return 0.0, f"⚠️ LLM call failed ({e}), unable to perform semantic evaluation"


def hybrid_html_evaluation(
    html_content: str,
    required_content: list[str],
    task_intent: str,
    page_url: str = ""
) -> tuple[float, str]:
    """Hybrid evaluation: exact match first, then LLM fallback.
    
    This combines the speed of exact matching with the intelligence of LLM.
    
    Args:
        html_content: Full HTML content from the page
        required_content: List of content that must be present
        task_intent: The task goal/intent
        page_url: URL of the page (for context)
        
    Returns:
        tuple: (score, explanation)
    """
    from scendroid.task_evals.webarena.webarena_evaluator import AndroidStringEvaluator
    
    explanations = []
    all_exact_match = True
    html_lower = html_content.lower()
    
    # Try exact match first
    for content in required_content:
        exact_match = AndroidStringEvaluator.must_include(content, html_content)
        if exact_match:
            explanations.append(f"✅ Exact match: '{content}' is present on the page")
        else:
            all_exact_match = False
            # Check if words exist separately
            words = content.lower().split()
            words_found = [w for w in words if w in html_lower]
            
            if len(words_found) == len(words):
                explanations.append(f"⚠️ All words of '{content}' are present on the page: {words_found}")
                explanations.append(f"    → Proceeding with LLM-based semantic evaluation...")
            else:
                missing = [w for w in words if w not in html_lower]
                explanations.append(f"❌ Missing words from '{content}': {missing}")
    
    # If all exact matches, no need for LLM
    if all_exact_match:
        return 1.0, "\n".join(explanations)
    
    # Otherwise, use LLM for semantic matching
    llm_score, llm_explanation = llm_html_content_match(
        html_content, required_content, task_intent, page_url
    )
    
    explanations.append("")
    explanations.append(llm_explanation)
    
    return llm_score, "\n".join(explanations)

