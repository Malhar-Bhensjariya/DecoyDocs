const express = require('express');
const IdsAlert = require('../models/IdsAlert');
const { authenticateToken, authenticateTokenAllowDecoy, requireAdmin, requireAdminOrDecoy } = require('./auth');

const router = express.Router();

// Get all IDS alerts (admin only — non-admin/suspicious users will receive decoy alerts)
router.get('/alerts', authenticateTokenAllowDecoy, requireAdminOrDecoy, async (req, res) => {
  try {
    const alerts = await IdsAlert.find()
      .populate('userId', 'username')
      .sort({ timestamp: -1 })
      .limit(50);
    res.json(alerts);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Create new IDS alert (called by IDS engine)
router.post('/alert', async (req, res) => {
  try {
    const { userId, username, anomalyScore, threshold, mouseEvents, sessionId } = req.body;

    const alert = new IdsAlert({
      userId,
      username,
      anomalyScore,
      threshold,
      mouseEvents,
      sessionId
    });

    await alert.save();
    res.status(201).json(alert);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get alerts for current user
router.get('/my-alerts', authenticateToken, async (req, res) => {
  try {
    const alerts = await IdsAlert.find({ userId: req.user.userId })
      .sort({ timestamp: -1 })
      .limit(10);
    res.json(alerts);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Update alert status (admin only — suspicious/non-admin requests will be diverted to decoy)
router.patch('/alert/:id', authenticateTokenAllowDecoy, requireAdminOrDecoy, async (req, res) => {
  try {
    const { status } = req.body;
    const alert = await IdsAlert.findByIdAndUpdate(
      req.params.id,
      { status },
      { new: true }
    );
    res.json(alert);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;