from google.adk.tools import FunctionTool
from .jobspy_tools import (
    scrape_jobs_tool,
    get_supported_countries,
    get_supported_sites,
    get_job_search_tips,
)

jobspy_tools = [
    FunctionTool(scrape_jobs_tool),
    FunctionTool(get_supported_countries),
    FunctionTool(get_supported_sites),
    FunctionTool(get_job_search_tips),
]
