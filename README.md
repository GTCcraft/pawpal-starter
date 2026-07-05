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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler._prioritize()` | Tasks w/ specific scheduled times can be sorted chronologically; all tasks can be sorted by priority, high to low |
| Filtering | `Scheduler.filter_tasks()` | Filter by completion status and/or pet name |
| Conflict handling | `Scheduler.detect_conflicts()` | Warns (without crashing) when two tasks share the same `scheduled_time` |
| Recurring tasks | `Task.mark_complete()`, `Pet.mark_task_complete()` | Completing a daily/weekly task spawns its next occurrence with an advanced `due_date` |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
