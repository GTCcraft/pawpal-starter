from datetime import time

import streamlit as st

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+. Add pets and tasks below, then generate a daily plan.
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


def _find_pet(owner: Owner, pet_name: str) -> Pet:
    return next(pet for pet in owner.pets if pet.name == pet_name)


def _time_to_str(t: time) -> str:
    return f"{t.hour:02d}:{t.minute:02d}"


if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
    st.session_state.owner.add_pet(Pet(name="Mochi", species="dog"))
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

owner = st.session_state.owner
scheduler = st.session_state.scheduler

st.subheader("Owner & Pets")
owner_name = st.text_input("Owner name", value=owner.name)
owner.name = owner_name

with st.form("add_pet_form", clear_on_submit=True):
    st.caption("Add a pet")
    pcol1, pcol2, pcol3 = st.columns([2, 2, 1])
    with pcol1:
        new_pet_name = st.text_input("Pet name", value="")
    with pcol2:
        new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
    with pcol3:
        st.write("")
        add_pet_submitted = st.form_submit_button("Add pet")
    if add_pet_submitted and new_pet_name:
        owner.add_pet(Pet(name=new_pet_name, species=new_pet_species))

st.table(
    [
        {"name": pet.name, "species": pet.species, "tasks": pet.get_task_count()}
        for pet in owner.pets
    ]
)

st.divider()

st.subheader("Add Task")
pet_names = [pet.name for pet in owner.pets]
task_pet_name = st.selectbox("Pet", pet_names)

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    repeats = st.selectbox("Repeats", ["One-time", "Daily", "Weekly"])
with col5:
    has_time = st.checkbox("This task has a specific time")
    task_time = st.time_input("Time", value=time(8, 0)) if has_time else None

if st.button("Add task") and pet_names:
    frequency = {"One-time": None, "Daily": Frequency.DAILY, "Weekly": Frequency.WEEKLY}[repeats]
    _find_pet(owner, task_pet_name).add_task(
        Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=Priority(priority),
            frequency=frequency,
            scheduled_time=_time_to_str(task_time) if task_time else None,
        )
    )

st.divider()

st.subheader("All Tasks")
all_tasks = owner.get_all_tasks()

fcol1, fcol2 = st.columns(2)
with fcol1:
    filter_pet = st.selectbox("Filter by pet", ["All"] + pet_names)
with fcol2:
    filter_status = st.selectbox("Filter by status", ["All", "Incomplete", "Complete"])

filtered_tasks = scheduler.filter_tasks(
    all_tasks,
    completed={"All": None, "Incomplete": False, "Complete": True}[filter_status],
    pet_name=None if filter_pet == "All" else filter_pet,
)

if filtered_tasks:
    for task in filtered_tasks:
        row_col1, row_col2 = st.columns([1, 6])
        with row_col1:
            checked = st.checkbox("Done", value=task.completed, key=f"complete_{id(task)}", label_visibility="collapsed")
        with row_col2:
            st.write(str(task))

        if checked and not task.completed:
            _find_pet(owner, task.pet_name).mark_task_complete(task)
        elif not checked and task.completed:
            task.completed = False
else:
    st.info("No tasks match this filter.")

st.divider()

st.subheader("Build Schedule")
scol1, scol2 = st.columns(2)
with scol1:
    day_start = st.time_input("Day starts at", value=time(8, 0))
with scol2:
    day_end = st.time_input("Day ends at", value=time(20, 0))

scheduler.start_time = _time_to_str(day_start)
scheduler.end_time = _time_to_str(day_end)

if st.button("Generate schedule"):
    plan = scheduler.plan(owner)

    st.text(plan.display())
    with st.expander("Why this plan?"):
        st.text(plan.explain())
