const express = require('express');
const path = require('path');
const http = require('http');

const app = express();
const PORT = process.env.PORT || 8080;

// Simple health check route for confirming the server is running
app.get('/healthz', (req, res) => {
  res.json({ status: 'ok', message: 'Server is running', port: PORT });
});

// API forwarding to Flask backend
app.use('/api', (req, res) => {
  console.log(`Proxying request to: ${req.url}`);
  
  // Parse body data if content-type is JSON
  let body = [];
  req.on('data', (chunk) => {
    body.push(chunk);
  });
  
  req.on('end', () => {
    body = Buffer.concat(body).toString();
    
    // Remove any auth tokens or similar headers that might cause issues
    const headers = {...req.headers};
    delete headers.host;
    
    const options = {
      hostname: '127.0.0.1',
      port: 5000,
      path: `/api${req.url}`,
      method: req.method,
      headers: headers
    };
    
    console.log(`Forwarding to: ${options.hostname}:${options.port}${options.path}`);

    const proxyReq = http.request(options, (proxyRes) => {
      console.log(`Got response from backend: ${proxyRes.statusCode}`);
      res.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(res);
    });

    proxyReq.on('error', (e) => {
      console.error(`Problem with request: ${e.message}`);
      res.status(500).send(`Backend server error: ${e.message}`);
    });

    if (req.method !== 'GET' && req.method !== 'HEAD' && body.length > 0) {
      proxyReq.write(body);
    }
    
    proxyReq.end();
  });
});

// In development mode, proxy to the React dev server
// Use proxy middleware for frontend
const { createProxyMiddleware } = require('http-proxy-middleware');

// Setup proxy to React dev server (in development)
const frontendDevUrl = 'http://localhost:3000';
console.log(`Proxying frontend requests to: ${frontendDevUrl}`);

// Proxy all non-API, non-healthz requests to the frontend
app.use('/', 
  createProxyMiddleware({
    target: frontendDevUrl,
    changeOrigin: true,
    ws: true, // Also proxy websockets for HMR
    pathFilter: (path) => {
      // Don't proxy API or health check requests
      return !path.startsWith('/api') && path !== '/healthz';
    },
    logLevel: 'debug',
    onError: (err, req, res) => {
      // If the frontend dev server is not available, show a friendly message
      console.error('Error connecting to frontend dev server:', err.message);
      res.status(503).send(`
        <html>
          <head>
            <title>Frontend Development Server Unavailable</title>
            <style>
              body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }
              .error { color: #721c24; background-color: #f8d7da; padding: 15px; border-radius: 4px; }
              h1 { color: #0066cc; }
              code { background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            </style>
          </head>
          <body>
            <h1>Frontend Development Server Unavailable</h1>
            <div class="error">
              <p>The frontend development server is not responding. This could be because:</p>
              <ul>
                <li>The React development server isn't running on port 3000</li>
                <li>There's a network configuration issue</li>
              </ul>
            </div>
            <p>Please ensure the frontend development server is running with: <code>cd frontend && npm run dev</code></p>
          </body>
        </html>
      `);
    }
  })
);

// Create HTTP server
const server = http.createServer(app);

// Add WebSocket proxy for Socket.IO with enhanced debugging and reliability
const { createProxyServer } = require('http-proxy');
const socketProxy = createProxyServer({
  target: 'http://127.0.0.1:5000',
  ws: true,
  changeOrigin: true,
  secure: false,
  // Set longer timeout for WebSocket connections
  timeout: 120000, // 2 minutes
});

// Listen for upgrade events (WebSocket)
server.on('upgrade', (req, socket, head) => {
  console.log(`Proxying websocket connection for: ${req.url}`);
  
  // Set socket timeout to prevent premature disconnects
  socket.setTimeout(0);
  socket.setKeepAlive(true, 0);
  
  // Add special handling based on URL path
  if (req.url.startsWith('/socket.io/')) {
    console.log('Socket.IO connection detected');
  } else if (req.url.startsWith('/ws')) {
    console.log('Custom WebSocket connection detected');
  }
  
  // Proxy the WebSocket connection
  socketProxy.ws(req, socket, head, {
    // Additional options for specific WebSocket request if needed
  }, (err) => {
    if (err) {
      console.error('WebSocket proxy error during setup:', err);
      socket.end();
    }
  });
});

// Handle various proxy events
socketProxy.on('error', (err, req, res) => {
  console.error('Proxy error:', err);
  // Handle socket errors in a non-HTTP context
  if (!res || !res.writeHead) {
    console.error('WebSocket proxy error (socket):', err);
    if (req && req.socket && !req.socket.destroyed) {
      req.socket.end();
    }
    return;
  }
  
  // Handle HTTP errors
  res.writeHead(500, { 'Content-Type': 'text/plain' });
  res.end('Proxy error');
});

// Log when proxy opens a connection
socketProxy.on('open', (proxySocket) => {
  console.log('Proxy target connection opened');
  
  // Handle proxy socket errors
  proxySocket.on('error', (err) => {
    console.error('Target connection error:', err);
  });
});

// Log when proxy closes a connection
socketProxy.on('close', (req, proxyRes, proxySocket) => {
  console.log('Proxy target connection closed');
});

// Start server and listen
server.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running at http://0.0.0.0:${PORT}`);
});