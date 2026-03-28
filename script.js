// Navbar Scroll Effect
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'var(--nav-bg)';
        navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.5)';
    } else {
        navbar.style.background = 'transparent';
        navbar.style.boxShadow = 'none';
    }
});

// Dropdown Mode Toggle
const body = document.getElementById('body-main');

document.addEventListener('DOMContentLoaded', () => {
    
    // Check saved mode
    const savedMode = localStorage.getItem('notesflix_mode');
    if (savedMode) {
        body.className = savedMode;
    }

    // Navbar mode toggle
    const modeToggle = document.getElementById('mode-toggle');
    if (modeToggle) {
        modeToggle.addEventListener('click', (e) => {
            e.preventDefault();
            if (body.classList.contains('dark-mode')) {
                setMode('light-mode');
            } else {
                setMode('dark-mode');
            }
        });
    }

    // Study Modes (Notes Page)
    const relaxModeBtn = document.getElementById('relax-mode');
    const deepModeBtn = document.getElementById('deep-mode');
    const examModeBtn = document.getElementById('exam-mode');

    if (relaxModeBtn) {
        relaxModeBtn.addEventListener('click', () => setMode('relax-mode'));
    }
    if (deepModeBtn) {
        deepModeBtn.addEventListener('click', () => setMode('deep-mode'));
    }
    if (examModeBtn) {
        examModeBtn.addEventListener('click', () => setMode('exam-mode'));
    }

    // AI Summary Trigger
    const aiBtn = document.getElementById('generate-summary');
    if (aiBtn) {
        aiBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const content = document.getElementById('notes-content').value;
            const resultBox = document.getElementById('ai-summary-result');
            const summaryDiv = document.getElementById('summary-content');
            
            // Get subject name to send to backend for fallback summary
            const subjectHeader = document.querySelector('.notes-header h2');
            const subject = subjectHeader ? subjectHeader.innerText : 'this subject';

            // Show loading
            aiBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            aiBtn.disabled = true;

            try {
                const response = await fetch('/generate-ai-summary', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ content: content, subject: subject })
                });
                
                const data = await response.json();
                
                // Display result
                summaryDiv.innerText = data.summary;
                resultBox.style.display = 'block';
                
            } catch (error) {
                console.error("Error generating summary:", error);
                alert("Failed to generate summary. Please try again.");
            } finally {
                // Reset button
                aiBtn.innerHTML = '<i class="fas fa-magic"></i> Generate AI Summary';
                aiBtn.disabled = false;
            }
        });
    }

    // Flash message auto disappear
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            });
        }, 4000);
    }
});

function setMode(modeClass) {
    body.className = modeClass;
    localStorage.setItem('notesflix_mode', modeClass);
}
