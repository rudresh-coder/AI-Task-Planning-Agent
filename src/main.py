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
        f"Using the task plan created for the goal '{user_goal}', "
        "execute the tasks.\n\n"
        "Rules:\n"
        "- Produce output in EXACTLY three sections:\n"
        " 1. AGENDA\n"
        " 2. CHECKLIST\n"
        " 3. TIMELINE\n"
        "- Use clear headings\n"
        "- Use bullet points\n"
        "- Keep content practical and concise"
    ),
    expected_output=(
        "Three clearly separated sections: AGENDA, CHECKLIST, TIMELINE."
    ),
    agent=execution_agent
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
        "IMPORTANT:\n"
        "- Output MUST start with '{' and end with '}'\n"
        "- Do NOT wrap in ```json fences\n"
        "- Do NOT output any extra text\n\n"
        "Schema:\n"
        "{\n"
        '  "agenda": [string],\n'
        '  "checklist": [string],\n'
        '  "timeline": [string]\n'
        "}\n"
    ),
    expected_output="Valid JSON only with keys agenda, checklist, timeline.",
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
try:
    raw = str(result).strip()

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw.rsplit("\n", 1)[0]

    data = json.loads(raw)
    print(json.dumps(data, indent=2, ensure_ascii=False))
except json.JSONDecodeError:
    print(result)