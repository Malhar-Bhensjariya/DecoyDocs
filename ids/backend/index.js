const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const jwt = require('jsonwebtoken');
const { router: authRoutes } = require('./routes/auth');
const idsRoutes = require('./routes/ids');
const decoyDocsRoutes = require('./routes/decoydocs');

// Load environment variables
dotenv.config();

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ],
    methods: ["GET", "POST", "PUT", "DELETE"]
  }
});

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/ids', idsRoutes);
app.use('/api/decoydocs', decoyDocsRoutes);

// Socket.IO authentication middleware
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  if (!token) {
    console.log('Socket connection rejected: No token provided');
    return next(new Error('Authentication error'));
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key');
    socket.user = decoded; // Attach decoded user info to socket
    console.log(`Socket authenticated for user: ${decoded.username}`);
    next();
  } catch (error) {
    console.log('Socket authentication failed:', error.message);
    next(new Error('Authentication error'));
  }
});

io.on('connection', (socket) => {
  console.log('User connected:', socket.id, '- User:', socket.user?.username || 'Unknown');

  // Handle mouse event batches
  socket.on('mouse-events', async (data) => {
    console.log(`  MOUSE TRACKING - User: ${socket.user?.username || 'Unknown'} (${socket.id})`);
    console.log(` Events received: ${data.length}`);
    console.log(` Sample event:`, JSON.stringify(data[0], null, 2));
    console.log(` Timestamp: ${new Date().toISOString()}`);
    console.log('─'.repeat(50));

    // Lightweight heuristic anomaly detection (placeholder for ML model):
    // - If a large batch (>=40) and very regular timing => mark suspicious
    try {
      const { markSuspicious } = require('./utils/suspicion');
      const IdsAlert = require('./models/IdsAlert');

      const events = Array.isArray(data) ? data : [];
      if (events.length >= 40) {
        // compute inter-event deltas (using epoch) and their std dev
        const epochs = events.map(e => e.epoch).filter(Boolean);
        if (epochs.length >= 2) {
          const deltas = [];
          for (let i = 1; i < epochs.length; i++) deltas.push(epochs[i] - epochs[i - 1]);
          const mean = deltas.reduce((s, v) => s + v, 0) / deltas.length;
          const variance = deltas.reduce((s, v) => s + Math.pow(v - mean, 2), 0) / deltas.length;
          const stddev = Math.sqrt(variance);

          // very low stddev + small mean (consistent perfect motion)
          if (stddev < 6 && mean >= 20 && mean <= 80) {
            const username = socket.user?.username || 'unknown';
            console.warn(`⚠️ Anomaly heuristic triggered for user=${username} (stddev=${stddev.toFixed(2)}ms)`);

            // create an IDS alert record
            try {
              const alert = new IdsAlert({
                userId: socket.user?.userId || null,
                username: username,
                anomalyScore: 0.99,
                threshold: 0.8,
                mouseEvents: events.slice(0, 200),
                sessionId: socket.id
              });
              await alert.save();
            } catch (saveErr) {
              console.error('Failed to save IDS alert:', saveErr.message);
            }

            // mark user as suspicious (TTL in memory)
            markSuspicious(username);

            // notify connected client socket to switch to decoy UI immediately
            try {
              socket.emit('force-decoy', { reason: 'anomaly', score: 0.99 });
            } catch (emitErr) {
              console.warn('Could not emit force-decoy to socket:', emitErr.message);
            }
          }
        }
      }
    } catch (err) {
      console.error('Error running anomaly heuristic:', err.message);
    }

    // Forward to IDS processing (ML pipeline will be integrated later)
  });

  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
  });
});

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URL || 'mongodb://localhost:27017/ids')
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB connection error:', err));

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = { io };