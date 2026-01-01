/**
 * Data formatting and validation utilities
 */

export function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

export function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR');
}

export function formatScore(score, decimals = 2) {
    if (score === null || score === undefined) return '-';
    return Number(score).toFixed(decimals);
}

export function formatDrugList(drugs) {
    if (!drugs || !Array.isArray(drugs)) return '-';
    return drugs.join(', ');
}

export function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

export function validatePatientId(patientId) {
    return patientId && patientId.trim().length > 0;
}

export function validateAge(age) {
    return age >= 0 && age <= 150;
}

export function getScoreColor(score, inverse = false) {
    // For efficacy/synergy (higher is better)
    if (!inverse) {
        if (score >= 0.8) return '#4CAF50';  // green
        if (score >= 0.6) return '#FFC107';  // yellow
        return '#F44336';  // red
    }
    // For toxicity (lower is better)
    else {
        if (score <= 3) return '#4CAF50';
        if (score <= 6) return '#FFC107';
        return '#F44336';
    }
}

export function getEvidenceBadge(evidence) {
    const badges = {
        '1A': { text: '1A', color: '#4CAF50', label: '최고 수준' },
        '1B': { text: '1B', color: '#66BB6A', label: '높은 수준' },
        '2A': { text: '2A', color: '#FFC107', label: '중간 수준' },
        '2B': { text: '2B', color: '#FFA726', label: '제한적' },
        '3': { text: '3', color: '#FF7043', label: '낮은 수준' },
    };
    return badges[evidence] || { text: evidence, color: '#9E9E9E', label: '미분류' };
}

export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

export function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.style.animation = 'slideIn 0.3s ease';

    document.body.appendChild(notification);

    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
