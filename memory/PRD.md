# ArogyaAI PRD

## Original Problem Statement
Build a production-ready full-stack web application called "ArogyaAI".

Tech Stack:
- Frontend: React (Vite) with Tailwind CSS
- Backend: Node.js with Express
- Database: Firebase Firestore
- Authentication: Firebase Auth
- AI Integration: Gemini API
- Maps: Google Maps API

Core Features:
1. User Authentication (Signup/Login with protected routes)
2. AI Symptom Checker
   - Chat interface (like WhatsApp)
   - User inputs symptoms
   - AI returns diagnosis + severity (Low/Medium/High)
3. Patient Dashboard
   - Stores history of symptoms and AI responses
4. Nearby Clinics
   - Google Maps integration showing nearby hospitals
5. Emergency SOS Button
   - Highlight when severity is high
6. Multilingual Support (English + Hindi basic)

Requirements:
- Clean folder structure (frontend + backend separate)
- Fully working API integration
- Environment variables setup
- Production-ready code (no placeholders)
- Proper error handling
- Responsive mobile-first UI

Output:
- Full project code (all files)
- Step-by-step setup instructions (VS Code)
- Commands to run frontend and backend
- API key setup guide (Firebase, Gemini, Maps)

Important:
- Keep it simple but complete
- Avoid unnecessary features
- Ensure everything runs without errors

## User Choices
- API keys available
- Use Emergent universal key for Gemini text generation
- Nearby clinics should use current location automatically
- Authentication should be email/password only
- English + Hindi toggle across main screens

## Architecture Decisions
- Implemented with the provided container starter architecture: React frontend + FastAPI backend + MongoDB.
- Used JWT-based email/password auth for protected routes and stable session handling.
- Used Gemini through the Emergent universal LLM key for live symptom triage responses.
- Stored users and symptom history in MongoDB for reliable persistence in the current environment.
- Implemented nearby clinic discovery with browser geolocation, backend nearby lookup, and Google Maps direction/open links.
- Added resilient clinic fallback results and staged loading feedback to avoid perceived hangs.

## User Personas
1. Patient needing quick first-step symptom guidance.
2. Returning user wanting to review past symptom assessments.
3. User under stress who needs a clear emergency path and nearby care quickly.
4. English/Hindi user preferring a simple, low-anxiety interface.

## Core Requirements
- Secure auth with protected routes
- WhatsApp-style symptom chat
- AI severity assessment with Low/Medium/High urgency
- History dashboard for past checks
- Nearby clinics using current location
- Emergency SOS action for high severity
- English/Hindi language toggle
- Responsive mobile-first UI
- Production-ready environment setup docs

## What Has Been Implemented
### 2026-04-01
- Built a complete bilingual landing, auth, dashboard, symptom chat, and nearby clinics experience.
- Added JWT signup/login, protected routes, and seeded demo access for testing.
- Integrated live Gemini symptom analysis with structured diagnosis, severity, next steps, and emergency messaging.
- Added MongoDB persistence for symptom history and dashboard severity summaries.
- Added nearby clinic lookup, Google Maps embed/direction links, emergency banner, and fallback search cards.
- Added English/Hindi copy system across the main app screens and polished Hindi clinic/chat wording.
- Added README setup instructions and test credentials memory file.
- Verified backend APIs with curl and automated pytest coverage; verified frontend flows with browser automation.
- Added a minimal demo-login compatibility fix: `/login` and `/api/login` now return `demo-token`, frontend login now uses the new demo endpoint, localhost CORS is explicitly enabled, and protected routes accept the demo token.
- Added an embedded dashboard symptom chat that replaces the old action card, calls the new `/api/analyze-symptoms` mock endpoint, shows user/AI chat bubbles, and displays a severity label without changing the overall dashboard layout.
- Replaced the dashboard chat mock with live Gemini analysis, kept a high-risk keyword override for chest pain/breathing/unconscious symptoms, and added a simple fallback response if Gemini is temporarily unavailable.
- Added lightweight per-user in-memory chat history storage for dashboard chats, merged that history into `/api/history`, and updated the dashboard Recent assessments section to show real User / AI / severity records with the newest items first.
- Added a simple dashboard Nearby Clinics section below chat using browser geolocation, a Google Maps embed view, and a new mocked `/api/clinics` endpoint returning 4 nearby clinic cards with names and coordinates.
- Added emergency alert behavior for High-severity symptom responses: `/api/analyze-symptoms` now returns an `emergency` flag, dashboard chat and history cards show a red emergency banner and red styling, and a visible SOS button now triggers an alert plus console log.
- Improved dashboard nearby clinics UX by moving the clinic list clearly below the map, adding approx distance labels plus “View on Map” actions that re-center the existing map on a selected clinic, and tightened navbar routing behavior for Home/Dashboard/Clinics with client-side navigation.
- Hardened `/api/auth/login` with httpOnly cookie support, login lockout after repeated failed attempts, and explicit in-app auth CORS handling while preserving the existing demo login flow.
- Cleaned the CRA frontend build setup for production by removing conflicting/unused packages, aligning React/date-fns versions for compatibility, fixing React hook warnings, adding Node 20 engine hints, generating `package-lock.json`, and verifying a clean production build with `npm run build`.
- Migrated the frontend build system from CRA/CRACO to Vite for more reliable Vercel deployment, added a Vite config with alias + `build` output targeting the `build` folder, switched the frontend to npm lockfile usage, added `frontend/vercel.json`, and verified the migrated app still loads correctly plus builds cleanly.
- Finalized frontend dependency resolution for Vercel by pinning `date-fns` to `^2.30.0`, deduping transitive installs via npm overrides, rebuilding the frontend from a clean npm install, removing yarn lockfile reliance, and clearing the remaining deployment blockers found during deployment analysis.
- Completed the Vite-only frontend cleanup by removing CRACO/Webpack remnants, deleting the old CRA entry files, switching the final Vite build output to `dist`, aligning `vercel.json` with the Vite output folder, and removing the last CRA-era env variable from `frontend/.env`.

## Prioritized Backlog
### P0
- None currently blocking the core user journey.

### P1
- Add profile settings so users can persist language preference to backend profile updates.
- Add richer clinic metadata (phone, specialty, open/closed status) from a premium provider.
- Add symptom chat conversation threading per session.

### P2
- Add downloadable visit summary / PDF.
- Add reminder nudges for follow-up symptoms.
- Add family member profiles and shared history views.

## Next Tasks List
- Add profile management and password reset flow.
- Expand multilingual coverage to more detailed medical guidance copy.
- Add analytics for common symptom categories and high-severity trends.
- Add clinic filters and speciality-based care discovery.
