// Wrapper to maintain backward compatibility when starting server from ids/backend
// Delegates to the actual Node server implementation located in ./node/index.js

try {
  require('./node/index.js');
} catch (err) {
  console.error('Failed to start Node backend from ids/backend/index.js:', err.message);
  process.exit(1);
}
