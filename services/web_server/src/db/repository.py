"""Database repository for MySQL queries."""

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

    def get_job_count_by_date(self) -> pd.DataFrame:
        """Get job count and average salary grouped by date."""
        query = """
        SELECT 
            DATE(appear_date) as date,
            COUNT(*) as jobCount,
            AVG((salary_min + salary_max) / 2) as avgSalary
        FROM dim_job
        GROUP BY DATE(appear_date)
        ORDER BY date DESC
        LIMIT 30
        """
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn)

    def get_top_skills(self, limit: int = 10) -> pd.DataFrame:
        """Get top skills by job count."""
        query = f"""
        SELECT 
            skill_name as label,
            COUNT(*) as value
        FROM skills
        GROUP BY skill_name
        ORDER BY value DESC
        LIMIT {limit}
        """
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn)

    def get_jobs_by_region(self) -> pd.DataFrame:
        """Get job count by region."""
        query = """
        SELECT 
            address_area as label,
            COUNT(*) as value
        FROM dim_job
        GROUP BY address_area
        ORDER BY value DESC
        """
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn)

    def get_jobs_by_industry(self) -> pd.DataFrame:
        """Get job count by industry."""
        query = """
        SELECT 
            ci.industry as label,
            COUNT(*) as value
        FROM dim_job dj
        JOIN cust_info ci ON dj.cust_no = ci.cust_no
        GROUP BY ci.industry
        ORDER BY value DESC
        """
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn)

    def get_salary_distribution(self) -> pd.DataFrame:
        """Get salary distribution in ranges."""
        query = """
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
        WHERE salary_min > 0 AND salary_max > 0
        GROUP BY label
        ORDER BY MIN((salary_min + salary_max) / 2)
        """
        with self.engine.connect() as conn:
            return pd.read_sql(query, conn)

    def get_total_jobs(self) -> int:
        """Get total job count."""
        query = "SELECT COUNT(*) as total FROM dim_job"
        with self.engine.connect() as conn:
            result = conn.execute(sa.text(query))
            row = result.fetchone()
            return row[0] if row else 0
