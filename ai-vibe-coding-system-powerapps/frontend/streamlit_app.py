import os
from typing import Any

import requests
import streamlit as st

st.set_page_config(
    page_title="AI Vibe Coding System for PowerApps",
    page_icon="AI",
    layout="wide",
)

API_BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
GENERATE_ENDPOINT = f"{API_BASE_URL}/api/v1/generate"

SAMPLE_PROMPTS = [
    "Create a form with Name and Capacity fields",
    "Create an asset intake form with Asset Name, Purchase Date, and Cost",
    "Generate a Patch formula to save employee details with validation",
    "Fix this PowerApps error: Incompatible types for comparison in If statement",
]


def _render_dynamic_field(field: dict[str, Any]) -> None:
    label = field.get("name", "Unnamed")
    kind = field.get("type", "text")

    if kind in {"text", "email", "phone"}:
        st.text_input(label, key=f"render_{label}_{kind}")
    elif kind == "multiline":
        st.text_area(label, key=f"render_{label}_{kind}")
    elif kind == "number":
        st.number_input(label, key=f"render_{label}_{kind}")
    elif kind == "date":
        st.date_input(label, key=f"render_{label}_{kind}")
    elif kind == "checkbox":
        st.checkbox(label, key=f"render_{label}_{kind}")
    elif kind == "dropdown":
        st.selectbox(label, options=["Option 1", "Option 2", "Option 3"], key=f"render_{label}_{kind}")
    else:
        st.text_input(f"{label} ({kind})", key=f"render_{label}_{kind}")


def _call_backend(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(GENERATE_ENDPOINT, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


st.title("AI Vibe Coding System for PowerApps")
st.caption("Generate PowerApps forms and formulas, or fix formula errors with AI.")

with st.sidebar:
    st.subheader("Configuration")
    provider = st.selectbox("AI Provider", options=["ollama", "openai"], index=0)
    mode = st.radio(
        "Mode",
        options=["generate_formula", "fix_powerapps_error"],
        format_func=lambda x: "Generate Formula" if x == "generate_formula" else "Fix PowerApps Error",
    )

    st.subheader("Sample Prompts")
    for idx, sample in enumerate(SAMPLE_PROMPTS):
        if st.button(f"Use sample {idx + 1}"):
            st.session_state["prompt_input"] = sample

col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("Prompt Input")
    prompt = st.text_area(
        "Describe your requirement",
        value=st.session_state.get("prompt_input", "Create a form with Name and Capacity fields"),
        height=160,
    )
    prompt_text = prompt or ""

    context: dict[str, Any] = {}
    if mode == "fix_powerapps_error":
        context["existing_formula"] = st.text_area("Existing formula", height=120)
        context["error_message"] = st.text_area("Error message", height=100)

    if st.button("Run AI", type="primary"):
        if not prompt_text.strip():
            st.error("Prompt is required.")
        else:
            payload = {
                "prompt": prompt_text,
                "mode": mode,
                "provider": provider,
                "context": context or None,
            }
            with st.spinner("Thinking and generating PowerApps JSON..."):
                try:
                    result = _call_backend(payload)
                    st.session_state["result"] = result
                    st.success("Generated successfully.")
                except requests.HTTPError as exc:
                    detail = "Unknown backend error"
                    try:
                        detail = exc.response.json().get("detail", detail)
                    except Exception:
                        detail = exc.response.text or detail
                    st.error(f"Backend error: {detail}")
                except requests.RequestException as exc:
                    st.error(f"Request failed: {exc}")

with col2:
    st.subheader("Generated Output")
    result = st.session_state.get("result")
    if not result:
        st.info("Run a prompt to see generated form fields and formula.")
    else:
        fields = result.get("fields", [])
        formula = result.get("formula", "")
        explanation = result.get("explanation")

        st.markdown("### Dynamic Form Preview")
        if not fields:
            st.warning("No fields returned.")
        for field in fields:
            _render_dynamic_field(field)

        st.markdown("### PowerApps Formula")
        st.code(formula or "No formula returned.", language="text")

        if explanation:
            st.markdown("### Explanation")
            st.write(explanation)

        st.markdown("### Raw JSON")
        st.json(result)
