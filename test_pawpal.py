"""Tests for the PawPal system.

Run with:  pytest

Organized by core behavior. Each test targets one behavior so a failure
names exactly what broke. Covers happy paths and the edge cases that tend
to break schedulers (empty pets, identical/unpadded times, one-off vs.
recurring tasks, and month/year boundaries).
"""

from datetime import date

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


# --------------------------------------------------------------------------- #
# Fixtures / helpers
# --------------------------------------------------------------------------- #
def make_scheduler_with_pets():
    """Build an owner with two pets and a spread of tasks for reuse."""
    owner = Owner(id=1, name="Britnie")
    rex = Pet(id=1, name="Rex", species="dog")
    mimi = Pet(id=2, name="Mimi", species="cat")
    owner.add_pet(rex)
    owner.add_pet(mimi)

    rex.add_task(Task(id=1, description="Morning walk", time="08:00", frequency="daily"))
    rex.add_task(Task(id=2, description="Dinner", time="18:00", frequency="daily"))
    mimi.add_task(Task(id=3, description="Feed", time="07:30", frequency="daily"))
    mimi.add_task(Task(id=4, description="Vet visit", time="14:00", frequency="once"))

    scheduler = Scheduler()
    scheduler.register_owner(owner)
    return scheduler, owner, rex, mimi


# --------------------------------------------------------------------------- #
# Existing behaviors (kept)
# --------------------------------------------------------------------------- #
def test_mark_complete_changes_status():
    """Task Completion: mark_complete() should flip is_complete to True."""
    task = Task(id=1, description="Morning walk", time="08:00", frequency="daily")

    # A new task starts out incomplete.
    assert task.is_complete is False

    task.mark_complete()

    # After marking complete, the status should have changed.
    assert task.is_complete is True


def test_add_task_increases_pet_task_count():
    """Task Addition: adding a task to a Pet increases that pet's task count."""
    pet = Pet(id=1, name="Rex", species="dog")

    # A new pet has no tasks yet.
    assert len(pet.tasks) == 0

    pet.add_task(Task(id=1, description="Dinner", time="18:00", frequency="daily"))

    # The task count should have grown by one.
    assert len(pet.tasks) == 1

    pet.add_task(Task(id=2, description="Breakfast", time="07:30", frequency="daily"))

    # Adding a second task grows the count again.
    assert len(pet.tasks) == 2


def test_add_task_sets_back_reference():
    """add_task() should link the task back to its pet."""
    pet = Pet(id=1, name="Rex", species="dog")
    task = Task(id=1, description="Dinner")
    pet.add_task(task)
    assert task.pet is pet


# --------------------------------------------------------------------------- #
# 1. Sorting by time
# --------------------------------------------------------------------------- #
def test_daily_plan_sorted_chronologically():
    """Happy path: daily_plan() orders pending tasks earliest-first."""
    scheduler, *_ = make_scheduler_with_pets()
    times = [t.time for t in scheduler.daily_plan()]
    assert times == ["07:30", "08:00", "14:00", "18:00"]


def test_sort_pushes_untimed_tasks_to_end():
    """Edge: untimed tasks (time == '') sort to the bottom, not the top."""
    scheduler, _, rex, _ = make_scheduler_with_pets()
    rex.add_task(Task(id=5, description="Cuddle", time="", frequency="once"))
    ordered = scheduler.sort_by_time()
    # The untimed task must be last.
    assert ordered[-1].description == "Cuddle"


def test_sort_handles_unpadded_times():
    """Edge: '8:00' must sort before '09:00' (sorted by minutes, not string)."""
    a = Task(id=1, description="early", time="8:00")
    b = Task(id=2, description="late", time="09:00")
    scheduler = Scheduler()
    ordered = scheduler.sort_by_time([b, a])
    assert [t.description for t in ordered] == ["early", "late"]


