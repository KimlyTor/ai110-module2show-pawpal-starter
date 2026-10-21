from __future__ import annotations

from datetime import date, datetime, time, timedelta

import pytest

from pawpal_system import CareTask, DailyScheduler, Owner, Pet


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


# @pytest.mark.parametrize(
#     ("field", "value"),
#     [
#         ("duration_minutes", 0),
#         ("duration_minutes", -1),
#         ("priority", "urgent"),
#         ("frequency", "monthly"),
#     ],
# )
# def test_care_task_rejects_invalid_values(field: str, value: object) -> None:
#     arguments = {
#         "description": "Care task",
#         "title": "Care task",
#         "due_date": datetime.combine(TODAY, time(9, 0)),
#     }
#     arguments[field] = value
#
#     with pytest.raises(ValueError):
#         CareTask(**arguments)
#
#
# def test_task_recurrence_starts_on_due_date() -> None:
#     once = make_task("One-time", due_date=TODAY, frequency="once")
#     daily = make_task("Daily", due_date=TODAY, frequency="daily")
#     weekly = make_task("Weekly", due_date=TODAY, frequency="weekly")
#
#     assert not once.is_due_on(TODAY - timedelta(days=1))
#     assert once.is_due_on(TODAY)
#     assert not once.is_due_on(TODAY + timedelta(days=1))
#     assert daily.is_due_on(TODAY + timedelta(days=1))
#     assert weekly.is_due_on(TODAY + timedelta(days=7))
#     assert not weekly.is_due_on(TODAY + timedelta(days=1))


def test_mark_complete_changes_status_and_excludes_task_from_schedule() -> None:
    task = make_task("Walk")
    assignments = [make_assignment(task)]

    assert task.is_completed is False

    task.mark_complete()

    assert task.is_completed is True
    assert DailyScheduler().build_daily_schedule(assignments, TODAY) == []


@pytest.mark.parametrize(
    ("frequency", "days_until_next"),
    [("daily", 1), ("weekly", 7)],
)
def test_completing_recurring_task_creates_next_occurrence(
    frequency: str, days_until_next: int
) -> None:
    pet = Pet(name="Mochi", species="dog")
    task = make_task("Walk", frequency=frequency, due_time=time(8, 30))
    pet.add_task(task)

    pet.complete_task(task)

    next_task = pet.list_tasks()[1]
    assert task.is_completed is True
    assert next_task is not task
    assert next_task.is_completed is False
    assert next_task.due_date == datetime.combine(
        date.today() + timedelta(days=days_until_next), time(8, 30)
    )
    assert next_task.frequency == frequency


def test_filter_tasks_by_completion_status() -> None:
    assignments = [
        make_assignment(make_task("Incomplete")),
        make_assignment(make_task("Complete", completed=True)),
    ]
    scheduler = DailyScheduler()

    assert [
        task.title
        for _, task in scheduler.filter_tasks_by_completion_status(
            assignments, is_completed=True
        )
    ] == ["Complete"]
    assert [
        task.title
        for _, task in scheduler.filter_tasks_by_completion_status(
            assignments, is_completed=False
        )
    ] == ["Incomplete"]


def test_find_time_conflicts_detects_overlaps_for_same_and_different_pets() -> None:
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    assignments = [
        (mochi, make_task("Walk", due_time=time(9, 0), duration=30)),
        (mochi, make_task("Medication", due_time=time(9, 15), duration=10)),
        (luna, make_task("Breakfast", due_time=time(9, 0), duration=10)),
    ]

    conflicts = DailyScheduler().find_time_conflicts(assignments, TODAY)

    assert conflicts == [
        (assignments[0], assignments[1]),
        (assignments[0], assignments[2]),
    ]


def test_find_time_conflicts_ignores_non_overlapping_or_unscheduled_tasks() -> None:
    assignments = [
        make_assignment(make_task("First", due_time=time(9, 0), duration=30)),
        make_assignment(make_task("Adjacent", due_time=time(9, 30), duration=10)),
        make_assignment(make_task("Other day", due_date=TODAY + timedelta(days=1))),
        make_assignment(make_task("Completed", completed=True)),
    ]

    assert DailyScheduler().find_time_conflicts(assignments, TODAY) == []


