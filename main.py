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

    # 3a. Shared routine — every pet gets its own breakfast, walk, and dinner.
    owner.add_daily_routine()

    # 3b. Pet-specific tasks — these belong to just one pet.
    mimi.add_task(Task(id=100, description="Vet visit", time="14:00", frequency="once"))
    rex.add_task(Task(id=101, description="Grooming", time="10:00", frequency="weekly"))

    # 4. Hand the pets to the scheduler (the "brain") and print the plan.
    scheduler = Scheduler()
    scheduler.register_owner(owner)

    print(f"Owner: {owner.name}")
    print(f"Pets:  {', '.join(pet.name for pet in owner.list_pets())}\n")

    print("Today's Schedule")
    print("-" * 40)

    # Group tasks that share the same time + description so a shared task
    # (e.g. Breakfast for every pet) shows both animals on one line instead
    # of repeating the time. Key preserves the plan's time order.
    grouped: dict[tuple[str, str, str], list[str]] = {}
    for task in scheduler.daily_plan():
        pet_name = task.pet.name if task.pet else "Unassigned"
        key = (task.time or "anytime", task.description, task.frequency)
        grouped.setdefault(key, []).append(pet_name)

    for (when, description, _frequency), pet_names in grouped.items():
        pets = " & ".join(pet_names)
        print(f"  {when:>7}  {pets}: {description}")


if __name__ == "__main__":
    main()
