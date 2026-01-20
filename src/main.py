from crewai import Agent, Task, Crew
from dotenv import load_dotenv

load_dotenv()

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

# TASK 1: TASK PLANNING
planning_task = Task(
    description=(
        "Given the goal: 'Plan and execute a one-day AI workshop for MCA students', "
        "create a SIMPLE task plan. \n\n"
        "Rules:\n"
        "- Return ONLY a numbered list\n"
        "- Each item must be a single clear task\n"
        "- DO NOT use sub-points or explanations\n"
        "- Keep it concise (6-8 tasks max)"
    ),
    expected_output=(
        "A clean numbered list of tasks with no sub-points."
    ),
    agent=planner_agent
)

# TASK 2: TASK EXECUTION
execution_task = Task(
    description=(
        "Execute the planned tasks for organizing a one-day AI workshop.\n\n"
        "Rules:\n"
        "- Produce output in EXACTLY three sections:\n"
        " 1. Agenda: A detailed agenda for the workshop\n"
        " 2. Checklist: A checklist of items to prepare\n"
        " 3. Timeline: A timeline for the day's events\n"
        "- Use clear headings for each section\n"
        "- use bullet points where appropriate\n"
        "- Keep content practical and concise"
    ),
    expected_output=(
        "Three clearly seperated sections: Agenda, Checklist, Timeline."
    ),
    agent=execution_agent
)

# CREW SETUP
crew = Crew(
    agents=[planner_agent, execution_agent],
    tasks=[planning_task, execution_task],
    verbose=True
)

# RUN THE CREW
result = crew.kickoff()

print("\n================ FINAL OUTPUT ================\n")
print(result)