def test_find_time_conflicts_checks_recurring_tasks_on_selected_date() -> None:
    recurring_task = make_task(
        "Daily walk",
        due_date=TODAY - timedelta(days=1),
        due_time=time(9, 0),
        duration=30,
        frequency="daily",
    )
    one_time_task = make_task("Medication", due_time=time(9, 15), duration=10)

    conflicts = DailyScheduler().find_time_conflicts(
        [make_assignment(recurring_task), make_assignment(one_time_task)], TODAY
    )

    assert len(conflicts) == 1


# def test_due_status_filters_incomplete_tasks() -> None:
#     assignments = [
#         make_assignment(make_task("Today")),
#         make_assignment(make_task("Upcoming", due_date=TODAY + timedelta(days=1))),
#         make_assignment(make_task("Overdue", due_date=TODAY - timedelta(days=1))),
#         make_assignment(make_task("Completed", completed=True)),
#     ]
#     scheduler = DailyScheduler()
#
#     assert [task.title for _, task in scheduler.filter_tasks_by_due_status(
#         assignments, TODAY, "today"
#     )] == ["Today"]
#     assert [task.title for _, task in scheduler.filter_tasks_by_due_status(
#         assignments, TODAY, "upcoming"
#     )] == ["Upcoming"]
#     assert [task.title for _, task in scheduler.filter_tasks_by_due_status(
#         assignments, TODAY, "overdue"
#     )] == ["Overdue"]
#
#
# def test_due_status_rejects_unknown_status() -> None:
#     with pytest.raises(ValueError, match="Status must"):
#         DailyScheduler().filter_tasks_by_due_status([], TODAY, "tomorrow")
#
#
# def test_schedule_prioritizes_priority_then_due_time() -> None:
#     assignments = [
#         make_assignment(
#             make_task("Later high", due_time=time(11, 0), priority="high")
#         ),
#         make_assignment(
#             make_task("Early medium", due_time=time(8, 0), priority="medium")
#         ),
#         make_assignment(
#             make_task("Early high", due_time=time(8, 0), priority="high")
#         ),
#     ]
#
#     schedule = DailyScheduler().build_daily_schedule(assignments, TODAY)
#
#     assert [task.title for _, task in schedule] == [
#         "Early high",
#         "Later high",
#         "Early medium",
#     ]
#
#
# def test_schedule_skips_tasks_that_do_not_fit_available_time() -> None:
#     assignments = [
#         make_assignment(make_task("High priority", duration=40, priority="high")),
#         make_assignment(make_task("Medium priority", duration=20)),
#         make_assignment(make_task("Low priority", duration=10, priority="low")),
#     ]
#
#     schedule = DailyScheduler().build_daily_schedule(
#         assignments, TODAY, available_minutes=30
#     )
#
#     assert [task.title for _, task in schedule] == ["Medium priority", "Low priority"]
#     assert sum(task.duration_minutes for _, task in schedule) <= 30
#
#
# def test_schedule_rejects_negative_available_time() -> None:
#     with pytest.raises(ValueError, match="cannot be negative"):
#         DailyScheduler().build_daily_schedule([], TODAY, available_minutes=-1)


def test_adding_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="dog")
    task = make_task("Walk")
    initial_count = len(pet.list_tasks())

    pet.add_task(task)

    assert len(pet.list_tasks()) == initial_count + 1
    assert pet.list_tasks() == [task]


# def test_owner_collects_tasks_with_their_pet() -> None:
#     mochi = Pet(name="Mochi", species="dog", tasks=[make_task("Walk")])
#     luna = Pet(name="Luna", species="cat", tasks=[make_task("Feed")])
#     owner = Owner(name="Jordan", pets=[mochi, luna])
#
#     assert owner.get_all_tasks() == [(mochi, mochi.tasks[0]), (luna, luna.tasks[0])]
