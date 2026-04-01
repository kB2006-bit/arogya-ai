import os
import logging
import uuid
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from ai_service import generate_brief_symptom_analysis, generate_symptom_assessment
from auth_utils import create_access_token, decode_access_token, get_password_hash, verify_password
from clinic_service import fetch_nearby_clinics
from schemas import (
    AuthResponse,
    DashboardSummary,
    NearbyClinicsResponse,
    SymptomCheckRequest,
    SymptomCheckResponse,
    UserCreate,
    UserLogin,
    UserPublic,
)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
users_collection = db.users
checks_collection = db.symptom_checks
chat_history_store: dict[str, list[dict[str, object]]] = {}
failed_login_attempts: dict[str, dict[str, object]] = {}

# Create the main app without a prefix
app = FastAPI(title="ArogyaAI API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")
security = HTTPBearer()


def utc_now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def utc_now():
    from datetime import datetime, timezone

    return datetime.now(timezone.utc)


def serialize_user(user: Dict[str, str]) -> UserPublic:
    return UserPublic(
        id=user["id"],
        email=user["email"],
        language=user.get("language", "en"),
        created_at=user["created_at"],
    )


def serialize_check(record: Dict[str, object]) -> SymptomCheckResponse:
    return SymptomCheckResponse(
        id=record["id"],
        message=record["message"],
        diagnosis=record["diagnosis"],
        severity=record["severity"],
        summary=record["summary"],
        next_steps=record["next_steps"],
        warning_signs=record["warning_signs"],
        emergency_message=record["emergency_message"],
        created_at=record["created_at"],
    )


def build_chat_history_record(user_email: str, message: str, response: str, severity: str) -> Dict[str, object]:
    return {
        "id": str(uuid.uuid4()),
        "user_email": user_email,
        "message": message,
        "diagnosis": response,
        "severity": severity,
        "summary": response,
        "next_steps": [],
        "warning_signs": [],
        "emergency_message": "Emergency! Seek immediate medical help" if severity == "High" else "",
        "created_at": utc_now_iso(),
    }


HISTORY_PROJECTION = {
    "_id": 0,
    "id": 1,
    "message": 1,
    "diagnosis": 1,
    "severity": 1,
    "summary": 1,
    "next_steps": 1,
    "warning_signs": 1,
    "emergency_message": 1,
    "created_at": 1,
}


class SymptomAnalyzeRequest(BaseModel):
    message: str


class ClinicsRequest(BaseModel):
    latitude: float
    longitude: float


def build_mock_clinics(latitude: float, longitude: float) -> list[Dict[str, object]]:
    return [
        {
            "id": "clinic-1",
            "name": "Arogya City Hospital",
            "latitude": round(latitude + 0.0062, 6),
            "longitude": round(longitude + 0.0041, 6),
        },
        {
            "id": "clinic-2",
            "name": "Sunrise Care Clinic",
            "latitude": round(latitude - 0.0048, 6),
            "longitude": round(longitude + 0.0035, 6),
        },
        {
            "id": "clinic-3",
            "name": "Metro Health Point",
            "latitude": round(latitude + 0.0039, 6),
            "longitude": round(longitude - 0.0056, 6),
        },
        {
            "id": "clinic-4",
            "name": "Green Cross Hospital",
            "latitude": round(latitude - 0.0051, 6),
            "longitude": round(longitude - 0.0042, 6),
        },
    ]


def get_request_identifier(request: Request, email: str) -> str:
    _ = request
    return email.lower()


def is_login_locked(identifier: str) -> bool:
    attempt_state = failed_login_attempts.get(identifier)
    if not attempt_state:
        return False
    locked_until = attempt_state.get("locked_until")
    if not locked_until:
        return False
    if utc_now() >= locked_until:
        failed_login_attempts.pop(identifier, None)
        return False
    return True


def register_failed_login(identifier: str) -> None:
    attempt_state = failed_login_attempts.get(identifier, {"count": 0, "locked_until": None})
    attempt_state["count"] += 1
    if attempt_state["count"] >= 5:
        from datetime import timedelta

        attempt_state["locked_until"] = utc_now() + timedelta(minutes=15)
    failed_login_attempts[identifier] = attempt_state


def clear_failed_login(identifier: str) -> None:
    failed_login_attempts.pop(identifier, None)


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]) * 60,
        path="/",
    )


def attach_auth_cors_headers(response: Response, request: Request) -> None:
    origin = request.headers.get("origin")
    allowed_origins = set(frontend_origin_candidates())
    if origin and (origin in allowed_origins or origin.endswith(".preview.emergentagent.com")):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Vary"] = "Origin"


