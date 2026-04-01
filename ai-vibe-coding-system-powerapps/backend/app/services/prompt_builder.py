from typing import Any

from app.schemas import AppMode


SYSTEM_MESSAGE = """
You are a senior Microsoft PowerApps architect and formula expert.
Your task is to convert user intent into valid PowerApps building blocks.

Rules:
1) Return ONLY valid JSON.
2) Never wrap the JSON in markdown code fences.
3) Use this exact schema:
{
  "fields": [
    {"name": "FieldName", "type": "text|number|date|dropdown|checkbox|email|phone|multiline"}
  ],
  "formula": "PowerApps formula text",
  "explanation": "Short optional explanation"
}
4) Ensure formula is syntactically plausible for PowerApps Patch/Set/UpdateContext usage.
5) If mode is fix_powerapps_error, prioritize corrected formula and include minimal fields when unknown.
6) If user asks for fields, include them in fields array with best-fit types.
""".strip()


def build_user_prompt(mode: AppMode, prompt: str, context: dict[str, Any] | None) -> str:
    if mode == AppMode.GENERATE_FORMULA:
        return (
            "Mode: generate_formula\n"
            "Goal: produce fields and a PowerApps formula from the request.\n"
            f"User prompt: {prompt}\n"
            f"Context: {context or {}}"
        )

    error_text = ""
    existing_formula = ""
    if context:
        error_text = str(context.get("error_message", ""))
        existing_formula = str(context.get("existing_formula", ""))

    return (
        "Mode: fix_powerapps_error\n"
        "Goal: fix the PowerApps issue and return corrected JSON output.\n"
        f"User prompt: {prompt}\n"
        f"Existing formula: {existing_formula}\n"
        f"Error details: {error_text}\n"
        f"Context: {context or {}}"
    )
