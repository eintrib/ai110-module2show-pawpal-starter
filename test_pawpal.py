"""Tests for the PawPal system.

Run with:  pytest
"""

from pawpal_system import Pet, Task


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
