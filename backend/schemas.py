from typing import List, Literal

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    language: Literal["en", "hi"] = "en"


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    language: Literal["en", "hi"]
    created_at: str


class AuthResponse(BaseModel):
    token: str
    user: UserPublic


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1000)


class SymptomCheckRequest(BaseModel):
    message: str = Field(min_length=3, max_length=1200)
    language: Literal["en", "hi"] = "en"
    history: List[ChatTurn] = Field(default_factory=list)


class SymptomCheckResponse(BaseModel):
    id: str
    message: str
    diagnosis: str
    severity: Literal["Low", "Medium", "High"]
    summary: str
    next_steps: List[str]
    warning_signs: List[str]
    emergency_message: str
    created_at: str


class DashboardSummary(BaseModel):
    total_checks: int
    low_alerts: int
    medium_alerts: int
    high_alerts: int
    recent_checks: List[SymptomCheckResponse]


class NearbyClinic(BaseModel):
    id: str
    name: str
    address: str
    distance_km: float
    latitude: float
    longitude: float
    maps_url: str


class NearbyClinicsResponse(BaseModel):
    map_embed_url: str
    emergency_number: str
    clinics: List[NearbyClinic]