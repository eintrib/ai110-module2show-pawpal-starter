"""PawPal — pet care app.

Core implementation of the four classes from the UML in diagrams/uml_draft.mmd.
Data-holding objects (Task, Pet) use dataclasses to keep the code clean.

Relationships:
    Owner  1 --> * Pet      (an owner manages many pets)
    Pet    1 --> * Task     (a pet has many tasks)
    Task   * --> 1 Pet      (back-reference, set when added to a pet)
    Scheduler --> * Pet     (the "brain" that works across all pets)
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single care activity for a pet (walk, feeding, grooming, ...)."""

    id: int
    description: str
    time: str = ""            # time of day, e.g. "08:00"
    frequency: str = "once"   # "once", "daily", or "weekly"
    is_complete: bool = False
    # CHANGE: added a back-reference so a Task can point to its Pet.
    # Original skeleton only allowed top-down navigation (Pet -> Task).
    pet: Pet | None = None

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.is_complete = True

    def reset(self) -> None:
        """Mark this task as not done (useful for recurring tasks)."""
        self.is_complete = False

    def reschedule(self, new_time: str) -> None:
        """Move this task to a new time of day."""
        # CHANGE: reschedule now updates `time` (was an empty stub before).
        self.time = new_time

    def __str__(self) -> str:
        """Return a short human-readable summary of the task."""
        status = "done" if self.is_complete else "todo"
        when = self.time or "anytime"
        return f"[{status}] {when} — {self.description} ({self.frequency})"


@dataclass
class Pet:
    """A pet owned by an Owner. Stores pet details and its list of tasks."""

    id: int
    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)
    # CHANGE: added a back-reference so a Pet can point to its Owner.
    owner: Owner | None = None

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and link it back to this pet."""
        # CHANGE: set the back-reference automatically so it can never drift
        # out of sync with the tasks list.
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Detach a task from this pet."""
        if task in self.tasks:
            self.tasks.remove(task)
            task.pet = None

    def list_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return list(self.tasks)

    def pending_tasks(self) -> list[Task]:
        """Return only the tasks that are not yet complete."""
        return [t for t in self.tasks if not t.is_complete]

    def __str__(self) -> str:
        """Return a short human-readable summary of the pet."""
        return f"{self.name} ({self.species}, {self.age}y)"


@dataclass
class Owner:
    """A person who manages one or more pets and all of their tasks."""

    id: int
    name: str
    email: str = ""
    phone: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet to this owner and link it back to this owner."""
        # CHANGE: set the Pet -> Owner back-reference automatically.
        pet.owner = self
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner."""
        if pet in self.pets:
            self.pets.remove(pet)
            pet.owner = None

    def list_pets(self) -> list[Pet]:
        """Return all pets owned by this owner."""
        return list(self.pets)

    def all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        # CHANGE: new method — flattens each pet's task list into one list so
        # an owner can see all of their pets' tasks at once.
        return [task for pet in self.pets for task in pet.tasks]

    def _next_task_id(self) -> int:
        """Return an unused task id across all of this owner's pets."""
        existing = [task.id for task in self.all_tasks()]
        return max(existing) + 1 if existing else 1

    def add_task_to_all(
        self, description: str, time: str = "", frequency: str = "daily"
    ) -> list[Task]:
        """Give the same task to every pet, with each pet getting its own copy."""
        # A separate Task per pet is required so completing one pet's task does
        # not mark the others done, and so each Task.pet back-reference is correct.
        created: list[Task] = []
        for pet in self.pets:
            task = Task(
                id=self._next_task_id(),
                description=description,
                time=time,
                frequency=frequency,
            )
            pet.add_task(task)  # sets task.pet back-reference automatically
            created.append(task)
        return created

    def add_daily_routine(self) -> None:
        """Give every pet the shared routine: breakfast, walk, and dinner."""
        # Pet-specific tasks (e.g. a vet visit) should still use pet.add_task(...).
        self.add_task_to_all("Breakfast", time="07:30", frequency="daily")
        self.add_task_to_all("Daily walk", time="08:00", frequency="daily")
        self.add_task_to_all("Dinner", time="18:00", frequency="daily")

    def __str__(self) -> str:
        """Return a short human-readable summary of the owner."""
        return f"{self.name} ({len(self.pets)} pet(s))"


