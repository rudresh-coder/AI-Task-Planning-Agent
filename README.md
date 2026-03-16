# AI Task Planner Agent

A lightweight AI agent app that converts a high-level goal into a clean, structured execution plan with three outputs:
- `agenda`
- `checklist`
- `timeline`

The project supports both a terminal workflow and a modern Streamlit web interface.

## What this project does

Given a user goal (for example, _"Plan a 4-week launch roadmap for my portfolio website"_), the app runs a multi-agent workflow and returns strictly validated JSON in this format:

```json
{
  "agenda": ["..."],
  "checklist": ["..."],
  "timeline": ["..."]
}
```

## Core Architecture

### 1) Multi-agent orchestration
Implemented in [src/planner_service.py](src/planner_service.py):

- `Task Planning Agent` → creates concise high-level tasks
- `Task Execution Agent` → expands plan content
- `Review Agent` → refines and removes fluff
- `Formatting Agent` → converts final content to strict JSON

The workflow is executed via CrewAI `Crew.kickoff()`.

### 2) Output cleanup + validation
Also in [src/planner_service.py](src/planner_service.py):

- `_strip_code_fence(raw)` removes markdown fences if model wraps output in ``` blocks
- JSON parsing with explicit error handling
- strict schema validation:
  - keys must be exactly `agenda`, `checklist`, `timeline`
  - each value must be `list[str]`

### 3) Two entry points

- CLI runner: [src/main.py](src/main.py)
- Web app: [src/streamlit_app.py](src/streamlit_app.py)

## Requirements

- Python 3.10+
- A valid LLM provider/API setup compatible with CrewAI/LiteLLM

Packages used (from [requirements.txt](requirements.txt)):

- `crewai`
- `python-dotenv`
- `streamlit`
- `litellm`

## Setup

1. Clone repo

```bash
git clone <your-repo-url>
cd AI-Task-Planner-Agent
```

2. Create and activate virtual environment

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Configure environment variables

Create a file at **src/.env** (important: this project loads `.env` from the `src` folder):

```env
MODEL=groq/llama-3.1-8b-instant
# Add provider key(s) required by your model backend, e.g.
# GROQ_API_KEY=...
# OPENAI_API_KEY=...
```

## Run the app

### Option A: Terminal mode

```bash
python src/main.py
```

### Option B: Streamlit web app

```bash
streamlit run src/streamlit_app.py
```

## License

Licensed under MIT. See [LICENSE](LICENSE).
