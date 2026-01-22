import json
from crewai import Agent, Task, Crew
from dotenv import load_dotenv

load_dotenv()

#user input
user_goal = input("\nEnter your goal for the AI Planning & Execution Agent:\n> ")

# 1. PLANNER AGENT
planner_agent = Agent(
    role="Task Planning Agent",
    goal="Break a high-level user goal into clear, actionable tasks",
    backstory=(
        "You are an expert task planner. "
        "You take a broad goal and decompose it into logical, executable steps."
    ),
    verbose=True
)

# 2. EXECUTION AGENT
execution_agent = Agent(
    role="Task Execution Agent",
    goal="Execute planned tasks and generate meaningful outputs",
    backstory=(
        "You are responsible for executing tasks step-by-step "
        "and producing clear, useful results."
    ),
    verbose=True
)

# 3. REVIEW AGENT
reviewer_agent = Agent(
    role="Review Agent",
    goal="Review outputs for clarity and conciseness",
    backstory=(
        "You improve clarity by removing fluff while preserving important details."
    ),
    verbose=True,
)

# 4. FORMATTING AGENT
formatter_agent = Agent(
    role="Formatting Agent",
    goal="Format content into clean sections with headings and bullet points",
    backstory=(
        "You are an expert technical editor who produces well-structured output."
    ),
    verbose=True,
)

# TASK 1: TASK PLANNING
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
    expected_output=(
        "A clean numbered list of tasks with no sub-points."
    ),
    agent=planner_agent
)

# TASK 2: TASK EXECUTION
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


#Task 3
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
    expected_output=(
        "A refined and cleaner version of the execution output."
    ),
    agent=reviewer_agent
)

# Task 4 : Formating agent
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

# CREW SETUP
crew = Crew(
    agents=[planner_agent,
            execution_agent,
            reviewer_agent,
            formatter_agent
            ],
    tasks=[planning_task,
           execution_task,
           review_task,
           formatting_task
           ],
    verbose=True
)

# RUN THE CREW
result = crew.kickoff()

print("\n================ FINAL OUTPUT ================\n")

raw = str(result).strip()

if raw.startswith("```"):
    lines = raw.splitlines()
    # drop first line like ``` or ```json
    lines = lines[1:]
    # drop last fence line if present
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    raw = "\n".join(lines).strip()

try:
    data = json.loads(raw)
except json.JSONDecodeError:
    print(result)
    raise SystemExit(1)

# validate schema strictly
if (
    not isinstance(data, dict)
    or set(data.keys()) != {"agenda", "checklist", "timeline"}
    or not all(isinstance(data[k], list) and all(isinstance(x, str) for x in data[k]) for k in data)
):
    print("Invalid JSON schema returned:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    raise SystemExit(1)

print(json.dumps(data, indent=2, ensure_ascii=False))