# CHANGE: the original UML had a per-pet `Schedule` (date range). The assignment
# asks for a `Scheduler` "brain" that works ACROSS all pets, so this class
# replaces Schedule and is a plain class (not a dataclass) since it holds
# behavior/logic rather than being a simple data record.
class Scheduler:
    """The 'brain': retrieves, organizes, and manages tasks across many pets."""

    def __init__(self, pets: list[Pet] | None = None) -> None:
        """Create a scheduler, optionally seeded with a list of pets."""
        self.pets: list[Pet] = list(pets) if pets else []

    def register_pet(self, pet: Pet) -> None:
        """Add a pet to the scheduler's view."""
        if pet not in self.pets:
            self.pets.append(pet)

    def register_owner(self, owner: Owner) -> None:
        """Add all of an owner's pets to the scheduler at once."""
        for pet in owner.pets:
            self.register_pet(pet)

    def all_tasks(self) -> list[Task]:
        """Return every task across every registered pet."""
        return [task for pet in self.pets for task in pet.tasks]

    def pending_tasks(self) -> list[Task]:
        """Return all incomplete tasks across every pet."""
        return [t for t in self.all_tasks() if not t.is_complete]

    def completed_tasks(self) -> list[Task]:
        """Return all completed tasks across every pet."""
        return [t for t in self.all_tasks() if t.is_complete]

    def tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Return the tasks belonging to a single pet."""
        return pet.list_tasks()

    def tasks_by_frequency(self, frequency: str) -> list[Task]:
        """Return all tasks matching a given frequency (e.g. 'daily')."""
        return [t for t in self.all_tasks() if t.frequency == frequency]

    def daily_plan(self) -> list[Task]:
        """Return today's pending tasks, ordered by time of day."""
        pending = self.pending_tasks()
        # Sort key is a tuple: (has-no-time, time). The bool sorts False (0)
        # before True (1), so timed tasks come first in time order and
        # untimed ("anytime") tasks fall to the bottom of the plan.
        return sorted(pending, key=lambda t: (t.time == "", t.time))

    def print_daily_plan(self) -> None:
        """Print a clear, well-explained daily plan ordered by time."""
        plan = self.daily_plan()
        if not plan:
            print("All tasks are complete — nothing left for today!")
            return

        print("=== PawPal Daily Plan ===")
        for task in plan:
            pet_name = task.pet.name if task.pet else "Unassigned"
            when = task.time or "anytime"
            print(f"  {when:>7}  {pet_name}: {task.description} ({task.frequency})")

    def complete_task(self, task: Task) -> None:
        """Mark a given task as complete."""
        task.mark_complete()

    def reset_recurring(self) -> None:
        """Reset daily/weekly tasks so they can be done again next cycle."""
        for task in self.all_tasks():
            if task.frequency in ("daily", "weekly"):
                task.reset()


if __name__ == "__main__":
    # Small demo so you can run `python pawpal_system.py` and see it work.
    owner = Owner(id=1, name="Britnie", email="britnie@example.com")

    rex = Pet(id=1, name="Rex", species="dog", breed="Labrador", age=3)
    mimi = Pet(id=2, name="Mimi", species="cat", breed="Tabby", age=5)
    owner.add_pet(rex)
    owner.add_pet(mimi)

    rex.add_task(Task(id=1, description="Morning walk", time="08:00", frequency="daily"))
    rex.add_task(Task(id=2, description="Dinner", time="18:00", frequency="daily"))
    mimi.add_task(Task(id=3, description="Feed", time="07:30", frequency="daily"))
    mimi.add_task(Task(id=4, description="Vet visit", time="14:00", frequency="once"))

    scheduler = Scheduler()
    scheduler.register_owner(owner)

    scheduler.print_daily_plan()

    # Complete the morning walk, then show the updated plan.
    print("\nRex finished his walk!\n")
    scheduler.complete_task(rex.tasks[0])
    scheduler.print_daily_plan()
