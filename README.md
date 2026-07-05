# PawPal+

A Streamlit app that helps a pet owner plan care tasks for their pet.

## ✨ Features

- Manage multiple pets under one owner profile
- Add care tasks with a duration, priority, and an optional fixed time of day
- Mark tasks as one-time, daily, or weekly — completing a recurring task automatically schedules its next occurrence
- Filter the task list by pet or by completion status
- Generate a daily plan for a configurable start/end window: fixed-time tasks are honored at their requested slot, flexible tasks fill the remaining gaps by priority
- Conflict warnings whenever two tasks are pinned to the same time
- Full reasoning behind every generated plan — why each task was scheduled, skipped, or flagged

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 🖥️ Sample Output
```
Today's Schedule:
  - 08:12  [ ] Rex: Vet appointment (15 min) [priority: high]
  - 08:27  [ ] Rex: Big high-priority task (20 min) [priority: high]
  - 08:47  [ ] Rex: Small low-priority task (10 min) [priority: low]

Scheduled 'Vet appointment' (priority: high, 15 min) at its requested time 08:12.
Scheduled 'Big high-priority task' (priority: high, 20 min) at 08:27.
Scheduled 'Small low-priority task' (priority: low, 10 min) at 08:47.
```

## 🧪 Testing PawPal+

`tests/test_pawpal.py` covers:

- **Happy paths**: adding a pet to an owner, adding tasks to a pet, and building a predictable daily plan from a known set of tasks
- **Edge cases**: generating a plan with no tasks, and with two tasks that conflict on the same scheduled time
- **Sorting**: `Scheduler.sort_by_time()` returns tasks in chronological order (untimed tasks last)
- **Recurrence**: marking a daily task complete spawns a new instance due the next day
- **Conflict detection**: `Scheduler.detect_conflicts()` flags tasks pinned to the same time

```bash
# Run the full test suite:
python -m pytest -q
```

Sample test output:

```
.........                                                                                                                                              [100%]
9 passed in 0.02s
```
Reliability: ⭐⭐⭐⭐
## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler._prioritize()` | Tasks w/ specific scheduled times can be sorted chronologically; all tasks can be sorted by priority, high to low |
| Filtering | `Scheduler.filter_tasks()` | Filter by completion status and/or pet name |
| Conflict handling | `Scheduler.detect_conflicts()` | Warns (without crashing) when two tasks share the same `scheduled_time` |
| Recurring tasks | `Task.mark_complete()`, `Pet.mark_task_complete()` | Completing a daily/weekly task spawns its next occurrence with an advanced `due_date` |

## 📸 Demo Walkthrough

1. Open the app and enter your name as the owner.
2. Add a pet (e.g., "Mochi", species "dog") using the **Add a pet** form.
3. Add a task for that pet in **Add Task** (e.g., "Morning walk", 30 min, high priority).
4. Check **All Tasks** — the new task appears.
5. Set the day's start/end time in **Build Schedule** and click **Generate schedule**.
6. View the task placed in **Today's Schedule**, and expand **Why this plan?** to see the scheduler's reasoning.

Other scheduling behaviors (sorting, filtering, conflict detection) are available in the app, and can be seen directly in the terminal by running `main.py`:

```
$ python main.py
=== Sorting by time ===
  08:00  Mochi: Morning walk (30 min) [priority: high]
  08:00  Mochi: Feeding (10 min) [priority: high]
  17:00  Mochi: Fetch in the yard (20 min) [priority: low]
   --   Luna: Litter box cleaning (10 min) [priority: medium]
   --   Luna: Brushing (15 min) [priority: low]

=== Filtering: incomplete tasks for Mochi ===
  Mochi: Fetch in the yard (20 min) [priority: low]
  Mochi: Feeding (10 min) [priority: high]

=== Conflict detection (Feeding and Morning walk both at 08:00) ===
  Warning: 'Morning walk' (Mochi) and 'Feeding' (Mochi) are both scheduled at 08:00.

Today's Schedule:
  - 08:00  Mochi: Feeding (10 min) [priority: high]
  - 08:10  Luna: Litter box cleaning (10 min) [priority: medium]
  - 08:20  Luna: Brushing (15 min) [priority: low]
  - 17:00  Mochi: Fetch in the yard (20 min) [priority: low]

Reasoning:
Scheduled 'Feeding' (priority: high, 10 min) at its requested time 08:00.
Scheduled 'Litter box cleaning' (priority: medium, 10 min) at 08:10.
Scheduled 'Brushing' (priority: low, 15 min) at 08:20.
'Fetch in the yard' at 17:00 extends past your available window (ends 09:00).
Scheduled 'Fetch in the yard' (priority: low, 20 min) at its requested time 17:00.
```
