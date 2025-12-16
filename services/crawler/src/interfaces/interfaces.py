from collections.abc import Iterator
from typing import Protocol


class JobRepository(Protocol):
    def insert_stage(self): ...

    def select_stage(self): ...


class Crawler(Protocol):
    def harvest_jobs(self, keyword, area) -> Iterator: ...
