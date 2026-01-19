import json
import os
import shlex
import sys
import requests
from typing import Dict, Any, Optional, Tuple

from .util import env_required

SYSTEM_PROMPT = (
    "You are StackFix, an agent that proposes minimal safe patches to fix a failing command. "
    "Return ONLY a single JSON object in the assistant message content, with keys: "
    "summary (string), confidence (0-1 number), patch_unified_diff (string), "
    "rerun_command (array of strings). "
    "No markdown, no backticks, no extra text. "
    "The patch must be a valid git unified diff that starts with: "
    "diff --git a/<path> b/<path>, includes --- a/<path>, +++ b/<path>, and hunk headers "
    "with ranges like @@ -1,2 +1,8 @@ (no bare @@ lines)."
)

PROMPT_MODE_SYSTEM_PROMPT = (
    "You are StackFix, a helpful AI coding assistant. "
    "Answer the user's question directly and concisely. "
    "If asked about code, provide clear explanations. "
    "If asked to modify code, explain what changes would be needed. "
    "Keep responses focused and practical."
)

STRICT_DIFF_PROMPT = (
    "Your diff was invalid. Return a valid git unified diff with proper @@ ranges. "
    "Return ONLY a single JSON object in the assistant message content with keys: "
    "summary, confidence, patch_unified_diff, rerun_command. "
    "patch_unified_diff MUST be a valid git unified diff only (no Begin Patch markers), "
    "starting with: diff --git a/<path> b/<path>, including ---/+++ lines, and hunk headers "
    "with ranges like @@ -1,2 +1,8 @@. Do NOT use bare @@. "
    "Example hunk header: @@ -1,2 +1,2 @@. No extra text."
)

_ENDPOINT_LOGGED = False


def _log_endpoint_once(url: str) -> None:
    global _ENDPOINT_LOGGED
    if _ENDPOINT_LOGGED:
        return
    _ENDPOINT_LOGGED = True
    print(f"[stackfix] Using model endpoint: {url}", file=sys.stderr)


def _is_debug() -> bool:
    return os.environ.get("STACKFIX_DEBUG") == "1"


def _redact_secrets(text: str) -> str:
    api_key = os.environ.get("MODEL_API_KEY")
    if api_key:
        text = text.replace(api_key, "[REDACTED]")
    for token_key in ["api_key", "apikey", "token", "authorization", "bearer"]:
        text = text.replace(token_key, f"{token_key[:2]}***")
    return text


def _debug_log(msg: str) -> None:
    if _is_debug():
        print(f"[stackfix][debug] {msg}", file=sys.stderr)


def _model_request_payload(context: Dict[str, Any], system_prompt: str = SYSTEM_PROMPT) -> Dict[str, Any]:
    max_tokens = int(os.environ.get("MODEL_MAX_TOKENS", "2000"))
    
    # For prompt mode, use plain text format and simpler prompt
    is_prompt_mode = context.get("mode") == "prompt"
    if is_prompt_mode and system_prompt == SYSTEM_PROMPT:
        system_prompt = PROMPT_MODE_SYSTEM_PROMPT
    
    # Build user message - for prompt mode, just send the prompt text
    if is_prompt_mode:
        user_content = context.get("prompt", "")
        if context.get("agent_instructions"):
            user_content = f"Project context:\n{context['agent_instructions']}\n\nUser question: {user_content}"
    else:
        user_content = json.dumps(context)
    
    payload = {
        "model": env_required("MODEL_NAME"),
        "temperature": 0.2,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    }
    # Only request JSON format for non-prompt mode
    if not is_prompt_mode and os.environ.get("STACKFIX_NO_RESPONSE_FORMAT") != "1":
        payload["response_format"] = {"type": "json_object"}
    return payload


def _call_direct(context: Dict[str, Any], system_prompt: str = SYSTEM_PROMPT) -> Dict[str, Any]:
    base_url = env_required("MODEL_BASE_URL").rstrip("/")
    api_key = env_required("MODEL_API_KEY")
    if base_url.endswith("/v1"):
        url = f"{base_url}/chat/completions"
    else:
        url = f"{base_url}/v1/chat/completions"
    _log_endpoint_once(url)
    payload = _model_request_payload(context, system_prompt=system_prompt)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    _debug_log(f"HTTP status: {resp.status_code}")
    resp.raise_for_status()
    raw_text = resp.text
    _debug_log(f"Raw response (first 500 chars): { _redact_secrets(raw_text[:500]) }")
    data = resp.json()
    content = _extract_content(data)
    return _parse_agent_response(content)


def _call_modal(endpoint: str, context: Dict[str, Any], system_prompt: str = SYSTEM_PROMPT) -> Dict[str, Any]:
    payload = _model_request_payload(context, system_prompt=system_prompt)
    resp = requests.post(endpoint, json=payload, timeout=60)
    _debug_log(f"HTTP status: {resp.status_code}")
    resp.raise_for_status()
    raw_text = resp.text
    _debug_log(f"Raw response (first 500 chars): { _redact_secrets(raw_text[:500]) }")
    data = resp.json()
    content = data.get("content") or data.get("response") or data
    if isinstance(content, dict):
        return _validate_agent_json(content)
    return _parse_agent_response(content)


