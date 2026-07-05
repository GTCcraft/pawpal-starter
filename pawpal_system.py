"""PawPal+ core domain classes.

This module mirrors diagrams/uml.mmd but adapts a few details to match
app.py's data shapes (e.g., string priorities like "low"/"medium"/"high",
task titles), plus additional requirements: task completion status (for
today's plan) and a Scheduler that organizes tasks across all of an
Owner's pets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Priority(str, Enum):
    """Task priority levels, matching the values used in app.py."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    """A single pet care task (e.g., walk, feeding, meds) for today's plan."""

    title: str
    duration_minutes: int
    priority: Priority
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done for today."""
        self.completed = True

    def __str__(self) -> str:
        """Render as a checklist line, e.g. "[x] Feeding (10 min) [priority: high]"."""
        status = "x" if self.completed else " "
        return f"[{status}] {self.title} ({self.duration_minutes} min) [priority: {self.priority.value}]"


@dataclass
class Pet:
    """A pet belonging to an Owner, with its own list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's list."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return this pet's care tasks."""
        return self.tasks

    def get_task_count(self) -> int:
        """Return how many care tasks this pet has."""
        return len(self.tasks)


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
class DailyPlan:
    """The result of scheduling: an ordered list of tasks plus reasoning."""

    scheduled_tasks: list[Task] = field(default_factory=list)
    unscheduled_tasks: list[Task] = field(default_factory=list)
    reasoning: str = ""

    def display(self) -> str:
        """Render the schedule itself: what's scheduled vs. left out."""
        lines = ["Today's Schedule:"]
        if not self.scheduled_tasks:
            lines.append("  (no tasks scheduled)")
        for task in self.scheduled_tasks:
            lines.append(f"  - {task}")
        if self.unscheduled_tasks:
            lines.append("Unscheduled (ran out of time):")
            for task in self.unscheduled_tasks:
                lines.append(f"  - {task}")
        return "\n".join(lines)

    def explain(self) -> str:
        """Return the scheduler's reasoning for why each task was kept or skipped."""
        return self.reasoning


@dataclass
class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an Owner's pets."""

    available_minutes: int

    def plan(self, owner: Owner) -> DailyPlan:
        """Build a DailyPlan from the combined tasks of all of owner's pets."""
        plan = DailyPlan()
        minutes_remaining = self.available_minutes
        reasons = []

        for task in self._prioritize(owner.get_all_tasks()):
            if self._fits_in_window(task, minutes_remaining):
                self._add_to_plan(plan, task)
                minutes_remaining -= task.duration_minutes
                reasons.append(
                    f"Scheduled '{task.title}' (priority: {task.priority.value}, "
                    f"{task.duration_minutes} min) — {minutes_remaining} min remaining."
                )
            else:
                plan.unscheduled_tasks.append(task)
                reasons.append(
                    f"Skipped '{task.title}' ({task.duration_minutes} min) — "
                    f"only {minutes_remaining} min remaining."
                )

        plan.reasoning = "\n".join(reasons)
        return plan

    def _prioritize(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks highest priority first."""
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(tasks, key=lambda task: order[task.priority])

    def _fits_in_window(self, task: Task, minutes_remaining: int) -> bool:
        """Check whether a task's duration fits in the remaining time."""
        return task.duration_minutes <= minutes_remaining

    def _add_to_plan(self, plan: DailyPlan, task: Task) -> None:
        """Append a task to a plan's scheduled tasks."""
        plan.scheduled_tasks.append(task)
