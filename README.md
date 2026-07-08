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

## 🖥️ Sample Output

Running `python main.py` produces the following output, showing the tasks
sorted into a single time-ordered daily plan across both pets:

```text
Owner: Britnie
Pets:  Rex, Mimi

Today's Schedule
----------------------------------------
    07:30  Rex & Mimi: Breakfast
    08:00  Rex & Mimi: Daily walk
    10:00  Rex: Grooming
    14:00  Mimi: Vet visit
    18:00  Rex & Mimi: Dinner
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

## 📐 Smarter Scheduling

All scheduling logic lives on the `Scheduler` class (the "brain") in
[`pawpal_system.py`](pawpal_system.py), with per-task helpers on `Task`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` (helper: `Scheduler._time_key()`) | Orders tasks by time of day, earliest first |
| Filtering | `Scheduler.filter_tasks(pet_name=..., status=...)` | Filter by pet name and/or completion status |
| Conflict handling | `Scheduler.find_conflicts()` | Warns on tasks booked at the same time |
| Recurring tasks | `Scheduler.complete_task()` + `Task.next_due_date()` | Completing a daily/weekly task spawns its next occurrence |

### Sorting — `Scheduler.sort_by_time()`

Returns tasks ordered by time of day. Instead of sorting on the raw `"HH:MM"`
string, it converts each time to **minutes since midnight** via the
`_time_key()` helper, so unpadded times like `"8:00"` sort correctly alongside
`"08:00"`. Untimed ("anytime") tasks fall to the bottom, and a malformed time
is treated as untimed rather than raising. It accepts any list of tasks, so it
composes with the filters below.

### Filtering — `Scheduler.filter_tasks(pet_name=..., status=...)`

One flexible query method. Both arguments are optional and combine with AND:

- `filter_tasks(pet_name="Rex")` — only Rex's tasks
- `filter_tasks(status="pending")` — only unfinished tasks
- `filter_tasks(pet_name="Rex", status="done")` — Rex's completed tasks

`status` accepts `"pending"`/`"todo"` or `"done"`/`"complete"`, and both the
status and pet-name matching are case-insensitive.

### Conflict detection — `Scheduler.find_conflicts()`

A lightweight check that catches double-booking. It buckets tasks into time
slots (by minutes since midnight, so `"8:00"` and `"08:00"` share a slot) and
returns a warning message for any slot holding two or more tasks — whether the
clash is within one pet or across different pets. It **returns a list of
warning strings and never raises**, so the program keeps running on a conflict.
Untimed tasks are skipped because they can't collide on a clock.

### Recurring tasks — `Scheduler.complete_task()` + `Task.next_due_date()`

When a `"daily"` or `"weekly"` task is marked complete via
`complete_task()`, the scheduler automatically creates a fresh `Task` for the
next occurrence (new id, not yet complete) and attaches it to the same pet.
`Task.next_due_date()` computes the new date with `datetime.timedelta`
(daily → today + 1 day, weekly → today + 7 days), which rolls month and year
boundaries accurately. A one-off (`"once"`) task returns `None` and does not
repeat.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
