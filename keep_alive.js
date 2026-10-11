#!/usr/bin/env node
/**
 * Render Backend Keep-Alive Pinger
 * 
 * Render's free tier spins down after 15 minutes of inactivity.
 * This script sends a lightweight HTTP GET request every 10 minutes
 * to keep your FastAPI backend awake 24/7.
 * 
 * Usage:
 *   node keep_alive.js <YOUR_RENDER_URL>
 * 
 * Example:
 *   node keep_alive.js https://quantum-crop-api.onrender.com
 */

const https = require('https');
const http = require('http');

// Read URL from command line argument, environment variable, or prompt
const targetUrl = process.argv[2] || process.env.BACKEND_URL;

if (!targetUrl) {
  console.error('\x1b[31m[ERROR]\x1b[0m Please provide your Render URL.');
  console.log('Usage: node keep_alive.js https://your-backend-url.onrender.com\n');
  process.exit(1);
}

// Clean URL: ensure protocol and target endpoint (use /docs since FastAPI serves it by default)
let baseUrl = targetUrl.replace(/\/+$/, '');
if (!baseUrl.startsWith('http://') && !baseUrl.startsWith('https://')) {
  baseUrl = 'https://' + baseUrl;
}
const pingEndpoint = `${baseUrl}/docs`;

// Render Web Service Health Check: Render requires all Web Services to listen on process.env.PORT.
// Without this server listening on PORT, Render stays "In progress" and times out.
const PORT = process.env.PORT || 3000;
const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    status: 'active',
    service: 'Render Keep-Alive Daemon',
    target: pingEndpoint,
    uptime_seconds: Math.floor(process.uptime())
  }));
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[Health Server] Listening on port ${PORT} (Render port binding satisfied)`);
});

// Interval in milliseconds (10 minutes = 600,000 ms; Render sleeps at 15 mins)
const INTERVAL_MS = 10 * 60 * 1000;

function formatTime() {
  return new Date().toLocaleTimeString('en-US', { hour12: false });
}

function ping() {
  const startTime = Date.now();
  const client = pingEndpoint.startsWith('https') ? https : http;

  console.log(`\x1b[36m[${formatTime()}]\x1b[0m Pinging ${pingEndpoint}...`);

  const req = client.get(pingEndpoint, (res) => {
    const latency = Date.now() - startTime;
    if (res.statusCode >= 200 && res.statusCode < 400) {
      console.log(`\x1b[32m[${formatTime()}] SUCCESS:\x1b[0m Status ${res.statusCode} | Latency: ${latency}ms | Backend is AWAKE.`);
    } else {
      console.log(`\x1b[33m[${formatTime()}] WARNING:\x1b[0m Received status ${res.statusCode} | Latency: ${latency}ms (Server woke up but returned non-200).`);
    }
    // Consume response data to free up memory
    res.resume();
  });

  req.on('error', (err) => {
    console.error(`\x1b[31m[${formatTime()}] FAILED:\x1b[0m ${err.message} (Server may be booting up or unreachable).`);
  });

  req.setTimeout(30000, () => {
    console.warn(`\x1b[33m[${formatTime()}] TIMEOUT:\x1b[0m Request took over 30s (Backend was likely asleep and is waking up).`);
    req.destroy();
  });
}

console.log('='.repeat(65));
console.log('   RENDER BACKEND KEEP-ALIVE DAEMON');
console.log('='.repeat(65));
console.log(`Target:   ${pingEndpoint}`);
console.log(`Interval: Every 10 minutes`);
console.log(`Status:   Running... (Press Ctrl+C to stop)`);
console.log('='.repeat(65));

// Initial immediate ping
ping();

// Periodic ping
setInterval(ping, INTERVAL_MS);
