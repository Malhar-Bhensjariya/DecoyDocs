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

      // Try to access DecoyDocs after 10 seconds (should be blocked for regular user)
      setTimeout(async () => {
        console.log('🤖 Bot: Attempting to access DecoyDocs (should be blocked)...');

        try {
          const decoyResponse = await fetch(`${SERVER_URL}/api/decoydocs`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (decoyResponse.status === 403) {
            console.log('🤖 Bot: Access denied to DecoyDocs (expected for regular user)');
          } else {
            console.log('🤖 Bot: Unexpected access to DecoyDocs!');
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