"""Dashboard API router with mock data support."""

from datetime import datetime, timedelta
import random

from fastapi import APIRouter

from src.models import CategoryPoint, DashboardData, DashboardMeta, TimeSeriesPoint

router = APIRouter(prefix="/api", tags=["dashboard"])


def generate_mock_data() -> DashboardData:
    """Generate mock dashboard data for frontend development."""
    # Generate 30 days of trend data
    today = datetime.now()
    trend = [
        TimeSeriesPoint(
            date=(today - timedelta(days=i)).strftime("%Y-%m-%d"),
            jobCount=random.randint(800, 1500),
            avgSalary=random.randint(45000, 65000),
        )
        for i in range(30)
    ]
    trend.reverse()

    # Top 10 skills
    skill_names = [
        "Python", "JavaScript", "React", "SQL", "Java",
        "TypeScript", "AWS", "Docker", "Node.js", "Kubernetes"
    ]
    skills = [
        CategoryPoint(label=name, value=random.randint(100, 500))
        for name in skill_names
    ]
    skills.sort(key=lambda x: x.value, reverse=True)

    # Regional distribution
    region_names = ["台北市", "新北市", "桃園市", "台中市", "高雄市", "新竹縣市", "台南市"]
    total_region_jobs = 5000
    regions = []
    remaining = total_region_jobs
    for i, name in enumerate(region_names):
        if i == len(region_names) - 1:
            value = remaining
        else:
            value = random.randint(100, remaining // 2)
            remaining -= value
        regions.append(CategoryPoint(
            label=name,
            value=value,
            percentage=round(value / total_region_jobs * 100, 1)
        ))
    regions.sort(key=lambda x: x.value, reverse=True)

    # Industry distribution
    industry_names = [
        "軟體/網路", "電子零組件", "半導體", "金融/保險",
        "資訊服務", "電腦系統", "其他"
    ]
    total_industry_jobs = 5000
    industries = []
    remaining = total_industry_jobs
    for i, name in enumerate(industry_names):
        if i == len(industry_names) - 1:
            value = remaining
        else:
            value = random.randint(200, remaining // 2)
            remaining -= value
        industries.append(CategoryPoint(
            label=name,
            value=value,
            percentage=round(value / total_industry_jobs * 100, 1)
        ))
    industries.sort(key=lambda x: x.value, reverse=True)

    # Salary distribution
    salary_ranges = [
        ("< 30K", 150), ("30K-40K", 450), ("40K-50K", 800),
        ("50K-60K", 600), ("60K-80K", 350), ("80K-100K", 150), ("> 100K", 50)
    ]
    total_salary_jobs = sum(v for _, v in salary_ranges)
    salary_dist = [
        CategoryPoint(
            label=label,
            value=value,
            percentage=round(value / total_salary_jobs * 100, 1)
        )
        for label, value in salary_ranges
    ]

    return DashboardData(
        meta=DashboardMeta(
            lastUpdated=today.isoformat(),
            totalJobs=sum(s.value for s in skills),
        ),
        trend=trend,
        skills=skills,
        regions=regions,
        industries=industries,
        salaryDist=salary_dist,
    )


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data() -> DashboardData:
    """
    Get aggregated dashboard data.
    
    Returns mock data for now. Switch to real DB queries when ready.
    """
    # TODO: Replace with real database queries:
    # from src.db import DatabaseRepository
    # repo = DatabaseRepository()
    # ... build DashboardData from repo queries
    
    return generate_mock_data()
