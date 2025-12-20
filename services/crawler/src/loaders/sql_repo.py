import os

import pandas as pd
import sqlalchemy as sa
from dotenv import load_dotenv

from src.interfaces.interfaces import SilverJobRepository

load_dotenv()


class TjmaDatabase(SilverJobRepository):
    # sql

    def __init__(self) -> None:
        # conn str: dialect+driver://username:password@host:port/database
        # 因為 host 會導向另一個 container, 所以不需要提供 port(預設也不用 3306)
        driver = os.getenv("SQL_DRIVER")
        username = os.getenv("SQL_CRAWLER_USER")
        password = os.getenv("SQL_CRAWLER_PASSWORD")
        host = os.getenv("DB_HOST")
        database = os.getenv("SQL_DATABASE")

        if not all([driver, username, password, host, database]):
            raise ValueError("Missing required database environment variables")

        conn_str = f"{driver}://{username}:{password}@{host}/{database}"
        self.engine = sa.create_engine(conn_str)

    def insert_stage(self, table: sa.Table, df: pd.DataFrame) -> None:
        """
        Insert DataFrame into MySQL table with upsert logic.
        Uses INSERT ... ON DUPLICATE KEY UPDATE for MySQL.

        Args:
            table: Target table name
            df: DataFrame to insert
        """

        def mysql_upsert(table, conn, keys, data_iter):
            """
            Custom insert method for pandas to_sql that performs upsert.
            """
            from sqlalchemy.dialects.mysql import insert

            data = [dict(zip(keys, row, strict=True)) for row in data_iter]
            if not data:
                return

            stmt = insert(table.table).values(data)

            # Build the ON DUPLICATE KEY UPDATE clause
            # Update all columns except primary key columns
            update_dict = {
                col.name: stmt.inserted[col.name] for col in stmt.inserted if not col.primary_key
            }

            if update_dict:
                stmt = stmt.on_duplicate_key_update(**update_dict)

            conn.execute(stmt)

        df.to_sql(
            name=table.name, con=self.engine, if_exists="append", index=False, method=mysql_upsert
        )

    def select_stage(
        self,
        table: sa.Table,
        columns: list[str] | None = None,
        condition: dict | None = None,
    ) -> pd.DataFrame:
        """
        Select data from MySQL table with optional column selection and conditions.

        Args:
            table: Target table name
            columns: List of column names to select. If None, selects all columns.
            condition: Dict of {column_name: value} for WHERE clause (uses AND logic).

        Returns:
            pd.DataFrame: Query results as a DataFrame.

        Example:
            # Select all columns
            df = repo.select_stage("jobs")

            # Select specific columns
            df = repo.select_stage("jobs", columns=["id", "title"])

            # Select with conditions
            df = repo.select_stage("jobs", columns=["id"], condition={"status": "active"})
        """
        # Build column selection
        if columns:
            select_cols = [table.c[col] for col in columns]
            stmt = sa.select(*select_cols)
        else:
            stmt = sa.select(table)

        # Add WHERE conditions
        if condition:
            for col_name, value in condition.items():
                stmt = stmt.where(table.c[col_name] == value)

        # Execute and return as DataFrame
        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            return pd.DataFrame(result.fetchall(), columns=list(result.keys()))
