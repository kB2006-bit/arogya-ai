# ArogyaAI

ArogyaAI is a bilingual health web app that helps users:

- create an account and sign in securely
- chat with an AI symptom checker in English or Hindi
- store symptom history and severity trends in a patient dashboard
- discover nearby hospitals and clinics using current location
- surface an emergency SOS path when severity is high

## Implemented Stack

- Frontend: React + Tailwind CSS + React Router
- Backend: FastAPI
- Database: MongoDB
- AI: Gemini through the Emergent universal LLM key
- Maps: Google Maps embed links + nearby clinic lookup from current coordinates

## Project Structure

```bash
/app
├── backend
│   ├── server.py
│   ├── ai_service.py
│   ├── auth_utils.py
│   ├── clinic_service.py
│   ├── schemas.py
│   ├── requirements.txt
│   └── .env
├── frontend
│   ├── src
│   │   ├── components
│   │   ├── context
│   │   ├── lib
│   │   └── pages
│   ├── package.json
│   └── .env
└── README.md
```

## VS Code Setup Guide

1. Open the project folder in VS Code.
2. Open one terminal for the backend and one for the frontend.
3. Make sure MongoDB is running locally.
4. Create or update the environment files listed below.
5. Install dependencies for backend and frontend.
6. Start both servers.

## Environment Variables

### Backend `/backend/.env`

```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"
JWT_SECRET="replace-with-a-long-random-secret"
ACCESS_TOKEN_EXPIRE_MINUTES="10080"
GEMINI_API_KEY="your-emergent-or-gemini-key"
GEMINI_MODEL="gemini-2.0-flash"
DEMO_USER_EMAIL="demo@arogyaai.app"
DEMO_USER_PASSWORD="Arogya123!"
```

### Frontend `/frontend/.env`

```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
```

## Install Commands

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
yarn install
```

## Run Commands

### Backend

```bash
cd backend
source .venv/bin/activate
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### Frontend

```bash
cd frontend
yarn start
```

## API Key Setup Guide

### Gemini / Emergent Universal Key

1. Open your Universal Key section.
2. Copy the LLM key.
3. Paste it into `GEMINI_API_KEY` in `backend/.env`.
4. Keep `GEMINI_MODEL` set to `gemini-2.0-flash` unless you want to switch models.

### MongoDB

1. Start your MongoDB instance locally or use a managed MongoDB URI.
2. Put the connection string in `MONGO_URL`.
3. Set `DB_NAME` to the database you want ArogyaAI to use.

### Maps / Location

1. No extra key is required for the current implementation.
2. The browser requests the user’s current location.
3. Nearby clinic cards open Google Maps directions directly.

## Main Routes

- `/` → landing page
- `/login` → login
- `/signup` → account creation
- `/dashboard` → patient dashboard
- `/chat` → AI symptom checker
- `/clinics` → nearby clinics and hospitals

## Demo Account

```text
Email: demo@arogyaai.app
Password: Arogya123!
```

## Production Notes

- Auth is protected with JWT tokens.
- Symptom results are stored per user in MongoDB.
- High-severity responses show a visible emergency call action.
- The UI is mobile-friendly and supports English/Hindi switching.
