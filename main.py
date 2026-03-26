from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler


def run_demo():
    
    owner = Owner(name="Sam")

    dog = Pet(name="Rex", species="dog")
    cat = Pet(name="Whiskers", species="cat")

    # Add tasks out of chronological order to demonstrate sorting
    dog.add_task(Task(title="Evening food", duration_minutes=10, priority="medium", category="feeding", due_time=None))
    dog.add_task(Task(title="Morning walk", duration_minutes=30, priority="high", category="walk", due_time=None))
    dog.add_task(Task(title="Pill", duration_minutes=5, priority="high", category="medication", due_time=None, frequency="daily"))

    cat.add_task(Task(title="Play with laser", duration_minutes=20, priority="medium", category="enrichment", due_time=None))
    cat.add_task(Task(title="Litter clean", duration_minutes=15, priority="high", category="grooming", due_time=None))

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(day_start=owner.available_start, day_end=owner.available_end)

    print("--- All raw tasks (unsorted) ---")
    for t in owner.all_tasks():
        print(f"{t.title} ({t.priority})")

    sorted_tasks = scheduler.sort_by_time(owner.all_tasks())
    print("\n--- Tasks sorted by time ---")
    for t in sorted_tasks:
        due = t.due_time.strftime('%H:%M') if t.due_time else 'no-time'
        print(f"{due} - {t.title}")

    print("\n--- Filtered tasks (not completed, dog Rex) ---")
    filtered = owner.filter_tasks(completed=False, pet_name="Rex")
    for t in filtered:
        print(f"{t.title} ({t.priority})")

    plan = scheduler.generate_daily_plan(owner, target_date=date.today())

    print("\n--- Today's Schedule ---")
    for item in plan["schedule"]:
        print(
            f"{item.start_time.strftime('%H:%M')} - {item.end_time.strftime('%H:%M')} | {item.task.title} | {item.task.category} | {item.task.priority}"
        )

    if plan["skipped"]:
        print("\nSkipped:")
        for skip in plan["skipped"]:
            print(f"- {skip['task']}: {skip['reason']}")

    if plan["conflicts"]:
        print("\nConflicts:")
        for c in plan["conflicts"]:
            print(f"- {c['task']}: {c['reason']}")

    if plan.get("schedule_conflicts"):
        print("\nSchedule overlaps:")
        for c in plan["schedule_conflicts"]:
            print(f"- {c['task1']} overlaps {c['task2']}: {c['reason']}")


if __name__ == "__main__":
    run_demo()
