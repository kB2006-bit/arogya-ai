# Arogya AI

**Your trusted AI health assistant for instant symptom assessment**

Arogya AI is an intelligent healthcare application that provides:

- 🤖 **AI-Powered Symptom Analysis** - Get instant medical guidance using advanced AI (Gemini 2.5 Flash)
- 🎯 **Smart Risk Assessment** - Clear severity ratings (Low/Medium/High) with specific actions
- 🏥 **Find Nearby Care** - Locate hospitals and clinics near you with distance and directions
- 📊 **Health History** - Track your symptom assessments over time
- 🌐 **Bilingual Support** - Available in English and Hindi
- 🚨 **Emergency Guidance** - Immediate action recommendations for high-risk symptoms

## Technology Stack

- **Frontend**: React + Vite + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **AI Engine**: Google Gemini 2.5 Flash (via Emergent LLM integration)
- **Maps**: Google Maps + OpenStreetMap Overpass API
- **Authentication**: JWT with httpOnly cookies

## Project Structure

```bash
/app
├── backend/
│   ├── server.py              # FastAPI main application
│   ├── ai_service.py          # Hybrid AI + rule-based symptom analysis
│   ├── auth_utils.py          # JWT authentication
│   ├── clinic_service.py      # Hospital/clinic finder
│   ├── schemas.py             # Pydantic models
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Route pages
│   │   ├── lib/               # Utilities and helpers
│   │   └── context/           # React context providers
│   ├── package.json
│   └── .env                   # Frontend environment
└── README.md
```
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

## Key Features

### 🤖 Intelligent Symptom Analysis
- **Hybrid AI System**: Combines Google Gemini AI with rule-based safety protocols
- **Smart Risk Classification**: Automatic detection of critical keywords (chest pain, bleeding, etc.)
- **Pattern Detection**: Identifies concerning symptom combinations
- **Medical Reasoning**: AI provides detailed diagnosis and recommendations
- **Safety Override**: Rule-based severity always takes precedence for medical safety

### 📊 Health Score Meter
- Visual risk indicator (0-100 scale)
- Animated progress bar
- Color-coded by severity (Green/Amber/Red)
- Clear messaging for each risk level

### 👨‍⚕️ Doctor Recommendations
- Intelligent specialist matching based on symptoms
- Automatic suggestions (Cardiologist, Neurologist, Dermatologist, etc.)
- Explains why specific specialist is recommended

### 🗺️ Find Nearby Healthcare
- Real-time location detection
- OpenStreetMap Overpass API integration
- Color-coded distance markers (< 2km = Green, 2-5km = Yellow, > 5km = Orange)
- Nearest hospital highlighting
- Estimated travel time
- Direct "Get Directions" to Google Maps

### 📜 Health History
- Local storage of all symptom assessments
- Searchable history with severity badges
- Individual delete and clear all options
- Confirmation dialogs for safety

### 🎨 Premium UI/UX
- Modern healthcare design system
- Smooth animations and transitions
- Loading states with professional indicators
- Error boundaries prevent crashes
- Mobile-responsive design
- Bilingual support (English/Hindi)

## Quick Start

### Prerequisites
- Node.js 18+ and yarn
- Python 3.11+
- MongoDB (local or remote)
- Emergent LLM Key (for AI features)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd arogya-ai
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
yarn install
```

4. **Environment Configuration**

Create `/backend/.env`:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
CORS_ORIGINS=*
JWT_SECRET=your-super-secret-jwt-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=10080
EMERGENT_LLM_KEY=sk-emergent-your-key-here
DEMO_USER_EMAIL=demo@arogyaai.app
DEMO_USER_PASSWORD=Arogya123!
```

Create `/frontend/.env`:
```env
REACT_APP_BACKEND_URL=
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false
```

5. **Start the Application**

Terminal 1 (Backend):
```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

Terminal 2 (Frontend):
```bash
cd frontend
yarn dev
```

6. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

### Demo Account
- Email: `demo@arogyaai.app`
- Password: `Arogya123!`

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
