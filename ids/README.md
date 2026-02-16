# IDS (Intrusion Detection System) - Academic Project

A web-based behavioral biometrics IDS with honeypot deception capabilities.

## Features

- **User Authentication**: JWT-based login with role-based access (admin/user)
- **Mouse Tracking**: Real-time behavioral biometrics collection
- **Anomaly Detection**: ML-powered analysis of mouse movement patterns
- **DecoyDocs Integration**: Honeypot documents for suspicious users
- **Attack Simulation**: Automated bot for testing IDS effectiveness

## Tech Stack

### Frontend
- React 19 + Vite
- Tailwind CSS
- Socket.IO Client
- React Router

### Backend
- Node.js + Express
- Socket.IO Server
- MongoDB + Mongoose
- JWT Authentication
- bcryptjs

## Setup Instructions

### 1. Backend Setup

```bash
cd ids/backend
npm install
```

Create `.env` file:
```
MONGODB_URL=mongodb+srv://malhar:lemon@123@cluster0.e21hq8f.mongodb.net/?appName=Cluster0
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
PORT=3001
```

Initialize default users:
```bash
npm run init-users
```

Start backend:
```bash
npm start
```

### 2. Frontend Setup

```bash
cd ids/frontend
npm install
npm run dev
```

### 3. MongoDB Setup

The application uses MongoDB Atlas. Make sure your connection string is correct in the `.env` file.

## Default Credentials

- **Admin**: `admin` / `admin123`
- **User**: `user` / `user123`

## Usage

1. Start the backend server
2. Start the frontend development server
3. Login with admin or user credentials
4. Mouse movements are automatically tracked and sent to the backend
5. Admin can view IDS alerts and manage DecoyDocs
6. Use the attack bot to simulate suspicious behavior

## Deceptive layer (honeypot) & Attack Simulation

We added a second, *deceptive* application layer that keeps suspicious actors inside a believable, read‑only frontend and returns plausible API responses instead of revealing authorization failures.

Key implementation details
- Detection & marking
  - Lightweight heuristic runs in the Socket.IO mouse-event handler (`ids/backend/index.js`). Suspicious mouse batches (highly regular timing) create an IDS alert and mark the username as suspicious in memory (`ids/backend/utils/suspicion.js`, TTL default 5 minutes).
  - The suspicion map is intentionally in-memory for fast responsiveness; see the Developer Notes below to persist it.

- Middleware behaviour
  - `authenticateTokenAllowDecoy` — accepts the request but marks it as a **decoy candidate** when token is missing/invalid (no immediate 401/403 sent).
  - `requireAdminOrDecoy` — used on admin-only routes; for flagged/decoy-candidate requests it returns realistic decoy payloads (and sets `X-Decoy: 1`) instead of a plain 403.
  - These keep attackers inside the deceptive surface while preserving normal access for legitimate admins.

- Real-time client diversion
  - Server emits a `force-decoy` Socket.IO event to a connected client when it is flagged; clients listen and immediately redirect to the deceptive UI.
  - Responses containing decoy payloads include header `X-Decoy: 1` so operators / tests can detect diversion.

- Frontend behaviour
  - `AuthContext` watches responses for `X-Decoy` and exposes `isDecoy` to the app.
  - `ProtectedRoute` silently redirects flagged sessions to `/decoy` (no warning shown to the user).
  - `MouseTracker` listens for `force-decoy` and forces a client-side redirect to `/decoy`.
  - New route: `/decoy` shows the deceptive, read‑only UI (`src/pages/DecoyLanding.jsx`).

How to test the decoy flow
1. Start backend and frontend (see Setup Instructions).
2. Login as regular user (`user` / `user123`) in the frontend.
3. Run the attack bot to simulate perfect robotic mouse movement:
   ```bash
   cd ids/backend
   node bot/attack-bot.js
   ```
4. Expected behavior:
   - Backend saves an IDS alert and marks the session suspicious.
   - Server emits `force-decoy`; the client is redirected to `/decoy`.
   - API responses for admin-only endpoints (e.g. `GET /api/decoydocs`) will return decoy payloads and include header `X-Decoy: 1`.
5. Manual override: send header `x-force-decoy: 1` to force decoy behaviour on a request.

Developer notes & config
- Suspicion TTL: `ids/backend/utils/suspicion.js` (DEFAULT_TTL_MS = 5min).
- Heuristic / alert creation: `ids/backend/index.js` (socket `mouse-events` handler).
- Middleware: see `ids/backend/routes/auth.js` (`authenticateTokenAllowDecoy`, `requireAdminOrDecoy`).
- Client-side redirect: `ids/frontend/src/components/MouseTracker.jsx` listens for `force-decoy` and `ids/frontend/src/contexts/AuthContext.jsx` handles `X-Decoy` header.

Design choices / fallbacks
- Decoy diversion is silent — attackers are not told they were redirected.
- Non-suspicious unauthorized requests still receive `403` as before.
- Current state is in-memory (fast); persisting flagged state and adding admin controls to view/clear flags is recommended as a next step.

## Project Structure

```
ids/
├── backend/
│   ├── models/          # MongoDB schemas
│   ├── routes/          # API endpoints
│   ├── bot/            # Attack simulation
│   ├── index.js        # Server entry point
│   └── .env           # Environment variables
└── frontend/
    ├── src/
    │   ├── components/ # Reusable components
    │   ├── contexts/  # React contexts
    │   ├── pages/     # Page components
    │   └── App.jsx    # Main app component
    └── tailwind.config.js
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/init` - Initialize default users

### IDS
- `GET /api/ids/alerts` - Get all alerts (admin only)
- `POST /api/ids/alert` - Create new alert
- `GET /api/ids/my-alerts` - Get user's alerts
- `PATCH /api/ids/alert/:id` - Update alert status

### DecoyDocs
- `GET /api/decoydocs` - List documents (admin only)
- `POST /api/decoydocs/create` - Create document (admin only)
- `GET /api/decoydocs/:id` - Get document details (admin only)

## Socket.IO Events

### Client → Server
- `mouse-events` - Batch of mouse movement data

### Server → Client
- Connection established with JWT authentication

## Security Notes

- JWT tokens are required for all protected routes
- Admin-only routes are protected by middleware
- Mouse tracking only occurs after successful login
- DecoyDocs are only accessible to admin users
- Attack simulation is contained and safe for academic use

## Academic Project Notes

This is a controlled simulation for educational purposes. The ML model for anomaly detection should be implemented by your teammates in the backend IDS processing logic.