# AI Vibe Coding System for PowerApps

A production-ready full-stack Python project that converts natural language into PowerApps-ready structured JSON and formulas.

## Features

- Streamlit frontend for prompt entry and interactive output
- FastAPI backend with clear API contracts and error handling
- AI provider switch: Ollama (local) or OpenAI
- Prompt-engineered system message for PowerApps expert behavior
- Strict JSON schema validation with fallback extraction logic
- Dynamic form rendering from AI-generated field definitions
- Formula generation and PowerApps error-fixing modes
- Loading spinner and robust UI error feedback
- Sample prompts for quick start

## Target JSON Output

The backend enforces this structure:

{
  "fields": [
    {"name": "Name", "type": "text"},
    {"name": "Capacity", "type": "number"}
  ],
  "formula": "PowerApps Patch formula",
  "explanation": "Optional short explanation"
}

## Project Structure

ai-vibe-coding-system-powerapps/
- backend/
  - app/
    - core/config.py
    - services/
      - prompt_builder.py
      - providers.py
      - llm_service.py
    - schemas.py
    - main.py
- frontend/
  - streamlit_app.py
- examples/
  - sample_prompts.md
- requirements.txt
- .env.example
- README.md

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   pip install -r requirements.txt
3. Copy environment template:
   copy .env.example .env
4. Update .env as needed.

## Run Backend

From the project root:

cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Health check:

http://127.0.0.1:8000/health

## Run Frontend

From the project root:

streamlit run frontend/streamlit_app.py

Open the shown URL (usually http://localhost:8501).

## Mode Guide

- Generate Formula
  - Provide natural language requirements (fields + logic)
- Fix PowerApps Error
  - Provide failing formula and error message in context fields

## AI Provider Switching

- In the Streamlit sidebar, choose provider:
  - ollama: local model via OLLAMA_BASE_URL and OLLAMA_MODEL
  - openai: cloud model via OPENAI_API_KEY and OPENAI_MODEL

## API Contract

POST /api/v1/generate

Request body:

{
  "prompt": "Create a form with Name and Capacity fields",
  "mode": "generate_formula",
  "provider": "ollama",
  "context": null
}

Response body:

{
  "fields": [
    {"name": "Name", "type": "text"},
    {"name": "Capacity", "type": "number"}
  ],
  "formula": "Patch(MyList, Defaults(MyList), {Name: txtName.Text, Capacity: Value(txtCapacity.Text)})",
  "explanation": "Creates a new record with Name and numeric Capacity"
}

## Notes

- If the model returns invalid JSON, backend returns a clean 400/502-style error.
- Ollama must be running locally for local inference.
- For production deployment, set restrictive CORS origins and run behind a proper ASGI server/process manager.
