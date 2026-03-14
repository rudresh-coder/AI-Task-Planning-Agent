import os
from pathlib import Path
import json
from crewai import Agent, Task, Crew
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))


def _strip_code_fence(raw: str) -> str:
    text = raw.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    return text


def generate_plan(user_goal: str) -> dict:
    llm_model = os.getenv("MODEL", "groq/llama-3.1-8b-instant")

    planner_agent = Agent(
        role="Task Planning Agent",
        goal="Break a high-level user goal into clear, actionable tasks",
        backstory=(
            "You are an expert task planner. "
            "You take a broad goal and decompose it into logical, executable steps."
        ),
        llm=llm_model,
        verbose=True,
    )

    execution_agent = Agent(
        role="Task Execution Agent",
        goal="Execute planned tasks and generate meaningful outputs",
        backstory=(
            "You are responsible for executing tasks step-by-step "
            "and producing clear, useful results."
        ),
        llm=llm_model,
        verbose=True,
    )

    reviewer_agent = Agent(
        role="Review Agent",
        goal="Review outputs for clarity and conciseness",
        backstory=(
            "You improve clarity by removing fluff while preserving important details."
        ),
        llm=llm_model,
        verbose=True,
    )

    formatter_agent = Agent(
        role="Formatting Agent",
        goal="Format content into clean sections with headings and bullet points",
        backstory=(
            "You are an expert technical editor who produces well-structured output."
        ),
        llm=llm_model,
        verbose=True,
    )

    planning_task = Task(
        description=(
            f"Given the user goal: '{user_goal}', "
            "create a SIMPLE task plan.\n\n"
            "Rules:\n"
            "- Return ONLY a numbered list\n"
            "- Each item must be a single clear task\n"
            "- DO NOT use sub-points or explanations\n"
            "- Keep it concise (6–8 tasks max)"
        ),
        expected_output=("A clean numbered list of tasks with no sub-points."),
        agent=planner_agent,
    )

    execution_task = Task(
        description=(
            f"For the goal '{user_goal}', generate content for a plan.\n\n"
            "Provide the following items (content only):\n"
            "- Agenda items\n"
            "- Checklist items\n"
            "- Timeline items\n\n"
            "Rules:\n"
            "- Do NOT format as JSON\n"
            "- Do NOT use markdown headings\n"
            "- Keep items short and actionable"
        ),
        expected_output="Plain text containing agenda, checklist, and timeline items.",
        agent=execution_agent,
    )

    review_task = Task(
        description=(
            "Review the execution output produced previously.\n\n"
            "Rules:\n"
            "- Remove unnecessary explanations\n"
            "- Improve clarity and structure\n"
            "- Preserve important details\n"
            "- Do NOT add new content\n"
            "- Do NOT try to enforce any final formatting"
        ),
        expected_output=("A refined and cleaner version of the execution output."),
        agent=reviewer_agent,
    )

    formatting_task = Task(
        description=(
            "Convert the reviewed content into ONLY valid JSON.\n\n"
            "HARD RULES:\n"
            "- Output MUST start with '{' and end with '}'\n"
            "- No ``` fences, no extra text\n"
            "- NO objects, NO nested arrays\n"
            "- Values must be ARRAYS OF STRINGS ONLY\n\n"
            "Exact schema:\n"
            "{\n"
            '  "agenda": ["string", "string"],\n'
            '  "checklist": ["string", "string"],\n'
            '  "timeline": ["string", "string"]\n'
            "}\n\n"
            "Formatting rules:\n"
            "- checklist strings should be like 'Category: item'\n"
            "- timeline strings should include a time/period prefix"
        ),
        expected_output='{"agenda":[...],"checklist":[...],"timeline":[...]}',
        agent=formatter_agent,
    )

    crew = Crew(
        agents=[planner_agent, execution_agent, reviewer_agent, formatter_agent],
        tasks=[planning_task, execution_task, review_task, formatting_task],
        verbose=True,
    )

    result = crew.kickoff()
    raw = _strip_code_fence(str(result))

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model did not return valid JSON. Output: {result}") from exc

    is_valid_schema = (
        isinstance(data, dict)
        and set(data.keys()) == {"agenda", "checklist", "timeline"}
        and all(
            isinstance(data[key], list)
            and all(isinstance(item, str) for item in data[key])
            for key in data
        )
    )

    if not is_valid_schema:
        raise ValueError(
            "Invalid JSON schema returned: "
            + json.dumps(data, indent=2, ensure_ascii=False)
        )

    return data
