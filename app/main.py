from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import db
from app.routers import auth_router, courses_router, exams_router, payments_router, admin_router

app = FastAPI(title="Gordon IT Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://robiulsunnyemon.github.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    if db.is_connected():
        await db.disconnect()

# Include routers
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(courses_router.router, prefix="/api/courses", tags=["Courses"])
app.include_router(exams_router.router, prefix="/api/exams", tags=["Practice Exams"])
app.include_router(payments_router.router, prefix="/api/payments", tags=["Payments"])
app.include_router(admin_router.router, prefix="/api/admin", tags=["Admin Operations"])

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "database": db.is_connected()}
