// Quantum Authentication System for X12 Server
// Handles user registration, login, and quantum token management

class QuantumAuth {
    constructor() {
        this.apiBase = window.location.origin + '/api';
        this.currentUser = null;
        this.quantumToken = null;
        this.isAuthenticated = false;
        
        // Check for existing session
        this.checkExistingSession();
    }

    // Check if user already has a valid session
    async checkExistingSession() {
        const token = localStorage.getItem('quantum_token');
        const userData = localStorage.getItem('quantum_user');
        
        if (token && userData) {
            try {
                // Verify token is still valid
                const isValid = await this.validateToken(token);
                if (isValid) {
                    this.quantumToken = token;
                    this.currentUser = JSON.parse(userData);
                    this.isAuthenticated = true;
                    this.updateUI();
                    console.log("Existing quantum session restored");
                } else {
                    this.clearSession();
                }
            } catch (error) {
                console.error("Session validation failed:", error);
                this.clearSession();
            }
        }
    }

    // Register a new user with quantum-enhanced security
    async register(username, email, password) {
        try {
            const response = await fetch(`${this.apiBase}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username,
                    email,
                    password,
                    quantum_key: this.generateQuantumKey()
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Registration successful
                this.quantumToken = data.token;
                this.currentUser = data.user;
                this.isAuthenticated = true;
                
                // Store session data
                localStorage.setItem('quantum_token', data.token);
                localStorage.setItem('quantum_user', JSON.stringify(data.user));
                
                this.updateUI();
                return { success: true, message: "Quantum registration successful!" };
            } else {
                return { success: false, message: data.error || "Registration failed" };
            }
        } catch (error) {
            console.error("Registration error:", error);
            return { success: false, message: "Network error during registration" };
        }
    }

    // Login with quantum authentication
    async login(username, password) {
        try {
            const response = await fetch(`${this.apiBase}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username,
                    password,
                    quantum_challenge: this.generateQuantumChallenge()
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Login successful
                this.quantumToken = data.token;
                this.currentUser = data.user;
                this.isAuthenticated = true;
                
                // Store session data
                localStorage.setItem('quantum_token', data.token);
                localStorage.setItem('quantum_user', JSON.stringify(data.user));
                
                this.updateUI();
                return { success: true, message: "Quantum login successful!" };
            } else {
                return { success: false, message: data.error || "Login failed" };
            }
        } catch (error) {
            console.error("Login error:", error);
            return { success: false, message: "Network error during login" };
        }
    }

    // Logout and clear quantum session
    logout() {
        // Notify server about logout
        fetch(`${this.apiBase}/logout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.quantumToken}`
            }
        }).catch(err => console.error("Logout notification failed:", err));
        
        this.clearSession();
        this.updateUI();
        return { success: true, message: "Logged out successfully" };
    }

    // Clear local session data
    clearSession() {
        this.quantumToken = null;
        this.currentUser = null;
        this.isAuthenticated = false;
        localStorage.removeItem('quantum_token');
        localStorage.removeItem('quantum_user');
    }

    // Validate quantum token with server
    async validateToken(token) {
        try {
            const response = await fetch(`${this.apiBase}/validate`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            return response.ok;
        } catch (error) {
            console.error("Token validation error:", error);
            return false;
        }
    }

    // Generate a quantum key for registration
    generateQuantumKey() {
        // Simulate quantum key generation
        const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
        let key = '';
        for (let i = 0; i < 64; i++) {
            key += chars[Math.floor(Math.random() * chars.length)];
        }
        return key;
    }

    // Generate a quantum challenge for login
    generateQuantumChallenge() {
        // Simulate quantum challenge generation
        return `qc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Update UI based on authentication status
    updateUI() {
        const loginBtn = document.getElementById('loginBtn');
        const registerBtn = document.getElementById('registerBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        const userInfo = document.getElementById('userInfo');
        const dashboardLink = document.getElementById('dashboardLink');
        
        if (this.isAuthenticated && this.currentUser) {
            // User is logged in
            if (loginBtn) loginBtn.style.display = 'none';
            if (registerBtn) registerBtn.style.display = 'none';
            if (logoutBtn) logoutBtn.style.display = 'block';
            if (userInfo) {
                userInfo.style.display = 'flex';
                userInfo.innerHTML = `
                    <span>Welcome, <strong>${this.currentUser.username}</strong></span>
                    <span class="quantum-badge">⚛️ Quantum User</span>
                `;
            }
            if (dashboardLink) dashboardLink.style.display = 'block';
        } else {
            // User is not logged in
            if (loginBtn) loginBtn.style.display = 'block';
            if (registerBtn) registerBtn.style.display = 'block';
            if (logoutBtn) logoutBtn.style.display = 'none';
            if (userInfo) {
                userInfo.style.display = 'none';
                userInfo.innerHTML = '';
            }
            if (dashboardLink) dashboardLink.style.display = 'none';
        }
    }

    // Get authentication header for API calls
    getAuthHeader() {
        if (this.quantumToken) {
            return { 'Authorization': `Bearer ${this.quantumToken}` };
        }
        return {};
    }
}

// Initialize quantum auth when document is ready
document.addEventListener('DOMContentLoaded', function() {
    window.quantumAuth = new QuantumAuth();
    
    // Setup modal functionality
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const closeButtons = document.querySelectorAll('.close-modal');
    
    // Open login modal
    if (loginBtn) {
        loginBtn.addEventListener('click', function() {
            if (loginModal) loginModal.style.display = 'block';
        });
    }
    
    // Open register modal
    if (registerBtn) {
        registerBtn.addEventListener('click', function() {
            if (registerModal) registerModal.style.display = 'block';
        });
    }
    
    // Logout button
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            window.quantumAuth.logout();
        });
    }
    
    // Close modals
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (loginModal) loginModal.style.display = 'none';
            if (registerModal) registerModal.style.display = 'none';
        });
    });
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (loginModal && event.target === loginModal) {
            loginModal.style.display = 'none';
        }
        if (registerModal && event.target === registerModal) {
            registerModal.style.display = 'none';
        }
    });
    
    // Login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            const loginStatus = document.getElementById('loginStatus');
            
            const result = await window.quantumAuth.login(username, password);
            
            if (result.success) {
                loginStatus.innerHTML = `<span class="success">${result.message}</span>`;
                setTimeout(() => {
                    if (loginModal) loginModal.style.display = 'none';
                    loginStatus.innerHTML = '';
                    loginForm.reset();
                }, 1500);
            } else {
                loginStatus.innerHTML = `<span class="error">${result.message}</span>`;
            }
        });
    }
    
    // Register form submission
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('registerUsername').value;
            const email = document.getElementById('registerEmail').value;
            const password = document.getElementById('registerPassword').value;
            const confirmPassword = document.getElementById('registerConfirmPassword').value;
            const registerStatus = document.getElementById('registerStatus');
            
            if (password !== confirmPassword) {
                registerStatus.innerHTML = `<span class="error">Passwords do not match</span>`;
                return;
            }
            
            const result = await window.quantumAuth.register(username, email, password);
            
            if (result.success) {
                registerStatus.innerHTML = `<span class="success">${result.message}</span>`;
                setTimeout(() => {
                    if (registerModal) registerModal.style.display = 'none';
                    registerStatus.innerHTML = '';
                    registerForm.reset();
                }, 1500);
            } else {
                registerStatus.innerHTML = `<span class="error">${result.message}</span>`;
            }
        });
    }
});
