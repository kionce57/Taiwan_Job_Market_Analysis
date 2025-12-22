"""Dashboard API router with MySQL data support."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.db import DatabaseRepository
from src.models import CategoryPoint, DashboardData, DashboardMeta, TimeSeriesPoint

router = APIRouter(prefix="/api", tags=["dashboard"])


def get_repository() -> DatabaseRepository:
    """Dependency injection for database repository."""
    return DatabaseRepository()


def calculate_percentage(value: int, total: int) -> float:
    """Calculate percentage safely."""
    return round(value / total * 100, 1) if total > 0 else 0.0


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    job_name: Optional[str] = Query(None, description="Filter by job name (partial match)"),
    repo: DatabaseRepository = Depends(get_repository),
) -> DashboardData:
    """
    Get aggregated dashboard data from MySQL.

    Args:
        job_name: Optional job name filter for partial matching
        repo: Database repository (injected)

    Returns:
        Aggregated dashboard statistics
    """
    # Fetch all data from MySQL
    trend_df = repo.get_job_count_by_date(job_name)
    skills_df = repo.get_top_skills(job_name)
    regions_df = repo.get_jobs_by_region(job_name)
    industries_df = repo.get_jobs_by_industry(job_name)
    salary_df = repo.get_salary_distribution(job_name)
    total_jobs = repo.get_total_jobs(job_name)

    # Transform trend data
    trend = [
        TimeSeriesPoint(
            date=row["date"].strftime("%Y-%m-%d")
            if hasattr(row["date"], "strftime")
            else str(row["date"]),
            jobCount=int(row["jobCount"]),
            avgSalary=float(row["avgSalary"] or 0),
        )
        for _, row in trend_df.iterrows()
    ]
    trend.reverse()  # Oldest first

    # Transform skills data
    skills = [
        CategoryPoint(label=row["label"], value=int(row["value"]))
        for _, row in skills_df.iterrows()
    ]

    # Transform regions data with percentage
    total_region_jobs = int(regions_df["value"].sum()) if not regions_df.empty else 0
    regions = [
        CategoryPoint(
            label=row["label"],
            value=int(row["value"]),
            percentage=calculate_percentage(int(row["value"]), total_region_jobs),
        )
        for _, row in regions_df.iterrows()
    ]

    # Transform industries data with percentage
    total_industry_jobs = int(industries_df["value"].sum()) if not industries_df.empty else 0
    industries = [
        CategoryPoint(
            label=row["label"],
            value=int(row["value"]),
            percentage=calculate_percentage(int(row["value"]), total_industry_jobs),
        )
        for _, row in industries_df.iterrows()
    ]

    # Transform salary distribution with percentage
    total_salary_jobs = int(salary_df["value"].sum()) if not salary_df.empty else 0
    salary_dist = [
        CategoryPoint(
            label=row["label"],
            value=int(row["value"]),
            percentage=calculate_percentage(int(row["value"]), total_salary_jobs),
        )
        for _, row in salary_df.iterrows()
    ]

    return DashboardData(
        meta=DashboardMeta(
            lastUpdated=datetime.now().isoformat(),
            totalJobs=total_jobs,
        ),
        trend=trend,
        skills=skills,
        regions=regions,
        industries=industries,
        salaryDist=salary_dist,
    )
