from datetime import date, timedelta

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def test_mark_complete_changes_task_status():
    task = Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog")
    assert pet.get_task_count() == 0

    pet.add_task(Task(title="Feeding", duration_minutes=10, priority=Priority.HIGH))

    assert pet.get_task_count() == 1


def test_add_pet_to_owner():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")

    owner.add_pet(pet)

    assert owner.pets == [pet]


def test_predictable_daily_plan():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(title="Feeding", duration_minutes=10, priority=Priority.HIGH))
    pet.add_task(Task(title="Walk", duration_minutes=20, priority=Priority.MEDIUM))

    scheduler = Scheduler(start_time="08:00", end_time="09:00")
    plan = scheduler.plan(owner)

    assert [entry.task.title for entry in plan.scheduled_tasks] == ["Feeding", "Walk"]
    assert [entry.start_time for entry in plan.scheduled_tasks] == ["08:00", "08:10"]
    assert plan.unscheduled_tasks == []


def test_plan_with_no_tasks():
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Mochi", species="dog"))

    plan = Scheduler().plan(owner)

    assert plan.scheduled_tasks == []
    assert plan.unscheduled_tasks == []
    assert "(no tasks scheduled)" in plan.display()


def test_plan_with_conflicting_tasks():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(title="Vet visit", duration_minutes=15, priority=Priority.HIGH, scheduled_time="08:00"))
    pet.add_task(Task(title="Grooming", duration_minutes=30, priority=Priority.MEDIUM, scheduled_time="08:00"))

    plan = Scheduler().plan(owner)

    scheduled_titles = [entry.task.title for entry in plan.scheduled_tasks]
    assert "Vet visit" in scheduled_titles
    assert "Grooming" in scheduled_titles
    assert "both scheduled at 08:00" in plan.explain()


def test_sort_by_time_returns_chronological_order():
    late = Task(title="Evening walk", duration_minutes=20, priority=Priority.LOW, scheduled_time="18:00")
    early = Task(title="Morning walk", duration_minutes=20, priority=Priority.LOW, scheduled_time="07:00")
    untimed = Task(title="Brushing", duration_minutes=10, priority=Priority.LOW)

    ordered = Scheduler().sort_by_time([late, early, untimed])

    assert ordered == [early, late, untimed]


def test_mark_daily_task_complete_creates_next_day_task():
    pet = Pet(name="Mochi", species="dog")
    task = Task(title="Feeding", duration_minutes=10, priority=Priority.HIGH, frequency=Frequency.DAILY)
    pet.add_task(task)

    pet.mark_task_complete(task)

    assert pet.get_task_count() == 2
    next_task = pet.get_tasks()[1]
    assert task.completed is True
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_detect_conflicts_flags_duplicate_times():
    first = Task(title="Vet visit", duration_minutes=15, priority=Priority.HIGH, scheduled_time="08:00")
    second = Task(title="Grooming", duration_minutes=30, priority=Priority.MEDIUM, scheduled_time="08:00")

    warnings = Scheduler().detect_conflicts([first, second])

    assert len(warnings) == 1
    assert "Vet visit" in warnings[0]
    assert "Grooming" in warnings[0]
    assert "08:00" in warnings[0]
