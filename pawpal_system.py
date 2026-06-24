"""PawPal — pet care app.

Class skeleton generated from the UML in diagrams/uml_draft.mmd.
Data-holding objects (Pet, Task) use dataclasses to keep the code clean.
Method bodies are intentionally left as stubs to be implemented later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    """A single care task for a pet (feeding, walk, vet visit, etc.)."""

    id: int
    title: str
    description: str = ""
    type: str = ""
    is_complete: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        ...

    def reschedule(self, new_date: date) -> None:
        """Move this task to a new date."""
        ...


@dataclass
class Pet:
    """A pet owned by an Owner."""

    id: int
    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        ...

    def list_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        ...


@dataclass
class Owner:
    """A person who owns one or more pets."""

    id: int
    name: str
    email: str = ""
    phone: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet to this owner."""
        ...

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        ...

    def list_pets(self) -> list[Pet]:
        """Return all pets owned by this owner."""
        ...


@dataclass
class Schedule:
    """Organizes tasks over a date range for a pet."""

    id: int
    start_date: date
    end_date: date
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this schedule."""
        ...

    def remove_task(self, task: Task) -> None:
        """Remove a task from this schedule."""
        ...

    def get_tasks_for_day(self, day: date) -> list[Task]:
        """Return all tasks scheduled for the given day."""
        ...