def test_sort_handles_malformed_time_without_raising():
    """Edge: a malformed time string must not break the whole sort."""
    good = Task(id=1, description="good", time="08:00")
    bad = Task(id=2, description="bad", time="25:99")
    scheduler = Scheduler()
    ordered = scheduler.sort_by_time([bad, good])
    # Bad time is treated as "anytime" and falls to the end.
    assert [t.description for t in ordered] == ["good", "bad"]


# --------------------------------------------------------------------------- #
# 2. Recurring task completion
# --------------------------------------------------------------------------- #
def test_complete_daily_task_schedules_next_day():
    """Happy path: completing a daily task spawns a fresh task for tomorrow."""
    scheduler, _, rex, _ = make_scheduler_with_pets()
    walk = rex.tasks[0]  # "Morning walk", daily

    next_task = scheduler.complete_task(walk, today=date(2026, 7, 7))

    assert walk.is_complete is True
    assert next_task is not None
    assert next_task.is_complete is False
    assert next_task.id != walk.id
    assert next_task.due_date == date(2026, 7, 8)  # today + 1 day
    assert next_task.pet is rex  # attached to the same pet


def test_complete_weekly_task_schedules_seven_days_out():
    """Happy path: a weekly task's next occurrence is today + 7 days."""
    pet = Pet(id=1, name="Rex", species="dog")
    task = Task(id=1, description="Grooming", time="10:00", frequency="weekly")
    pet.add_task(task)
    scheduler = Scheduler([pet])

    next_task = scheduler.complete_task(task, today=date(2026, 7, 7))
    assert next_task.due_date == date(2026, 7, 14)


def test_complete_once_task_returns_none():
    """Edge: a one-off task is completed but spawns no next occurrence."""
    scheduler, _, _, mimi = make_scheduler_with_pets()
    vet = mimi.tasks[1]  # "Vet visit", once
    before = len(mimi.tasks)

    result = scheduler.complete_task(vet, today=date(2026, 7, 7))

    assert vet.is_complete is True
    assert result is None
    assert len(mimi.tasks) == before  # no new task added


def test_next_due_date_rolls_month_boundary():
    """Edge: daily task completed on Jan 31 lands on Feb 1."""
    task = Task(id=1, description="Walk", frequency="daily")
    assert task.next_due_date(date(2026, 1, 31)) == date(2026, 2, 1)


def test_next_due_date_rolls_year_boundary():
    """Edge: daily task completed on Dec 31 lands on Jan 1 of next year."""
    task = Task(id=1, description="Walk", frequency="daily")
    assert task.next_due_date(date(2026, 12, 31)) == date(2027, 1, 1)


def test_next_due_date_once_returns_none():
    """Edge: a one-off task has no next occurrence."""
    task = Task(id=1, description="Vet", frequency="once")
    assert task.next_due_date(date(2026, 7, 7)) is None


def test_reset_recurring_only_resets_repeating_tasks():
    """reset_recurring() reopens daily/weekly tasks but leaves one-offs done."""
    scheduler, _, _, _ = make_scheduler_with_pets()
    for t in scheduler.all_tasks():
        t.mark_complete()

    scheduler.reset_recurring()

    for t in scheduler.all_tasks():
        if t.frequency in ("daily", "weekly"):
            assert t.is_complete is False
        else:  # "once"
            assert t.is_complete is True


# --------------------------------------------------------------------------- #
# 3. Conflict detection
# --------------------------------------------------------------------------- #
def test_find_conflicts_flags_same_time_across_pets():
    """Happy path: two pets with an 08:00 task produce one conflict warning."""
    owner = Owner(id=1, name="Britnie")
    rex = Pet(id=1, name="Rex", species="dog")
    mimi = Pet(id=2, name="Mimi", species="cat")
    owner.add_pet(rex)
    owner.add_pet(mimi)
    rex.add_task(Task(id=1, description="Walk", time="08:00"))
    mimi.add_task(Task(id=2, description="Feed", time="08:00"))
    scheduler = Scheduler()
    scheduler.register_owner(owner)

    conflicts = scheduler.find_conflicts()
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_find_conflicts_treats_unpadded_time_as_same_slot():
    """Edge: '8:00' and '08:00' must count as the same time slot."""
    a = Task(id=1, description="Walk", time="8:00")
    b = Task(id=2, description="Feed", time="08:00")
    scheduler = Scheduler()
    conflicts = scheduler.find_conflicts([a, b])
    assert len(conflicts) == 1


