from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Owner:
    name: str
    pets: list["Pet"]

    def __post_init__(self) -> None:
        """Ensure the owner has at least one pet."""
        if not self.pets:
            raise ValueError("An owner must have at least one pet.")

    def update_details(self, name: str) -> None:
        """Update the owner's name."""
        self.name = name

    def add_pet(self, pet: "Pet") -> None:
        """Add a pet to the owner."""
        self.pets.append(pet)

    def list_pets(self) -> list["Pet"]:
        """Return a copy of the owner's pets."""
        return self.pets.copy()

    def get_all_tasks(self) -> list[tuple["Pet", "CareTask"]]:
        """Return every pet's tasks together with the pet each task belongs to."""
        return [
            (pet, task)
            for pet in self.pets
            for task in pet.list_tasks()
        ]

    def remove_pet(self, pet: "Pet") -> None:
        """Remove a pet that belongs to the owner."""
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
        """Validate and associate this pet's initial tasks."""
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
        """Update the pet's name and species."""
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
        """Return a copy of the pet's tasks."""
        return self.tasks.copy()

    def remove_task(self, task: "CareTask") -> None:
        """Remove a task that belongs to this pet."""
        task_index = next(
            (
                index
                for index, existing_task in enumerate(self.tasks)
                if existing_task is task
            ),
            None,
        )
        if task_index is None:
            raise ValueError("Task does not belong to this pet.")
        del self.tasks[task_index]
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
    duration_minutes: int = 1
    priority: str = "medium"
    frequency: str = "once"
    _pet: "Pet | None" = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Validate the task's duration, priority, and frequency."""
        if self.duration_minutes <= 0:
            raise ValueError("Task duration must be greater than zero.")
        if self.priority not in {"low", "medium", "high"}:
            raise ValueError("Priority must be 'low', 'medium', or 'high'.")
        if self.frequency not in {"once", "daily", "weekly"}:
            raise ValueError("Frequency must be 'once', 'daily', or 'weekly'.")

    def is_due_on(self, selected_date: date) -> bool:
        """Check whether this task has an occurrence on the selected date."""
        first_due_date = self.due_date.date()
        if selected_date < first_due_date:
            return False
        if self.frequency == "daily":
            return True
        if self.frequency == "weekly":
            return (selected_date - first_due_date).days % 7 == 0
        return selected_date == first_due_date

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True


TaskAssignment = tuple[Pet, CareTask]


@dataclass
class DailyScheduler:
    def get_tasks(self, owner: Owner) -> list[TaskAssignment]:
        """Retrieve all pet-task pairs through the owner's task accessor."""
        return owner.get_all_tasks()

    def sort_tasks_by_due_date(
        self, tasks: list[TaskAssignment]
    ) -> list[TaskAssignment]:
        """Sort pet-task pairs by their due dates."""
        return sorted(tasks, key=lambda assignment: assignment[1].due_date)

    def filter_tasks_by_due_status(
        self, tasks: list[TaskAssignment], selected_date: date, status: str
    ) -> list[TaskAssignment]:
        """Filter incomplete tasks by their due status on a selected date."""
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
            and (
                assignment[1].is_due_on(selected_date)
                if status == "today"
                else matches_status(assignment[1].due_date.date())
            )
        ]

    def build_daily_schedule(
        self,
        tasks: list[TaskAssignment],
        selected_date: date,
        available_minutes: Optional[int] = None,
    ) -> list[TaskAssignment]:
        """Prioritize today's tasks within the available time."""
        due_today = self.filter_tasks_by_due_status(tasks, selected_date, "today")
        if available_minutes is not None and available_minutes < 0:
            raise ValueError("Available time cannot be negative.")

        priority_order = {"high": 0, "medium": 1, "low": 2}
        prioritized = sorted(
            due_today,
            key=lambda assignment: (
                priority_order[assignment[1].priority],
                assignment[1].due_date,
            ),
        )
        if available_minutes is None:
            return prioritized

        schedule: list[TaskAssignment] = []
        remaining_minutes = available_minutes
        for assignment in prioritized:
            duration = assignment[1].duration_minutes
            if duration <= remaining_minutes:
                schedule.append(assignment)
                remaining_minutes -= duration
        return schedule
