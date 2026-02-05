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

## Attack Simulation

Run the attack bot to test IDS detection:

```bash
cd ids/backend
node bot/attack-bot.js
```

The bot will:
- Login as a regular user
- Send perfectly linear mouse movements (highly suspicious)
- Attempt to access DecoyDocs (should be blocked)

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