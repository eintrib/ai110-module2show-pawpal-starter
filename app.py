import streamlit as st

# Bring the PawPal classes from pawpal_system.py into this app.
from pawpal_system import Owner, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Session "vault": create the Owner ONCE, then reuse it across reruns. ---
# Without this, every button click would rebuild an empty Owner and lose data.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(id=1, name="Jordan")

owner = st.session_state.owner

st.subheader("Owner")
# Keep the owner's name in sync with the input box.
owner.name = st.text_input("Owner name", value=owner.name)

# --- Add a Pet ---------------------------------------------------------------
st.subheader("Add a Pet")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    # Owner.add_pet() is the Phase 2 method that handles this data.
    new_pet = Pet(id=len(owner.pets) + 1, name=pet_name, species=species)
    owner.add_pet(new_pet)
    st.success(f"Added {pet_name} the {species}!")

if owner.pets:
    st.write("Current pets: " + ", ".join(str(pet) for pet in owner.list_pets()))
else:
    st.info("No pets yet. Add one above.")

# --- Schedule a Task ---------------------------------------------------------
st.subheader("Schedule a Task")
if not owner.pets:
    st.warning("Add a pet first, then you can schedule tasks for it.")
else:
    pet_names = [pet.name for pet in owner.pets]
    target = st.selectbox("Which pet?", pet_names + ["All pets (shared task)"])
    description = st.text_input("Task", value="Morning walk")
    task_time = st.text_input("Time (HH:MM)", value="08:00")
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=1)

    if st.button("Add task"):
        if target == "All pets (shared task)":
            # Owner.add_task_to_all() gives every pet its own copy.
            owner.add_task_to_all(description, time=task_time, frequency=frequency)
        else:
            # Owner.add_task_to_pet() builds the Task (with a unique id) and
            # adds it to the chosen pet via Pet.add_task().
            pet = next(p for p in owner.pets if p.name == target)
            owner.add_task_to_pet(pet, description, time=task_time, frequency=frequency)
        st.success("Task scheduled!")

st.divider()

# --- Generate schedule -------------------------------------------------------
st.subheader("Today's Schedule")

# Hand the owner's pets to the Scheduler "brain" once; every view below is
# built from its methods (sorting, filtering, conflict detection).
scheduler = Scheduler()
scheduler.register_owner(owner)

if not scheduler.all_tasks():
    st.info("No tasks scheduled yet. Add some above.")
else:
    # --- Filters: powered by Scheduler.filter_tasks() ------------------------
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        pet_choice = st.selectbox(
            "Show tasks for", ["All pets"] + [pet.name for pet in owner.pets]
        )
    with fcol2:
        status_choice = st.selectbox("Status", ["All", "Pending", "Done"])

    filtered = scheduler.filter_tasks(
        pet_name=None if pet_choice == "All pets" else pet_choice,
        status=None if status_choice == "All" else status_choice.lower(),
    )
    # Scheduler.sort_by_time() orders whatever list we hand it, earliest first.
    plan = scheduler.sort_by_time(filtered)

    # --- Conflict warnings: powered by Scheduler.find_conflicts() ------------
    # Check the FULL plan for clashes (not just the filtered view) so a hidden
    # overlap can't slip past the owner. Surface each conflict prominently and
    # tell them what to do about it, since a double-booking needs an action.
    conflicts = scheduler.find_conflicts()
    if conflicts:
        st.warning(
            f"**{len(conflicts)} scheduling conflict"
            f"{'s' if len(conflicts) > 1 else ''} found** — "
            "two tasks are booked at the same time. "
            "Consider rescheduling one so nothing gets missed."
        )
        for message in conflicts:
            st.warning(message)
    else:
        st.success("✅ No scheduling conflicts — everything is spaced out nicely.")

    # Which time slots clash? Bucket by the Scheduler's own time key (minutes
    # since midnight) so "8:00" and "08:00" are treated as the same slot when
    # flagging the affected rows in the table below.
    slot_counts: dict[int, int] = {}
    for task in scheduler.all_tasks():
        if task.time:
            key = Scheduler._time_key(task)
            slot_counts[key] = slot_counts.get(key, 0) + 1
    conflict_slots = {key for key, count in slot_counts.items() if count > 1}

    # --- The plan as a clean table -------------------------------------------
    if not plan:
        st.info("No tasks match this filter.")
    else:
        rows = []
        for task in plan:
            pet_label = task.pet.name if task.pet else "Unassigned"
            when = task.time or "anytime"
            rows.append(
                {
                    "Time": when,
                    "Pet": pet_label,
                    "Task": task.description,
                    "Frequency": task.frequency,
                    "Status": "✅ done" if task.is_complete else "⏳ pending",
                    "": "⚠️"
                    if task.time and Scheduler._time_key(task) in conflict_slots
                    else "",
                }
            )
        st.table(rows)
