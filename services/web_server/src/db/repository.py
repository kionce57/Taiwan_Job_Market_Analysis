"""Database repository for MySQL queries."""

from __future__ import annotations

import os
import urllib.parse

import pandas as pd
import sqlalchemy as sa
from dotenv import load_dotenv

load_dotenv()


class DatabaseRepository:
    """Repository for dashboard data queries."""

    def __init__(self) -> None:
        """Initialize database connection."""
        driver = os.getenv("SQL_DRIVER", "mysql+mysqlconnector")
        username = os.getenv("SQL_WEB_USER")
        password = os.getenv("SQL_WEB_PASSWORD")
        host = os.getenv("DB_HOST", "localhost")
        database = os.getenv("SQL_DATABASE")

        if not all([username, password, database]):
            raise ValueError("Missing required database environment variables")

        username = urllib.parse.quote_plus(str(username))
        password = urllib.parse.quote_plus(str(password))

        conn_str = f"{driver}://{username}:{password}@{host}/{database}"
        self.engine = sa.create_engine(conn_str)

    def _build_job_filter(self, job_name: str | None) -> str:
        """Build WHERE clause for job_name filter."""
        if not job_name:
            return ""
        # Use parameterized query in the actual methods to prevent SQL injection
        return "WHERE job_name LIKE :job_name"

    def get_job_count_by_date(self, job_name: str | None = None) -> pd.DataFrame:
        """Get job count and average salary grouped by date."""
        filter_clause = "WHERE job_name LIKE :job_name" if job_name else ""
        query = f"""
        SELECT
            DATE(appear_date) as date,
            COUNT(*) as jobCount,
            AVG((salary_min + salary_max) / 2) as avgSalary
        FROM dim_job
        {filter_clause}
        GROUP BY DATE(appear_date)
        ORDER BY date DESC
        LIMIT 30
        """
        with self.engine.connect() as conn:
            params = {"job_name": f"%{job_name}%"} if job_name else {}
            return pd.read_sql(sa.text(query), conn, params=params)

    def get_top_skills(self, job_name: str | None = None, limit: int = 10) -> pd.DataFrame:
        """Get top skills by job count."""
        join_clause = ""
        filter_clause = ""

        if job_name:
            join_clause = "JOIN dim_job dj ON bs.job_uid = dj.id"
            filter_clause = "WHERE dj.job_name LIKE :job_name"

        query = f"""
        SELECT
            bs.skill_name as label,
            COUNT(*) as value
        FROM bridge_skills bs
        {join_clause}
        {filter_clause}
        GROUP BY bs.skill_name
        ORDER BY value DESC
        LIMIT {limit}
        """
        with self.engine.connect() as conn:
            params = {"job_name": f"%{job_name}%"} if job_name else {}
            return pd.read_sql(sa.text(query), conn, params=params)

    def get_jobs_by_region(self, job_name: str | None = None) -> pd.DataFrame:
        """Get job count by region."""
        filter_clause = "WHERE job_name LIKE :job_name" if job_name else ""
        query = f"""
        SELECT
            address_area as label,
            COUNT(*) as value
        FROM dim_job
        {filter_clause}
        GROUP BY address_area
        ORDER BY value DESC
        """
        with self.engine.connect() as conn:
            params = {"job_name": f"%{job_name}%"} if job_name else {}
            return pd.read_sql(sa.text(query), conn, params=params)

    def get_jobs_by_industry(self, job_name: str | None = None) -> pd.DataFrame:
        """Get job count by industry."""
        filter_clause = "WHERE dj.job_name LIKE :job_name" if job_name else ""
        query = f"""
        SELECT
            ci.industry as label,
            COUNT(*) as value
        FROM dim_job dj
        JOIN cust_info ci ON dj.cust_no = ci.cust_no
        {filter_clause}
        GROUP BY ci.industry
        ORDER BY value DESC
        """
        with self.engine.connect() as conn:
            params = {"job_name": f"%{job_name}%"} if job_name else {}
            return pd.read_sql(sa.text(query), conn, params=params)

    def get_salary_distribution(self, job_name: str | None = None) -> pd.DataFrame:
        """Get salary distribution in ranges."""
        filter_clause = "AND job_name LIKE :job_name" if job_name else ""
        query = f"""
        SELECT
            CASE
                WHEN (salary_min + salary_max) / 2 < 30000 THEN '< 30K'
                WHEN (salary_min + salary_max) / 2 < 40000 THEN '30K-40K'
                WHEN (salary_min + salary_max) / 2 < 50000 THEN '40K-50K'
                WHEN (salary_min + salary_max) / 2 < 60000 THEN '50K-60K'
                WHEN (salary_min + salary_max) / 2 < 80000 THEN '60K-80K'
                WHEN (salary_min + salary_max) / 2 < 100000 THEN '80K-100K'
                ELSE '> 100K'
            END as label,
            COUNT(*) as value
        FROM dim_job
        WHERE salary_min > 0 AND salary_max > 0 {filter_clause}
        GROUP BY label
        ORDER BY MIN((salary_min + salary_max) / 2)
        """
        with self.engine.connect() as conn:
            params = {"job_name": f"%{job_name}%"} if job_name else {}
            return pd.read_sql(sa.text(query), conn, params=params)

    def get_total_jobs(self, job_name: str | None = None) -> int:
        """Get total job count."""
        filter_clause = "WHERE job_name LIKE :job_name" if job_name else ""
        query = f"SELECT COUNT(*) as total FROM dim_job {filter_clause}"
        with self.engine.connect() as conn:
            params = {"job_name": f"%{job_name}%"} if job_name else {}
            result = conn.execute(sa.text(query), params)
            row = result.fetchone()
            return row[0] if row else 0
