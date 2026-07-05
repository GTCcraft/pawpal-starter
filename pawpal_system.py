"""PawPal+ core domain classes.

This module mirrors diagrams/uml.mmd but adapts a few details to match
app.py's data shapes (e.g., string priorities like "low"/"medium"/"high",
task titles), plus additional requirements: task completion status (for
today's plan) and a Scheduler that organizes tasks across all of an
Owner's pets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum


class Priority(str, Enum):
    """Task priority levels, matching the values used in app.py."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Frequency(str, Enum):
    """How often a recurring task repeats. Unset means a one-time task."""

    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    """A single pet care task (e.g., walk, feeding, meds) for today's plan."""

    title: str
    duration_minutes: int
    priority: Priority
    completed: bool = False
    pet_name: str = ""
    scheduled_time: str | None = None
    due_date: date = field(default_factory=date.today)
    frequency: Frequency | None = None

    def mark_complete(self) -> Task | None:
        """Mark this task done for today; return its next occurrence if it recurs."""
        self.completed = True
        if self.frequency is None:
            return None

        interval = timedelta(days=1) if self.frequency == Frequency.DAILY else timedelta(weeks=1)
        next_due = max(date.today(), self.due_date) + interval
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            pet_name=self.pet_name,
            scheduled_time=self.scheduled_time,
            due_date=next_due,
            frequency=self.frequency,
        )

    def __str__(self) -> str:
        """Render as a task line, e.g. "Mochi: Feeding (10 min) [priority: high]"."""
        pet_part = f"{self.pet_name}: " if self.pet_name else ""
        return f"{pet_part}{self.title} ({self.duration_minutes} min) [priority: {self.priority.value}]"


@dataclass
class Pet:
    """A pet belonging to an Owner, with its own list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's list, stamping it with this pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return this pet's care tasks."""
        return self.tasks

    def get_task_count(self) -> int:
        """Return how many care tasks this pet has."""
        return len(self.tasks)

    def mark_task_complete(self, task: Task) -> None:
        """Mark a task complete and add its next occurrence, if it recurs."""
        next_task = task.mark_complete()
        if next_task is not None:
            self.add_task(next_task)


@dataclass
class Owner:
    """The pet owner, who manages multiple pets and their tasks."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return tasks across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.get_tasks()]


@dataclass
class ScheduledEntry:
    """A task placed on the daily timeline at a specific computed start time."""

    start_time: str
    task: Task


@dataclass
class DailyPlan:
    """The result of scheduling: an ordered list of tasks plus reasoning."""

    scheduled_tasks: list[ScheduledEntry] = field(default_factory=list)
    unscheduled_tasks: list[Task] = field(default_factory=list)
    reasoning: str = ""

    def display(self) -> str:
        """Render the schedule itself: what's scheduled vs. left out."""
        lines = ["Today's Schedule:"]
        if not self.scheduled_tasks:
            lines.append("  (no tasks scheduled)")
        for entry in self.scheduled_tasks:
            lines.append(f"  - {entry.start_time}  {entry.task}")
        if self.unscheduled_tasks:
            lines.append("Unscheduled (no time available):")
            for task in self.unscheduled_tasks:
                lines.append(f"  - {task}")
        return "\n".join(lines)

    def explain(self) -> str:
        """Return the scheduler's reasoning for why each task was kept or skipped."""
        return self.reasoning


