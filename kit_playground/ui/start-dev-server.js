#!/usr/bin/env node
/**
 * Wrapper script for react-scripts start with proper error handling
 * Handles ECONNRESET and other socket errors gracefully without crashing
 *
 * This script is automatically invoked by:
 * - `make playground` (via dev.sh/dev.bat → npm start)
 * - `npm start` in the kit_playground/ui directory
 *
 * It prevents the development server from crashing when clients disconnect
 * abruptly (browser tab closes, network issues, etc.)
 */

// Install global error handlers before starting the server
process.on('uncaughtException', (err) => {
  // Handle connection reset errors gracefully - these are expected when clients disconnect
  if (err.code === 'ECONNRESET' || err.code === 'EPIPE' || err.code === 'ECONNABORTED') {
    console.log(`[${new Date().toISOString()}] Connection closed by client (${err.code})`);
    return;
  }

  // For other uncaught exceptions, log and continue (don't crash the server)
  console.error('[UNCAUGHT EXCEPTION]', err);
  console.error('Server continuing to run...');
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('[UNHANDLED REJECTION]', reason);
  console.error('Server continuing to run...');
});

// Patch the http and https modules to add error handlers to all sockets
const http = require('http');
const https = require('https');

const originalHttpCreateServer = http.createServer;
const originalHttpsCreateServer = https.createServer;

function wrapServer(server) {
  server.on('connection', (socket) => {
    // Add error handler to prevent crashes from socket errors
    socket.on('error', (err) => {
      if (err.code === 'ECONNRESET' || err.code === 'EPIPE' || err.code === 'ECONNABORTED') {
        // These are normal when clients disconnect - just log at debug level
        console.log(`[${new Date().toISOString()}] Socket error (${err.code}) - client disconnected`);
      } else {
        console.error('Socket error:', err.code || err.message);
      }
    });
  });
  return server;
}

http.createServer = function(...args) {
  const server = originalHttpCreateServer.apply(this, args);
  return wrapServer(server);
};

https.createServer = function(...args) {
  const server = originalHttpsCreateServer.apply(this, args);
  return wrapServer(server);
};

// Now start react-scripts
console.log('Starting development server with enhanced error handling...');
require('react-scripts/scripts/start');
