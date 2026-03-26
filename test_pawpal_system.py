import pytest
from datetime import date, time
from pawpal_system import Owner, Pet, Task, Scheduler


def test_add_pet_and_tasks():
    owner = Owner(name="Alex")
    pet = Pet(name="Nala", species="cat")
    owner.add_pet(pet)

    task = Task(title="Feed Nala", duration_minutes=10, priority="high", category="feeding")
    pet.add_task(task)

    all_tasks = owner.all_tasks()
    assert len(all_tasks) == 1
    assert all_tasks[0].title == "Feed Nala"


def test_scheduler_prioritizes_high_tasks():
    owner = Owner(name="Alex")
    pet = Pet(name="Nala")
    pet.add_task(Task(title="Walk", duration_minutes=30, priority="low", category="walk"))
    pet.add_task(Task(title="Medication", duration_minutes=10, priority="high", category="medication"))
    owner.add_pet(pet)

    scheduler = Scheduler(day_start=time(hour=6), day_end=time(hour=22))
    plan = scheduler.generate_daily_plan(owner, target_date=date.today())

    assert len(plan["schedule"]) == 2
    assert plan["schedule"][0].task.title == "Medication"
    assert plan["schedule"][1].task.title == "Walk"


def test_skips_task_when_not_enough_time():
    owner = Owner(name="Alex")
    pet = Pet(name="Nala")
    # 20h day would be 960 minutes.
    # Add one task extremely large so it skips.
    pet.add_task(Task(title="Long Marathon", duration_minutes=2000, priority="high", category="other"))
    owner.add_pet(pet)

    scheduler = Scheduler(day_start=time(hour=6), day_end=time(hour=22))
    plan = scheduler.generate_daily_plan(owner, target_date=date.today())

    assert len(plan["schedule"]) == 0
    assert len(plan["skipped"]) == 1
    assert plan["skipped"][0]["task"] == "Long Marathon"


def test_recurring_task_included_on_matching_weekday(monkeypatch):
    owner = Owner(name="Alex")
    pet = Pet(name="Nala")
    task = Task(title="Daily play", duration_minutes=15, priority="medium", category="enrichment", recurring_weekdays=[date.today().weekday()])
    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(day_start=time(hour=6), day_end=time(hour=22))
    plan = scheduler.generate_daily_plan(owner, target_date=date.today())

    assert len(plan["schedule"]) == 1
    assert plan["schedule"][0].task.title == "Daily play"
