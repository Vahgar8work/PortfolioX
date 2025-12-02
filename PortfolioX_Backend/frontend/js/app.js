// Global state
let currentPortfolios = [];
let selectedPortfolioId = null;

// Initialize app on load
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    // Load saved settings
    const savedUrl = localStorage.getItem('apiBaseUrl');
    const savedToken = localStorage.getItem('apiToken');
    
    if (savedUrl) {
        document.getElementById('apiBaseUrl').value = savedUrl;
    }
    if (savedToken) {
        document.getElementById('apiToken').value = savedToken;
    }

    // Load initial data
    await loadDashboard();
    await loadPortfolios();
}

// Navigation
function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(function(section) {
        section.classList.remove('active');
    });
    
    // Remove active class from nav links
    const links = document.querySelectorAll('.nav-link');
    links.forEach(function(link) {
        link.classList.remove('active');
    });
    
    // Show selected section
    const targetSection = document.getElementById(sectionName + '-section');
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Add active class to clicked nav link
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(function(link) {
        if (link.getAttribute('onclick').indexOf(sectionName) > -1) {
            link.classList.add('active');
        }
    });
    
    // Load section-specific data
    if (sectionName === 'dashboard') {
        loadDashboard();
    } else if (sectionName === 'portfolios') {
        loadPortfolios();
    } else if (sectionName === 'analytics') {
        populatePortfolioSelector();
    }
}

// Dashboard Functions
async function loadDashboard() {
    try {
        const portfolios = await API.getPortfolios();
        currentPortfolios = portfolios;
        
        let totalValue = 0;
        let totalGain = 0;
        let totalInvested = 0;
        
        portfolios.forEach(function(p) {
            totalValue += parseFloat(p.current_value || 0);
            totalGain += parseFloat(p.total_gain_loss || 0);
            totalInvested += parseFloat(p.total_invested || 0);
        });
        
        const totalReturn = totalInvested > 0 ? ((totalGain / totalInvested) * 100) : 0;
        
        // Update stats
        document.getElementById('totalValue').textContent = formatCurrency(totalValue);
        document.getElementById('totalGain').textContent = formatCurrency(totalGain);
        const gainElem = document.getElementById('totalGain');
        gainElem.className = totalGain >= 0 ? 'positive' : 'negative';
        document.getElementById('totalReturn').textContent = totalReturn.toFixed(2) + '%';
        document.getElementById('portfolioCount').textContent = portfolios.length;
        
        // Update recent activity
        displayRecentActivity(portfolios);
        
    } catch (error) {
        console.error('Failed to load dashboard:', error);
    }
}

function displayRecentActivity(portfolios) {
    const container = document.getElementById('recentActivity');
    
    if (portfolios.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No portfolios found</p></div>';
        return;
    }
    
    const html = portfolios.slice(0, 5).map(function(p) {
        const gain = parseFloat(p.total_gain_loss || 0);
        const gainPercent = parseFloat(p.total_gain_pct || 0);
        const gainClass = gain >= 0 ? 'positive' : 'negative';
        
        return '<div class="portfolio-stat">' +
            '<div>' +
            '<strong>' + p.name + '</strong>' +
            '<p style="color: #6b7280; font-size: 0.875rem;">' + (p.description || 'No description') + '</p>' +
            '</div>' +
            '<div style="text-align: right;">' +
            '<div style="font-size: 1.25rem; font-weight: bold;">' + formatCurrency(p.current_value) + '</div>' +
            '<div class="' + gainClass + '" style="font-size: 0.875rem;">' +
            (gain >= 0 ? '+' : '') + formatCurrency(gain) + ' (' + gainPercent.toFixed(2) + '%)' +
            '</div>' +
            '</div>' +
            '</div>';
    }).join('');
    
    container.innerHTML = html;
}

async function refreshDashboard() {
    showToast('Refreshing dashboard...', 'info');
    await loadDashboard();
    showToast('Dashboard refreshed!', 'success');
}

