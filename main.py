from datetime import date, datetime, time, timedelta

from pawpal_system import CareTask, DailyScheduler, Owner, Pet


def main() -> None:
    today = date.today()
    tomorrow = today + timedelta(days=1)
    first_pet = Pet(name="Mochi", species="dog")
    owner = Owner(name="Jordan", pets=[first_pet])
    second_pet = Pet(name="Luna", species="cat")
    owner.add_pet(second_pet)

    first_pet.add_task(
        CareTask(
            description="Tomorrow's breakfast",
            title="Feed",
            due_date=datetime.combine(tomorrow, time(7, 0)),
            duration_minutes=10,
            priority="medium",
            frequency="daily",
        )
    )
    second_pet.add_task(
        CareTask(
            description="Evening playtime",
            title="Play",
            due_date=datetime.combine(today, time(17, 30)),
            duration_minutes=20,
            priority="low",
            frequency="daily",
        )
    )
    completed_task = CareTask(
        description="Morning walk",
        title="Walk",
        due_date=datetime.combine(today, time(8, 0)),
        duration_minutes=30,
        priority="high",
        frequency="daily",
    )
    first_pet.add_task(completed_task)
    completed_task.mark_complete()
    first_pet.add_task(
        CareTask(
            description="Morning walk",
            title="Walk",
            due_date=datetime.combine(today, time(9, 0)),
            duration_minutes=30,
            priority="high",
            frequency="once",
        )
    )
    second_pet.add_task(
        CareTask(
            description="Breakfast",
            title="Breakfast",
            due_date=datetime.combine(today, time(9, 0)),
            duration_minutes=10,
            priority="medium",
            frequency="daily",
        )
    )

    scheduler = DailyScheduler()
    all_tasks = scheduler.get_tasks(owner)

    # Show tasks in their original order and with their completion status.
    print("Tasks in insertion order:")
    for pet, task in all_tasks:
        status = "completed" if task.is_completed else "incomplete"
        print(f"- {task.due_date:%Y-%m-%d %H:%M} {pet.name}: {task.title} ({status})")

    # Demonstrate sorting by full due date and by time of day.
    print("\nTasks sorted by date and time:")
    for pet, task in scheduler.sort_tasks_by_due_date(all_tasks):
        print(f"- {task.due_date:%Y-%m-%d %H:%M} {pet.name}: {task.title}")

    print("\nTasks sorted by time of day (date ignored):")
    for pet, task in scheduler.sort_by_time(all_tasks):
        print(f"- {task.due_date:%Y-%m-%d %H:%M} {pet.name}: {task.title}")

    # Separate completed tasks from tasks that still need care.
    print("\nCompleted tasks:")
    for pet, task in scheduler.filter_tasks_by_completion_status(
        all_tasks, is_completed=True
    ):
        print(f"- {pet.name}: {task.title}")

    print("\nIncomplete tasks:")
    for pet, task in scheduler.filter_tasks_by_completion_status(
        all_tasks, is_completed=False
    ):
        print(f"- {pet.name}: {task.title}")

    # Build today's time-limited plan and report overlapping task times.
    schedule = scheduler.build_daily_schedule(
        all_tasks, selected_date=today, available_minutes=60
    )
    conflicts = scheduler.find_time_conflicts(schedule, selected_date=today)
    for (first_conflict_pet, first_conflict_task), (
        second_conflict_pet,
        second_conflict_task,
    ) in conflicts:
        print(
            f"WARNING: Time conflict: {first_conflict_pet.name}'s "
            f"{first_conflict_task.title} overlaps "
            f"{second_conflict_pet.name}'s {second_conflict_task.title}."
        )

    print(f"\nToday's Schedule for {owner.name} ({len(owner.list_pets())} pets):")
    for pet, task in schedule:
        print(
            f"- {task.due_date:%H:%M} {pet.name}: {task.title} "
            f"({task.duration_minutes} min, {task.priority} priority, "
            f"{task.frequency})"
        )


if __name__ == "__main__":
    main()
