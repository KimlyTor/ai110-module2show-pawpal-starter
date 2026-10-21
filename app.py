from datetime import date, datetime, time

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

    for pet in st.session_state.pets:
        if pet["tasks"]:
            st.write(f"Tasks for **{pet['name']}**:")
            headers = st.columns([2, 1, 1, 1, 2, 2])
            for column, label in zip(
                headers,
                [
                    "Task",
                    "Duration",
                    "Priority",
                    "Frequency",
                    "Due",
                    "Status / action",
                ],
            ):
                column.markdown(f"**{label}**")

            for task_index, task in enumerate(pet["tasks"]):
                task_columns = st.columns(
                    [2, 1, 1, 1, 2, 2], vertical_alignment="center"
                )
                task_columns[0].write(task["title"])
                task_columns[1].write(f"{task['duration_minutes']} min")
                task_columns[2].write(task["priority"].title())
                task_columns[3].write(task["frequency"].title())
                task_columns[4].write(
                    f"{task['due_date'].isoformat()} "
                    f"{task['due_time'].strftime('%H:%M')}"
                )

                if task.get("is_completed", False):
                    task_columns[5].success("Completed")
                elif task_columns[5].button(
                    "Mark complete",
                    key=f"complete_{pet['id']}_{task_index}",
                    type="secondary",
                    use_container_width=True,
                ):
                    task_model = CareTask(
                        description=task["title"],
                        title=task["title"],
                        due_date=datetime.combine(
                            task["due_date"], task["due_time"]
                        ),
                        duration_minutes=task["duration_minutes"],
                        priority=task["priority"],
                        frequency=task["frequency"],
                    )
                    pet_model = Pet(
                        pet["name"], pet["species"], tasks=[task_model]
                    )
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
            st.caption(f"No tasks added for {pet['name']} yet.")

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

        for (first_pet, first_task), (second_pet, second_task) in time_conflicts:
            st.warning(
                f"Time conflict: {first_pet.name}'s {first_task.title} overlaps "
                f"{second_pet.name}'s {second_task.title}."
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
