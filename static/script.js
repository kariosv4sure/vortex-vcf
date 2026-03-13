// ===== TYPEWRITER EFFECT - HYPE BUILDER (Fixed height, no layout shift) =====
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
        setTimeout(typeWriter, 2000); // Pause at end
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
    // Remove all non-digit characters
    const digitsOnly = phone.replace(/\D/g, '');
    
    // Check if it's empty
    if (digitsOnly.length === 0) return false;
    
    // Check if it's a valid length (at least 7 digits, max 15)
    if (digitsOnly.length < 7 || digitsOnly.length > 15) return false;
    
    // Check if it has valid characters (allows +, -, spaces, parentheses)
    const validFormat = /^[\d\+\-\s\(\)]+$/.test(phone);
    if (!validFormat) return false;
    
    return true;
}

function validateName(name) {
    // Trim and check if empty
    const trimmed = name.trim();
    if (trimmed.length === 0) return false;
    
    // Check minimum length (at least 2 characters)
    if (trimmed.length < 2) return false;
    
    // Check maximum length (50 characters max)
    if (trimmed.length > 50) return false;
    
    // Check for valid characters (letters, spaces, dots, hyphens, apostrophes)
    const validName = /^[a-zA-Z\s\.\-']+$/.test(trimmed);
    if (!validName) return false;
    
    return true;
}

// ===== ANTI-DEVTOOLS =====
(function() {
    // Disable right click
    document.addEventListener('contextmenu', e => e.preventDefault());

    // Disable keyboard shortcuts
    document.addEventListener('keydown', e => {
        if (e.key === 'F12' ||
            (e.ctrlKey && e.shiftKey && e.key === 'I') ||
            (e.ctrlKey && e.shiftKey && e.key === 'J') ||
            (e.ctrlKey && e.key === 'U') ||
            (e.ctrlKey && e.key === 'S')) {
            e.preventDefault();
            return false;
        }
    });

    // Detect dev tools
    let devToolsOpen = false;
    const element = new Image();
    Object.defineProperty(element, 'id', {
        get: function() {
            devToolsOpen = true;
            throw new Error('Dev tools detected');
        }
    });

    setInterval(() => {
        devToolsOpen = false;
        console.log(element);
        if (devToolsOpen) {
            document.body.innerHTML = `
                <div style="height:100vh; display:flex; justify-content:center; align-items:center; background:#0a0a0a; color:white; font-family:'Inter',sans-serif; text-align:center; padding:20px;">
                    <div style="max-width:400px;">
                        <h1 style="font-weight:300; font-size:2rem; margin-bottom:20px;">◇</h1>
                        <p style="opacity:0.7; font-size:0.9rem;">Developer tools detected · Access denied</p>
                        <p style="opacity:0.4; font-size:0.8rem; margin-top:20px;">Vortex VCF</p>
                    </div>
                </div>
            `;
        }
    }, 1000);
})();

// ===== MAIN SUBMIT FUNCTION =====
async function submitContact() {
    const name = document.getElementById('nameInput').value.trim();
    const number = document.getElementById('numberInput').value.trim();
    const submitBtn = document.querySelector('.submit-btn');
    const loading = document.getElementById('loading');
    const errorMsg = document.getElementById('errorMessage');

    // PROPER VALIDATION
    if (!validateName(name)) {
        showError('Please enter a valid name (letters only, min 2 characters)');
        return;
    }
    
    if (!validatePhoneNumber(number)) {
        showError('Please enter a valid phone number (7-15 digits)');
        return;
    }

    // Show loading, disable button
    loading.classList.remove('hidden');
    submitBtn.disabled = true;
    errorMsg.classList.add('hidden');

    try {
        // Clean phone number (remove all non-digits for storage)
        const cleanNumber = number.replace(/\D/g, '');
        
        // Send to backend
        const response = await fetch('/api/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                phone: cleanNumber
            })
        });

        const data = await response.json();

        if (response.ok) {
            // UPDATE BOTH COUNTERS - LIVE!
            document.getElementById('counterNumber').textContent = data.total;
            
            // Also update the counter in channel section if it exists
            const updatedCounter = document.getElementById('updatedCounterNumber');
            if (updatedCounter) {
                updatedCounter.textContent = data.total;
            }
            
            // Update stats text
            const statsElement = document.getElementById('stats');
            if (statsElement) {
                statsElement.innerHTML = `<span>${data.total}</span> people in the vortex 🔥`;
            }

            // Hide form, show channel section
            document.getElementById('formSection').style.display = 'none';
            document.getElementById('channelSection').classList.remove('hidden');

            // Clear inputs
            document.getElementById('nameInput').value = '';
            document.getElementById('numberInput').value = '';
            
            // Optional: Show success message
            console.log('Contact added successfully!');
        } else {
            showError(data.error || 'Something went wrong!');
        }
    } catch (error) {
        showError('Network error - please try again!');
        console.error('Error:', error);
    } finally {
        // Hide loading, enable button
        loading.classList.add('hidden');
        submitBtn.disabled = false;
    }
}

// ===== ERROR DISPLAY FUNCTION =====
function showError(message) {
    const errorMsg = document.getElementById('errorMessage');
    errorMsg.textContent = message;
    errorMsg.classList.remove('hidden');

    // Auto hide after 3 seconds
    setTimeout(() => {
        errorMsg.classList.add('hidden');
    }, 3000);
}

// ===== CHECK STATS ON PAGE LOAD =====
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.total !== undefined) {
            // Update main counter
            const counterNumber = document.getElementById('counterNumber');
            if (counterNumber) {
                counterNumber.textContent = data.total;
            }
            
            // Update stats text
            const statsElement = document.getElementById('stats');
            if (statsElement) {
                statsElement.innerHTML = `<span>${data.total}</span> people in the vortex 🔥`;
            }
            
            // Update updated counter if it exists
            const updatedCounter = document.getElementById('updatedCounterNumber');
            if (updatedCounter) {
                updatedCounter.textContent = data.total;
            }
        }
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

// ===== SMOOTH ENTRANCE ANIMATION =====
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

// ===== PAGE LOAD INITIALIZATION =====
window.addEventListener('load', async () => {
    // Start typewriter effect
    setTimeout(typeWriter, 500);
    
    // Update stats from server
    await updateStats();
    
    // Animate entrance
    animateEntrance();
    
    // Add input formatting for phone number (optional)
    const phoneInput = document.getElementById('numberInput');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            // Basic formatting - remove any obviously invalid characters as user types
            this.value = this.value.replace(/[^\d\+\-\s\(\)]/g, '');
        });
    }
});

// ===== ADMIN FUNCTIONS (Protected) =====
async function getContacts() {
    try {
        const response = await fetch('/admin/api/contacts');
        if (response.status === 401) {
            console.log('Authentication required');
            return;
        }
        const data = await response.json();
        console.log('All contacts:', data);
        return data;
    } catch (error) {
        console.error('Error fetching contacts:', error);
    }
}

async function exportCSV() {
    window.location.href = '/admin/export/csv';
}

async function exportVCF() {
    window.location.href = '/admin/export/vcf';
}

// ===== PERIODIC STATS UPDATE (every 30 seconds) =====
setInterval(async () => {
    await updateStats();
}, 30000);
