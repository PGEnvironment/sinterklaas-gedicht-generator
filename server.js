const express = require('express');
const cors = require('cors');
const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Store SSE connections and poem data
const connections = new Map(); // session_id -> SSE response
const poemData = new Map(); // session_id -> { status, poem }

// SSE endpoint - Frontend connects here
app.get('/stream/:session_id', (req, res) => {
    const sessionId = req.params.session_id;
    
    // Set headers for SSE
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('Access-Control-Allow-Origin', '*');
    
    // Store connection
    connections.set(sessionId, res);
    
    // Send initial connection message
    res.write(`data: ${JSON.stringify({ status: 'connected' })}\n\n`);
    
    // Check if poem data already exists and send it
    if (poemData.has(sessionId)) {
        const data = poemData.get(sessionId);
        res.write(`data: ${JSON.stringify(data)}\n\n`);
        
        if (data.status === 'completed') {
            // Close connection if already completed
            connections.delete(sessionId);
            res.end();
            return;
        }
    }
    
    // Handle client disconnect
    req.on('close', () => {
        connections.delete(sessionId);
    });
});

// POST endpoint - n8n calls this when status changes to "generating"
app.post('/status/generating', (req, res) => {
    const { session_id } = req.body;
    
    if (!session_id) {
        return res.status(400).json({ error: 'session_id is required' });
    }
    
    // Update poem data
    poemData.set(session_id, {
        status: 'generating',
        session_id: session_id
    });
    
    // Send update to connected clients
    const connection = connections.get(session_id);
    if (connection) {
        connection.write(`data: ${JSON.stringify({
            status: 'generating',
            session_id: session_id
        })}\n\n`);
    }
    
    res.json({ success: true, message: 'Status updated to generating' });
});

// POST endpoint - n8n calls this when poem is completed
app.post('/status/completed', (req, res) => {
    const { session_id, poem } = req.body;
    
    if (!session_id || !poem) {
        return res.status(400).json({ error: 'session_id and poem are required' });
    }
    
    // Update poem data
    poemData.set(session_id, {
        status: 'completed',
        poem: poem,
        session_id: session_id
    });
    
    // Send update to connected clients
    const connection = connections.get(session_id);
    if (connection) {
        connection.write(`data: ${JSON.stringify({
            status: 'completed',
            poem: poem,
            session_id: session_id
        })}\n\n`);
        
        // Close connection after sending completed status
        connections.delete(session_id);
        connection.end();
    }
    
    res.json({ success: true, message: 'Poem completed and sent' });
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok', connections: connections.size, poems: poemData.size });
});

// Get port from environment or use default
const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

app.listen(PORT, HOST, () => {
    console.log(`Poem status server running on ${HOST}:${PORT}`);
    console.log(`SSE endpoint: /stream/:session_id`);
    console.log(`POST endpoints: /status/generating, /status/completed`);
});

