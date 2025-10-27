"""Lightweight helpers for running JobSpy job searches.

The original project exposed these helpers through an MCP server.  This module
keeps only the reusable pieces so another agent can call the functions
directly, without needing an MCP runtime.
"""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd

from jobspy import scrape_jobs
from jobspy.model import Country

logger = logging.getLogger(__name__)

# Default configuration
_DEFAULT_SITES = ("indeed", "linkedin", "zip_recruiter", "google")
_VALID_SITES = {
    "linkedin",
    "indeed",
    "glassdoor",
    "zip_recruiter",
    "google",
    "bayt",
    "naukri",
    "bdjobs",
}


def _trim_description(text: str, limit: int = 300) -> str:
    """Keep descriptions readable by trimming extra text."""
    return text if len(text) <= limit else f"{text[:limit]}..."


def scrape_jobs_tool(
    search_term: str,
    *,
    location: Optional[str] = None,
    site_name: Optional[list[str]] = None,
    results_wanted: int = 15,
    job_type: Optional[str] = None,
    is_remote: bool = False,
    hours_old: Optional[int] = None,
    distance: int = 50,
    easy_apply: bool = False,
    country_indeed: str = "usa",
    linkedin_fetch_description: bool = False,
    offset: int = 0,
    verbose: int = 1,
) -> str:
    """Search for jobs using JobSpy and return a formatted summary."""
    logger.info("Starting job search for '%s'", search_term)
    sites = list(site_name) if site_name is not None else list(_DEFAULT_SITES)

    invalid_sites = [site for site in sites if site not in _VALID_SITES]
    if invalid_sites:
        return (
            "Error: invalid site names: "
            f"{invalid_sites}. Valid sites: {sorted(_VALID_SITES)}"
        )

    try:
        jobs_df = scrape_jobs(
            site_name=sites,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            job_type=job_type,
            is_remote=is_remote,
            hours_old=hours_old,
            distance=distance,
            easy_apply=easy_apply,
            country_indeed=country_indeed,
            linkedin_fetch_description=linkedin_fetch_description,
            offset=offset,
            verbose=verbose,
            description_format="markdown",
        )
    except Exception as exc:  # pragma: no cover - passthrough for callers
        logger.exception("Error scraping jobs: %s", exc)
        return f"Error scraping jobs: {exc}"

    if jobs_df.empty:
        logger.info("No jobs found for '%s'", search_term)
        return (
            "No jobs found that match your criteria. "
            "Try adjusting your search parameters."
        )

    results_summary = f"Found {len(jobs_df)} jobs for '{search_term}'"
    if location:
        results_summary += f" in {location}"

    listings = []
    for index, (_, job) in enumerate(jobs_df.iterrows(), start=1):
        listing_parts = [f"{index}. {job.get('title', 'N/A')}"]
        listing_parts.append(f"Company: {job.get('company', 'N/A')}")
        listing_parts.append(f"Location: {job.get('location', 'N/A')}")
        listing_parts.append(f"Source: {job.get('site', 'N/A').title()}")

        if pd.notna(job.get("job_type")):
            listing_parts.append(f"Type: {job.get('job_type')}")
        if pd.notna(job.get("date_posted")):
            listing_parts.append(f"Posted: {job.get('date_posted')}")

        if pd.notna(job.get("min_amount")) and pd.notna(job.get("max_amount")):
            currency = job.get("currency", "USD")
            interval = job.get("interval", "yearly")
            salary_range = (
                f"{job.get('min_amount'):,.0f} - "
                f"{job.get('max_amount'):,.0f} {currency} ({interval})"
            )
            listing_parts.append(f"Salary: {salary_range}")

        if job.get("is_remote"):
            listing_parts.append("Remote work available")

        if pd.notna(job.get("job_url")):
            listing_parts.append(f"Apply: {job.get('job_url')}")

        if pd.notna(job.get("description")):
            description = _trim_description(str(job.get("description")))
            listing_parts.append(f"Description: {description}")

        if pd.notna(job.get("company_industry")):
            listing_parts.append(f"Industry: {job.get('company_industry')}")
        if pd.notna(job.get("job_level")):
            listing_parts.append(f"Level: {job.get('job_level')}")
        if pd.notna(job.get("skills")):
            listing_parts.append(f"Skills: {job.get('skills')}")
        if pd.notna(job.get("experience_range")):
            listing_parts.append(f"Experience: {job.get('experience_range')}")
        if pd.notna(job.get("company_rating")):
            listing_parts.append(f"Company Rating: {job.get('company_rating')}/5")

        listings.append("\n".join(listing_parts))

    remote_column = jobs_df.get("is_remote")
    if remote_column is not None:
        remote_count = int(remote_column.fillna(False).astype(bool).sum())
    else:
        remote_count = 0

    summary_lines = [
        results_summary,
        "",
        "\n---\n".join(listings),
        "",
        "Search Summary",
        f"Total jobs found: {len(jobs_df)}",
        f"Sites searched: {', '.join(sites)}",
        f"Remote jobs: {remote_count}",
    ]

    min_amounts = jobs_df.get("min_amount")
    max_amounts = jobs_df.get("max_amount")
    if min_amounts is not None and max_amounts is not None:
        salary_mask = pd.notna(min_amounts) & pd.notna(max_amounts)
        salary_jobs = jobs_df[salary_mask]
        if not salary_jobs.empty:
            avg_min = salary_jobs["min_amount"].mean()
            avg_max = salary_jobs["max_amount"].mean()
            summary_lines.extend(
                [
                    f"Jobs with salary info: {len(salary_jobs)}",
                    f"Average salary range: {avg_min:,.0f} - {avg_max:,.0f}",
                ]
            )

    logger.info("Job search completed for '%s'", search_term)
    return "\n".join(summary_lines)


