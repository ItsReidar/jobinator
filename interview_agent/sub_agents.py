from google.adk.agents import Agent
from .linkedin_tool.tools import jobspy_tools
from .config import config

research_agent = Agent(
    name="research_agent",
    model=config.worker_model,
    description="Researches job opportunities based on user preferences.",
    instruction="""
    You are a job research assistant. Your goal is to find suitable job openings for the user based on their preferences shared below.
    Use the scrape_jobs_tool to find jobs on the web.
    You can ask the user for their preferences like job title, location, and keywords.
    Use get_supported_countries, get_supported_sites, and get_job_search_tips to get more information about the job search capabilities.
    Present the findings to the user in a clear and structured way.

    {user_profile}

    After looking for the jobs and presenting the summary, if the user wants to apply for any of the jobs, hand over the job details to the application_writer_agent to help draft the application.
    """,
    tools=jobspy_tools,
)

application_writer_agent = Agent(
    name="application_writer_agent",
    model=config.worker_model,
    description="Writes job applications, cover letters, and resumes.",
    instruction="""
    You are a professional application writer. Your task is to help the user write compelling job applications.
    You can write cover letters, and resumes.
    Ask the user for the job description and their personal information to tailor the application.
    """,
)
