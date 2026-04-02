import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import Cookie, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from ai_service import generate_brief_symptom_analysis, generate_symptom_assessment
from auth_utils import create_access_token, decode_access_token, get_password_hash, verify_password
from clinic_service import fetch_nearby_clinics
from schemas import (
    AuthResponse,
    DashboardSummary,
    NearbyClinic,
    NearbyClinicsResponse,
    SymptomCheckRequest,
    SymptomCheckResponse,
    UserCreate,
    UserLogin,
    UserPublic,
)

load_dotenv()

app = FastAPI(title="ArogyaAI", version="2.0")

# CORS Configuration
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "arogyaai_db")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
users_collection = db["users"]
symptom_checks_collection = db["symptom_checks"]
login_attempts_collection = db["login_attempts"]

# Demo User Configuration
DEMO_USER_EMAIL = os.environ.get("DEMO_USER_EMAIL", "demo@arogyaai.app")
DEMO_USER_PASSWORD = os.environ.get("DEMO_USER_PASSWORD", "Arogya123!")

# Login Security
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


# -------------------------
# HELPER FUNCTIONS
# -------------------------
async def get_user_by_email(email: str):
    return await users_collection.find_one({"email": email})


async def create_user(email: str, password: str, language: str = "en"):
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(password)
    now = datetime.now(timezone.utc).isoformat()
    
    user_doc = {
        "id": user_id,
        "email": email,
        "password_hash": hashed_password,
        "language": language,
        "created_at": now,
    }
    
    await users_collection.insert_one(user_doc)
    return user_doc


async def verify_auth_token(token: Optional[str]) -> dict:
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await users_collection.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def check_login_lockout(email: str) -> bool:
    """Check if user is locked out due to failed login attempts"""
    attempt_record = await login_attempts_collection.find_one({"email": email})
    
    if not attempt_record:
        return False
    
    if attempt_record.get("failed_attempts", 0) >= MAX_LOGIN_ATTEMPTS:
        last_attempt = datetime.fromisoformat(attempt_record.get("last_attempt"))
        elapsed = (datetime.now(timezone.utc) - last_attempt).total_seconds() / 60
        
        if elapsed < LOCKOUT_DURATION_MINUTES:
            return True
        else:
            # Reset after lockout period
            await login_attempts_collection.update_one(
                {"email": email},
                {"$set": {"failed_attempts": 0}}
            )
    
    return False


async def record_failed_login(email: str):
    """Record a failed login attempt"""
    now = datetime.now(timezone.utc).isoformat()
    
    existing = await login_attempts_collection.find_one({"email": email})
    if existing:
        await login_attempts_collection.update_one(
            {"email": email},
            {
                "$inc": {"failed_attempts": 1},
                "$set": {"last_attempt": now}
            }
        )
    else:
        await login_attempts_collection.insert_one({
            "email": email,
            "failed_attempts": 1,
            "last_attempt": now
        })


async def reset_login_attempts(email: str):
    """Reset login attempts on successful login"""
    await login_attempts_collection.update_one(
        {"email": email},
        {"$set": {"failed_attempts": 0}}
    )


# -------------------------
# ROOT ROUTE
# -------------------------
@app.get("/")
async def root():
    return {"message": "ArogyaAI API Running 🚀", "version": "2.0"}


# -------------------------
# AUTH ROUTES
# -------------------------
@app.post("/api/auth/signup", response_model=AuthResponse)
async def signup(user_data: UserCreate, response: Response):
    # Check if user already exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user = await create_user(user_data.email, user_data.password, user_data.language)
    
    # Create access token
    access_token = create_access_token({"sub": user["id"]})
    
    # Set httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=604800  # 7 days
    )
    
    return AuthResponse(
        token=access_token,
        user=UserPublic(
            id=user["id"],
            email=user["email"],
            language=user["language"],
            created_at=user["created_at"]
        )
    )


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(credentials: UserLogin, response: Response):
    # Check if user is locked out
    if await check_login_lockout(credentials.email):
        raise HTTPException(
            status_code=429,
            detail=f"Too many failed login attempts. Please try again in {LOCKOUT_DURATION_MINUTES} minutes."
        )
    
    # Find user
    user = await get_user_by_email(credentials.email)
    if not user:
        await record_failed_login(credentials.email)
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        await record_failed_login(credentials.email)
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Reset login attempts on successful login
    await reset_login_attempts(credentials.email)
    
    # Create access token
    access_token = create_access_token({"sub": user["id"]})
    
    # Set httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=604800  # 7 days
    )
    
    return AuthResponse(
        token=access_token,
        user=UserPublic(
            id=user["id"],
            email=user["email"],
            language=user["language"],
            created_at=user["created_at"]
        )
    )


@app.get("/api/auth/me", response_model=UserPublic)
async def get_current_user(access_token: Optional[str] = Cookie(None)):
    user = await verify_auth_token(access_token)
    
    return UserPublic(
        id=user["id"],
        email=user["email"],
        language=user["language"],
        created_at=user["created_at"]
    )


@app.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}


