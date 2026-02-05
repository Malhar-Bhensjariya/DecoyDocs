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
  socket.on('mouse-events', (data) => {
    console.log(`  MOUSE TRACKING - User: ${socket.user?.username || 'Unknown'} (${socket.id})`);
    console.log(` Events received: ${data.length}`);
    console.log(` Sample event:`, JSON.stringify(data[0], null, 2));
    console.log(` Timestamp: ${new Date().toISOString()}`);
    console.log('─'.repeat(50));

    // Forward to IDS processing (will be implemented by teammates)
    // For now, just log the data
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