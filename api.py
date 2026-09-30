from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import get_db, get_latest_plan, get_user


router = APIRouter(
    prefix="/api",
    tags=["API"],
)


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "FitBuddy",
    }


@router.get("/users/{user_id}")
def get_user_details(
    user_id: str,
    db: Session = Depends(get_db),
):
    user = get_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    latest_plan = get_latest_plan(db, user)

    return {
        "user": {
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
        },
        "latest_plan": {
            "id": latest_plan.id if latest_plan else None,
            "created_at": (
                latest_plan.created_at.isoformat()
                if latest_plan
                else None
            ),
            "has_updated_plan": bool(
                latest_plan and latest_plan.updated_plan
            ),
        },
    }