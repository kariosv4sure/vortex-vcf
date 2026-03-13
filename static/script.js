// ===== TYPEWRITER EFFECT - HYPE BUILDER =====
const typewriterTexts = [
    "⚡ Status Goes Viral!",
    "📱 +1000 Views Daily",
    "🔥 Exclusive Contacts",
    "🚀 Join The Wave",
    "⭐ More Likes Daily",
    "💫 Stand Out Now",
    "🎯 Grow Your Reach"
];

let textIndex = 0;
let charIndex = 0;
let isDeleting = false;
let currentText = '';

function typeWriter() {
    const element = document.getElementById('typewriter');
    if (!element) return;

    if (isDeleting) {
        currentText = typewriterTexts[textIndex].substring(0, charIndex - 1);
        charIndex--;
    } else {
        currentText = typewriterTexts[textIndex].substring(0, charIndex + 1);
        charIndex++;
    }

    element.textContent = currentText;

    if (!isDeleting && charIndex === typewriterTexts[textIndex].length) {
        isDeleting = true;
        setTimeout(typeWriter, 2000);
    } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        textIndex = (textIndex + 1) % typewriterTexts.length;
        setTimeout(typeWriter, 500);
    } else {
        const speed = isDeleting ? 50 : 100;
        setTimeout(typeWriter, speed);
    }
}

// ===== VALIDATION FUNCTIONS =====
function validatePhoneNumber(phone) {
    if (!phone) return false;
    const digitsOnly = phone.replace(/\D/g, '');
    return digitsOnly.length >= 7 && digitsOnly.length <= 15;
}

function validateName(name) {
    if (!name) return false;
    const trimmed = name.trim();
    return trimmed.length >= 2 && trimmed.length <= 50;
}

// ===== ANTI-DEVTOOLS =====
(function() {
    document.addEventListener('contextmenu', e => e.preventDefault());
    document.addEventListener('keydown', e => {
        if (e.key === 'F12' ||
            (e.ctrlKey && e.shiftKey && e.key === 'I') ||
            (e.ctrlKey && e.shiftKey && e.key === 'J') ||
            (e.ctrlKey && e.key === 'U')) {
            e.preventDefault();
            return false;
        }
    });
})();

// ===== MAIN SUBMIT FUNCTION =====
async function submitContact() {
    const name = document.getElementById('nameInput').value.trim();
    const number = document.getElementById('numberInput').value.trim();
    const submitBtn = document.querySelector('.submit-btn');
    const loading = document.getElementById('loading');
    const errorMsg = document.getElementById('errorMessage');
    const formSection = document.getElementById('formSection');
    const channelSection = document.getElementById('channelSection');

    // Validation
    if (!validateName(name)) {
        showError('Please enter a valid name (min 2 characters)');
        return;
    }

    if (!validatePhoneNumber(number)) {
        showError('Please enter a valid phone number (7-15 digits)');
        return;
    }

    // Show loading
    loading.classList.remove('hidden');
    submitBtn.disabled = true;
    errorMsg.classList.add('hidden');

    try {
        const cleanNumber = number.replace(/\D/g, '');

        const response = await fetch('/api/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, phone: cleanNumber })
        });

        const data = await response.json();

        if (response.ok) {
            // Update counters
            const counterNumber = document.getElementById('counterNumber');
            const updatedCounter = document.getElementById('updatedCounterNumber');
            
            if (counterNumber) counterNumber.textContent = data.total;
            if (updatedCounter) updatedCounter.textContent = data.total;

            // Show channel section, hide form
            if (formSection) formSection.style.display = 'none';
            if (channelSection) channelSection.classList.remove('hidden');

            // Clear inputs
            document.getElementById('nameInput').value = '';
            document.getElementById('numberInput').value = '';
        } else {
            showError(data.error || 'Something went wrong!');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Network error - please try again!');
    } finally {
        loading.classList.add('hidden');
        submitBtn.disabled = false;
    }
}

// ===== ERROR DISPLAY =====
function showError(message) {
    const errorMsg = document.getElementById('errorMessage');
    if (errorMsg) {
        errorMsg.textContent = message;
        errorMsg.classList.remove('hidden');
        setTimeout(() => errorMsg.classList.add('hidden'), 3000);
    }
}

// ===== UPDATE STATS =====
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) {
            console.log('Stats endpoint not available yet');
            return;
        }
        const data = await response.json();
        
        const counterNumber = document.getElementById('counterNumber');
        const updatedCounter = document.getElementById('updatedCounterNumber');
        
        if (counterNumber && data.total !== undefined) {
            counterNumber.textContent = data.total;
        }
        if (updatedCounter && data.total !== undefined) {
            updatedCounter.textContent = data.total;
        }
    } catch (error) {
        // Silently fail - stats will update on next submission
        console.log('Stats update skipped (normal on first load)');
    }
}

// ===== ANIMATION =====
function animateEntrance() {
    const glassCard = document.querySelector('.glass-card');
    if (glassCard) {
        glassCard.style.opacity = '0';
        glassCard.style.transform = 'translateY(10px)';
        setTimeout(() => {
            glassCard.style.transition = 'all 0.6s ease';
            glassCard.style.opacity = '1';
            glassCard.style.transform = 'translateY(0)';
        }, 100);
    }
}

// ===== INIT =====
window.addEventListener('load', () => {
    setTimeout(typeWriter, 500);
    updateStats();
    animateEntrance();
    
    const phoneInput = document.getElementById('numberInput');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^\d\+\-\s\(\)]/g, '');
        });
    }
});

// ===== PERIODIC UPDATE (every 30 sec) =====
setInterval(updateStats, 30000);
