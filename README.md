# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Features

PawPal+ turns a loose list of pet-care tasks into an ordered, conflict-checked
daily plan across every pet an owner has. The scheduling logic lives on the
`Scheduler` class in [`pawpal_system.py`](pawpal_system.py); see
[Smarter Scheduling](#-smarter-scheduling) below for the implementation details.

- **⏱️ Sorting by time** — builds a single daily plan ordered earliest-first.
  Times are compared as *minutes since midnight*, so unpadded values like
  `"8:00"` sort correctly next to `"08:00"`, and untimed ("anytime") tasks fall
  to the bottom instead of breaking the order.
- **⚠️ Conflict warnings** — detects double-booking by bucketing tasks into
  time slots and flagging any slot with two or more tasks — whether the clash is
  within one pet or across different pets. It returns warning messages and never
  crashes on a conflict.
- **🔁 Daily & weekly recurrence** — completing a recurring task automatically
  spawns its next occurrence, with the date advanced by `timedelta`
  (daily → +1 day, weekly → +7 days) so month and year boundaries roll over
  correctly. One-off tasks simply complete and do not repeat.
- **🔎 Filtering** — query tasks by pet name and/or completion status; the two
  filters combine with AND and are case-insensitive.
- **👪 Multi-pet & shared routines** — the scheduler plans across all of an
  owner's pets at once, and helpers like `add_task_to_all()` and
  `add_daily_routine()` give every pet its own copy of a shared task.
- **🖥️ Interactive Streamlit UI** — add pets and tasks, filter the plan, and see
  sorted results and conflict warnings rendered as tables and alerts
  ([`app.py`](app.py)).

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

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

**What the tests cover** — 27 tests in [`test_pawpal.py`](test_pawpal.py),
organized by the system's core scheduling behaviors, covering both happy paths
and the edge cases that tend to break schedulers:

- **Sorting correctness** — tasks return in chronological order; unpadded times
  (`"8:00"`) sort correctly, untimed tasks fall to the bottom, and a malformed
  time is handled instead of raising.
- **Recurrence logic** — completing a daily task spawns a fresh task for the
  next day (weekly → +7 days), one-off tasks spawn nothing, and the date math
  correctly rolls month and year boundaries.
- **Conflict detection** — duplicate times are flagged (within one pet or
  across pets), `"8:00"` and `"08:00"` count as the same slot, and untimed
  tasks are ignored.
- **Filtering** — by pet name and/or status, case-insensitively and combined
  with AND; an unknown status raises `ValueError`.
- **Empty / boundary states** — a pet with no tasks, an empty scheduler, an
  all-complete plan, and an unassigned task all behave gracefully.

Successful test run:

```text
============================= test session starts ==============================
platform darwin -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0 -- /Users/britniem/ai110-module2show-pawpal-starter/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/britniem/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collecting ... collected 27 items

test_pawpal.py::test_mark_complete_changes_status PASSED                 [  3%]
test_pawpal.py::test_add_task_increases_pet_task_count PASSED            [  7%]
test_pawpal.py::test_add_task_sets_back_reference PASSED                 [ 11%]
test_pawpal.py::test_daily_plan_sorted_chronologically PASSED            [ 14%]
test_pawpal.py::test_sort_pushes_untimed_tasks_to_end PASSED             [ 18%]
test_pawpal.py::test_sort_handles_unpadded_times PASSED                  [ 22%]
test_pawpal.py::test_sort_handles_malformed_time_without_raising PASSED  [ 25%]
test_pawpal.py::test_complete_daily_task_schedules_next_day PASSED       [ 29%]
test_pawpal.py::test_complete_weekly_task_schedules_seven_days_out PASSED [ 33%]
test_pawpal.py::test_complete_once_task_returns_none PASSED              [ 37%]
test_pawpal.py::test_next_due_date_rolls_month_boundary PASSED           [ 40%]
test_pawpal.py::test_next_due_date_rolls_year_boundary PASSED            [ 44%]
test_pawpal.py::test_next_due_date_once_returns_none PASSED              [ 48%]
test_pawpal.py::test_reset_recurring_only_resets_repeating_tasks PASSED  [ 51%]
test_pawpal.py::test_find_conflicts_flags_same_time_across_pets PASSED   [ 55%]
test_pawpal.py::test_find_conflicts_treats_unpadded_time_as_same_slot PASSED [ 59%]
test_pawpal.py::test_find_conflicts_ignores_untimed_tasks PASSED         [ 62%]
test_pawpal.py::test_find_conflicts_none_when_times_differ PASSED        [ 66%]
test_pawpal.py::test_filter_by_pet_name_is_case_insensitive PASSED       [ 70%]
test_pawpal.py::test_filter_by_status_pending_and_done PASSED            [ 74%]
test_pawpal.py::test_filter_combines_pet_and_status PASSED               [ 77%]
test_pawpal.py::test_filter_unknown_status_raises PASSED                 [ 81%]
test_pawpal.py::test_filter_no_args_returns_everything PASSED            [ 85%]
test_pawpal.py::test_pet_with_no_tasks_returns_empty_lists PASSED        [ 88%]
test_pawpal.py::test_empty_scheduler_next_task_id_is_one PASSED          [ 92%]
test_pawpal.py::test_print_daily_plan_when_all_complete PASSED           [ 96%]
test_pawpal.py::test_conflict_message_handles_unassigned_task PASSED     [100%]

============================== 27 passed in 0.02s ==============================
```

### Confidence Level

⭐⭐⭐⭐⭐ (5 / 5)

All 27 tests pass, and they exercise every core behavior — sorting, recurrence,
conflict detection, and filtering — across both happy paths and the tricky edge
cases (empty pets, identical/unpadded times, one-off vs. recurring tasks, and
month/year boundaries). No bugs surfaced during testing. The one caveat holding
this at "very confident" rather than "proven in production" is that these are
unit tests of the scheduling logic in [`pawpal_system.py`](pawpal_system.py);
the Streamlit UI layer in [`app.py`](app.py) is not yet covered by automated
tests.

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

## 🎬 Demo Walkthrough

PawPal+ can be used two ways: the interactive **Streamlit app** (`app.py`) for
day-to-day planning, and the **CLI demo** (`main.py`) that exercises the full
scheduler in one run.

### The Streamlit app

Launch it with:

```bash
streamlit run app.py
```

Main features and the actions a user can perform:

- **Owner** — set the owner's name.
- **Add a Pet** — enter a pet name, pick a species (dog / cat / other), and add
  it. Added pets are listed back, and the app blocks task creation until at
  least one pet exists.
- **Schedule a Task** — choose a pet (or *All pets* for a shared task), then
  enter a description, a time (`HH:MM`), and a frequency (once / daily / weekly).
- **Today's Schedule** — the plan renders as a clean table (Time · Pet · Task ·
  Frequency · Status), with two filters: **Show tasks for** (a specific pet or
  all) and **Status** (all / pending / done).