@dataclass
class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an Owner's pets."""

    start_time: str = "08:00"
    end_time: str = "20:00"

    def plan(self, owner: Owner) -> DailyPlan:
        """Build a DailyPlan: a timeline from start_time to end_time.

        Anchored tasks (with a scheduled_time) are placed at their requested
        time. Flexible tasks (no scheduled_time) fill the gaps between/after
        anchors, in priority order, using only the next-highest-priority
        remaining task per gap (no backtracking to a smaller one that might
        also fit).
        """
        today = date.today()
        eligible = [
            task for task in owner.get_all_tasks() if not task.completed and task.due_date <= today
        ]
        anchored = self.sort_by_time([task for task in eligible if task.scheduled_time is not None])
        flexible = self._prioritize([task for task in eligible if task.scheduled_time is None])

        day_start = self._to_minutes(self.start_time)
        day_end = self._to_minutes(self.end_time)

        plan = DailyPlan()
        reasons = []
        cursor = day_start
        flexible_queue = list(flexible)

        def fill_gap(gap_end: int) -> None:
            nonlocal cursor
            while flexible_queue and self._fits_in_window(flexible_queue[0], gap_end - cursor):
                task = flexible_queue.pop(0)
                self._add_to_plan(plan, task, self._to_clock(cursor))
                reasons.append(
                    f"Scheduled '{task.title}' (priority: {task.priority.value}, "
                    f"{task.duration_minutes} min) at {self._to_clock(cursor)}."
                )
                cursor += task.duration_minutes

        for anchor in anchored:
            anchor_start = self._to_minutes(anchor.scheduled_time)
            fill_gap(min(anchor_start, day_end))

            if cursor > anchor_start:
                reasons.append(
                    f"'{anchor.title}' was requested at {anchor.scheduled_time}, but earlier "
                    f"tasks run until {self._to_clock(cursor)} — keeping it at its requested time."
                )
            if anchor_start + anchor.duration_minutes > day_end:
                reasons.append(
                    f"'{anchor.title}' at {anchor.scheduled_time} extends past your available "
                    f"window (ends {self.end_time})."
                )

            self._add_to_plan(plan, anchor, anchor.scheduled_time)
            reasons.append(
                f"Scheduled '{anchor.title}' (priority: {anchor.priority.value}, "
                f"{anchor.duration_minutes} min) at its requested time {anchor.scheduled_time}."
            )
            cursor = max(cursor, anchor_start) + anchor.duration_minutes

        fill_gap(day_end)

        for task in flexible_queue:
            plan.unscheduled_tasks.append(task)
            reasons.append(
                f"Skipped '{task.title}' ({task.duration_minutes} min) — "
                f"no gap large enough before {self.end_time}."
            )

        for warning in self.detect_conflicts(eligible):
            reasons.append(f"Warning: {warning}")

        plan.reasoning = "\n".join(reasons)
        return plan

    def _prioritize(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks highest priority first."""
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(tasks, key=lambda task: order[task.priority])

    def _fits_in_window(self, task: Task, minutes_remaining: int) -> bool:
        """Check whether a task's duration fits in the remaining time."""
        return task.duration_minutes <= minutes_remaining

    def _add_to_plan(self, plan: DailyPlan, task: Task, start_time: str) -> None:
        """Append a task to a plan's scheduled tasks at the given start time."""
        plan.scheduled_tasks.append(ScheduledEntry(start_time=start_time, task=task))

    def _to_minutes(self, time_str: str) -> int:
        """Convert an "HH:MM" clock string to minutes since midnight."""
        hours, minutes = time_str.split(":")
        return int(hours) * 60 + int(minutes)

    def _to_clock(self, minutes: int) -> str:
        """Convert minutes since midnight to an "HH:MM" clock string."""
        minutes %= 24 * 60
        return f"{minutes // 60:02d}:{minutes % 60:02d}"

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks chronologically by scheduled_time; untimed tasks sort last."""
        return sorted(tasks, key=lambda task: (task.scheduled_time is None, task.scheduled_time or ""))

    def filter_tasks(
        self,
        tasks: list[Task],
        *,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Filter tasks by completion status and/or owning pet's name."""
        filtered = tasks
        if completed is not None:
            filtered = [task for task in filtered if task.completed == completed]
        if pet_name is not None:
            filtered = [task for task in filtered if task.pet_name == pet_name]
        return filtered

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return a warning for each pair of tasks pinned to the same scheduled_time."""
        warnings = []
        seen: dict[str, Task] = {}
        for task in tasks:
            if task.scheduled_time is None:
                continue
            other = seen.get(task.scheduled_time)
            if other is not None:
                warnings.append(
                    f"'{other.title}' ({other.pet_name}) and '{task.title}' ({task.pet_name}) "
                    f"are both scheduled at {task.scheduled_time}."
                )
            else:
                seen[task.scheduled_time] = task
        return warnings
