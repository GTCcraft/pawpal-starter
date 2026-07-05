"""PawPal+ core domain classes.

This module contains class stubs only (no scheduling logic yet). It mirrors
diagrams/uml.mmd but adapts a few details to match app.py's data shapes
(e.g., string priorities like "low"/"medium"/"high", task titles).

Fill in method bodies incrementally as you implement scheduling behavior.
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
    """A single pet care task (e.g., walk, feeding, meds)."""

    title: str
    duration_minutes: int
    priority: Priority

    def __str__(self) -> str:
        raise NotImplementedError


@dataclass
class Pet:
    """A pet belonging to an Owner, with its own list of care tasks."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner, who may have one or more pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError


@dataclass
class DailyPlan:
    """The result of scheduling: an ordered list of tasks plus reasoning."""

    scheduled_tasks: list[Task] = field(default_factory=list)
    unscheduled_tasks: list[Task] = field(default_factory=list)
    reasoning: str = ""

    def display(self) -> str:
        raise NotImplementedError

    def explain(self) -> str:
        raise NotImplementedError


@dataclass
class Scheduler:
    """Builds a DailyPlan from a Pet's tasks under a time constraint."""

    available_minutes: int

    def plan(self, pet: Pet) -> DailyPlan:
        raise NotImplementedError

    def _prioritize(self, tasks: list[Task]) -> list[Task]:
        raise NotImplementedError

    def _fits_in_window(self, task: Task, minutes_remaining: int) -> bool:
        raise NotImplementedError

    def _add_to_plan(self, plan: DailyPlan, task: Task) -> None:
        raise NotImplementedError
