from __future__ import annotations

from datetime import date, datetime, time, timedelta

from pawpal_system import CareTask, DailyScheduler, Pet


TODAY = date(2026, 10, 20)


def make_task(
    title: str,
    *,
    due_date: date = TODAY,
    due_time: time = time(9, 0),
    duration: int = 10,
    priority: str = "medium",
    frequency: str = "once",
    completed: bool = False,
) -> CareTask:
    return CareTask(
        description=title,
        title=title,
        due_date=datetime.combine(due_date, due_time),
        duration_minutes=duration,
        priority=priority,
        frequency=frequency,
        is_completed=completed,
    )


def make_assignment(task: CareTask, pet: Pet | None = None) -> tuple[Pet, CareTask]:
    return (pet or Pet(name="Mochi", species="dog"), task)


def test_mark_complete_changes_status_and_excludes_task_from_schedule() -> None:
    """Completed tasks are marked done and omitted from the daily schedule."""
    task = make_task("Walk")
    assignments = [make_assignment(task)]

    assert task.is_completed is False

    task.mark_complete()

    assert task.is_completed is True
    assert DailyScheduler().build_daily_schedule(assignments, TODAY) == []


def test_sorting_correctness_returns_tasks_in_chronological_order() -> None:
    """Tasks are returned in chronological due-date order."""
    tasks = [
        make_assignment(
            make_task("Late", due_date=TODAY + timedelta(days=2), due_time=time(15, 0))
        ),
        make_assignment(make_task("Early", due_date=TODAY, due_time=time(8, 0))),
        make_assignment(make_task("Middle", due_date=TODAY, due_time=time(11, 30))),
    ]

    ordered = DailyScheduler().sort_tasks_by_due_date(tasks)

    assert [task.title for _, task in ordered] == ["Early", "Middle", "Late"]


def test_recurrence_logic_daily_task_creates_next_day_task() -> None:
    """Completing daily occurrences creates the next task on each following day."""
    pet = Pet(name="Mochi", species="dog")
    task = make_task(
        "Morning walk", due_date=TODAY, due_time=time(7, 0), frequency="daily"
    )
    pet.add_task(task)

    pet.complete_task(task)

    next_task = pet.list_tasks()[1]
    assert task.is_completed is True
    assert next_task.is_completed is False
    assert next_task.frequency == "daily"
    assert next_task.due_date == datetime.combine(
        TODAY + timedelta(days=1), time(7, 0)
    )

    pet.complete_task(next_task)

    following_task = pet.list_tasks()[2]
    assert following_task.due_date == datetime.combine(
        TODAY + timedelta(days=2), time(7, 0)
    )


def test_recurrence_logic_weekly_task_creates_next_week_task() -> None:
    """Completing weekly occurrences creates the next task seven days later."""
    pet = Pet(name="Mochi", species="dog")
    task = make_task(
        "Weekly grooming", due_date=TODAY, due_time=time(7, 0), frequency="weekly"
    )
    pet.add_task(task)

    pet.complete_task(task)

    next_task = pet.list_tasks()[1]
    assert next_task.due_date == datetime.combine(
        TODAY + timedelta(days=7), time(7, 0)
    )

    pet.complete_task(next_task)

    following_task = pet.list_tasks()[2]
    assert following_task.due_date == datetime.combine(
        TODAY + timedelta(days=14), time(7, 0)
    )


def test_conflict_detection_flags_duplicate_times() -> None:
    """Tasks with overlapping intervals at the same start time are flagged."""
    first = make_assignment(make_task("Walk", due_time=time(9, 0), duration=30))
    second = make_assignment(make_task("Feeding", due_time=time(9, 0), duration=20))

    conflicts = DailyScheduler().find_time_conflicts([first, second], TODAY)

    assert conflicts == [(first, second)]


def test_adding_task_increases_pet_task_count() -> None:
    """Adding a task increases the pet's task list by one."""
    pet = Pet(name="Mochi", species="dog")
    task = make_task("Walk")
    initial_count = len(pet.list_tasks())

    pet.add_task(task)

    assert len(pet.list_tasks()) == initial_count + 1
    assert pet.list_tasks() == [task]
