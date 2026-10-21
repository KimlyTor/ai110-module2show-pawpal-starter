from datetime import date, datetime, time, timedelta

import pandas as pd
import streamlit as st

from pawpal_system import CareTask, DailyScheduler, Owner, Pet

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Plan pet care tasks by priority, due date, and the time available.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner and Pets")
if "owner_name_value" not in st.session_state:
    st.session_state.owner_name_value = (
        st.session_state.owner.name if "owner" in st.session_state else "Jordan"
    )
if "owner_name_editing" not in st.session_state:
    st.session_state.owner_name_editing = False

owner_name_column, owner_edit_column = st.columns([5, 1], vertical_alignment="center")
with owner_name_column:
    if st.session_state.owner_name_editing:
        owner_name = st.text_input(
            "Owner name",
            key="owner_name_input",
        )
    else:
        owner_name = st.session_state.owner_name_value
        st.metric("Owner name", owner_name)
with owner_edit_column:
    owner_edit_clicked = st.button(
        "Save" if st.session_state.owner_name_editing else "Edit",
        key="toggle_owner_name_editing",
    )

if owner_edit_clicked:
    if st.session_state.owner_name_editing:
        if not owner_name.strip():
            st.error("Enter an owner name before saving.")
        else:
            st.session_state.owner_name_value = owner_name.strip()
            st.session_state.owner_name_editing = False
            st.rerun()
    else:
        st.session_state.owner_name_input = st.session_state.owner_name_value
        st.session_state.owner_name_editing = True
        st.rerun()

if "pets" not in st.session_state:
    st.session_state.pets = []
if "next_pet_id" not in st.session_state:
    st.session_state.next_pet_id = 1

