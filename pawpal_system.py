from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict
import uuid

PRIORITY_SCORES = {"high": 3, "medium": 2, "low": 1}

@dataclass
class Task:
    """Represents a single pet care task."""
    title: str
    duration_minutes: int
    priority: str = "medium"  # low, medium, high
    category: str = "general"  # walk, feeding, medication, grooming, appointment
    description: str = ""
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    recurring_weekdays: Optional[List[int]] = None  # 0=Monday...6=Sunday
    frequency: Optional[str] = None  # daily, weekly
    created_at: datetime = field(default_factory=datetime.now)
    completed: bool = False
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """Validate priority and duration values at creation."""
        if self.priority not in PRIORITY_SCORES:
            raise ValueError("priority must be one of: low, medium, high")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be > 0")
        if self.frequency and self.frequency not in {"daily", "weekly"}:
            raise ValueError("frequency must be one of: daily, weekly, or None")

    def mark_completed(self):
        """Mark this task as completed."""
        self.completed = True

    def is_recurring_on(self, day: date) -> bool:
        """Return true if task recurs on the given weekday."""
        if self.recurring_weekdays:
            return day.weekday() in self.recurring_weekdays
        return False

    def should_schedule_on(self, day: date) -> bool:
        """Determine whether this task should be considered for scheduling on the given day."""
        if self.completed:
            return False

        if self.due_date and self.due_date != day:
            return False

        if self.recurring_weekdays and self.is_recurring_on(day):
            return True

        if self.frequency == "daily":
            return True

        if self.frequency == "weekly":
            return self.due_date is None or self.due_date.weekday() == day.weekday()

        # Non-recurring, no due date: schedule any day
        return self.due_date is None


@dataclass
class ScheduledTask:
    task: Task
    start_time: datetime
    end_time: datetime
    rationale: str = ""


class Pet:
    """Stores information and task list for a single pet."""

    def __init__(self, name: str, species: str = "dog", age_months: Optional[int] = None):
        self.name = name
        self.species = species
        self.age_months = age_months
        self.tasks: List[Task] = []

    def add_task(self, task: Task):
        """Add a new task for this pet."""
        self.tasks.append(task)

    def remove_task(self, task_id: str):
        """Remove a task by its task_id."""
        self.tasks = [task for task in self.tasks if task.task_id != task_id]

    def mark_task_complete(self, task_id: str, current_date: Optional[date] = None) -> Optional[Task]:
        """Mark a task completed and schedule its next occurrence if recurring."""
        if current_date is None:
            current_date = date.today()

        for task in self.tasks:
            if task.task_id == task_id:
                task.mark_completed()
                next_task = None

                if task.frequency == "daily":
                    next_due = (task.due_date or current_date) + timedelta(days=1)
                    next_task = Task(
                        title=task.title,
                        duration_minutes=task.duration_minutes,
                        priority=task.priority,
                        category=task.category,
                        description=task.description,
                        due_date=next_due,
                        due_time=task.due_time,
                        recurring_weekdays=task.recurring_weekdays,
                        frequency=task.frequency,
                    )

                elif task.frequency == "weekly":
                    next_due = (task.due_date or current_date) + timedelta(days=7)
                    next_task = Task(
                        title=task.title,
                        duration_minutes=task.duration_minutes,
                        priority=task.priority,
                        category=task.category,
                        description=task.description,
                        due_date=next_due,
                        due_time=task.due_time,
                        recurring_weekdays=task.recurring_weekdays,
                        frequency=task.frequency,
                    )

                if next_task is not None:
                    self.tasks.append(next_task)
                return next_task

        return None

    def get_pending_tasks(self) -> List[Task]:
        """Return tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]


class Owner:
    """Manages one or more pets and aggregates their tasks."""

    def __init__(self, name: str, email: Optional[str] = None):
        self.name = name
        self.email = email
        self.pets: List[Pet] = []
        # default available window from 06:00 to 22:00
        self.available_start = time(hour=6, minute=0)
        self.available_end = time(hour=22, minute=0)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str):
        """Remove a pet by name."""
        self.pets = [pet for pet in self.pets if pet.name != pet_name]

    def all_tasks(self) -> List[Task]:
        """Collect all tasks from all owned pets."""
        tasks: List[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks

    def get_pending_tasks(self) -> List[Task]:
        """Return all non-completed tasks across all pets."""
        return [t for t in self.all_tasks() if not t.completed]

    def filter_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Return tasks filtered by completion status and/or pet name."""
        filtered: List[Task] = []
        for pet in self.pets:
            if pet_name and pet.name != pet_name:
                continue
            for t in pet.tasks:
                if completed is not None and t.completed != completed:
                    continue
                filtered.append(t)
        return filtered


