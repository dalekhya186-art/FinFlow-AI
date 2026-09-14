from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models.user import User


router = APIRouter(
    prefix="/settings",
    tags=["Settings"]
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


class SettingsRequest(BaseModel):

    email: str
    name: str

    automatic_verification: bool = True

    ai_categorization: bool = True

    processing_notifications: bool = True


@router.get("/")
def get_settings(
    email: str,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == email
    ).first()


    if not user:

        return {
            "status": "error",
            "message": "User not found"
        }


    return {

        "status": "success",

        "settings": {

            "id": user.id,

            "name": user.name or "",

            "email": user.email,

            "automatic_verification":
                user.automatic_verification,

            "ai_categorization":
                user.ai_categorization,

            "processing_notifications":
                user.processing_notifications

        }

    }


@router.put("/")
def update_settings(
    request: SettingsRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()


    if not user:

        return {
            "status": "error",
            "message": "User not found"
        }


    user.name = request.name.strip()

    user.email = request.email.strip()

    user.automatic_verification = (
        request.automatic_verification
    )

    user.ai_categorization = (
        request.ai_categorization
    )

    user.processing_notifications = (
        request.processing_notifications
    )


    db.commit()

    db.refresh(user)


    return {

        "status": "success",

        "message":
            "Settings updated successfully",

        "settings": {

            "id": user.id,

            "name": user.name,

            "email": user.email,

            "automatic_verification":
                user.automatic_verification,

            "ai_categorization":
                user.ai_categorization,

            "processing_notifications":
                user.processing_notifications

        }

    }