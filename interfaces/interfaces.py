from typing import Protocol


class JobRepository(Protocol):
    def insert_stage(self): ...

    def select_stage(self): ...
