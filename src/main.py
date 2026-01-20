from crewai import Agent, Task, Crew
from dotenv import load_dotenv

load_dotenv()

# 1.Planner Agent
planner_agent = Agent(
    role="Research Planner Agent",
    goal="Break a high-level goal into actionable tasks",
    backstory=(
        "You are an expert research planner."
        "You decide what subtopics must be researched to fully understand a topic."
    ),
    verbose=True
)

# 2. Research Agent
research_agent = Agent(
    role="Research Agent",
    goal="Research a topic and produce a clear summary",
    backstory=(
        "You are a research expert who gathers information and explains it clearly."
    ),
    verbose=True
)

#Task 1: Planing Task
planning_task = Task(
    description=(
        "Given the research topic: 'Agentic AI in Education',"
        "list the key subtopics that should be researched."
    ),
    expected_output=(
        "A numbered list of research subtopics."
    ),
    agent=planner_agent
)

#Task 2: Research Task
research_task = Task(
    description=(
        "Research the topic 'Agentic AI Education' based on the planned subtopics "
        "and provide a concise summary."
    ),
    expected_output=(
        "A structured summary explaining the topic clearly."
    ),
    agent=research_agent
)

#Crew Setup
crew = Crew(
    agents=[planner_agent, research_agent],
    tasks=[planning_task, research_task],
    verbose=True
)

#Run the crew
result = crew.kickoff()

print("\n================ FINAL OUTPUT ================\n")
print(result)