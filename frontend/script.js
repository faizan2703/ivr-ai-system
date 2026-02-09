/**
 * IVR AI Agent System - Frontend JavaScript
 */

// Configuration
const config = {
    apiEndpoint: localStorage.getItem('apiEndpoint') || 'http://localhost:8000',
    maxRetries: parseInt(localStorage.getItem('maxRetries') || '3'),
    timeout: parseInt(localStorage.getItem('timeout') || '30') * 1000,
};

// Global State
let currentCallId = null;
let callDurationInterval = null;
let callStartTime = null;
let allDocuments = [];

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('IVR AI Agent System loaded');
    checkBackendStatus();
    loadDashboardData();
    loadSettings();
    
    // Load knowledge base on startup
    loadKnowledgeBase();
});

// ============================================
// Section Navigation
// ============================================

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Remove active from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });

    // Show selected section
    document.getElementById(sectionId).classList.add('active');

    // Add active to clicked nav link
    event?.target?.classList.add('active');

    // Reload section-specific data
    if (sectionId === 'dashboard') {
        loadDashboardData();
    } else if (sectionId === 'knowledge') {
        loadKnowledgeBase();
    }
}

// ============================================
// API Helper Functions
// ============================================

async function apiCall(method, endpoint, data = null) {
    const url = `${config.apiEndpoint}${endpoint}`;
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        timeout: config.timeout
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`API Error [${method} ${endpoint}]:`, error);
        throw error;
    }
}

// ============================================
// Toast Notifications
// ============================================

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================
// Dashboard Functions
// ============================================

async function loadDashboardData() {
    try {
        // Check health
        const health = await apiCall('GET', '/api/v1/health');
        const status = health.services.api === 'running' ? 'Online' : 'Offline';
        document.getElementById('systemStatus').textContent = status;
        document.getElementById('backendStatus').textContent = status;

        // Get active calls
        refreshActiveCalls();

        // Get knowledge base stats
        const kbData = await apiCall('GET', '/api/v1/knowledge/documents');
        document.getElementById('docsCount').textContent = kbData.total || 0;
        allDocuments = kbData.documents || [];

    } catch (error) {
        console.error('Error loading dashboard:', error);
        document.getElementById('backendStatus').innerHTML = 
            '<span class="badge badge-danger">Offline</span>';
    }
}

async function refreshActiveCalls() {
    try {
        const data = await apiCall('GET', '/api/v1/calls/active');
        const callsList = document.getElementById('activeCallsList');
        
        document.getElementById('activeCallsCount').textContent = data.count || 0;
        document.getElementById('totalCallsCount').textContent = (parseInt(document.getElementById('totalCallsCount').textContent) || 0) + (data.count > 0 ? 1 : 0);

        if (!data.calls || data.calls.length === 0) {
            callsList.innerHTML = '<p class="empty-state">No active calls</p>';
            return;
        }

        callsList.innerHTML = data.calls.map(call => `
            <div class="call-item">
                <div class="call-item-header">
                    <span class="call-item-name">${call.user_name}</span>
                    <span class="call-item-status badge badge-success">${call.status}</span>
                </div>
                <p style="margin: 0.5rem 0; font-size: 0.9rem; color: var(--secondary);">
                    <i class="fas fa-id-card"></i> ${call.call_id}
                </p>
                <p style="margin: 0; font-size: 0.85rem; color: var(--secondary);">
                    Duration: ${formatDuration(call.duration)}
                </p>
            </div>
        `).join('');

    } catch (error) {
        console.error('Error loading active calls:', error);
    }
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    }
    return `${minutes}m ${secs}s`;
}

function checkBackendStatus() {
    const statusEl = document.getElementById('backendStatus');
    statusEl.innerHTML = '<span class="badge badge-loading">Checking...</span>';
    
    apiCall('GET', '/api/v1/health')
        .then(() => {
            statusEl.innerHTML = '<span class="badge badge-success">Connected</span>';
        })
        .catch(() => {
            statusEl.innerHTML = '<span class="badge badge-danger">Disconnected</span>';
        });
}

// ============================================
// Call Management Functions
// ============================================

