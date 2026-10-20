from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Owner:
    name: str
    pets: list["Pet"]

    def __post_init__(self) -> None:
        if not self.pets:
            raise ValueError("An owner must have at least one pet.")

    def update_details(self, name: str) -> None:
        self.name = name

    def add_pet(self, pet: "Pet") -> None:
        self.pets.append(pet)

    def list_pets(self) -> list["Pet"]:
        return self.pets.copy()

    def remove_pet(self, pet: "Pet") -> None:
        pet_index = next(
            (
                index
                for index, existing_pet in enumerate(self.pets)
                if existing_pet is pet
            ),
            None,
        )
        if pet_index is None:
            raise ValueError("Pet does not belong to this owner.")
        if len(self.pets) == 1:
            raise ValueError("An owner must have at least one pet.")
        del self.pets[pet_index]


@dataclass
class Pet:
    name: str
    species: str
    tasks: list["CareTask"] = field(default_factory=list)

    def __post_init__(self) -> None:
        task_ids: set[int] = set()
        for task in self.tasks:
            if task._pet is not None and task._pet is not self:
                raise ValueError("Create a separate CareTask for each pet.")
            if id(task) in task_ids:
                raise ValueError("A task can only be added once to a pet.")
            task_ids.add(id(task))
        for task in self.tasks:
            task._pet = self

    def update_details(self, name: str, species: str) -> None:
        self.name = name
        self.species = species

    def add_task(self, task: "CareTask") -> None:
        """Attach a task instance that is tracked independently for this pet."""
        if task._pet is not None and task._pet is not self:
            raise ValueError("Create a separate CareTask for each pet.")
        if any(existing_task is task for existing_task in self.tasks):
            raise ValueError("This task is already added to this pet.")
        task._pet = self
        self.tasks.append(task)

    def list_tasks(self) -> list["CareTask"]:
        return self.tasks.copy()

    def remove_task(self, task: "CareTask") -> None:
        self.tasks.remove(task)
        task._pet = None

    def complete_task(self, task: "CareTask") -> None:
        """Complete a task attached to this pet."""
        if not any(existing_task is task for existing_task in self.tasks):
            raise ValueError("Task does not belong to this pet.")
        task.mark_complete()


@dataclass
class CareTask:
    """A task instance with completion status tracked for one pet."""

    description: str
    title: str
    due_date: datetime
    is_completed: bool = False
    _pet: "Pet | None" = field(default=None, init=False, repr=False, compare=False)

    def mark_complete(self) -> None:
        self.is_completed = True


TaskAssignment = tuple[Pet, CareTask]


@dataclass
class DailyScheduler:
    def get_tasks(self, pets: list[Pet]) -> list[TaskAssignment]:
        """Gather pet-task pairs while preserving each pet's independent tasks."""
        return [(pet, task) for pet in pets for task in pet.list_tasks()]

    def sort_tasks_by_due_date(
        self, tasks: list[TaskAssignment]
    ) -> list[TaskAssignment]:
        return sorted(tasks, key=lambda assignment: assignment[1].due_date)

    def filter_tasks_by_due_status(
        self, tasks: list[TaskAssignment], selected_date: date, status: str
    ) -> list[TaskAssignment]:
        status_filters = {
            "today": lambda task_date: task_date == selected_date,
            "upcoming": lambda task_date: task_date > selected_date,
            "overdue": lambda task_date: task_date < selected_date,
        }
        if status not in status_filters:
            raise ValueError("Status must be 'today', 'upcoming', or 'overdue'.")

        matches_status = status_filters[status]
        return [
            assignment
            for assignment in tasks
            if not assignment[1].is_completed
            and matches_status(assignment[1].due_date.date())
        ]

    def build_daily_schedule(
        self, tasks: list[TaskAssignment], selected_date: date
    ) -> list[TaskAssignment]:
        due_today = self.filter_tasks_by_due_status(tasks, selected_date, "today")
        return self.sort_tasks_by_due_date(due_today)
