from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from app.db import db
from app.routers.auth_router import get_current_user
from pydantic import BaseModel

router = APIRouter()

class UserProgressRequest(BaseModel):
    completed: bool

@router.get("")
async def get_courses():
    courses = await db.course.find_many(include={"lessons": True})
    # Return courses with basic information
    return courses

@router.get("/{course_id}")
async def get_course_details(course_id: str, user_token: Optional[str] = None):
    # Determine the user
    user = None
    if user_token:
        # Resolve user manually to avoid crashing if token is invalid or guest
        try:
            from jose import jwt
            import os
            JWT_SECRET = os.getenv("JWT_SECRET", "gordon_jwt_secret_key_extremely_secure_12345")
            payload = jwt.decode(user_token, JWT_SECRET, algorithms=["HS256"])
            email = payload.get("sub")
            if email:
                user = await db.user.find_unique(where={"email": email})
        except Exception:
            pass

    course = await db.course.find_unique(
        where={"id": course_id},
        include={"lessons": True}
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course.lessons.sort(key=lambda l: l.orderIndex)

    # Access control: Mask video URLs and texts for unpaid/anonymous users for lessons index > 1
    processed_lessons = []
    is_premium = user is not None and user.membershipLevel == "premium"
    
    # Get user progress if logged in
    completed_lessons = set()
    if user:
        progress = await db.userprogress.find_many(where={"userId": user.id, "completed": True})
        completed_lessons = {p.lessonId for p in progress}

    for idx, lesson in enumerate(course.lessons):
        lesson_data = lesson.dict()
        lesson_data["completed"] = lesson.id in completed_lessons
        
        # Free users only get access to the first lesson (index 0)
        if idx == 0 or is_premium:
            # Full access
            pass
        else:
            # Mask sensitive data
            lesson_data["videoUrl"] = ""
            lesson_data["textContent"] = "Upgrade to premium to access this lesson's content."
            lesson_data["isLocked"] = True
            
        processed_lessons.append(lesson_data)
        
    course_data = course.dict()
    course_data["lessons"] = processed_lessons
    return course_data

@router.post("/lessons/{lesson_id}/progress")
async def update_lesson_progress(lesson_id: str, data: UserProgressRequest, current_user = Depends(get_current_user)):
    # Validate lesson exists
    lesson = await db.lesson.find_unique(where={"id": lesson_id})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
        
    # Update or create progress
    progress = await db.userprogress.upsert(
        where={
            "userId_lessonId": {
                "userId": current_user.id,
                "lessonId": lesson_id
            }
        },
        data={
            "create": {
                "userId": current_user.id,
                "lessonId": lesson_id,
                "completed": data.completed
            },
            "update": {
                "completed": data.completed
            }
        }
    )
    return {"status": "success", "completed": progress.completed}
