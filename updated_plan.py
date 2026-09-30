import json

from google.genai import types

from .config import get_settings
from .gemini_generator import get_client
from .schemas import WorkoutPlanResponse


settings = get_settings()


def update_workout_plan(
    original_plan: str,
    feedback: str,
) -> str:
    client = get_client()

    prompt = f"""
You are updating an existing FitBuddy 7-day workout plan.

Original plan:
{original_plan}

User feedback:
{feedback}

Create a revised 7-day plan.

Return exactly 7 days.

Every day must contain:
- day
- focus
- warm_up
- exercises
- cool_down

Every exercise must contain:
- name
- sets
- reps_or_duration
- rest

Use the user's feedback to make reasonable changes.

Safety requirements:
- Do not diagnose medical conditions.
- Do not prescribe medical treatment.
- Do not recommend performance-enhancing drugs.
- Do not recommend dangerous dehydration.
- Do not recommend extreme calorie restriction.
- Keep the workout practical and safe.
"""

    response = client.models.generate_content(
        model=settings.workout_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=WorkoutPlanResponse,
            temperature=0.5,
            max_output_tokens=7000,
        ),
    )

    parsed = response.parsed

    if parsed is not None:
        return parsed.model_dump_json(indent=2)

    if response.text:
        data = json.loads(response.text)

        validated = WorkoutPlanResponse.model_validate(data)

        return validated.model_dump_json(indent=2)

    raise RuntimeError(
        "Gemini returned an empty updated plan."
    )