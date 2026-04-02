from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import uuid
from typing import Dict

app = FastAPI(title="ArogyaAI SIMPLE", version="1.0")

security = HTTPBearer()

# -------------------------
# SIMPLE IN-MEMORY STORAGE
# -------------------------
users_db = {}
history_db = {}

# -------------------------
# MODELS
# -------------------------
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class SymptomRequest(BaseModel):
    message: str

# -------------------------
# AUTH HELPERS
# -------------------------
def fake_token(user_id):
    return f"token-{user_id}"

def get_user_from_token(token: str):
    if token.startswith("token-"):
        user_id = token.split("token-")[1]
        return users_db.get(user_id)
    return None

# -------------------------
# AUTH ROUTES
# -------------------------
@app.post("/signup")
def signup(data: UserCreate):
    user_id = str(uuid.uuid4())
    users_db[user_id] = {
        "id": user_id,
        "email": data.email,
        "password": data.password
    }
    return {"message": "User created"}

@app.post("/login")
def login(data: UserLogin):
    for user in users_db.values():
        if user["email"] == data.email and user["password"] == data.password:
            return {"token": fake_token(user["id"])}

    raise HTTPException(status_code=401, detail="Invalid credentials")

# -------------------------
# PROTECTED ROUTE
# -------------------------
def get_current_user(token: str):
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# -------------------------
# AI MOCK RESPONSE
# -------------------------
def analyze(message: str):
    if "fever" in message.lower():
        return {"response": "Possible viral infection", "severity": "Medium"}
    return {"response": "Seems mild", "severity": "Low"}

# -------------------------
# MAIN FEATURE
# -------------------------
@app.post("/analyze")
def analyze_symptoms(data: SymptomRequest, token: str):
    user = get_current_user(token)

    result = analyze(data.message)

    user_history = history_db.setdefault(user["id"], [])
    user_history.append({
        "message": data.message,
        "result": result
    })

    return result

@app.get("/history")
def get_history(token: str):
    user = get_current_user(token)
    return history_db.get(user["id"], [])

# -------------------------
# ROOT
# -------------------------
@app.get("/")
def root():
    return {"message": "ArogyaAI Running 🚀"}