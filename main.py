from datetime import date, datetime, time

from pawpal_system import CareTask, DailyScheduler, Owner, Pet


def main() -> None:
    today = date.today()
    first_pet = Pet(name="Mochi", species="dog")
    owner = Owner(name="Jordan", pets=[first_pet])
    second_pet = Pet(name="Luna", species="cat")
    owner.add_pet(second_pet)

    first_pet.add_task(
        CareTask(
            description="Morning walk",
            title="Walk",
            due_date=datetime.combine(today, time(8, 0)),
            duration_minutes=30,
            priority="high",
            frequency="daily",
        )
    )
    second_pet.add_task(
        CareTask(
            description="Breakfast",
            title="Feed",
            due_date=datetime.combine(today, time(9, 0)),
            duration_minutes=10,
            priority="medium",
            frequency="daily",
        )
    )
    first_pet.add_task(
        CareTask(
            description="Evening playtime",
            title="Play",
            due_date=datetime.combine(today, time(17, 30)),
            duration_minutes=20,
            priority="low",
            frequency="daily",
        )
    )

    scheduler = DailyScheduler()
    all_tasks = scheduler.get_tasks(owner)
    schedule = scheduler.build_daily_schedule(
        all_tasks, selected_date=today, available_minutes=60
    )

    print(f"Today's Schedule for {owner.name} ({len(owner.list_pets())} pets):")
    for pet, task in schedule:
        print(
            f"- {task.due_date:%H:%M} {pet.name}: {task.title} "
            f"({task.duration_minutes} min, {task.priority} priority, "
            f"{task.frequency})"
        )


if __name__ == "__main__":
    main()
