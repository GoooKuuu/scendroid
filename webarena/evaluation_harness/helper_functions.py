"""Implements helper functions to assist evaluation cases where other evaluators are not suitable."""
import json
import os
from typing import Any
from urllib.parse import urlparse

import openai
import requests
from playwright.sync_api import CDPSession, Page

from browser_env.env_config import (
    ACCOUNTS,
    GITLAB,
    MAP,
    REDDIT,
    SHOPPING,
    SHOPPING_ADMIN,
    WIKIPEDIA,
)

# Initialize LLM API client
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


def shopping_get_auth_token() -> str:
    # disabled proxy, to avoid using http_proxy/https_proxy from system environment variables
    response = requests.post(
        url=f"{SHOPPING}/rest/default/V1/integration/admin/token",
        headers={"content-type": "application/json"},
        data=json.dumps(
            {
                "username": ACCOUNTS["shopping_site_admin"]["username"],
                "password": ACCOUNTS["shopping_site_admin"]["password"],
            }
        ),
        proxies={"http": None, "https": None},  # disabled proxy
    )
    token: str = response.json()
    return token


def shopping_get_latest_order_url() -> str:
    """Get the latest order url from the shopping website."""

    header = {
        "Authorization": f"Bearer {shopping_get_auth_token()}",
        "Content-Type": "application/json",
    }

    params = {
        "searchCriteria[sortOrders][0][field]": "created_at",
        "searchCriteria[sortOrders][0][direction]": "DESC",
        "searchCriteria[pageSize]": "1",
    }

    response = requests.get(
        f"{SHOPPING}/rest/V1/orders", params=params, headers=header,
        proxies={"http": None, "https": None},  # disabled proxy
    )
    assert response.status_code == 200
    response_obj = response.json()["items"][0]
    order_id = int(response_obj["increment_id"])
    order_url = f"{SHOPPING}/sales/order/view/order_id/{order_id}/"
    return order_url


def shopping_get_sku_latest_review_author(sku: str) -> str:
    """Get the latest review for shopping admin."""
    header = {
        "Authorization": f"Bearer {shopping_get_auth_token()}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"{SHOPPING}/rest/V1/products/{sku}/reviews", headers=header,
        proxies={"http": None, "https": None},  # disabled proxy
    )
    assert response.status_code == 200
    response_obj = response.json()
    if len(response_obj) == 0:
        return ""
    author: str = response_obj[-1]["nickname"]
    return author


def shopping_get_sku_latest_review_rating(sku: str) -> str:
    """Get the latest review for shopping admin."""
    header = {
        "Authorization": f"Bearer {shopping_get_auth_token()}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"{SHOPPING}/rest/V1/products/{sku}/reviews", headers=header,
        proxies={"http": None, "https": None},  # disabled proxy
    )
    assert response.status_code == 200
    response_obj = response.json()
    if len(response_obj) == 0:
        return ""
    assert response_obj[0]["ratings"][0]["rating_name"] == "Rating"
    rating: str = str(response_obj[-1]["ratings"][0]["percent"])
    return rating


def reddit_get_post_url(url: str) -> str:
    """Get the post url"""
    # Url is http://domain/f/subreddit/post_id/...
    # get domain, subreddit, post_id
    domain = urlparse(url).netloc
    tok_url = urlparse(url).path.split("/")
    # not a valid post/comment url, return the url as is
    if len(tok_url) < 4:
        return url
    if tok_url[1] != "f":
        return url
    subreddit = urlparse(url).path.split("/")[2]
    post_id = urlparse(url).path.split("/")[3]
    scheme = urlparse(url).scheme
    post_url = f"{scheme}://{domain}/f/{subreddit}/{post_id}/"
    return post_url


def gitlab_get_project_memeber_role(page: Page, account_name: str) -> str:
    # get the account index
    try:
        account_idx = page.evaluate(
            f"""(() => {{
                const elements = document.querySelectorAll("td[data-label='Account'] span.gl-avatar-labeled-sublabel");
                let index = -1;  // Default value if not found

                for(let i = 0; i < elements.length; i++) {{
                    if(elements[i].outerText === '@{account_name}') {{
                        index = i;
                        break;
                    }}
                }}

                return index;
            }})()"""
        )

        # get the role
        role: str = page.evaluate(
            f"""(() => {{
                return document.querySelectorAll("td.col-max-role span")[{account_idx}].outerText;
            }})()"""
        )
    except Exception:
        role = ""

    return role