async function initiateCall(event) {
    event.preventDefault();
    
    const formData = {
        user_name: document.getElementById('userName').value,
        user_phone: document.getElementById('userPhone').value,
        call_topic: document.getElementById('callTopic').value,
        language: document.getElementById('language').value || 'en'
    };

    try {
        const response = await apiCall('POST', '/api/v1/calls/initiate', formData);
        currentCallId = response.call_id;
        callStartTime = new Date();

        showToast(`Call initiated: ${response.message}`, 'success');

        // Show call interface
        document.getElementById('callForm').style.display = 'none';
        document.getElementById('callInterface').style.display = 'block';
        document.getElementById('currentCallId').textContent = currentCallId;
        document.getElementById('chatMessages').innerHTML = '';

        // Start duration timer
        startCallDurations();

        // Add welcome message
        addMessageToChat('agent', response.message);

    } catch (error) {
        showToast(`Error initiating call: ${error.message}`, 'error');
    }
}

function startCallDuration() {
    if (callDurationInterval) clearInterval(callDurationInterval);
    
    callDurationInterval = setInterval(() => {
        if (callStartTime) {
            const elapsed = Math.floor((new Date() - callStartTime) / 1000);
            document.getElementById('callDuration').textContent = formatDuration(elapsed);
        }
    }, 1000);
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message || !currentCallId) {
        showToast('Please type a message', 'error');
        return;
    }

    // Add user message to chat
    addMessageToChat('user', message);
    input.value = '';

    try {
        const response = await apiCall('POST', '/api/v1/conversations/message', {
            call_id: currentCallId,
            message: message
        });

        // Add agent response
        addMessageToChat('agent', response.agent_response);

        // Show intent and confidence
        console.log(`Intent: ${response.intent}, Confidence: ${response.confidence}`);

        if (response.requires_transfer) {
            showToast(`Transfer Required: ${response.transfer_reason || 'Customer requesting agent'}`, 'info');
        }

    } catch (error) {
        showToast(`Error sending message: ${error.message}`, 'error');
    }
}

function handleMessageKeypress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function addMessageToChat(type, content) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const time = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
    });
    
    messageDiv.innerHTML = `
        ${content}
        <div class="message-time">${time}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function endCall() {
    if (!currentCallId) return;

    if (!confirm('Are you sure you want to end this call?')) {
        return;
    }

    try {
        const response = await apiCall('POST', `/api/v1/calls/end/${currentCallId}`, {});
        
        showToast('Call ended successfully', 'success');
        clearInterval(callDurationInterval);

        // Get conversation history
        const history = await apiCall('GET', `/api/v1/conversations/history/${currentCallId}`);
        console.log('Conversation Summary:', history.summary);

        // Reset UI
        resetCallUI();
        currentCallId = null;

    } catch (error) {
        showToast(`Error ending call: ${error.message}`, 'error');
    }
}

function transferCall() {
    if (!currentCallId) return;
    
    showToast('Call transferred to human agent', 'info');
    // In a real system, this would transfer to an actual queue
}

function resetCallUI() {
    document.getElementById('callForm').style.display = 'block';
    document.getElementById('callInterface').style.display = 'none';
    document.getElementById('callDuration').textContent = '00:00';
    document.getElementById('callForm').reset();
}

// ============================================
// Knowledge Base Functions
// ============================================

async function loadKnowledgeBase() {
    try {
        const data = await apiCall('GET', '/api/v1/knowledge/documents');
        allDocuments = data.documents || [];
        displayDocuments(allDocuments);
    } catch (error) {
        console.error('Error loading knowledge base:', error);
        showToast('Error loading knowledge base', 'error');
    }
}

function displayDocuments(documents) {
    const container = document.getElementById('documentsList');
    
    if (!documents || documents.length === 0) {
        container.innerHTML = '<p class="empty-state">No documents found</p>';
        return;
    }

    container.innerHTML = documents.map((doc, index) => `
        <div class="doc-item">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <strong>${doc.title}</strong>
                    <div style="font-size: 0.85rem; color: var(--secondary); margin-top: 0.25rem;">
                        Category: <span class="badge" style="background: #e0e0e0; color: var(--dark);">${doc.category}</span>
                    </div>
                    <p style="font-size: 0.9rem; margin: 0.5rem 0; color: var(--secondary);">
                        ${doc.preview}
                    </p>
                </div>
                <button class="btn btn-secondary" style="padding: 0.5rem 1rem; font-size: 0.9rem;" onclick="deleteDocument('${doc.document_id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

