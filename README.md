# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Implementation Summary

PawPal+ turns pet care tasks into a daily plan. An `Owner` keeps track of `Pet` objects, and each pet manages its own `CareTask` objects, which store details like due date, duration, priority, and recurrence. The `DailyScheduler` finds incomplete tasks due on the selected day, prioritizes them, and fits them into the available time. Finally, the Streamlit app collects the details and displays the plan.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule for Jordan (2 pets):
- 08:00 Mochi: Walk (30 min, high priority, daily)
- 09:00 Luna: Feed (10 min, medium priority, daily)
- 17:30 Mochi: Play (20 min, low priority, daily)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Scheduling Logic

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `DailyScheduler.build_daily_schedule` | Prioritizes high-priority tasks, then earlier due times. |
| Filtering | `DailyScheduler.filter_tasks_by_due_status` | Selects incomplete tasks due today, upcoming, or overdue. |
| Time constraint | `DailyScheduler.build_daily_schedule` | Includes tasks that fit within available minutes; tasks that do not fit are skipped. |
| Recurrence | `CareTask.is_due_on` | Supports one-time, daily, and weekly occurrences, starting on the task's due date. |
| Task validation | `CareTask` | Requires positive duration, low/medium/high priority, and once/daily/weekly frequency. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