// Portfolios Functions
async function loadPortfolios() {
    try {
        const container = document.getElementById('portfoliosList');
        container.innerHTML = '<div class="loading">Loading portfolios...</div>';
        
        const portfolios = await API.getPortfolios();
        currentPortfolios = portfolios;
        
        if (portfolios.length === 0) {
            container.innerHTML = '<div class="empty-state">' +
                '<i class="fas fa-briefcase"></i>' +
                '<p>No portfolios yet. Create your first portfolio!</p>' +
                '</div>';
            return;
        }
        
        const html = portfolios.map(function(p) {
            const gain = parseFloat(p.total_gain_loss || 0);
            const gainPercent = parseFloat(p.total_gain_pct || 0);
            const gainClass = gain >= 0 ? 'positive' : 'negative';
            
            return '<div class="portfolio-card" onclick="selectPortfolio(' + p.id + ')">' +
                '<h3>' + p.name + '</h3>' +
                '<p style="color: #6b7280; margin-bottom: 1rem;">' + (p.description || 'No description') + '</p>' +
                '<div class="portfolio-stat">' +
                '<span>Current Value</span>' +
                '<strong>' + formatCurrency(p.current_value) + '</strong>' +
                '</div>' +
                '<div class="portfolio-stat">' +
                '<span>Invested</span>' +
                '<strong>' + formatCurrency(p.total_invested) + '</strong>' +
                '</div>' +
                '<div class="portfolio-stat">' +
                '<span>Gain/Loss</span>' +
                '<strong class="' + gainClass + '">' +
                (gain >= 0 ? '+' : '') + formatCurrency(gain) + ' (' + gainPercent.toFixed(2) + '%)' +
                '</strong>' +
                '</div>' +
                '<div class="portfolio-stat">' +
                '<span>Status</span>' +
                '<span class="badge ' + (p.is_active ? 'success' : 'danger') + '">' +
                (p.is_active ? 'Active' : 'Inactive') +
                '</span>' +
                '</div>' +
                '</div>';
        }).join('');
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Failed to load portfolios:', error);
    }
}

function selectPortfolio(portfolioId) {
    selectedPortfolioId = portfolioId;
    showSection('analytics');
    document.getElementById('analyticsPortfolioSelect').value = portfolioId;
    loadAnalytics();
}

function createPortfolio() {
    showToast('Portfolio creation feature coming soon!', 'info');
}

// Analytics Functions
function populatePortfolioSelector() {
    const select = document.getElementById('analyticsPortfolioSelect');
    
    const options = currentPortfolios.map(function(p) {
        return '<option value="' + p.id + '">' + p.name + '</option>';
    }).join('');
    
    select.innerHTML = '<option value="">Select Portfolio</option>' + options;
    
    if (selectedPortfolioId) {
        select.value = selectedPortfolioId;
        loadAnalytics();
    }
}

async function loadAnalytics() {
    const portfolioId = document.getElementById('analyticsPortfolioSelect').value;
    
    if (!portfolioId) {
        document.getElementById('analyticsContent').innerHTML = 
            '<div class="empty-state">' +
            '<i class="fas fa-chart-line"></i>' +
            '<p>Select a portfolio to view analytics</p>' +
            '</div>';
        document.getElementById('analyticsResults').style.display = 'none';
        return;
    }
    
    try {
        document.getElementById('analyticsContent').innerHTML = '<div class="loading">Loading analytics...</div>';
        
        const analysis = await API.getAnalysis(portfolioId);
        
        if (!analysis || !analysis.results) {
            document.getElementById('analyticsContent').innerHTML = 
                '<div class="empty-state">' +
                '<i class="fas fa-exclamation-circle"></i>' +
                '<p>No analysis available. Click "Run Analysis" to generate.</p>' +
                '</div>';
            return;
        }
        
        displayAnalytics(analysis.results);
        
    } catch (error) {
        console.error('Failed to load analytics:', error);
        document.getElementById('analyticsContent').innerHTML = 
            '<div class="empty-state">' +
            '<i class="fas fa-times-circle"></i>' +
            '<p>Failed to load analytics. Please try again.</p>' +
            '</div>';
    }
}

