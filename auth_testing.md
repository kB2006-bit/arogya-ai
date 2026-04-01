# Auth Testing Notes

## Demo Login Endpoint
- POST `/api/login`
- POST `/login`
- POST `/api/auth/login`
- GET `/api/auth/me`

## Demo Credentials
- Email: `demo@arogyaai.app`
- Password: `Arogya123!`

## Expected Responses
- Success: `{ "success": true, "token": "demo-token", "user": { "email": "demo@arogyaai.app" } }`
- Failure: `{ "success": false, "message": "Invalid credentials" }`

## Quick Checks
- Invalid credentials should show the backend error message in the login form.
- Valid credentials should store `demo-token` in localStorage and redirect to `/dashboard`.
- Protected routes should continue working with `demo-token`.
- `/api/auth/login` should also set an `access_token` httpOnly cookie.
- Repeated invalid `/api/auth/login` attempts should lock the login flow temporarily.