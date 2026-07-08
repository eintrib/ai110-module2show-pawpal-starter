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
from datetime import date, timedelta


@dataclass
class Task:
    """A single care activity for a pet (walk, feeding, grooming, ...)."""

    id: int
    description: str
    time: str = ""            # time of day, e.g. "08:00"
    frequency: str = "once"   # "once", "daily", or "weekly"
    is_complete: bool = False
    # CHANGE: added a calendar date so a recurring task knows *which day* it is
    # due. Combined with `time`, this pins the task to a real point in time.
    due_date: date | None = None
    # CHANGE: added a back-reference so a Task can point to its Pet.
    # Original skeleton only allowed top-down navigation (Pet -> Task).
    pet: Pet | None = None

    # How far ahead each frequency repeats. "once" is absent on purpose: a
    # one-off task has no next occurrence.
    _REPEAT_INTERVALS = {
        "daily": timedelta(days=1),
        "weekly": timedelta(days=7),
    }

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.is_complete = True

    def next_due_date(self, from_date: date | None = None) -> date | None:
        """Return the date of this task's next occurrence, or None if one-off.

        Uses ``timedelta`` to advance the date accurately (it rolls month and
        year boundaries for you, so "daily" on Jan 31 correctly lands on Feb 1).
        The step is measured from ``from_date`` when given, otherwise from this
        task's own ``due_date``, otherwise from today.
        """
        interval = self._REPEAT_INTERVALS.get(self.frequency)
        if interval is None:
            return None  # "once" (or anything unrecognised) does not repeat
        base = from_date or self.due_date or date.today()
        return base + interval

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
        day = f" {self.due_date.isoformat()}" if self.due_date else ""
        return f"[{status}]{day} {when} — {self.description} ({self.frequency})"


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

    def add_task_to_pet(
        self, pet: Pet, description: str, time: str = "", frequency: str = "once"
    ) -> Task:
        """Create a task with a unique id and add it to one specific pet."""
        task = Task(
            id=self._next_task_id(),
            description=description,
            time=time,
            frequency=frequency,
        )
        pet.add_task(task)
        return task

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

    def filter_tasks(
        self,
        *,
        pet_name: str | None = None,
        status: str | None = None,
    ) -> list[Task]:
        """Return tasks filtered by pet name and/or completion status.

        Both filters are optional and combine (AND):
            filter_tasks()                      -> every task
            filter_tasks(pet_name="Rex")        -> only Rex's tasks
            filter_tasks(status="pending")      -> only unfinished tasks
            filter_tasks(pet_name="Rex", status="done")  -> Rex's done tasks

        `status` accepts "done"/"complete" or "pending"/"todo"
        (case-insensitive). Pet name matching is also case-insensitive.
        """
        tasks = self.all_tasks()

        if pet_name is not None:
            wanted = pet_name.lower()
            tasks = [t for t in tasks if t.pet and t.pet.name.lower() == wanted]

        if status is not None:
            key = status.lower()
            if key in ("done", "complete", "completed"):
                tasks = [t for t in tasks if t.is_complete]
            elif key in ("pending", "todo", "incomplete"):
                tasks = [t for t in tasks if not t.is_complete]
            else:
                raise ValueError(f"Unknown status filter: {status!r}")

        return tasks

    @staticmethod
    def _time_key(task: Task) -> int:
        """Return a task's time as minutes-since-midnight, for sorting.

        Untimed tasks (time == "") return a large sentinel so they sort to
        the end. Any unparseable time is treated the same way rather than
        raising, so one bad string can't break the whole plan.
        """
        try:
            hours, minutes = task.time.split(":")
            return int(hours) * 60 + int(minutes)
        except (ValueError, AttributeError):
            return 24 * 60  # "anytime" / malformed -> after every real time

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks sorted by time of day (earliest first).

        Works on any list of tasks; defaults to every task the scheduler
        knows about. Timed tasks come first in chronological order and
        untimed tasks fall to the bottom. Handles unpadded times like
        "8:00" correctly because it sorts on minutes, not on the raw string.
        """
        source = self.all_tasks() if tasks is None else tasks
        return sorted(source, key=self._time_key)

    def daily_plan(self) -> list[Task]:
        """Return today's pending tasks, ordered by time of day."""
        return self.sort_by_time(self.pending_tasks())

    def find_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Return warning messages for tasks scheduled at the same time.

        Lightweight strategy: bucket tasks into time slots (by minutes since
        midnight, so "8:00" and "08:00" count as the same slot) and flag any
        slot holding more than one task. Works whether the clash is within one
        pet or across different pets. Untimed ("anytime") tasks are skipped
        because they can't collide on a clock.

        Returns a (possibly empty) list of human-readable strings — it never
        raises, so callers can simply print whatever comes back.
        """
        source = self.all_tasks() if tasks is None else tasks

        slots: dict[int, list[Task]] = {}
        for task in source:
            if not task.time:
                continue  # no fixed time -> nothing to conflict with
            slots.setdefault(self._time_key(task), []).append(task)

        warnings: list[str] = []
        for minutes, group in sorted(slots.items()):
            if len(group) < 2:
                continue  # only one task in this slot -> no conflict
            when = f"{minutes // 60:02d}:{minutes % 60:02d}"
            who = ", ".join(
                f"{t.pet.name if t.pet else 'Unassigned'}'s '{t.description}'"
                for t in group
            )
            warnings.append(
                f"⚠️  Conflict at {when}: {len(group)} tasks overlap — {who}"
            )
        return warnings

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

    def _next_task_id(self) -> int:
        """Return an unused task id across every registered pet."""
        existing = [t.id for t in self.all_tasks()]
        return max(existing) + 1 if existing else 1

    def complete_task(self, task: Task, today: date | None = None) -> Task | None:
        """Mark a task complete and, if it recurs, schedule its next occurrence.

        For a "daily" or "weekly" task this creates a *fresh* Task for the next
        occurrence (a new id, not yet complete), dates it with ``timedelta``
        (daily -> today + 1 day, weekly -> today + 7 days), and attaches it to
        the same pet. Returns the newly created Task, or None for a one-off
        task that does not repeat.
        """
        task.mark_complete()

        # Base the next occurrence on the completion day, so finishing a daily
        # task today schedules it for tomorrow (today + 1 day).
        next_date = task.next_due_date(today or date.today())
        if next_date is None:
            return None

        next_task = Task(
            id=self._next_task_id(),
            description=task.description,
            time=task.time,
            frequency=task.frequency,
            due_date=next_date,
        )
        if task.pet is not None:
            task.pet.add_task(next_task)  # sets the pet back-reference
        return next_task

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