def _parse_agent_response(content: str) -> Dict[str, Any]:
    parsed: Optional[Dict[str, Any]] = None
    warning: Optional[str] = None
    if content is None:
        return _fallback_response("", "Agent returned empty content")
    try:
        parsed = json.loads(content)
    except Exception:
        warning = "Agent response was not valid JSON; falling back to raw content"
        return _fallback_response(content, warning)
    return _validate_agent_json(parsed, raw_content=content)


def _extract_content(data: Dict[str, Any]) -> str:
    def _get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    choices = _get(data, "choices")
    if isinstance(choices, list) and choices:
        choice = choices[0]
        message = _get(choice, "message")
        if message is not None:
            content = _get(message, "content")
            if isinstance(content, list):
                parts = []
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        parts.append(part["text"])
                if parts:
                    _debug_log("Parsed content from message.content list")
                    return "".join(parts)
            if content is not None and content.strip():
                _debug_log("Parsed content from message.content")
                return content
            # Check for reasoning_content (used by some models like Nebius)
            reasoning_content = _get(message, "reasoning_content")
            if reasoning_content is not None and str(reasoning_content).strip():
                _debug_log("Parsed content from message.reasoning_content")
                return str(reasoning_content)
            tool_calls = _get(message, "tool_calls")
            if isinstance(tool_calls, list) and tool_calls:
                fn = _get(tool_calls[0], "function", {})
                args = _get(fn, "arguments")
                if args:
                    _debug_log("Parsed content from message.tool_calls.function.arguments")
                    return args
        text = _get(choice, "text")
        if text is not None:
            _debug_log("Parsed content from choice.text")
            return text
    keys = list(data.keys()) if isinstance(data, dict) else dir(data)
    raise RuntimeError(f"Agent returned no content to parse; top-level keys: {keys}")


def _normalize_rerun_command(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v is not None]
    if isinstance(value, str):
        try:
            return shlex.split(value)
        except Exception:
            return [value]
    return [str(value)]


def _coerce_confidence(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except Exception:
            return None
    return None


def _fallback_response(content: str, warning: Optional[str]) -> Dict[str, Any]:
    return {
        "summary": content.strip(),
        "confidence": None,
        "patch_unified_diff": "",
        "rerun_command": [],
        "_raw_content": content,
        "_warning": warning,
    }


def _validate_agent_json(parsed: Dict[str, Any], raw_content: Optional[str] = None) -> Dict[str, Any]:
    if not isinstance(parsed, dict):
        return _fallback_response(raw_content or str(parsed), "Agent JSON was not an object")

    summary = parsed.get("summary")
    if summary is None:
        summary = ""
    summary = str(summary)

    patch = parsed.get("patch_unified_diff") or ""
    if patch is None:
        patch = ""
    patch = str(patch)

    rerun = _normalize_rerun_command(parsed.get("rerun_command"))
    confidence = _coerce_confidence(parsed.get("confidence"))

    return {
        "summary": summary,
        "confidence": confidence,
        "patch_unified_diff": patch,
        "rerun_command": rerun,
        "_raw_content": raw_content,
        "_warning": None,
    }


def _is_valid_unified_diff(diff_text: str) -> bool:
    if not isinstance(diff_text, str):
        return False
    if "diff --git " not in diff_text or "--- " not in diff_text or "+++ " not in diff_text:
        return False
    lines = diff_text.splitlines()
    has_hunk = False
    for line in lines:
        if line.startswith("@@"):
            if not line.startswith("@@ -"):
                return False
            if not _is_valid_hunk_header(line):
                return False
            has_hunk = True
    return has_hunk


def _is_valid_hunk_header(line: str) -> bool:
    import re
    return re.match(r"^@@ -\d+(,\d+)? \+\d+(,\d+)? @@", line) is not None


def call_agent(context: Dict[str, Any]) -> Dict[str, Any]:
    endpoint = os.environ.get("STACKFIX_ENDPOINT")
    if endpoint:
        result = _call_modal(endpoint, context)
    else:
        result = _call_direct(context)

    patch = result.get("patch_unified_diff", "")
    if _is_valid_unified_diff(patch):
        return result

    _debug_log("Invalid patch format; retrying once with strict diff prompt")
    if endpoint:
        result = _call_modal(endpoint, context, system_prompt=STRICT_DIFF_PROMPT)
    else:
        result = _call_direct(context, system_prompt=STRICT_DIFF_PROMPT)
    patch = result.get("patch_unified_diff", "")
    if _is_valid_unified_diff(patch):
        return result
    _debug_log("Agent returned invalid unified diff after retry; passing to fallback applier")
    return result