def frontend_origin_candidates() -> list[str]:
    candidates = ["http://localhost:3000"]
    raw_env_candidates = [
        os.environ.get("FRONTEND_URL", ""),
        os.environ.get("REACT_APP_BACKEND_URL", ""),
    ]

    frontend_env_path = ROOT_DIR.parent / "frontend" / ".env"
    if frontend_env_path.exists():
        for line in frontend_env_path.read_text().splitlines():
            if line.startswith("REACT_APP_BACKEND_URL="):
                raw_env_candidates.append(line.split("=", 1)[1].strip().strip('"'))

    for item in raw_env_candidates:
        if not item:
            continue
        parsed = urlparse(item)
        if parsed.scheme and parsed.netloc:
            origin = f"{parsed.scheme}://{parsed.netloc}"
            if origin not in candidates:
                candidates.append(origin)

    return candidates


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
) -> Dict[str, str]:
    token = request.cookies.get("access_token")
    if credentials and credentials.credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    if token == "demo-token":
        demo_user = await users_collection.find_one({"email": os.environ["DEMO_USER_EMAIL"].lower()}, {"_id": 0})
        if demo_user:
            return demo_user

    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user = await users_collection.find_one({"id": payload.get("sub")}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def seed_demo_user() -> None:
    demo_email = os.environ["DEMO_USER_EMAIL"].lower()
    demo_password = os.environ["DEMO_USER_PASSWORD"]
    existing = await users_collection.find_one({"email": demo_email}, {"_id": 0})
    if existing:
        return

    await users_collection.insert_one(
        {
            "id": str(uuid.uuid4()),
            "email": demo_email,
            "password_hash": get_password_hash(demo_password),
            "language": "en",
            "created_at": utc_now_iso(),
        }
    )


@app.on_event("startup")
async def startup_db() -> None:
    await users_collection.create_index("email", unique=True)
    await checks_collection.create_index([("user_id", 1), ("created_at", -1)])
    await seed_demo_user()

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "ArogyaAI API is running"}


