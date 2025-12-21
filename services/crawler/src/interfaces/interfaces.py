import sqlalchemy as sa
import pandas as pd
from collections.abc import Iterator
from typing import Protocol


class BronzeJobRepository(Protocol):
    def insert_stage(self, datas: list): ...

    def select_stage(self, job_name_regex: str | None = None, projection: dict | None = None): ...


class SilverJobRepository(Protocol):
    def insert_stage(self, table: sa.Table, df: pd.DataFrame) -> None: ...

    def select_stage(
        self,
        table: sa.Table,
        columns: list[str] | None = None,
        condition: dict | None = None,
    ) -> pd.DataFrame: ...


class Crawler(Protocol):
    def harvest_jobs(self, keyword, area) -> Iterator: ...
