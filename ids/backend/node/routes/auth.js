const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');

const router = express.Router();

// Initialize default users (run once)
router.post('/init', async (req, res) => {
  try {
    // Create admin user
    const adminExists = await User.findOne({ username: 'admin' });
    if (!adminExists) {
      const hashedPassword = await bcrypt.hash('admin123', 10);
      const admin = new User({
        username: 'admin',
        password: hashedPassword,
        role: 'admin'
      });
      await admin.save();
    }

    // Create regular user
    const userExists = await User.findOne({ username: 'user' });
    if (!userExists) {
      const hashedPassword = await bcrypt.hash('user123', 10);
      const user = new User({
        username: 'user',
        password: hashedPassword,
        role: 'user'
      });
      await user.save();
    }

    res.json({ message: 'Default users initialized' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Login route
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    // Find user
    const user = await User.findOne({ username });
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Check password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Generate JWT token
    const token = jwt.sign(
      { userId: user._id, username: user.username, role: user.role },
      process.env.JWT_SECRET || 'your-secret-key',
      { expiresIn: '24h' }
    );

    res.json({
      token,
      user: {
        id: user._id,
        username: user.username,
        role: user.role
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Middleware to verify JWT token (original behavior)
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key', (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.user = user;
    next();
  });
};

// Middleware variant: allow request to continue but mark for decoy if token missing/invalid
// Use this for routes where attackers should be silently diverted to decoy content.
const authenticateTokenAllowDecoy = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    // do NOT send 401 here — mark as "decoy candidate" and continue
    req.user = null;
    req._decoyCandidate = true;
    return next();
  }

  jwt.verify(token, process.env.JWT_SECRET || 'your-secret-key', (err, user) => {
    if (err) {
      // invalid token -> treat as potential bypass attempt
      req.user = null;
      req._decoyCandidate = true;
      return next();
    }
    req.user = user;
    next();
  });
};

// Middleware to check admin role (strict)
const requireAdmin = (req, res, next) => {
  if (!req.user || req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Admin access required' });
  }
  next();
};

// Middleware: if user is not admin, serve decoy responses instead of returning 403.
// This keeps attackers inside the deceptive layer while legitimate admins still work normally.
const { isSuspicious } = require('../utils/suspicion');
const path = require('path');
const fs = require('fs').promises;

const requireAdminOrDecoy = async (req, res, next) => {
  // If authenticated admin -> proceed normally
  if (req.user && req.user.role === 'admin') {
    return next();
  }

  // If the user was explicitly flagged suspicious (IDS) or token looked tampered -> serve decoy
  const username = req.user?.username || req.headers['x-username'] || null;
  const flagged = isSuspicious(username) || req._decoyCandidate || req.headers['x-force-decoy'] === '1';

  if (!flagged) {
    // Not suspicious — return normal 403 so regular users still see access denied
    return res.status(403).json({ error: 'Admin access required' });
  }

  // Serve decoy response depending on the requested resource
  // - For DecoyDocs list/details: return the decoy docs (from storage)
  // - For IDS alerts: return a believable, fake alerts list
  // - Otherwise: respond with a generic decoy payload
  try {
    if (req.path.startsWith('/')) {
      // route context: check the originalUrl to choose response
      if (req.baseUrl && req.baseUrl.includes('decoydocs')) {
        // Return the same shape as the real decoydocs list endpoint
        const STORAGE_DIR = path.join(__dirname, '../../storage');
        for (const file of files) {
          if (file.endsWith('.json')) {
            const filePath = path.join(STORAGE_DIR, file);
            const content = await fs.readFile(filePath, 'utf8');
            const docData = JSON.parse(content);
            decoyDocs.push({
              id: docData.id,
              title: docData.title,
              createdAt: docData.createdAt,
              status: docData.status,
              filePath: docData.filePath
            });
          }
        }
        res.set('X-Decoy', '1');
        return res.json(decoyDocs);
      }

      if (req.baseUrl && req.baseUrl.includes('ids') && req.path.startsWith('/alerts')) {
        // Fake alerts for attacker to browse
        const fakeAlerts = [
          { _id: 'a1', username: 'finance_user', anomalyScore: 0.72, threshold: 0.8, status: 'detected', timestamp: new Date() },
          { _id: 'a2', username: 'contract_admin', anomalyScore: 0.65, threshold: 0.8, status: 'investigating', timestamp: new Date() }
        ];
        res.set('X-Decoy', '1');
        return res.json(fakeAlerts);
      }
    }

    // Generic decoy fallback
    res.set('X-Decoy', '1');
    return res.json({ message: 'Resource not found', decoy: true });
  } catch (err) {
    console.error('Error serving decoy response:', err.message);
    return res.status(500).json({ error: 'Internal server error' });
  }
};

// Get current user info
router.get('/me', authenticateToken, async (req, res) => {
  try {
    const user = await User.findById(req.user.userId).select('-password');

    // If this user is currently flagged suspicious in memory, signal client to render decoy UI
    try {
      const { isSuspicious } = require('../utils/suspicion');
      if (isSuspicious(user.username)) {
        res.set('X-Decoy', '1');
      }
    } catch (err) {
      // non-fatal: continue without header
      console.warn('Could not check suspicion state:', err.message);
    }

    res.json(user);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = { router, authenticateToken, authenticateTokenAllowDecoy, requireAdmin, requireAdminOrDecoy };