def get_supported_countries() -> str:
    """Return a formatted list of supported countries."""
    lines = ["Supported Countries for Job Searches", ""]

    for country in Country:
        country_names = country.value[0]
        lines.append(f"- {country.name}: {country_names}")

    lines.extend(
        [
            "",
            "Note: Use one of the identifiers above for the 'country_indeed' parameter.",
            "",
            "Popular Options:",
            "- usa, us, united states",
            "- uk, united kingdom",
            "- canada",
            "- australia",
            "- germany",
            "- france",
            "- india",
            "- singapore",
        ]
    )
    return "\n".join(lines)


def get_supported_sites() -> str:
    """Return descriptions for each job board supported by JobSpy."""
    sites_info = {
        "linkedin": "Professional networking platform with job listings.",
        "indeed": "Large job search engine with broad coverage.",
        "glassdoor": "Job listings with company reviews and salary data.",
        "zip_recruiter": "Job matching platform focused on US and Canada.",
        "google": "Aggregated job listings surfaced through Google search.",
        "bayt": "Middle East focused job portal.",
        "naukri": "India's leading job portal with detailed listings.",
        "bdjobs": "Primary job portal for Bangladesh.",
    }

    lines = ["Supported Job Board Sites", ""]
    lines.extend(f"- {site}: {description}" for site, description in sites_info.items())
    lines.extend(
        [
            "",
            "Usage Tips",
            "- Start with ['indeed', 'zip_recruiter'] for broad US coverage.",
            "- Combine ['indeed', 'linkedin', 'glassdoor', 'google'] for a wide net.",
            "- Include regional sites like 'bayt', 'naukri', or 'bdjobs' for specific markets.",
            "- LinkedIn has the strictest rate limits; Indeed is generally the most reliable.",
        ]
    )
    return "\n".join(lines)


def get_job_search_tips() -> str:
    """Return a collection of suggestions for running effective searches."""
    return (
        "JobSpy Job Search Tips and Best Practices\n\n"
        "Search Term Optimization\n"
        "- Be specific: e.g. 'python developer' instead of 'developer'.\n"
        "- Use quotes for exact phrases such as \"machine learning engineer\".\n"
        "- Try variations like 'software engineer' or 'software developer'.\n"
        "- Include technologies: 'React developer', 'AWS engineer'.\n"
        "- Consider seniority levels: 'senior', 'junior', 'lead'.\n\n"
        "Location Strategies\n"
        "- Remote jobs: set is_remote=True or location='Remote'.\n"
        "- Specific cities: e.g. 'San Francisco, CA' or 'New York, NY'.\n"
        "- State or country searches: 'California', 'Texas', 'United Kingdom'.\n"
        "- Run separate searches for multiple locations.\n\n"
        "Site Selection Guide\n"
        "- Begin with a couple of reliable sites to validate a search.\n"
        "- Indeed is reliable with broader coverage.\n"
        "- LinkedIn offers quality results but strict rate limits.\n"
        "- ZipRecruiter is strong for US and Canada roles.\n"
        "- Google rewards very specific search terms.\n\n"
        "Performance Tips\n"
        "- Start with 10-20 results and increase only if needed.\n"
        "- Use hours_old to focus on recent postings (24, 48, 72).\n"
        "- Enable linkedin_fetch_description only when you need full text.\n"
        "- Offset helps paginate through large result sets.\n\n"
        "Advanced Filtering\n"
        "- job_type supports fulltime, parttime, internship, contract.\n"
        "- easy_apply filters for quick-apply postings.\n"
        "- distance sets the search radius for location-based queries.\n"
        "- country_indeed alters the target market for Indeed and Glassdoor.\n\n"
        "Common Issues and Fixes\n"
        "- No results: broaden search terms or choose different sites.\n"
        "- Rate limiting: reduce results_wanted and add time between runs.\n"
        "- LinkedIn blocks: lower frequency or rotate proxies.\n"
        "- Slow searches: disable LinkedIn description fetching.\n\n"
        "Sample Searches\n"
        "Remote work:\n"
        "  search_term='software engineer'\n"
        "  location='Remote'\n"
        "  is_remote=True\n"
        "  site_name=['indeed', 'zip_recruiter']\n\n"
        "Local jobs:\n"
        "  search_term='marketing manager'\n"
        "  location='Austin, TX'\n"
        "  distance=25\n"
        "  site_name=['indeed', 'glassdoor']\n\n"
        "Recent postings:\n"
        "  search_term='data scientist'\n"
        "  hours_old=48\n"
        "  site_name=['linkedin', 'indeed']\n"
        "  linkedin_fetch_description=True\n\n"
        "Entry-level focus:\n"
        "  search_term='junior developer OR entry level programmer'\n"
        "  job_type='fulltime'\n"
        "  easy_apply=True\n\n"
        "Iterative Search Process\n"
        "1. Start broad with a small set of sites.\n"
        "2. Review the initial results for signal.\n"
        "3. Adjust keywords or filters based on what you see.\n"
        "4. Expand to more sites if coverage looks thin.\n"
        "5. Compare results across job boards for variety.\n\n"
        "Happy job hunting!"
    )


__all__ = [
    "scrape_jobs_tool",
    "get_supported_countries",
    "get_supported_sites",
    "get_job_search_tips",
]
