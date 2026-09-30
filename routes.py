import json

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .config import get_settings
from .database import (
    delete_user,
    get_all_users,
    get_db,
    get_latest_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
)
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .schemas import FeedbackRequest, UserInput
from .updated_plan import update_workout_plan


router = APIRouter()

templates = Jinja2Templates(directory="templates")

settings = get_settings()


def render_error(
    request: Request,
    message: str,
    status_code: int = 500,
):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "message": message,
        },
        status_code=status_code,
    )


def pretty_plan(plan_json: str):
    try:
        data = json.loads(plan_json)
        return data.get("days", [])
    except Exception:
        return []


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse,
)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        user_input = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        user = save_user(
            db=db,
            user_id=user_input.user_id,
            username=user_input.username,
            age=user_input.age,
            weight=user_input.weight,
            goal=user_input.goal,
            intensity=user_input.intensity,
        )

        workout = generate_workout_gemini(user)

        nutrition = generate_nutrition_tip_with_flash(
            user_input.goal
        )

        plan = save_plan(
            db=db,
            user=user,
            original_plan=workout,
            nutrition_tip=nutrition,
        )

        days = pretty_plan(plan.original_plan)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": plan,
                "days": days,
                "current_plan": plan.original_plan,
            },
        )

    except ValueError as exc:
        return render_error(
            request,
            str(exc),
            422,
        )

    except Exception as exc:
        return render_error(
            request,
            str(exc),
            500,
        )


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse,
)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        feedback_request = FeedbackRequest(
            user_id=user_id,
            feedback=feedback,
        )

        user = get_user(
            db,
            feedback_request.user_id,
        )

        if not user:
            return render_error(
                request,
                "User not found.",
                404,
            )

        plan = get_latest_plan(
            db,
            user,
        )

        if not plan:
            return render_error(
                request,
                "No workout plan found for this user.",
                404,
            )

        current_plan = (
            plan.updated_plan
            if plan.updated_plan
            else plan.original_plan
        )

        revised_plan = update_workout_plan(
            original_plan=current_plan,
            feedback=feedback_request.feedback,
        )

        update_plan(
            db=db,
            plan=plan,
            updated_plan=revised_plan,
            feedback=feedback_request.feedback,
        )

        days = pretty_plan(revised_plan)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": plan,
                "days": days,
                "current_plan": revised_plan,
            },
        )

    except ValueError as exc:
        return render_error(
            request,
            str(exc),
            422,
        )

    except Exception as exc:
        return render_error(
            request,
            str(exc),
            500,
        )


@router.get(
    "/view-all-users",
    response_class=HTMLResponse,
)
def view_all_users(
    request: Request,
    admin_key: str = "",
    db: Session = Depends(get_db),
):
    if admin_key != settings.admin_key:
        return render_error(
            request,
            "Unauthorized. Invalid admin key.",
            403,
        )

    users = get_all_users(db)

    user_data = []

    for user in users:
        latest_plan = get_latest_plan(
            db,
            user,
        )

        user_data.append(
            {
                "user": user,
                "latest_plan": latest_plan,
                "days": (
                    pretty_plan(
                        latest_plan.updated_plan
                        or latest_plan.original_plan
                    )
                    if latest_plan
                    else []
                ),
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": user_data,
            "admin_key": admin_key,
        },
    )


@router.post(
    "/admin/delete/{user_id}"
)
def admin_delete_user(
    user_id: str,
    admin_key: str = Form(...),
    db: Session = Depends(get_db),
):
    if admin_key != settings.admin_key:
        return HTMLResponse(
            content="Unauthorized",
            status_code=403,
        )

    delete_user(
        db=db,
        user_id=user_id,
    )

    return RedirectResponse(
        url=f"/view-all-users?admin_key={admin_key}",
        status_code=303,
    )