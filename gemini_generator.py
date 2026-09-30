import json

from google import genai
from google.genai import types

from .config import get_settings
from .database import User
from .schemas import WorkoutPlanResponse


settings = get_settings()


def get_client():
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add your Gemini API key to the .env file."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_workout_gemini(user: User) -> str:
    client = get_client()

    prompt = f"""
You are FitBuddy, a responsible fitness planning assistant.

Create a personalized 7-day workout plan using these user details:

Name: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Intensity: {user.intensity}

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

Requirements:
- Keep the plan practical and beginner-friendly where appropriate.
- Match the requested intensity.
- Include recovery/rest.
- Avoid dangerous or extreme exercise.
- Do not prescribe medication.
- Do not diagnose medical conditions.
- Do not recommend performance-enhancing drugs.
- Do not recommend dangerous dehydration.
- Do not recommend extreme calorie restriction.
- If an exercise could be unsuitable for an injury or medical condition,
  advise professional clearance.
- Use clear exercise names and realistic durations.
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
        return parsed.model_dump_json(
            indent=2
        )

    if response.text:
        data = json.loads(response.text)

        validated = WorkoutPlanResponse.model_validate(
            data
        )

        return validated.model_dump_json(
            indent=2
        )

    raise RuntimeError(
        "Gemini returned an empty workout plan."
    )