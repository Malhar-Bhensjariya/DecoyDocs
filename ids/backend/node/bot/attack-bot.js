const io = require('socket.io-client');

// Configuration
const SERVER_URL = 'http://localhost:3001';
const TEST_USERNAME = 'user'; // Use regular user account
const TEST_PASSWORD = 'user123';

// Simulate anomalous mouse behavior (perfect, robotic movements)
function generateAnomalousMouseEvents() {
  const events = [];
  const baseTime = Date.now();
  let movementId = 'bot_' + Math.random().toString(36).substr(2, 9);

  // Generate linear, constant-speed movements (very suspicious)
  for (let i = 0; i < 50; i++) {
    const timestamp = new Date(baseTime + (i * 40)).toISOString(); // Perfect 25fps timing
    const epoch = baseTime + (i * 40);

    // Linear movement from (100,100) to (800,600)
    const progress = i / 49;
    const x = Math.round(100 + (700 * progress));
    const y = Math.round(100 + (500 * progress));

    events.push({
      eventType: 'movement',
      x: x,
      y: y,
      timestamp: timestamp,
      epoch: epoch,
      movementId: movementId
    });
  }

  // Add some clicks at perfect intervals
  for (let i = 0; i < 5; i++) {
    const timestamp = new Date(baseTime + (1000 * (i + 1))).toISOString();
    const epoch = baseTime + (1000 * (i + 1));

    events.push({
      eventType: 'left_press',
      x: 400 + (i * 50),
      y: 300,
      timestamp: timestamp,
      epoch: epoch,
      movementId: movementId
    });

    events.push({
      eventType: 'left_release',
      x: 400 + (i * 50),
      y: 300,
      timestamp: timestamp.replace('T', 'T').replace(/\.\d{3}Z/, '.001Z'), // 1ms later
      epoch: epoch + 1,
      movementId: movementId
    });
  }

  return events;
}

async function loginAndAttack() {
  // Helper: fire a beacon URL and log outcome
  async function fireBeacon(url, label = '') {
    try {
      // Normalize relative URLs to the honeypot beacon base
      const BEACON_BASE = process.env.BEACON_BASE || 'http://localhost:5000';
      if (url.startsWith('/')) url = `${BEACON_BASE}${url}`;
      if (url.includes('localhost:3001')) url = url.replace('http://localhost:3001', BEACON_BASE);

      const resp = await fetch(url, { method: 'GET' });
      console.log(`    [BEACON] ${label || url} -> ${resp.status}`);
      return resp.ok;
    } catch (err) {
      console.log(`    [BEACON] ${label || url} -> ERROR: ${err.message}`);
      return false;
    }
  }

  try {
    console.log('🤖 Bot: Starting attack simulation...');

    // First, login to get JWT token
    const loginResponse = await fetch(`${SERVER_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: TEST_USERNAME,
        password: TEST_PASSWORD
      })
    });

    if (!loginResponse.ok) {
      throw new Error('Login failed');
    }

    const loginData = await loginResponse.json();
    const token = loginData.token;

    console.log('🤖 Bot: Logged in successfully');

    // Connect to Socket.IO with authentication
    const socket = io(SERVER_URL, {
      auth: {
        token: token
      }
    });

    socket.on('connect', () => {
      console.log('🤖 Bot: Connected to IDS server');

      // Start sending anomalous mouse data every 2 seconds
      const interval = setInterval(() => {
        const mouseEvents = generateAnomalousMouseEvents();
        console.log(`🤖 Bot: Sending ${mouseEvents.length} anomalous mouse events`);

        socket.emit('mouse-events', mouseEvents);
      }, 2000);

      // Try to access DecoyDocs after 10 seconds — after anomalous mouse-events the user should be diverted to decoy content
      // After anomalous mouse-events, attempt to enumerate decoy docs and fire any embedded beacons
      setTimeout(async () => {
        console.log('🤖 Bot: Attempting to access DecoyDocs (expect DECoy content if flagged)...');

        try {
          const decoyResponse = await fetch(`${SERVER_URL}/api/decoydocs`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          const isDecoy = decoyResponse.headers.get('x-decoy') === '1';

          if (decoyResponse.ok && isDecoy) {
            console.log('🤖 Bot: Received DECoy content (user successfully diverted)');

            // Parse decoy list and look for beacon info
            const docs = await decoyResponse.json();
            for (const d of docs) {
              try {
                // Prefer beacon_urls exposed in the decoy listing
                if (d.beacon_urls) {
                  console.log(`    [+] Found beacon_urls for doc ${d.id || d.uuid}`);
                  for (const [k, url] of Object.entries(d.beacon_urls)) {
                    await fireBeacon(url, `${d.title || d.id} (${k})`);
                  }
                  continue;
                }

                // Fallback: attempt to GET metadata via download/json (may be admin-only)
                try {
                  const metaResp = await fetch(`${SERVER_URL}/api/decoydocs/${d.id}/download/json`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                  });
                  if (metaResp.ok) {
                    const meta = await metaResp.json();
                    if (meta.beacon) await fireBeacon(meta.beacon, `${d.title || d.id} (beacon)`);
                    if (meta.beacon_urls) {
                      for (const url of Object.values(meta.beacon_urls)) await fireBeacon(url, `${d.title || d.id} (beacon_urls)`);
                    }
                    continue; // done with this doc
                  }
                } catch (err) {
                  // ignore — try next discovery method
                }

                // Last-resort: construct reasonable beacon candidates using known patterns
                const BEACON_BASE = process.env.BEACON_BASE || 'http://localhost:5000';
                const candidates = [];
                if (d.uuid) {
                  candidates.push(`${BEACON_BASE}/api/beacon?resource_id=${encodeURIComponent(d.uuid)}`);
                }
                if (d.id) {
                  candidates.push(`${BEACON_BASE}/api/beacon?resource_id=${encodeURIComponent(d.id)}`);
                  candidates.push(`${BEACON_BASE}/fonts/inter-regular.woff2?resource_id=${encodeURIComponent(d.id)}`);
                  candidates.push(`${BEACON_BASE}/assets/media/logo.png?resource_id=${encodeURIComponent(d.id)}`);
                }
                for (const c of candidates) await fireBeacon(c, `${d.title || d.id} (candidate)`);

              } catch (err) {
                console.log('    [-] Error processing doc entry:', err && err.message ? err.message : err);
              }
            }

          } else if (decoyResponse.status === 403) {
            console.log('🤖 Bot: Access denied to DecoyDocs (regular user, not flagged)');
          } else {
            console.log('🤖 Bot: Unexpected response to DecoyDocs:', decoyResponse.status);
          }
        } catch (error) {
          console.log('🤖 Bot: Error accessing DecoyDocs:', error.message);
        }
      }, 10000);

      // Stop after 30 seconds
      setTimeout(() => {
        clearInterval(interval);
        socket.disconnect();
        console.log('🤖 Bot: Attack simulation complete');
        process.exit(0);
      }, 30000);
    });

    socket.on('disconnect', () => {
      console.log('🤖 Bot: Disconnected from server');
    });

    socket.on('force-decoy', (payload) => {
      console.log('🤖 Bot: Received force-decoy from server', payload);
    });

    socket.on('connect_error', (error) => {
      console.log('🤖 Bot: Connection error:', error.message);
    });

  } catch (error) {
    console.error('🤖 Bot: Error:', error.message);
    process.exit(1);
  }
}

// Run the attack simulation
loginAndAttack();