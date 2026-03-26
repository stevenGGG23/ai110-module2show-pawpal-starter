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

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
