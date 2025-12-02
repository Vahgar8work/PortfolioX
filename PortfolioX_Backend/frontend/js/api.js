// API Configuration
const API_CONFIG = {
    baseUrl: localStorage.getItem('apiBaseUrl') || 'http://localhost:8000',
    token: localStorage.getItem('apiToken') || null
};

// API Helper Functions
const API = {
    // Get headers with authentication
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (API_CONFIG.token) {
            headers['Authorization'] = 'Bearer ' + API_CONFIG.token;
        }
        
        return headers;
    },

    // Generic fetch with error handling
    async fetch(endpoint, options) {
        options = options || {};
        
        try {
            const url = API_CONFIG.baseUrl + endpoint;
            const response = await fetch(url, {
                ...options,
                headers: this.getHeaders()
            });

            if (!response.ok) {
                throw new Error('HTTP ' + response.status + ': ' + response.statusText);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            showToast('API Error: ' + error.message, 'error');
            throw error;
        }
    },

    // Portfolios
    async getPortfolios() {
        return this.fetch('/portfolios/');
    },

    async getPortfolio(id) {
        return this.fetch('/portfolios/' + id + '/');
    },

    // Analytics
    async triggerAnalysis(portfolioId) {
        return this.fetch('/analytics/api/' + portfolioId + '/analyze/', {
            method: 'POST'
        });
    },

    async getAnalysis(portfolioId) {
        return this.fetch('/analytics/api/' + portfolioId + '/analysis/');
    },

    async getPerformance(portfolioId) {
        return this.fetch('/analytics/api/' + portfolioId + '/performance/');
    },

    async getRecommendations(portfolioId) {
        return this.fetch('/analytics/api/' + portfolioId + '/recommendations/');
    },

    // Test connection
    async testConnection() {
        try {
            await this.fetch('/portfolios/');
            return true;
        } catch (error) {
            return false;
        }
    }
};

// Update API config
function updateApiConfig(baseUrl, token) {
    API_CONFIG.baseUrl = baseUrl;
    API_CONFIG.token = token;
    localStorage.setItem('apiBaseUrl', baseUrl);
    localStorage.setItem('apiToken', token || '');
}
