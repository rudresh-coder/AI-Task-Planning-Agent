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
        "break it down into clear, actionable tasks."
    ),
    expected_output=(
        "A numbered list of well-defined tasks required to achieve the goal."
    ),
    agent=planner_agent
)

# TASK 2: TASK EXECUTION
execution_task = Task(
    description=(
        "Execute the planned tasks for organizing a one-day AI workshop. "
        "Generate structured outputs such as agenda, checklist, and timeline."
    ),
    expected_output=(
        "A structured execution output including agenda, checklist, and timeline."
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
