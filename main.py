"""Temporary terminal testing ground for the PawPal+ domain classes.

Run with: python main.py
"""

from pawpal_system import Owner, Pet, Priority, Scheduler, Task

owner = Owner(name="Jordan")

mochi = Pet(name="Mochi", species="dog")
mochi.add_task(Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH))
mochi.add_task(Task(title="Feeding", duration_minutes=10, priority=Priority.HIGH))
mochi.add_task(Task(title="Fetch in the yard", duration_minutes=20, priority=Priority.LOW))

luna = Pet(name="Luna", species="cat")
luna.add_task(Task(title="Litter box cleaning", duration_minutes=10, priority=Priority.MEDIUM))
luna.add_task(Task(title="Brushing", duration_minutes=15, priority=Priority.LOW))

owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler(available_minutes=60)
daily_plan = scheduler.plan(owner)

print(daily_plan.display())
print()
print("Reasoning:")
print(daily_plan.explain())
