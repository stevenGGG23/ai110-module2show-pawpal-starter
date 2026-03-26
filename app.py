import streamlit as st

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

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority}
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

from pawpal_system import Owner, Pet, Task, Scheduler

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    owner = Owner(name=owner_name)
    pet = Pet(name=pet_name, species=species)

    for raw in st.session_state.tasks:
        task = Task(
            title=raw.get("title", "Untitled"),
            duration_minutes=int(raw.get("duration_minutes", 0)),
            priority=raw.get("priority", "medium"),
            category=raw.get("category", "general"),
        )
        pet.add_task(task)

    owner.add_pet(pet)
    scheduler = Scheduler(day_start=time(hour=6), day_end=time(hour=22))
    plan = scheduler.generate_daily_plan(owner)

    st.markdown("### Generated Schedule")
    if plan["schedule"]:
        rows = []
        for item in plan["schedule"]:
            rows.append({
                "Time": f"{item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')}",
                "Task": item.task.title,
                "Category": item.task.category,
                "Priority": item.task.priority,
                "Rationale": item.rationale,
            })
        st.table(rows)
    else:
        st.info("No tasks could be scheduled.")

    if plan["skipped"]:
        st.markdown("### Skipped Tasks")
        for skip in plan["skipped"]:
            st.write(f"- {skip['task']}: {skip['reason']}")

    if plan["conflicts"]:
        st.warning("Potential conflicts detected")
        for c in plan["conflicts"]:
            st.write(f"- {c['task']}: {c['reason']}")

    explanation = scheduler.explain_schedule(plan)
    st.markdown("### Explanation")
    st.text(explanation)

