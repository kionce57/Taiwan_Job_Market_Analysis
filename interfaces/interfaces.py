from typing import Protocol


class JobRepository(Protocol):
    def insert_stage(self): ...

    """Bronze stage"""

    def select_stage(self): ...

    """Bronze stage"""

    # def curate(self): ...
    # """Silver stage"""