# -------------------------
# SYMPTOM CHECKER ROUTES
# -------------------------
@app.post("/api/symptom-checker", response_model=SymptomCheckResponse)
async def check_symptoms(request: SymptomCheckRequest, access_token: Optional[str] = Cookie(None)):
    user = await verify_auth_token(access_token)
    
    # Generate AI assessment
    history = [{"role": turn.role, "content": turn.content} for turn in request.history]
    assessment = await generate_symptom_assessment(request.message, request.language, history)
    
    # Create symptom check record
    check_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    check_doc = {
        "id": check_id,
        "user_id": user["id"],
        "message": request.message,
        "diagnosis": assessment["diagnosis"],
        "severity": assessment["severity"],
        "summary": assessment["summary"],
        "next_steps": assessment["next_steps"],
        "warning_signs": assessment["warning_signs"],
        "emergency_message": assessment["emergency_message"],
        "language": request.language,
        "created_at": now,
    }
    
    await symptom_checks_collection.insert_one(check_doc)
    
    return SymptomCheckResponse(**check_doc)


@app.post("/api/analyze-symptoms")
async def analyze_symptoms_brief(request: SymptomCheckRequest, access_token: Optional[str] = Cookie(None)):
    """Simplified symptom analysis for dashboard chat"""
    user = await verify_auth_token(access_token)
    
    # Generate brief AI analysis
    result = await generate_brief_symptom_analysis(request.message)
    
    # Store in history
    check_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    check_doc = {
        "id": check_id,
        "user_id": user["id"],
        "message": request.message,
        "diagnosis": result["response"],
        "severity": result["severity"],
        "summary": result["response"],
        "next_steps": [],
        "warning_signs": [],
        "emergency_message": "Seek urgent care if symptoms worsen.",
        "language": request.language,
        "created_at": now,
    }
    
    await symptom_checks_collection.insert_one(check_doc)
    
    return {
        "response": result["response"],
        "severity": result["severity"],
        "emergency": result["severity"] == "High"
    }


@app.get("/api/history")
async def get_symptom_history(access_token: Optional[str] = Cookie(None)):
    user = await verify_auth_token(access_token)
    
    # Fetch user's symptom checks
    cursor = symptom_checks_collection.find({"user_id": user["id"]}).sort("created_at", -1)
    checks = await cursor.to_list(length=100)
    
    # Format for response
    history = []
    for check in checks:
        history.append({
            "id": check["id"],
            "message": check["message"],
            "diagnosis": check.get("diagnosis", ""),
            "severity": check["severity"],
            "summary": check.get("summary", ""),
            "next_steps": check.get("next_steps", []),
            "warning_signs": check.get("warning_signs", []),
            "emergency_message": check.get("emergency_message", ""),
            "created_at": check["created_at"],
        })
    
    return history


@app.get("/api/dashboard", response_model=DashboardSummary)
async def get_dashboard(access_token: Optional[str] = Cookie(None)):
    user = await verify_auth_token(access_token)
    
    # Fetch user's symptom checks
    cursor = symptom_checks_collection.find({"user_id": user["id"]}).sort("created_at", -1)
    checks = await cursor.to_list(length=100)
    
    # Calculate summary stats
    total_checks = len(checks)
    low_alerts = sum(1 for c in checks if c["severity"] == "Low")
    medium_alerts = sum(1 for c in checks if c["severity"] == "Medium")
    high_alerts = sum(1 for c in checks if c["severity"] == "High")
    
    # Format recent checks
    recent_checks = [
        SymptomCheckResponse(
            id=check["id"],
            message=check["message"],
            diagnosis=check.get("diagnosis", ""),
            severity=check["severity"],
            summary=check.get("summary", ""),
            next_steps=check.get("next_steps", []),
            warning_signs=check.get("warning_signs", []),
            emergency_message=check.get("emergency_message", ""),
            created_at=check["created_at"],
        )
        for check in checks[:10]
    ]
    
    return DashboardSummary(
        total_checks=total_checks,
        low_alerts=low_alerts,
        medium_alerts=medium_alerts,
        high_alerts=high_alerts,
        recent_checks=recent_checks,
    )


# -------------------------
# CLINIC ROUTES
# -------------------------
@app.get("/api/clinics/nearby", response_model=NearbyClinicsResponse)
async def get_nearby_clinics(lat: float, lng: float, access_token: Optional[str] = Cookie(None)):
    await verify_auth_token(access_token)
    
    result = await fetch_nearby_clinics(lat, lng)
    
    return NearbyClinicsResponse(
        map_embed_url=result["map_embed_url"],
        emergency_number=result["emergency_number"],
        clinics=[NearbyClinic(**clinic) for clinic in result["clinics"]]
    )


# -------------------------
# DEMO/LEGACY ROUTES
# -------------------------
@app.post("/api/login")
async def demo_login(response: Response):
    """Legacy demo login endpoint for compatibility"""
    # Create demo token
    demo_token = "demo-token"
    
    response.set_cookie(
        key="access_token",
        value=demo_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800
    )
    
    return {"token": demo_token}


# -------------------------
# STARTUP EVENT
# -------------------------
@app.on_event("startup")
async def startup_event():
    """Initialize database indexes and demo user"""
    # Create indexes
    await users_collection.create_index("email", unique=True)
    await symptom_checks_collection.create_index("user_id")
    await login_attempts_collection.create_index("email")
    
    # Create demo user if not exists
    demo_user = await get_user_by_email(DEMO_USER_EMAIL)
    if not demo_user:
        await create_user(DEMO_USER_EMAIL, DEMO_USER_PASSWORD, "en")
        print(f"✅ Demo user created: {DEMO_USER_EMAIL}")