function displayAnalytics(data) {
    document.getElementById('analyticsContent').style.display = 'none';
    document.getElementById('analyticsResults').style.display = 'block';
    
    // Health Score
    const healthScore = data.health_score || 0;
    const healthBadge = document.getElementById('healthScore');
    healthBadge.textContent = 'Health: ' + healthScore.toFixed(0) + '/100';
    healthBadge.className = 'badge ' + (healthScore >= 70 ? 'success' : (healthScore >= 40 ? 'warning' : 'danger'));
    
    // Risk Metrics
    document.getElementById('sharpeRatio').textContent = (data.sharpe_ratio || 0).toFixed(3);
    document.getElementById('volatility').textContent = (data.volatility || 0).toFixed(2) + '%';
    document.getElementById('maxDrawdown').textContent = (data.max_drawdown || 0).toFixed(2) + '%';
    document.getElementById('var').textContent = (data.var_95 || 0).toFixed(2) + '%';
    document.getElementById('alpha').textContent = (data.alpha || 0).toFixed(3);
    document.getElementById('beta').textContent = (data.beta || 0).toFixed(3);
    
    // Returns
    const returns = ['1d', '1w', '1m', '3m', '6m', '1y'];
    returns.forEach(function(period) {
        const value = data['return_' + period] || 0;
        const elem = document.getElementById('return' + period);
        elem.textContent = (value >= 0 ? '+' : '') + value.toFixed(2) + '%';
        elem.className = value >= 0 ? 'positive' : 'negative';
    });
    
    // Recommendations
    displayRecommendations(data.recommendations);
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations');
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<p style="color: #6b7280;">No recommendations available</p>';
        return;
    }
    
    const html = recommendations.map(function(rec) {
        let type = 'recommendation-item';
        if (rec.priority === 'high') {
            type += ' danger';
        } else if (rec.priority === 'medium') {
            type += ' warning';
        }
        
        return '<div class="' + type + '">' +
            '<strong>' + (rec.title || 'Recommendation') + '</strong>' +
            '<p>' + (rec.description || rec) + '</p>' +
            '</div>';
    }).join('');
    
    container.innerHTML = html;
}

async function triggerAnalysis() {
    const portfolioId = document.getElementById('analyticsPortfolioSelect').value;
    
    if (!portfolioId) {
        showToast('Please select a portfolio first', 'error');
        return;
    }
    
    try {
        showToast('Starting analysis...', 'info');
        await API.triggerAnalysis(portfolioId);
        showToast('Analysis started! Refreshing in 3 seconds...', 'success');
        
        setTimeout(function() {
            loadAnalytics();
        }, 3000);
        
    } catch (error) {
        showToast('Failed to start analysis', 'error');
    }
}

// Settings Functions
function saveSettings() {
    const baseUrl = document.getElementById('apiBaseUrl').value.trim();
    const token = document.getElementById('apiToken').value.trim();
    
    if (!baseUrl) {
        showToast('Please enter API Base URL', 'error');
        return;
    }
    
    updateApiConfig(baseUrl, token);
    showToast('Settings saved successfully!', 'success');
}

async function testConnection() {
    const table = document.getElementById('apiEndpointsTable');
    table.innerHTML = '<tr><td colspan="3">Testing connection...</td></tr>';
    
    const endpoints = [
        { path: '/portfolios/', method: 'GET', name: 'Get Portfolios' },
        { path: '/analytics/api/1/analysis/', method: 'GET', name: 'Get Analysis' }
    ];
    
    const results = [];
    
    for (let i = 0; i < endpoints.length; i++) {
        const endpoint = endpoints[i];
        try {
            await API.fetch(endpoint.path);
            results.push({
                name: endpoint.name,
                method: endpoint.method,
                status: '<span style="color: var(--success);">&#10003; Connected</span>'
            });
        } catch (error) {
            results.push({
                name: endpoint.name,
                method: endpoint.method,
                status: '<span style="color: var(--danger);">&#10007; Failed</span>'
            });
        }
    }
    
    const html = results.map(function(r) {
        return '<tr>' +
            '<td>' + r.name + '</td>' +
            '<td>de>' + r.method + '</code></td>' +
            '<td>' + r.status + '</td>' +
            '</tr>';
    }).join('');
    
    table.innerHTML = html;
}

// Utility Functions
function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2
    }).format(value || 0);
}

function showToast(message, type) {
    type = type || 'info';
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast ' + type + ' show';
    
    setTimeout(function() {
        toast.classList.remove('show');
    }, 3000);
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.clear();
        showToast('Logged out successfully', 'success');
        setTimeout(function() {
            location.reload();
        }, 1000);
    }
}
