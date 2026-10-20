from dataclasses import dataclass, field
from datetime import date


@dataclass
class Owner:
    name: str
    pets: list["Pet"] = field(default_factory=list)

    def update_details(self, name: str) -> None:
        ...


@dataclass
class Pet:
    name: str
    species: str
    care_tasks: list["CareTask"] = field(default_factory=list)

    def update_details(self, name: str, species: str) -> None:
        ...


@dataclass
class CareTask:
    title: str
    duration: int
    priority: str
    due_date: date
    is_completed: bool = False

    def mark_complete(self) -> None:
        ...


@dataclass
class DailyPlan:
    date: date
    tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        ...

    def show_schedule(self) -> None:
        ...
