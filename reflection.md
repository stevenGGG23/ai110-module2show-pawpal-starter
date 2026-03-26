# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Owner: holds owner metadata, a list of pets, and methods to add/remove pets and aggregate tasks.
- Pet: represents a single pet, stores tasks, and offers pending-task accessors.
- Task: data class for a care action; stores title, duration, category, priority, optional due_time, recurring weekdays, and completion state.
- Scheduler: builds a day plan for an owner by collecting pending tasks across pets, sorting by priority and due time, resolving schedule constraints, and returning scheduled/skipped/conflicting sets.

**b. Design changes**

- Initial design had Task and Pet only. I added Owner to centrally manage multi-pet scenarios and keep task aggregation in one place.
- I also added a dedicated `ScheduledTask` class to separate raw tasks from scheduled instances with assigned time slots.
- A conflict detection pass (`detect_conflicts`) and a basic recurring-task expansion step were added while implementing scheduling logic.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- The scheduler enforces an availability window (08:00–22:00 by default), task duration, and hard due times.
- It prioritizes tasks by priority level (high/medium/low), due time, and shorter duration as tie breaker.
- Recurring and date-specific tasks are included only on applicable days.

**b. Tradeoffs**

- The scheduler only checks conflicts at discrete scheduled start/end boundaries, not every possible overlapping block; it may schedule two tasks back-to-back rather than trying to reslot them optimally.
- This tradeoff simplifies logic and keeps runtime O(n^2) vs complex constraint solving, matching a minimum viable pet planner.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- I rejected an AI suggestion that proposed overly complex constraint solving using linear programming library (pulp). I opted for a lightweight, understandable greedy scheduling approach that is sufficient for MVP and easier to test.
- I verified algorithm correctness with unit tests (`test_pawpal_system.py`, `tests/test_pawpal.py`) and manual CLI runs of `main.py`.

**c. Copilot strategy reflections**

- Most effective Copilot features:
  - inline code completions for methods like `Scheduler.detect_schedule_conflicts` and `Task.mark_completed` recurrence.
  - ability to provide context with `#file:pawpal_system.py` and ask for structured method suggestions.
- Using separate chat sessions for each phase kept design and builder iterations isolated, which made debugging simpler and reduced accidental drift.
- As lead architect, I favored clear explicit code over complicated AI-generated one-liners, and I retained AI ideas that aligned with modularity and maintainability.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

**Confidence Level:** ⭐⭐⭐⭐⭐ (5/5)

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
