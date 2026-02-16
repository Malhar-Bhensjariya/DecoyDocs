// Simple in-memory suspicious user tracker (TTL-based)
// Used by IDS socket handler and auth middleware to decide when to serve decoy content.

const suspicious = new Map(); // username -> expiryTimestamp (ms)

const DEFAULT_TTL_MS = 5 * 60 * 1000; // 5 minutes

function markSuspicious(username, ttlMs = DEFAULT_TTL_MS) {
  if (!username) return;
  const expiry = Date.now() + ttlMs;
  suspicious.set(username, expiry);
}

function isSuspicious(username) {
  if (!username) return false;
  const expiry = suspicious.get(username);
  if (!expiry) return false;
  if (Date.now() > expiry) {
    suspicious.delete(username);
    return false;
  }
  return true;
}

function clearSuspicion(username) {
  suspicious.delete(username);
}

module.exports = { markSuspicious, isSuspicious, clearSuspicion };
