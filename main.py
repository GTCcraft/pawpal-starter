"""Temporary terminal testing ground for the PawPal+ domain classes.

Run with: python main.py
"""

from pawpal_system import Owner, Pet, Priority, Scheduler, Task

owner = Owner(name="Jordan")

mochi = Pet(name="Mochi", species="dog")
luna = Pet(name="Luna", species="cat")
owner.add_pet(mochi)
owner.add_pet(luna)

# Tasks are added out of order, and some carry a fixed scheduled_time
# (including a deliberate collision) to exercise sorting/filtering/conflicts.
fetch = Task(title="Fetch in the yard", duration_minutes=20, priority=Priority.LOW, scheduled_time="17:00")
walk = Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH, scheduled_time="08:00")
feeding = Task(title="Feeding", duration_minutes=10, priority=Priority.HIGH, scheduled_time="08:00")
litter = Task(title="Litter box cleaning", duration_minutes=10, priority=Priority.MEDIUM)
brushing = Task(title="Brushing", duration_minutes=15, priority=Priority.LOW)

mochi.add_task(fetch)
mochi.add_task(walk)
mochi.add_task(feeding)
luna.add_task(litter)
luna.add_task(brushing)

walk.mark_complete()

scheduler = Scheduler(start_time="08:00", end_time="09:00")
all_tasks = owner.get_all_tasks()

print("=== Sorting by time ===")
for task in scheduler.sort_by_time(all_tasks):
    print(f"  {task.scheduled_time or ' -- '}  {task}")

print()
print("=== Filtering: incomplete tasks for Mochi ===")
for task in scheduler.filter_tasks(all_tasks, completed=False, pet_name="Mochi"):
    print(f"  {task}")

print()
print("=== Conflict detection (Feeding and Morning walk both at 08:00) ===")
conflicts = scheduler.detect_conflicts(all_tasks)
if conflicts:
    for warning in conflicts:
        print(f"  Warning: {warning}")
else:
    print("  No conflicts found.")

print()
daily_plan = scheduler.plan(owner)
print(daily_plan.display())
print()
print("Reasoning:")
print(daily_plan.explain())