@api_router.post("/auth/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup_user(payload: UserCreate, response: Response, request: Request):
    email = payload.email.lower()
    existing = await users_collection.find_one({"email": email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")

    user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "password_hash": get_password_hash(payload.password),
        "language": payload.language,
        "created_at": utc_now_iso(),
    }
    await users_collection.insert_one(user)
    public_user = serialize_user(user)
    token = create_access_token({"sub": user["id"], "email": user["email"]})
    set_auth_cookie(response, token)
    attach_auth_cors_headers(response, request)
    return AuthResponse(token=token, user=public_user)


@api_router.post("/auth/login", response_model=AuthResponse)
async def login_user(payload: UserLogin, request: Request, response: Response):
    email = payload.email.lower()
    identifier = get_request_identifier(request, email)
    if is_login_locked(identifier):
        attach_auth_cors_headers(response, request)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many failed login attempts. Try again later")

    user = await users_collection.find_one({"email": email}, {"_id": 0})
    if not user or not verify_password(payload.password, user["password_hash"]):
        register_failed_login(identifier)
        if is_login_locked(identifier):
            attach_auth_cors_headers(response, request)
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many failed login attempts. Try again later")
        attach_auth_cors_headers(response, request)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    clear_failed_login(identifier)
    public_user = serialize_user(user)
    token = create_access_token({"sub": user["id"], "email": user["email"]})
    set_auth_cookie(response, token)
    attach_auth_cors_headers(response, request)
    return AuthResponse(token=token, user=public_user)


@api_router.options("/auth/login")
async def auth_login_options(request: Request):
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    attach_auth_cors_headers(response, request)
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "content-type, authorization"
    return response


async def handle_demo_login(payload: UserLogin):
    email = payload.email.lower()
    if email == os.environ["DEMO_USER_EMAIL"].lower() and payload.password == os.environ["DEMO_USER_PASSWORD"]:
        return {
            "success": True,
            "token": "demo-token",
            "user": {"email": email},
        }

    return {
        "success": False,
        "message": "Invalid credentials",
    }


@app.post("/login")
async def demo_login(payload: UserLogin):
    return await handle_demo_login(payload)


@api_router.post("/login")
async def demo_login_api(payload: UserLogin):
    return await handle_demo_login(payload)


@api_router.get("/auth/me", response_model=UserPublic)
async def get_me(current_user: Dict[str, str] = Depends(get_current_user)):
    return serialize_user(current_user)


@api_router.post("/clinics")
async def get_mock_clinics(
    payload: ClinicsRequest,
    current_user: Dict[str, str] = Depends(get_current_user),
):
    _ = current_user
    return {"clinics": build_mock_clinics(payload.latitude, payload.longitude)}


async def handle_symptom_analysis(payload: SymptomAnalyzeRequest):
    analysis = await generate_brief_symptom_analysis(payload.message)
    analysis["emergency"] = analysis["severity"] == "High"
    return analysis


@app.post("/analyze-symptoms")
async def analyze_symptoms(
    payload: SymptomAnalyzeRequest,
    current_user: Dict[str, str] = Depends(get_current_user),
):
    try:
        analysis = await handle_symptom_analysis(payload)
        user_history = chat_history_store.setdefault(current_user["email"], [])
        user_history.insert(0, build_chat_history_record(current_user["email"], payload.message, analysis["response"], analysis["severity"]))
        return analysis
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Gemini symptom analysis failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unable to analyze symptoms right now") from exc


@api_router.post("/analyze-symptoms")
async def analyze_symptoms_api(
    payload: SymptomAnalyzeRequest,
    current_user: Dict[str, str] = Depends(get_current_user),
):
    try:
        analysis = await handle_symptom_analysis(payload)
        user_history = chat_history_store.setdefault(current_user["email"], [])
        user_history.insert(0, build_chat_history_record(current_user["email"], payload.message, analysis["response"], analysis["severity"]))
        return analysis
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Gemini symptom analysis failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Unable to analyze symptoms right now") from exc


@api_router.post("/symptom-checker", response_model=SymptomCheckResponse)
async def run_symptom_checker(
    payload: SymptomCheckRequest,
    current_user: Dict[str, str] = Depends(get_current_user),
):
    assessment = await generate_symptom_assessment(
        message=payload.message,
        language=payload.language,
        history=[item.model_dump() for item in payload.history],
    )

    record = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "message": payload.message,
        "language": payload.language,
        "diagnosis": assessment["diagnosis"],
        "severity": assessment["severity"],
        "summary": assessment["summary"],
        "next_steps": assessment["next_steps"],
        "warning_signs": assessment["warning_signs"],
        "emergency_message": assessment["emergency_message"],
        "created_at": utc_now_iso(),
    }
    await checks_collection.insert_one(record)
    return serialize_check(record)


@api_router.get("/history", response_model=list[SymptomCheckResponse])
async def get_history(current_user: Dict[str, str] = Depends(get_current_user)):
    stored_chat_history = chat_history_store.get(current_user["email"], [])
    records = await checks_collection.find(
        {"user_id": current_user["id"]},
        HISTORY_PROJECTION,
    ).sort("created_at", -1).to_list(50)
    combined_history = [*stored_chat_history, *records]
    combined_history.sort(key=lambda record: record["created_at"], reverse=True)
    return [serialize_check(record) for record in combined_history[:50]]


@app.get("/history", response_model=list[SymptomCheckResponse])
async def get_history_root(current_user: Dict[str, str] = Depends(get_current_user)):
    return await get_history(current_user)


@api_router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard(current_user: Dict[str, str] = Depends(get_current_user)):
    severity_records = await checks_collection.find(
        {"user_id": current_user["id"]},
        {"_id": 0, "severity": 1},
    ).to_list(100)
    recent_records = await checks_collection.find(
        {"user_id": current_user["id"]},
        HISTORY_PROJECTION,
    ).sort("created_at", -1).to_list(5)

    return DashboardSummary(
        total_checks=len(severity_records),
        low_alerts=sum(1 for record in severity_records if record["severity"] == "Low"),
        medium_alerts=sum(1 for record in severity_records if record["severity"] == "Medium"),
        high_alerts=sum(1 for record in severity_records if record["severity"] == "High"),
        recent_checks=[serialize_check(record) for record in recent_records],
    )


@api_router.get("/clinics/nearby", response_model=NearbyClinicsResponse)
async def get_nearby_clinics(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    current_user: Dict[str, str] = Depends(get_current_user),
):
    _ = current_user
    try:
        clinic_data = await fetch_nearby_clinics(lat, lng)
        return NearbyClinicsResponse(**clinic_data)
    except Exception as exc:
        logger.exception("Nearby clinic lookup failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to fetch nearby clinics right now",
        ) from exc

# Include the router in the main app
app.include_router(api_router)

cors_origins = frontend_origin_candidates()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://.*\.preview\.emergentagent\.com",
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()