def llm_fuzzy_match(pred: str, reference: str, question: str) -> tuple[float, str]:
    """Check whether the prediction matches the reference with Gemini-2.5-Pro
    
    Returns:
        tuple: (score, explanation) where score is 0.0 or 1.0, and explanation is the reasoning
    """
    messages: list[dict[str, Any]] = []
    # construct the question to ask
    message = "Help a teacher to grade the answer of a student given a question. Keep in mind that the student may use different phrasing or wording to answer the question. The goal is to evaluate whether the answer is semantically equivalent to the reference answer.\n"
    message += f"question: {question}\n"
    message += f"reference answer: {reference}\n"
    message += "all the string 'N/A' that you see is a special sequence that means 'not achievable'\n"
    message += f"student answer: {pred}\n"
    message += "\nPlease provide your response in the following format:\n"
    message += "Judgement: [correct/incorrect/partially correct]\n"
    message += "Reasoning: [Explain why you made this judgement in 1-2 sentences]"
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": message},
    ]

    try:
        client = _get_gemini_client()
        response = client.chat.completions.create(
            model="gemini-2.5-pro",
        messages=messages,
        temperature=0,
        max_tokens=768,
        top_p=1.0,
        )
        
        # Debug: print response structure
        print(f"🔍 [DEBUG] LLM Response: {response}")
        
        # Check if response has choices
        if not response.choices or len(response.choices) == 0:
            raise ValueError(f"Empty choices in response: {response}")
        
        response_text = response.choices[0].message.content
        
        # Check if content is None
        if response_text is None:
            raise ValueError(f"None content in response: {response.choices[0]}")
        
        response_lower = response_text.lower()
        
        # Extract reasoning (use case-insensitive split)
        reasoning = response_text
        if "reasoning:" in response_lower:
            # Split using lowercase version, then strip
            parts = response_lower.split("reasoning:", 1)
            if len(parts) > 1:
                # Find the position in original text
                pos = response_text.lower().find("reasoning:")
                if pos != -1:
                    reasoning = response_text[pos + len("reasoning:"):].strip()
        elif "explanation:" in response_lower:
            parts = response_lower.split("explanation:", 1)
            if len(parts) > 1:
                pos = response_text.lower().find("explanation:")
                if pos != -1:
                    reasoning = response_text[pos + len("explanation:"):].strip()
        
        # Determine score
        if "partially correct" in response_lower or "incorrect" in response_lower:
            return 0.0, f"🤖 LLM judge: mismatch - {reasoning}"
        else:
            return 1.0, f"🤖 LLMjudge: match - {reasoning}"
    except Exception as e:
        fallback_msg = f"⚠️ LLM call failed ({e}), falling back to exact match"
        print(f"❌ [DEBUG] LLM fuzzy_match error: {e}")
        import traceback
        traceback.print_exc()
        is_match = pred.strip().lower() == reference.strip().lower()
        if is_match:
            return 1.0, fallback_msg + " - exact match success"
    else:
            return 0.0, fallback_msg + f" - prediction '{pred}' does not match reference '{reference}'"


def llm_ua_match(pred: str, reference: str, question: str) -> tuple[float, str]:
    """Check whether the prediction identifies the same unachievable reason with Gemini-2.5-Pro
    
    Returns:
        tuple: (score, explanation) where score is 0.0 or 1.0, and explanation is the reasoning
    """
    messages: list[dict[str, Any]] = []
    # construct the question to ask
    message = ""
    message += f"task: {question}\n"
    message += f"actual unachievable reason: {reference}\n"
    message += f"reported unachievable reason: {pred}\n"
    message += (
        "The task described above is inherently unachievable due to the reason specified under 'actual unachievable reason'. "
        "An individual previously attempted this task and was unable to complete it. They provided a reason for their failure, "
        "which is listed under 'reported unachievable reason'. Your role is to review both the actual and reported reasons. "
        "Determine if the reported reason aligns with the actual reason, even if implicitly.\n\n"
        "Please provide your response in the following format:\n"
        "Judgement: [same/different]\n"
        "Reasoning: [Explain why you believe the reported reason does or does not align with the actual reason in 1-2 sentences]"
    )
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": message},
    ]

    try:
        client = _get_gemini_client()
        response = client.chat.completions.create(
            model="gemini-2.5-pro",
        messages=messages,
        temperature=0,
        max_tokens=768,
        top_p=1.0,
        )
        
        # Debug: print response structure
        print(f"🔍 [DEBUG] LLM UA Match Response: {response}")
        
        # Check if response has choices
        if not response.choices or len(response.choices) == 0:
            raise ValueError(f"Empty choices in response: {response}")
        
        response_text = response.choices[0].message.content
        
        # Check if content is None
        if response_text is None:
            raise ValueError(f"None content in response: {response.choices[0]}")
        
        response_lower = response_text.lower()
        
        # Extract reasoning (use case-insensitive extraction)
        reasoning = response_text
        if "reasoning:" in response_lower:
            # Find position in original text
            pos = response_text.lower().find("reasoning:")
            if pos != -1:
                reasoning = response_text[pos + len("reasoning:"):].strip()
        elif "explanation:" in response_lower:
            pos = response_text.lower().find("explanation:")
            if pos != -1:
                reasoning = response_text[pos + len("explanation:"):].strip()
        
        # Determine score
        if "different" in response_lower:
            return 0.0, f"🤖 LLM judge: inconsistent reasons - {reasoning}"
        else:
            return 1.0, f"🤖 LLM judge: consistent reasons - {reasoning}"
    except Exception as e:
        fallback_msg = f"⚠️ LLM call failed ({e}), falling back to containment check"
        print(f"❌ [DEBUG] LLM ua_match error: {e}")
        import traceback
        traceback.print_exc()
        is_match = reference.lower() in pred.lower()
        if is_match:
            return 1.0, fallback_msg + f" - prediction contains reference reason"
    else:
            return 0.0, fallback_msg + f" - prediction '{pred}' does not contain reference reason '{reference}'"


class PseudoPage:
    def __init__(self, original_page: Page, url: str):
        self.url = url
        self.original_page = original_page

    def __getattr__(self, attr: str) -> Any:
        # Delegate attribute access to the original page object
        if attr not in ["url"]:
            return getattr(self.original_page, attr)
        else:
            return getattr(self, attr)
