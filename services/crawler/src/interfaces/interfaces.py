from collections.abc import Iterator
from typing import Protocol


class BronzeJobRepository(Protocol):
    def insert_stage(self): ...

    def select_stage(self): ...


class SilverJobRepository(Protocol):
    def insert_stage(self): ...

    def select_stage(self): ...


class Crawler(Protocol):
    def harvest_jobs(self, keyword, area) -> Iterator: ...