with st.form("add_pet_form", clear_on_submit=True):
    st.markdown("### Add a Pet")
    pet_name = st.text_input("Pet name", placeholder="e.g. Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet = st.form_submit_button("Add pet")

if add_pet:
    if not pet_name.strip():
        st.error("Enter a pet name before adding it.")
    else:
        st.session_state.pets.append(
            {
                "id": st.session_state.next_pet_id,
                "name": pet_name.strip(),
                "species": species,
                "tasks": [],
            }
        )
        st.session_state.next_pet_id += 1

if st.session_state.pets:
    st.write("Your pets:")
    for pet in st.session_state.pets:
        st.write(f"- **{pet['name']}** ({pet['species']})")
else:
    st.info("Add a pet before adding care tasks.")

st.markdown("### Tasks")
st.caption("Add care tasks with a due date, time, frequency, duration, and priority.")

if st.session_state.pets:
    pets_by_id = {pet["id"]: pet for pet in st.session_state.pets}
    with st.form("add_task_form", clear_on_submit=True):
        selected_pet_id = st.selectbox(
            "Assign task to",
            options=list(pets_by_id),
            format_func=lambda pet_id: (
                f"{pets_by_id[pet_id]['name']} ({pets_by_id[pet_id]['species']})"
            ),
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", placeholder="e.g. Morning walk")
            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20
            )
        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        with col3:
            due_date = st.date_input(
                "Due date",
                value=date.today(),
                min_value=date.today(),
            )
            due_time = st.time_input("Due time", value=time(9, 0))
        add_task = st.form_submit_button("Add task")

    if add_task:
        if not task_title.strip():
            st.error("Enter a task title before adding it.")
        else:
            pets_by_id[selected_pet_id]["tasks"].append(
                {
                    "title": task_title.strip(),
                    "duration_minutes": int(duration),
                    "priority": priority,
                    "due_date": due_date,
                    "due_time": due_time,
                    "frequency": frequency,
                    "is_completed": False,
                }
            )

    st.markdown("### Your tasks")
    status_filter = st.selectbox(
        "Filter tasks by status",
        ["All", "Incomplete", "Completed"],
        key="task_status_filter",
    )
    task_sort = st.selectbox(
        "Sort tasks by",
        ["Due date/time", "Pet name", "Status"],
        key="task_sort",
    )
    task_entries = [
        (pet, task_index, task)
        for pet in st.session_state.pets
        for task_index, task in enumerate(pet["tasks"])
        if status_filter == "All"
        or task.get("is_completed", False) == (status_filter == "Completed")
    ]
    if task_sort == "Pet name":
        task_entries.sort(key=lambda entry: entry[0]["name"].casefold())
    elif task_sort == "Status":
        task_entries.sort(key=lambda entry: entry[2].get("is_completed", False))
    else:
        task_entries.sort(
            key=lambda entry: (
                entry[2]["due_date"],
                entry[2]["due_time"],
            )
        )

    task_rows = pd.DataFrame(
        [
            {
                "Pet": pet["name"],
                "Task": task["title"],
                "Duration": f"{task['duration_minutes']} min",
                "Priority": task["priority"].title(),
                "Frequency": task["frequency"].title(),
                "Due": datetime.combine(task["due_date"], task["due_time"]),
                "Status": (
                    "Completed"
                    if task.get("is_completed", False)
                    else "Incomplete"
                ),
            }
            for pet, _, task in task_entries
        ],
        columns=[
            "Pet",
            "Task",
            "Duration",
            "Priority",
            "Frequency",
            "Due",
            "Status",
        ],
    )
    styled_task_rows = task_rows.style.map(
        lambda status: (
            "color: #2E8B57; font-weight: bold" if status == "Completed" else ""
        ),
        subset=["Status"],
    )
    st.dataframe(styled_task_rows, use_container_width=True, hide_index=True)

    if not task_entries:
        st.caption("No tasks match this status filter.")
    else:
        incomplete_entries = [
            entry for entry in task_entries if not entry[2].get("is_completed", False)
        ]
        if incomplete_entries:
            entries_by_key = {
                (pet["id"], task_index): entry
                for entry in incomplete_entries
                for pet, task_index, _ in [entry]
            }
            selected_entry_index = st.selectbox(
                "Choose an incomplete task to mark complete",
                options=list(entries_by_key),
                format_func=lambda key: (
                    f"{entries_by_key[key][0]['name']}: "
                    f"{entries_by_key[key][2]['title']} "
                    f"({entries_by_key[key][2]['due_date'].isoformat()} "
                    f"{entries_by_key[key][2]['due_time'].strftime('%H:%M')})"
                ),
                key=f"task_to_complete_{tuple(entries_by_key)}",
            )
            selected_entry = entries_by_key[selected_entry_index]
            pet = selected_entry[0]
            task = selected_entry[2]
            if st.button(
                "Mark complete",
                key=f"complete_{pet['id']}_{selected_entry_index[1]}",
                type="secondary",
            ):
                task_model = CareTask(
                    description=task["title"],
                    title=task["title"],
                    due_date=datetime.combine(task["due_date"], task["due_time"]),
                    duration_minutes=task["duration_minutes"],
                    priority=task["priority"],
                    frequency=task["frequency"],
                )
                pet_model = Pet(pet["name"], pet["species"], tasks=[task_model])
                pet_model.complete_task(task_model)
                task["is_completed"] = True

                if len(pet_model.tasks) > 1:
                    next_task = pet_model.tasks[-1]
                    pet["tasks"].append(
                        {
                            "title": next_task.title,
                            "duration_minutes": next_task.duration_minutes,
                            "priority": next_task.priority,
                            "frequency": next_task.frequency,
                            "due_date": next_task.due_date.date(),
                            "due_time": next_task.due_date.time(),
                            "is_completed": next_task.is_completed,
                        }
                    )
                st.rerun()
        else:
            st.caption("No incomplete tasks in this view to mark complete.")

st.divider()

st.subheader("Build Schedule")
selected_date = st.date_input(
    "Schedule date",
    value=date.today(),
    min_value=date.today(),
)
available_minutes = st.number_input(
    "Available time (minutes)", min_value=0, max_value=1440, value=60
)

if st.button("Generate schedule"):
    if not owner_name.strip():
        st.error("Enter an owner name to generate a schedule.")
    elif not st.session_state.pets:
        st.error("Add at least one pet before generating a schedule.")
    else:
        pets = [
            Pet(
                name=pet["name"],
                species=pet["species"],
                tasks=[
                    CareTask(
                        description=task["title"],
                        title=task["title"],
                        due_date=datetime.combine(task["due_date"], task["due_time"]),
                        duration_minutes=task["duration_minutes"],
                        priority=task["priority"],
                        frequency=task["frequency"],
                        is_completed=task.get("is_completed", False),
                    )
                    for task in pet["tasks"]
                ],
            )
            for pet in st.session_state.pets
        ]
        if "owner" not in st.session_state:
            st.session_state.owner = Owner(name=owner_name.strip(), pets=pets)
        else:
            st.session_state.owner.update_details(owner_name.strip())
            st.session_state.owner.pets = pets
        owner = st.session_state.owner
        scheduler = DailyScheduler()
        all_tasks = scheduler.get_tasks(owner)
        schedule = scheduler.build_daily_schedule(
            all_tasks, selected_date, int(available_minutes)
        )
        time_conflicts = scheduler.find_time_conflicts(schedule, selected_date)
        due_today = scheduler.filter_tasks_by_due_status(
            all_tasks, selected_date, "today"
        )

        if time_conflicts:
            conflicts_by_window: dict[
                tuple[datetime, datetime], list[tuple[Pet, CareTask]]
            ] = {}
            for (first_pet, first_task), (second_pet, second_task) in time_conflicts:
                first_start = datetime.combine(selected_date, first_task.due_date.time())
                first_end = first_start + timedelta(
                    minutes=first_task.duration_minutes
                )
                second_start = datetime.combine(
                    selected_date, second_task.due_date.time()
                )
                second_end = second_start + timedelta(
                    minutes=second_task.duration_minutes
                )
                overlap_start = max(first_start, second_start)
                overlap_end = min(first_end, second_end)
                conflicting_tasks = conflicts_by_window.setdefault(
                    (overlap_start, overlap_end), []
                )
                for assignment in (
                    (first_pet, first_task),
                    (second_pet, second_task),
                ):
                    if not any(
                        existing_pet is assignment[0]
                        and existing_task is assignment[1]
                        for existing_pet, existing_task in conflicting_tasks
                    ):
                        conflicting_tasks.append(assignment)

            conflict_messages = []
            for (overlap_start, overlap_end), assignments in conflicts_by_window.items():
                task_names = [
                    f"{pet.name}'s {task.title}" for pet, task in assignments
                ]
                if len(task_names) == 2:
                    conflicting_tasks_text = " and ".join(task_names)
                else:
                    conflicting_tasks_text = (
                        ", ".join(task_names[:-1]) + f", and {task_names[-1]}"
                    )
                conflict_messages.append(
                    f"- **{overlap_start:%H:%M}–{overlap_end:%H:%M}:** "
                    f"{conflicting_tasks_text} overlap."
                )
            st.warning(
                "**Scheduling conflicts detected**\n\n"
                + "\n".join(conflict_messages)
                + "\n\nConsider changing one task's time."
            )

        if schedule:
            st.markdown(f"### Daily plan for {owner.name}")
            remaining_minutes = int(available_minutes)
            for pet, task in schedule:
                remaining_after_task = remaining_minutes - task.duration_minutes
                st.write(
                    f"- **{task.due_date.strftime('%H:%M')} — {pet.name}: "
                    f"{task.title}** "
                    f"({task.duration_minutes} min, {task.priority} priority, "
                    f"{task.frequency})"
                )
                st.caption(
                    f"Why it's scheduled: It is due at "
                    f"{task.due_date.strftime('%H:%M')} on "
                    f"{selected_date.isoformat()}. The scheduler considers "
                    "higher-priority tasks first, then earlier due times. "
                    f"This task fits the {remaining_minutes} minutes remaining, "
                    f"leaving {remaining_after_task} minutes."
                )
                remaining_minutes = remaining_after_task
        elif not due_today:
            st.info("No incomplete tasks due on this date.")

        scheduled_task_ids = {id(task) for _, task in schedule}
        skipped_tasks = [
            task for _, task in due_today if id(task) not in scheduled_task_ids
        ]
        if skipped_tasks:
            with st.expander("Tasks not scheduled (time limit)"):
                for task in skipped_tasks:
                    st.caption(
                        f"{task.title} — due {task.due_date.strftime('%H:%M')}"
                    )
