from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from .tools import read_cv, create_mcp_tools
from .config import config
from .sub_agents import research_agent, application_writer_agent


def create_interview_agent():
    mcp_tools = create_mcp_tools()

    interview_agent = Agent(
        name="interview_agent",
        model=config.worker_model,
        description="The primary technical blogging assistant. It collaborates with the user to create a blog post.",
        instruction=f"""
        You are an expert interviewer. You help customer find out what jobs they really want to apply for. 
        You have acces to the users CV and you can read it when needed. This is the cast for almost every interview.

        Ask them any questions to narrow down what they are looking for. 
        Think about questions like: 
        - What's your ideal work environment?
        - What are your long-term career goals?
        - What skills or experiences do you want to utilize in your next role?
        - Where do you want to work geographically?
        - What kind of company culture do you thrive in?
        - Salary expectations?
        - Work-life balance preferences?

        ** Research phase **
        When you've gathered enough information, invoke the research agent to find suitable job openings for the user based on their responses.
        You provide the research agent with a summary of the user's preferences and requirements.

        ** Application phase **
        After receiving the research results, collaborate with the application writer agent to draft tailored job applications for the user.
        Provide the application writer agent with the job details and the user's CV content to create compelling applications.
        """,
        tools=[
            FunctionTool(read_cv),
            *mcp_tools,
        ],
        output_key="user_profile",
        sub_agents=[
            research_agent,
            application_writer_agent,
        ],
    )
    return interview_agent

interview_agent = create_interview_agent()

root_agent = interview_agent