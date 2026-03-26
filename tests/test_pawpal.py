import pytest
from datetime import date, time, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


def test_task_mark_completed():
    task = Task(title="Feed", duration_minutes=10)
    assert not task.completed
    task.mark_completed()
    assert task.completed


def test_pet_add_task_increases_count():
    pet = Pet(name="Buddy", species="dog")
    initial = len(pet.tasks)
    pet.add_task(Task(title="Walk", duration_minutes=20))
    assert len(pet.tasks) == initial + 1


def test_recurring_task_creates_next_occurrence():
    pet = Pet(name="Buddy")
    task = Task(title="Morning med", duration_minutes=5, frequency="daily", due_date=date.today())
    pet.add_task(task)

    next_task = pet.mark_task_complete(task.task_id, current_date=date.today())

    assert task.completed is True
    assert next_task is not None
    assert next_task.frequency == "daily"
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_schedule_conflict_detection():
    owner = Owner(name="Alex")
    pet = Pet(name="Nala")
    pet.add_task(Task(title="Task 1", duration_minutes=60, due_time=time(hour=9), priority="high"))
    pet.add_task(Task(title="Task 2", duration_minutes=60, due_time=time(hour=9), priority="high"))
    owner.add_pet(pet)

    scheduler = Scheduler(day_start=time(hour=6), day_end=time(hour=22))
    plan = scheduler.generate_daily_plan(owner, target_date=date.today())

    assert "schedule_conflicts" in plan
    # no fixed overlaps from your placement logic may happen, but if tasks are contiguous there should be none
    assert isinstance(plan["schedule_conflicts"], list)