def test_find_conflicts_ignores_untimed_tasks():
    """Edge: untimed tasks can't collide on a clock."""
    a = Task(id=1, description="Cuddle", time="")
    b = Task(id=2, description="Nap", time="")
    scheduler = Scheduler()
    assert scheduler.find_conflicts([a, b]) == []


def test_find_conflicts_none_when_times_differ():
    """Happy path: distinct times produce no warnings."""
    scheduler, *_ = make_scheduler_with_pets()
    assert scheduler.find_conflicts() == []


# --------------------------------------------------------------------------- #
# 4. Filtering
# --------------------------------------------------------------------------- #
def test_filter_by_pet_name_is_case_insensitive():
    """Happy path + edge: pet name matching ignores case."""
    scheduler, _, rex, _ = make_scheduler_with_pets()
    tasks = scheduler.filter_tasks(pet_name="rex")
    assert len(tasks) == 2
    assert all(t.pet is rex for t in tasks)


def test_filter_by_status_pending_and_done():
    """Happy path: status filter splits pending from done tasks."""
    scheduler, _, rex, _ = make_scheduler_with_pets()
    rex.tasks[0].mark_complete()

    assert len(scheduler.filter_tasks(status="done")) == 1
    assert len(scheduler.filter_tasks(status="pending")) == 3


def test_filter_combines_pet_and_status():
    """Happy path: pet_name and status combine with AND."""
    scheduler, _, rex, _ = make_scheduler_with_pets()
    rex.tasks[0].mark_complete()

    done_rex = scheduler.filter_tasks(pet_name="Rex", status="DONE")
    assert len(done_rex) == 1
    assert done_rex[0].description == "Morning walk"


def test_filter_unknown_status_raises():
    """Edge: an unrecognized status is a programmer error, not silent."""
    scheduler, *_ = make_scheduler_with_pets()
    with pytest.raises(ValueError):
        scheduler.filter_tasks(status="garbage")


def test_filter_no_args_returns_everything():
    """Happy path: no filters returns all tasks."""
    scheduler, *_ = make_scheduler_with_pets()
    assert len(scheduler.filter_tasks()) == 4


# --------------------------------------------------------------------------- #
# 5. Empty / boundary states
# --------------------------------------------------------------------------- #
def test_pet_with_no_tasks_returns_empty_lists():
    """Edge: a pet with no tasks yields empty plans, not errors."""
    pet = Pet(id=1, name="Ghost", species="fish")
    scheduler = Scheduler([pet])
    assert scheduler.daily_plan() == []
    assert scheduler.pending_tasks() == []
    assert scheduler.find_conflicts() == []


def test_empty_scheduler_next_task_id_is_one():
    """Edge: the first task id in an empty scheduler is 1."""
    scheduler = Scheduler()
    assert scheduler._next_task_id() == 1
    assert scheduler.all_tasks() == []


def test_print_daily_plan_when_all_complete(capsys):
    """Edge: nothing pending prints the friendly 'all complete' message."""
    scheduler, *_ = make_scheduler_with_pets()
    for t in scheduler.all_tasks():
        t.mark_complete()

    scheduler.print_daily_plan()
    out = capsys.readouterr().out
    assert "nothing left" in out.lower()


def test_conflict_message_handles_unassigned_task():
    """Edge: a task with no pet is labeled 'Unassigned', not a crash."""
    a = Task(id=1, description="Walk", time="09:00")  # no pet
    b = Task(id=2, description="Feed", time="09:00")
    scheduler = Scheduler()
    conflicts = scheduler.find_conflicts([a, b])
    assert len(conflicts) == 1
    assert "Unassigned" in conflicts[0]
