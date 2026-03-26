# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Features

PawPal+ supports:

- Owner/pet/task models with full task metadata (category, duration, due date/time, recurrence, priority)
- `Scheduler.generate_daily_plan` with window-aware scheduling (06:00-22:00 default)
- `Scheduler.sort_by_time` to display tasks by due time
- `Owner.filter_tasks` to query pending/completed tasks per pet
- Recurring task lifecycle: complete daily/weekly tasks auto-schedules next occurrence
- Conflict detection:
  - `Scheduler.detect_conflicts` (due-time vs available schedule urgency)
  - `Scheduler.detect_schedule_conflicts` (overlapping scheduled slots)
- Rich UI feedback via Streamlit (`st.success`, `st.warning`, `st.error`, `st.table`)

## 📸 Demo

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank"><img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Smarter Scheduling

This implementation includes improved logic in `pawpal_system.py`:

- sort tasks by priority + due time and optional `Scheduler.sort_by_time` by due time
- filter tasks by `completed` status and `pet_name` in `Owner.filter_tasks`
- recurring task handling (`daily`, `weekly`) in `Task.frequency` and `Pet.mark_task_complete`
- conflict detection with `Scheduler.detect_conflicts` (due-time urgency) and `Scheduler.detect_schedule_conflicts` (overlapping schedule slots)
- explanations and skipped task reports in plan output

