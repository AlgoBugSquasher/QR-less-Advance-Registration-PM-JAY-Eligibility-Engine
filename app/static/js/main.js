/**
 * Hospital Token System - Main JavaScript
 * Handles client-side interactivity, form validation, and AJAX calls
 */

// Document Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize application on page load
 */
function initializeApp() {
    // Add smooth animations to elements
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animation = `fadeInUp 0.5s ease forwards`;
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // Initialize tooltips if available
    initializeTooltips();

    // Setup form handlers
    setupFormHandlers();

    // Setup navigation
    setupNavigation();
}

/**
 * Setup form handlers and validation
 */
function setupFormHandlers() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', validateLoginForm);
    }

    // Register form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', validateRegisterForm);
    }
}

/**
 * Validate login form
 */
function validateLoginForm(e) {
    const loginInput = document.getElementById('login_input');
    const password = document.getElementById('password');

    if (!loginInput.value.trim()) {
        showAlert('Please enter your mobile number or email', 'warning');
        e.preventDefault();
        return false;
    }

    if (!password.value) {
        showAlert('Please enter your password', 'warning');
        e.preventDefault();
        return false;
    }

    return true;
}

/**
 * Validate register form
 */
function validateRegisterForm(e) {
    const fullName = document.getElementById('full_name');
    const mobile = document.getElementById('mobile_number');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');

    // Validate full name
    if (!fullName.value.trim() || fullName.value.length < 2) {
        showAlert('Please enter a valid full name', 'warning');
        e.preventDefault();
        return false;
    }

    // Validate mobile
    if (!isValidMobile(mobile.value)) {
        showAlert('Please enter a valid 10-digit mobile number', 'warning');
        e.preventDefault();
        return false;
    }

    // Validate email
    if (!isValidEmail(email.value)) {
        showAlert('Please enter a valid email address', 'warning');
        e.preventDefault();
        return false;
    }

    // Validate password
    if (!password.value || password.value.length < 6) {
        showAlert('Password must be at least 6 characters long', 'warning');
        e.preventDefault();
        return false;
    }

    // Validate password match
    if (password.value !== confirmPassword.value) {
        showAlert('Passwords do not match', 'warning');
        e.preventDefault();
        return false;
    }

    return true;
}

/**
 * Validate mobile number format
 */
function isValidMobile(mobile) {
    const cleaned = mobile.replace(/\D/g, '');
    return cleaned.length === 10 || cleaned.length === 12;
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <i class="fas fa-info-circle"></i> ${message}
        <button type="button" onclick="this.parentElement.style.display='none'" style="float: right; background: none; border: none; color: inherit; cursor: pointer; font-size: 1.2rem;">×</button>
    `;

    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            alertDiv.style.display = 'none';
        }, 5000);
    }
}

/**
 * Setup navigation interactions
 */
function setupNavigation() {
    // Highlight current page in navbar
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    const navToggle = document.getElementById('navToggle');
    const navbarMenu = document.getElementById('navbarMenu');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && href.includes(currentPage)) {
            link.style.color = 'var(--accent-color)';
            link.style.borderBottom = '2px solid var(--accent-color)';
        }
    });

    if (navToggle && navbarMenu) {
        navToggle.addEventListener('click', function() {
            const isOpen = navbarMenu.classList.toggle('open');
            this.setAttribute('aria-expanded', isOpen);
        });

        navbarMenu.addEventListener('click', function(event) {
            const clickedLink = event.target.closest('.nav-link');
            const clickedLogout = event.target.closest('.btn-logout');
            if (clickedLink || clickedLogout) {
                navbarMenu.classList.remove('open');
                navToggle.setAttribute('aria-expanded', false);
            }
        });

        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                navbarMenu.classList.remove('open');
                navToggle.setAttribute('aria-expanded', false);
            }
        });
    }
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    // Check if tooltip elements exist and add hover behavior
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseover', showTooltip);
        element.addEventListener('mouseout', hideTooltip);
    });
}

/**
 * Show tooltip
 */
function showTooltip(e) {
    const tooltip = e.target.getAttribute('data-tooltip');
    if (tooltip) {
        const tooltipEl = document.createElement('div');
        tooltipEl.className = 'tooltip';
        tooltipEl.textContent = tooltip;
        tooltipEl.style.position = 'absolute';
        tooltipEl.style.background = 'var(--primary-color)';
        tooltipEl.style.color = 'white';
        tooltipEl.style.padding = '0.5rem 1rem';
        tooltipEl.style.borderRadius = '4px';
        tooltipEl.style.fontSize = '0.85rem';
        tooltipEl.style.zIndex = '1000';
        document.body.appendChild(tooltipEl);
    }
}

/**
 * Hide tooltip
 */
function hideTooltip() {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(t => t.remove());
}

/**
 * Fetch queue status via AJAX
 */
function updateQueueStatus(departmentCode) {
    fetch(`/token/queue-status/${departmentCode}`)
        .then(response => response.json())
        .then(data => {
            console.log('Queue Status:', data);
            // Update UI with queue information
            const queueDisplay = document.getElementById(`queue-${departmentCode}`);
            if (queueDisplay) {
                queueDisplay.innerHTML = `
                    Queue: ${data.current_queue} patients
                    <br>
                    Wait Time: ${data.estimated_wait_time} minutes
                `;
            }
        })
        .catch(error => console.error('Error fetching queue status:', error));
}

/**
 * Format time in human-readable format
 */
function formatTime(minutes) {
    if (minutes === 0) return 'No wait';
    if (minutes < 60) return `${minutes} minutes`;

    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (mins === 0) return `${hours} hour${hours > 1 ? 's' : ''}`;
    return `${hours}h ${mins}m`;
}

/**
 * Copy token number to clipboard
 */
function copyToClipboard(text) {
    const temp = document.createElement('input');
    temp.value = text;
    document.body.appendChild(temp);
    temp.select();
    document.execCommand('copy');
    document.body.removeChild(temp);
    showAlert('Token number copied to clipboard!', 'success');
}

/**
 * Print token
 */
function printToken() {
    window.print();
}

/**
 * Close alert
 */
function closeAlert(element) {
    element.parentElement.style.display = 'none';
}

/**
 * Reload page
 */
function reloadPage() {
    location.reload();
}

/**
 * Logout user
 */
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = '/auth/logout';
    }
}

/**
 * Cancel token with confirmation
 */
function cancelToken(tokenId) {
    if (confirm('Are you sure you want to cancel this token? This action cannot be undone.')) {
        document.querySelector(`form[data-token-id="${tokenId}"]`).submit();
    }
}

/**
 * Add CSS animations
 */
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    .fade-in {
        animation: fadeInUp 0.5s ease;
    }

    .slide-in {
        animation: slideIn 0.5s ease;
    }

    .scale-in {
        animation: scaleIn 0.5s ease;
    }
`;
document.head.appendChild(style);

// Export functions for use in HTML
window.showAlert = showAlert;
window.copyToClipboard = copyToClipboard;
window.printToken = printToken;
window.closeAlert = closeAlert;
window.reloadPage = reloadPage;
window.logout = logout;
window.cancelToken = cancelToken;
window.updateQueueStatus = updateQueueStatus;
