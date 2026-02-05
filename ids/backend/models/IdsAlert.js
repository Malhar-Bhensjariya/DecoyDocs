const mongoose = require('mongoose');

const idsAlertSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  username: {
    type: String,
    required: true
  },
  anomalyScore: {
    type: Number,
    required: true
  },
  threshold: {
    type: Number,
    required: true
  },
  mouseEvents: [{
    eventType: String,
    x: Number,
    y: Number,
    timestamp: String,
    epoch: Number,
    movementId: String
  }],
  sessionId: {
    type: String,
    required: true
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  status: {
    type: String,
    enum: ['detected', 'investigating', 'resolved'],
    default: 'detected'
  }
});

module.exports = mongoose.model('IdsAlert', idsAlertSchema);