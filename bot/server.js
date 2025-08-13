#!/usr/bin/env node
/**
 * Wikipedia Path Finder - Express API Server
 * 
 * Provides a RESTful API for the Wikipedia pathfinding bot with proper
 * error handling, request validation, and CORS support.
 * 
 * @author Gildian Gonzales
 * @license MIT
 */

const express = require("express");
const { spawn } = require("child_process");
const fs = require('fs').promises;
const path = require('path');
const colors = require("colors");
const cors = require('cors');

// Configuration
const PORT = process.env.PORT || 4000;
const BOT_FILE = 'main.py';
const BOT_DATA_PATH = './path.json';
const REQUEST_TIMEOUT = 180000; // 3 minutes
const PYTHON_EXECUTABLE = process.env.PYTHON_PATH || path.join(__dirname, '..', '.venv', 'bin', 'python');

// Initialize Express app
const app = express();

// Middleware
app.use(cors({
    origin: process.env.NODE_ENV === 'production' 
        ? ['https://your-domain.com'] 
        : ['http://localhost:5173', 'http://localhost:3000'],
    credentials: true
}));

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Request logging middleware
app.use((req, res, next) => {
    const timestamp = new Date().toISOString();
    console.log(`${timestamp} ${req.method} ${req.path}`.cyan);
    next();
});

// Validation middleware
const validateSearchRequest = (req, res, next) => {
    const { isRandom, startArticle, endArticle, algo } = req.body;
    
    // Validate algorithm
    const validAlgorithms = ['best_first_search', 'depth_first_search'];
    if (algo && !validAlgorithms.includes(algo)) {
        return res.status(400).json({
            error: 'Invalid algorithm',
            valid_algorithms: validAlgorithms
        });
    }
    
    // Validate articles for non-random searches
    if (!isRandom) {
        if (!startArticle || !endArticle) {
            return res.status(400).json({
                error: 'Start and end articles are required for non-random searches'
            });
        }
        
        if (typeof startArticle !== 'string' || typeof endArticle !== 'string') {
            return res.status(400).json({
                error: 'Article names must be strings'
            });
        }
        
        if (startArticle.trim().length === 0 || endArticle.trim().length === 0) {
            return res.status(400).json({
                error: 'Article names cannot be empty'
            });
        }
    }
    
    next();
};

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
    });
});

// API documentation endpoint
app.get('/api', (req, res) => {
    res.json({
        title: 'Wikipedia Path Finder API',
        version: '1.0.0',
        endpoints: {
            'POST /': {
                description: 'Find path between Wikipedia articles',
                parameters: {
                    isRandom: 'boolean - Use random articles (default: true)',
                    startArticle: 'string - Starting article (required if not random)',
                    endArticle: 'string - Target article (required if not random)', 
                    algo: 'string - Algorithm to use (best_first_search or depth_first_search)'
                },
                example: {
                    isRandom: false,
                    startArticle: 'Python (programming language)',
                    endArticle: 'Machine learning',
                    algo: 'best_first_search'
                }
            },
            'GET /health': {
                description: 'Health check endpoint'
            }
        }
    });
});

// Main search endpoint
app.post("/", validateSearchRequest, async (req, res) => {
    const startTime = Date.now();
    const { isRandom = true, startArticle, endArticle, algo = 'best_first_search' } = req.body;
    
    // Build command arguments
    const args = [BOT_FILE, '--client'];
    
    if (isRandom) {
        args.push('random');
    } else {
        args.push(startArticle.trim(), endArticle.trim());
    }
    
    args.push(algo);
    
    console.log(`🚀 Starting search with args: ${args.join(' ')}`.green);
    
    // Set up timeout
    const timeout = setTimeout(() => {
        console.log('⏰ Request timeout'.red);
        if (!res.headersSent) {
            res.status(408).json({
                error: 'Request timeout',
                message: `Search exceeded ${REQUEST_TIMEOUT / 1000} seconds`
            });
        }
    }, REQUEST_TIMEOUT);
    
    try {
        // Spawn Python process
        const wikiBot = spawn(PYTHON_EXECUTABLE, args, {
            cwd: __dirname,
            stdio: ['ignore', 'pipe', 'pipe']
        });
        
        let stdout = '';
        let stderr = '';
        
        // Collect output
        wikiBot.stdout.on('data', (data) => {
            const dataString = data.toString();
            stdout += dataString;
            
            // Log interesting output (not just spinner characters)
            if (dataString.length > 2 && 
                (dataString.includes('Finding') || dataString.includes('Error') || 
                 dataString.includes('Processing') || dataString.includes('Goal'))) {
                console.log(`Bot: ${dataString.trim()}`.yellow);
            }
        });
        
        wikiBot.stderr.on('data', (data) => {
            stderr += data.toString();
            console.error(`Bot Error: ${data.toString().trim()}`.red);
        });
        
        // Handle process completion
        wikiBot.on('close', async (code) => {
            clearTimeout(timeout);
            
            if (res.headersSent) {
                return; // Response already sent (timeout)
            }
            
            const duration = Date.now() - startTime;
            console.log(`🏁 Bot process completed with code ${code} in ${duration}ms`.cyan);
            
            try {
                if (code !== 0) {
                    throw new Error(`Bot process failed with code ${code}\nStderr: ${stderr}`);
                }
                
                // Read results
                const jsonData = await fs.readFile(path.join(__dirname, BOT_DATA_PATH), 'utf8');
                const botData = JSON.parse(jsonData);
                
                // Add metadata
                botData.metadata = {
                    duration_ms: duration,
                    timestamp: new Date().toISOString(),
                    algorithm_used: algo,
                    random_search: isRandom
                };
                
                console.log(`✅ Search completed: ${botData.start} → ${botData.end}`.green);
                console.log(`📊 Results: ${botData.results.length} algorithm(s), ${duration}ms`.green);
                
                res.status(200).json(botData);
                
            } catch (error) {
                console.error(`❌ Error reading results: ${error.message}`.red);
                res.status(500).json({
                    error: 'Failed to read search results',
                    details: error.message,
                    stdout: stdout,
                    stderr: stderr
                });
            }
        });
        
        // Handle process errors
        wikiBot.on('error', (error) => {
            clearTimeout(timeout);
            
            if (!res.headersSent) {
                console.error(`❌ Failed to start bot process: ${error.message}`.red);
                res.status(500).json({
                    error: 'Failed to start search process',
                    details: error.message
                });
            }
        });
        
    } catch (error) {
        clearTimeout(timeout);
        
        if (!res.headersSent) {
            console.error(`❌ Unexpected error: ${error.message}`.red);
            res.status(500).json({
                error: 'Internal server error',
                details: error.message
            });
        }
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(`❌ Unhandled error: ${err.message}`.red);
    console.error(err.stack);
    
    if (!res.headersSent) {
        res.status(500).json({
            error: 'Internal server error',
            message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
        });
    }
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Not Found',
        message: `Endpoint ${req.method} ${req.path} not found`,
        available_endpoints: ['GET /health', 'GET /api', 'POST /']
    });
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Received SIGINT, shutting down gracefully...'.yellow);
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Received SIGTERM, shutting down gracefully...'.yellow);
    process.exit(0);
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Wikipedia Path Finder API running on port ${PORT}`.magenta);
    console.log(`📖 API documentation: http://localhost:${PORT}/api`.cyan);
    console.log(`❤️  Health check: http://localhost:${PORT}/health`.cyan);
    console.log(`🔍 Environment: ${process.env.NODE_ENV || 'development'}`.cyan);
});
