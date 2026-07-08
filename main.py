"""PawPal — demo script.

Builds a small pet-care setup and prints today's schedule to the terminal.
Run with:  python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # 1. Create an owner.
    owner = Owner(id=1, name="Britnie", email="britnie@example.com")

    # 2. Create at least two pets and register them to the owner.
    rex = Pet(id=1, name="Rex", species="dog", breed="Labrador", age=3)
    mimi = Pet(id=2, name="Mimi", species="cat", breed="Tabby", age=5)
    owner.add_pet(rex)
    owner.add_pet(mimi)

    # 3. Add tasks deliberately OUT OF ORDER (dinner before breakfast, etc.)
    #    to prove that sort_by_time() — not the insertion order — decides the
    #    final schedule.
    rex.add_task(Task(id=1, description="Dinner", time="18:00", frequency="daily"))
    rex.add_task(Task(id=2, description="Morning walk", time="08:00", frequency="daily"))
    rex.add_task(Task(id=3, description="Grooming", time="10:00", frequency="weekly"))
    mimi.add_task(Task(id=4, description="Vet visit", time="14:00", frequency="once"))
    mimi.add_task(Task(id=5, description="Breakfast", time="7:30", frequency="daily"))
    mimi.add_task(Task(id=6, description="Play time", frequency="daily"))  # no time

    # Two tasks at the SAME time on purpose, to trigger conflict detection:
    #  - Cross-pet clash: Mimi's feed at 08:00 collides with Rex's 08:00 walk.
    #  - Same-pet clash: Rex has two different 18:00 tasks at once.
    mimi.add_task(Task(id=7, description="Feed", time="08:00", frequency="daily"))
    rex.add_task(Task(id=8, description="Take medication", time="18:00", frequency="daily"))

    # Mark a couple of tasks done so the status filter has something to show.
    rex.tasks[1].mark_complete()   # Rex's morning walk
    mimi.tasks[1].mark_complete()  # Mimi's breakfast

    # 4. Hand the pets to the scheduler (the "brain").
    scheduler = Scheduler()
    scheduler.register_owner(owner)

    print(f"Owner: {owner.name}")
    print(f"Pets:  {', '.join(pet.name for pet in owner.list_pets())}\n")

    # --- Sorting: all tasks, sorted by time even though added out of order ---
    print("All tasks, sorted by time")
    print("-" * 40)
    for task in scheduler.sort_by_time():
        print(f"  {task}")

    # --- Filtering by pet name (then sorted) ---
    print("\nRex's tasks only")
    print("-" * 40)
    for task in scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Rex")):
        print(f"  {task}")

    # --- Filtering by completion status (then sorted) ---
    print("\nStill pending (across all pets)")
    print("-" * 40)
    for task in scheduler.sort_by_time(scheduler.filter_tasks(status="pending")):
        print(f"  {task}")

    print("\nAlready done")
    print("-" * 40)
    for task in scheduler.sort_by_time(scheduler.filter_tasks(status="done")):
        print(f"  {task}")

    # --- Conflict detection: warn (don't crash) on same-time tasks ---
    print("\nSchedule conflicts")
    print("-" * 40)
    conflicts = scheduler.find_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts — every task has the clock to itself.")


if __name__ == "__main__":
    main()
