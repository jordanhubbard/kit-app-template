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

// Add webpack hooks for hot-reload notifications
// This needs to run before react-scripts starts
const webpack = require('webpack');
const originalRun = webpack.Compiler.prototype.run;
const originalWatch = webpack.Compiler.prototype.watch;

let isFirstCompile = true;

// Hook into webpack compiler to detect recompilation
webpack.Compiler.prototype.watch = function(...args) {
  this.hooks.watchRun.tap('HotReloadNotifier', (compiler) => {
    if (!isFirstCompile) {
      const timestamp = new Date().toLocaleString();
      console.log('\n' + '='.repeat(60));
      console.log(`🔄 FRONTEND HOT-RELOAD at ${timestamp}`);
      console.log('   Frontend code changes detected and recompiling...');
      console.log('='.repeat(60) + '\n');
    }
  });

  this.hooks.done.tap('HotReloadNotifier', (stats) => {
    if (!isFirstCompile) {
      const timestamp = new Date().toLocaleString();
      const duration = stats.endTime - stats.startTime;
      console.log('\n' + '='.repeat(60));
      console.log(`✅ FRONTEND RELOAD COMPLETE at ${timestamp}`);
      console.log(`   Compilation finished in ${duration}ms`);
      console.log('='.repeat(60) + '\n');
    }
    isFirstCompile = false;
  });

  return originalWatch.apply(this, args);
};

// Now start react-scripts
console.log('Starting development server with enhanced error handling...');
require('react-scripts/scripts/start');