### Example workflow

1. **Add a pet** — type `Rex`, species `dog`, click **Add pet**. A success
   message confirms `Rex` was added.
2. **Schedule tasks** — add `Morning walk` at `08:00` (daily) and `Dinner` at
   `18:00` (daily) for Rex; add a shared `Feed` at `08:00` (daily) for *All
   pets*.
3. **View today's schedule** — the table shows the tasks sorted by time. Because
   Rex's walk and the shared feed both sit at `08:00`, a conflict warning
   appears above the table.
4. **Filter** — switch **Status** to *Pending* to hide anything already done, or
   pick a single pet to focus the plan.

### Key Scheduler behaviors shown

- **Sorting by time** — tasks entered out of order (e.g. Dinner before
  Breakfast) still appear earliest-first; untimed tasks sort to the bottom.
- **Conflict warnings** — same-time tasks are flagged, both within one pet and
  across pets, and shown as a prominent alert with an ⚠️ marker on the affected
  rows.
- **Filtering** — by pet name and by completion status, combined and
  case-insensitive.
- **Daily recurrence** — completing a daily task schedules its next occurrence
  for the following day.

### Sample CLI output

Running the demo script exercises every behavior above end-to-end:

```bash
python main.py
```

```text
Owner: Britnie
Pets:  Rex, Mimi

All tasks, sorted by time
----------------------------------------
  [done] 7:30 — Breakfast (daily)
  [done] 08:00 — Morning walk (daily)
  [todo] 08:00 — Feed (daily)
  [todo] 10:00 — Grooming (weekly)
  [todo] 14:00 — Vet visit (once)
  [todo] 18:00 — Dinner (daily)
  [todo] 18:00 — Take medication (daily)
  [todo] anytime — Play time (daily)

Rex's tasks only
----------------------------------------
  [done] 08:00 — Morning walk (daily)
  [todo] 10:00 — Grooming (weekly)
  [todo] 18:00 — Dinner (daily)
  [todo] 18:00 — Take medication (daily)

Still pending (across all pets)
----------------------------------------
  [todo] 08:00 — Feed (daily)
  [todo] 10:00 — Grooming (weekly)
  [todo] 14:00 — Vet visit (once)
  [todo] 18:00 — Dinner (daily)
  [todo] 18:00 — Take medication (daily)
  [todo] anytime — Play time (daily)

Already done
----------------------------------------
  [done] 7:30 — Breakfast (daily)
  [done] 08:00 — Morning walk (daily)

Schedule conflicts
----------------------------------------
  ⚠️  Conflict at 08:00: 2 tasks overlap — Rex's 'Morning walk', Mimi's 'Feed'
  ⚠️  Conflict at 18:00: 2 tasks overlap — Rex's 'Dinner', Rex's 'Take medication'

Recurring tasks
----------------------------------------
  Completing: [todo] 2026-07-07 18:00 — Dinner (daily)
  Auto-created next occurrence: [todo] 2026-07-08 18:00 — Dinner (daily)
```