async function addDocument(event) {
    event.preventDefault();

    const formData = {
        title: document.getElementById('docTitle').value,
        content: document.getElementById('docContent').value,
        category: document.getElementById('docCategory').value,
        tags: []
    };

    try {
        const response = await apiCall('POST', '/api/v1/knowledge/documents', formData);
        showToast(`Document added: ${response.title}`, 'success');
        
        // Reset form and reload
        document.getElementById('docForm').reset();
        loadKnowledgeBase();

    } catch (error) {
        showToast(`Error adding document: ${error.message}`, 'error');
    }
}

async function searchKB() {
    const query = document.getElementById('searchQuery').value.trim();
    
    if (!query) {
        loadKnowledgeBase();
        return;
    }

    try {
        const response = await apiCall('POST', '/api/v1/knowledge/search', {
            query: query,
            top_k: 5
        });

        const results = response.results.map(r => ({
            ...r,
            document_id: r.document_id || `result-${Math.random()}`,
            preview: r.content.substring(0, 150) + '...'
        }));

        displayDocuments(results);
        showToast(`Found ${response.total_results} results`, 'success');

    } catch (error) {
        showToast(`Search error: ${error.message}`, 'error');
    }
}

function handleSearchKeypress(event) {
    if (event.key === 'Enter') {
        searchKB();
    }
}

async function deleteDocument(docId) {
    if (!confirm('Delete this document?')) return;

    try {
        await apiCall('DELETE', `/api/v1/knowledge/documents/${docId}`);
        showToast('Document deleted', 'success');
        loadKnowledgeBase();
    } catch (error) {
        showToast(`Error deleting document: ${error.message}`, 'error');
    }
}

async function uploadDocument(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${config.apiEndpoint}/api/v1/knowledge/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Upload failed');

        showToast(`Document uploaded: ${file.name}`, 'success');
        loadKnowledgeBase();
    } catch (error) {
        showToast(`Error uploading document: ${error.message}`, 'error');
    }
}

// ============================================
// Settings Functions
// ============================================

function loadSettings() {
    document.getElementById('apiEndpoint').value = config.apiEndpoint;
    document.getElementById('maxRetries').value = config.maxRetries;
    document.getElementById('timeout').value = config.timeout / 1000;
    document.getElementById('lastUpdated').textContent = new Date().toLocaleString();
}

function saveSettings(event) {
    event.preventDefault();

    const newEndpoint = document.getElementById('apiEndpoint').value;
    const newMaxRetries = document.getElementById('maxRetries').value;
    const newTimeout = document.getElementById('timeout').value;

    localStorage.setItem('apiEndpoint', newEndpoint);
    localStorage.setItem('maxRetries', newMaxRetries);
    localStorage.setItem('timeout', newTimeout);

    config.apiEndpoint = newEndpoint;
    config.maxRetries = parseInt(newMaxRetries);
    config.timeout = parseInt(newTimeout) * 1000;

    showToast('Settings saved successfully', 'success');
    document.getElementById('lastUpdated').textContent = new Date().toLocaleString();
}

// ============================================
// Utility Functions
// ============================================

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    const pad = (n) => n.toString().padStart(2, '0');
    
    if (hours > 0) {
        return `${pad(hours)}:${pad(minutes)}:${pad(secs)}`;
    }
    return `${pad(minutes)}:${pad(secs)}`;
}

// WebSocket support for real-time conversations (optional)
function connectWebSocket() {
    if (!currentCallId) return;

    const wsProtocol = config.apiEndpoint.startsWith('https') ? 'wss' : 'ws';
    const wsUrl = config.apiEndpoint.replace(/https?/, wsProtocol);
    const ws = new WebSocket(`${wsUrl}/api/v1/conversations/ws/${currentCallId}`);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.agent_response) {
            addMessageToChat('agent', data.agent_response);
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    return ws;
}

// Alias for call duration (fixed typo)
function startCallDurations() {
    startCallDuration();
}