class Scheduler:
    """Scheduling engine that builds daily plans from owner and pet tasks."""

    def __init__(self, day_start: time = time(hour=6), day_end: time = time(hour=22)):
        """Initialize scheduler with a daily working window."""
        if day_start >= day_end:
            raise ValueError("day_start must be before day_end")
        self.day_start = day_start
        self.day_end = day_end

    def _sort_tasks(self, tasks: List[Task], for_date: date) -> List[Task]:
        """Return a prioritized list of tasks for the day."""
        def sort_key(task: Task):
            due = task.due_time if task.due_time is not None else time(hour=23, minute=59)
            return (-PRIORITY_SCORES.get(task.priority, 1), due, task.duration_minutes, task.created_at)

        tasks_sorted = sorted(tasks, key=sort_key)
        return tasks_sorted

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by due_time value; tasks without due_time go last."""
        return sorted(tasks, key=lambda task: task.due_time if task.due_time is not None else time(hour=23, minute=59))

    def _expand_recurring_tasks(self, tasks: List[Task], target_date: date) -> List[Task]:
        """Include only tasks that apply to the target date based on recurrence."""
        expanded: List[Task] = []
        for task in tasks:
            if task.completed:
                continue
            if task.recurring_weekdays and task.is_recurring_on(target_date):
                expanded.append(task)
            elif not task.recurring_weekdays:
                expanded.append(task)
        return expanded

    def detect_conflicts(self, tasks: List[Task]) -> List[Dict[str, str]]:
        """Fake conflicts based on due_time urgency and available start window."""
        conflicts: List[Dict[str, str]] = []
        tasks_with_due = [t for t in tasks if t.due_time is not None]
        tasks_with_due = sorted(tasks_with_due, key=lambda t: t.due_time)
        for task in tasks_with_due:
            due_minute = task.due_time.hour * 60 + task.due_time.minute
            available_minute = self.day_start.hour * 60 + self.day_start.minute
            if task.duration_minutes > (due_minute - available_minute):
                conflicts.append({"task": task.title, "reason": "Not enough time before due_time"})
        return conflicts

    def detect_schedule_conflicts(self, schedule: List[ScheduledTask]) -> List[Dict[str, str]]:
        """Find overlapping scheduled tasks and return warnings."""
        warnings: List[Dict[str, str]] = []
        for i in range(len(schedule)):
            for j in range(i + 1, len(schedule)):
                a = schedule[i]
                b = schedule[j]
                # overlap if a starts before b ends and b starts before a ends
                if a.start_time < b.end_time and b.start_time < a.end_time:
                    warnings.append({
                        "task1": a.task.title,
                        "task2": b.task.title,
                        "reason": "Tasks overlap in scheduled time",
                    })
        return warnings

    def generate_daily_plan(self, owner: Owner, target_date: Optional[date] = None) -> Dict[str, List]:
        if target_date is None:
            target_date = date.today()

        candidate_tasks = [t for t in owner.get_pending_tasks() if t.should_schedule_on(target_date)]
        candidate_tasks = self._expand_recurring_tasks(candidate_tasks, target_date)

        tasks = self._sort_tasks(candidate_tasks, target_date)

        schedule: List[ScheduledTask] = []
        skipped: List[Dict[str, str]] = []

        current_dt = datetime.combine(target_date, self.day_start)
        end_dt = datetime.combine(target_date, self.day_end)

        for task in tasks:
            if task.duration_minutes <= 0:
                skipped.append({"task": task.title, "reason": "Invalid duration"})
                continue

            start_dt = current_dt
            end_task_dt = start_dt + timedelta(minutes=task.duration_minutes)

            if task.due_time:
                due_dt = datetime.combine(target_date, task.due_time)
                # Ensure end before due
                if end_task_dt > due_dt:
                    # try to fit earlier by anchored schedule to due
                    alt_end = due_dt
                    alt_start = alt_end - timedelta(minutes=task.duration_minutes)
                    if alt_start >= datetime.combine(target_date, self.day_start):
                        start_dt, end_task_dt = alt_start, alt_end
                        # backfill to next free time after this task for subsequent tasks
                        current_dt = datetime.combine(target_date, self.day_start)
                        for scheduled in schedule:
                            if scheduled.end_time <= start_dt:
                                current_dt = max(current_dt, scheduled.end_time)
                        current_dt = max(current_dt, end_task_dt)
                    else:
                        skipped.append({"task": task.title, "reason": "Cannot fit before due_time"})
                        continue

            if end_task_dt > end_dt:
                skipped.append({"task": task.title, "reason": "Not enough daily hours remaining"})
                continue

            # Check overlap with existing schedule and move forward if needed
            while any(s.start_time < end_task_dt and start_dt < s.end_time for s in schedule):
                start_dt = max((s.end_time for s in schedule if s.start_time < end_task_dt and start_dt < s.end_time), default=start_dt)
                end_task_dt = start_dt + timedelta(minutes=task.duration_minutes)
                if end_task_dt > end_dt:
                    break

            if end_task_dt > end_dt:
                skipped.append({"task": task.title, "reason": "Not enough daily hours after conflict adjustments"})
                continue

            scheduled = ScheduledTask(
                task=task,
                start_time=start_dt,
                end_time=end_task_dt,
                rationale=f"Priority {task.priority}, category {task.category}"
            )
            schedule.append(scheduled)
            current_dt = end_task_dt

        schedule_sorted = sorted(schedule, key=lambda s: s.start_time)
        schedule_conflicts = self.detect_schedule_conflicts(schedule_sorted)

        return {
            "date": target_date,
            "schedule": schedule_sorted,
            "skipped": skipped,
            "conflicts": self.detect_conflicts(tasks),
            "schedule_conflicts": schedule_conflicts,
        }

    def explain_schedule(self, plan: Dict[str, List]) -> str:
        lines: List[str] = [f"Schedule for {plan['date']}:\n"]
        for item in plan["schedule"]:
            lines.append(
                f"{item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')} {item.task.title} ({item.task.category}, {item.task.priority}) -- {item.rationale}"  # noqa: E501
            )
        if plan["skipped"]:
            lines.append("\nSkipped tasks:")
            for skip in plan["skipped"]:
                lines.append(f"- {skip['task']}: {skip['reason']}")
        if plan["conflicts"]:
            lines.append("\nDetected potential conflicts:")
            for c in plan["conflicts"]:
                lines.append(f"- {c['task']}: {c['reason']}")
        if plan.get("schedule_conflicts"):
            lines.append("\nDetected schedule overlaps:")
            for c in plan["schedule_conflicts"]:
                lines.append(f"- {c['task1']} overlaps {c['task2']}: {c['reason']}")
        return "\n".join(lines)
