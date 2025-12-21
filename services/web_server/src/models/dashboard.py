"""Pydantic models for Dashboard API responses."""

from pydantic import BaseModel


class TimeSeriesPoint(BaseModel):
    """Single data point for time series charts."""

    date: str
    jobCount: int
    avgSalary: float


class CategoryPoint(BaseModel):
    """Single data point for category-based charts."""

    label: str
    value: int
    percentage: float | None = None


class DashboardMeta(BaseModel):
    """Dashboard metadata."""

    lastUpdated: str
    totalJobs: int


class DashboardData(BaseModel):
    """Complete dashboard response schema."""

    meta: DashboardMeta
    trend: list[TimeSeriesPoint]
    skills: list[CategoryPoint]
    regions: list[CategoryPoint]
    industries: list[CategoryPoint]
    salaryDist: list[CategoryPoint]
