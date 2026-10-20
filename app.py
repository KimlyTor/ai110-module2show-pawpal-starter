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

PawPal+ schedules incomplete tasks due on the selected day, prioritizing high-priority tasks
while fitting as many tasks as possible into the available time.
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

st.subheader("Owner and Pet")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add care tasks with a due date, time, frequency, duration, and priority.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    due_date = st.date_input("Due date", value=date.today())
with col5:
    due_time = st.time_input("Due time", value=time(9, 0))
with col6:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

if st.button("Add task"):
    if not task_title.strip():
        st.error("Enter a task title before adding it.")
    else:
        st.session_state.tasks.append(
            {
                "title": task_title.strip(),
                "duration_minutes": int(duration),
                "priority": priority,
                "due_date": due_date,
                "due_time": due_time,
                "frequency": frequency,
            }
        )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                **task,
                "due_date": task["due_date"].isoformat(),
                "due_time": task["due_time"].strftime("%H:%M"),
            }
            for task in st.session_state.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
selected_date = st.date_input("Schedule date", value=date.today())
available_minutes = st.number_input(
    "Available time (minutes)", min_value=0, max_value=1440, value=60
)

if st.button("Generate schedule"):
    if not owner_name.strip() or not pet_name.strip():
        st.error("Enter both an owner name and a pet name to generate a schedule.")
    else:
        pet_tasks = [
            CareTask(
                description=task["title"],
                title=task["title"],
                due_date=datetime.combine(task["due_date"], task["due_time"]),
                duration_minutes=task["duration_minutes"],
                priority=task["priority"],
                frequency=task["frequency"],
            )
            for task in st.session_state.tasks
        ]
        pet = Pet(name=pet_name.strip(), species=species, tasks=pet_tasks)
        owner = Owner(name=owner_name.strip(), pets=[pet])
        scheduler = DailyScheduler()
        all_tasks = scheduler.get_tasks(owner)
        schedule = scheduler.build_daily_schedule(
            all_tasks, selected_date, int(available_minutes)
        )

        if schedule:
            st.markdown(f"### Daily plan for {pet.name}")
            for _, task in schedule:
                st.write(
                    f"- **{task.due_date.strftime('%H:%M')} — {task.title}** "
                    f"({task.duration_minutes} min, {task.priority} priority, "
                    f"{task.frequency}). "
                    f"Included because it is due on {selected_date.isoformat()} "
                    "and fits the available time."
                )
        else:
            st.info("No incomplete tasks due on this date fit the available time.")

        due_today = scheduler.filter_tasks_by_due_status(
            all_tasks, selected_date, "today"
        )
        scheduled_task_ids = {id(task) for _, task in schedule}
        skipped_tasks = [
            task for _, task in due_today if id(task) not in scheduled_task_ids
        ]
        if skipped_tasks:
            st.caption(
                "Not scheduled because of the time limit: "
                + ", ".join(task.title for task in skipped_tasks)
            )
