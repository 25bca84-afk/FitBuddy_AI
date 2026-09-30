from typing import Literal

from pydantic import BaseModel, Field, field_validator


Goal = Literal[
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
]


Intensity = Literal[
    "low",
    "medium",
    "high",
]


class UserInput(BaseModel):
    username: str = Field(
        min_length=2,
        max_length=120,
    )

    user_id: str = Field(
        min_length=2,
        max_length=80,
    )

    age: int = Field(
        ge=13,
        le=100,
    )

    weight: float = Field(
        gt=20,
        le=500,
    )

    goal: Goal

    intensity: Intensity

    @field_validator(
        "username",
        "user_id",
    )
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class FeedbackRequest(BaseModel):
    user_id: str = Field(
        min_length=2,
        max_length=80,
    )

    feedback: str = Field(
        min_length=3,
        max_length=2000,
    )

    @field_validator(
        "user_id",
        "feedback",
    )
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class Exercise(BaseModel):
    name: str
    sets: str
    reps_or_duration: str
    rest: str


class DayPlan(BaseModel):
    day: str
    focus: str
    warm_up: str
    exercises: list[Exercise]
    cool_down: str


class WorkoutPlanResponse(BaseModel):
    days: list[DayPlan] = Field(
        min_length=7,
        max_length=7,
    )


class NutritionTipResponse(BaseModel):
    tip: str
    recovery_note: str