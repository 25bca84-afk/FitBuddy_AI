from google.genai import types

from .config import get_settings
from .gemini_generator import get_client
from .schemas import NutritionTipResponse


settings = get_settings()


def generate_nutrition_tip_with_flash(user_goal: str) -> str:
    client = get_client()

    prompt = f"""
Create a short, practical wellness nutrition tip for someone whose fitness goal is:

{user_goal}

Return:
- tip
- recovery_note

Focus on balanced meals, adequate protein, hydration, fruits and vegetables,
reasonable portions, and sleep/recovery.

Do not provide medical treatment.
Do not diagnose diseases.
Do not recommend extreme diets.
Do not recommend dangerous calorie restriction.
"""

    response = client.models.generate_content(
        model=settings.tip_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=NutritionTipResponse,
            temperature=0.4,
            max_output_tokens=1000,
        ),
    )

    parsed = response.parsed

    if parsed is None:
        raise RuntimeError(
            "Gemini returned an empty nutrition response."
        )

    return (
        f"Nutrition tip: {parsed.tip}\n\n"
        f"Recovery note: {parsed.recovery_note}"
    )