document.addEventListener('DOMContentLoaded', () => {

    // 1. Study Modes Handler
    const studyModeSelect = document.getElementById('study-mode');
    if (studyModeSelect) {
        // Load saved mode or default
        const savedMode = localStorage.getItem('studyMode') || 'default';
        document.body.setAttribute('data-study-mode', savedMode);
        studyModeSelect.value = savedMode;

        studyModeSelect.addEventListener('change', (e) => {
            const mode = e.target.value;
            document.body.setAttribute('data-study-mode', mode);
            localStorage.setItem('studyMode', mode);
        });
    }

    // 2. Flash Messages Auto-hide
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 300);
        }, 5000);
    });

    // 3. AI Summarizer handler
    const btnGenerateAi = document.getElementById('btn-generate-ai');
    if (btnGenerateAi) {
        btnGenerateAi.addEventListener('click', async () => {
            const aiResultBox = document.getElementById('ai-result-box');
            const aiSpinner = document.getElementById('ai-spinner');
            const aiSummaryText = document.getElementById('ai-summary-text');
            
            // Gather all user notes from the DOM
            const noteElements = document.querySelectorAll('.note-content');
            let fullContent = '';
            noteElements.forEach(el => fullContent += el.textContent + ' ');

            if (fullContent.trim() === '') {
                alert("You need to add some notes first before generating a summary!");
                return;
            }

            aiResultBox.classList.remove('hidden');
            aiSpinner.classList.remove('hidden');
            aiSummaryText.textContent = '';
            btnGenerateAi.disabled = true;

            try {
                const response = await fetch('/api/summarize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ content: fullContent })
                });
                
                const data = await response.json();
                aiSpinner.classList.add('hidden');
                
                // Typing effect for the AI summary
                let i = 0;
                const txt = data.summary;
                function typeWriter() {
                    if (i < txt.length) {
                        aiSummaryText.innerHTML += txt.charAt(i);
                        i++;
                        setTimeout(typeWriter, 15);
                    }
                }
                typeWriter();

            } catch (error) {
                console.error('Error generating summary:', error);
                aiSpinner.classList.add('hidden');
                aiSummaryText.textContent = 'Failed to generate summary. Please try again.';
            } finally {
                btnGenerateAi.disabled = false;
            }
        });
    }

});

// Global Window functions

// Netflix horizontal scroll slider
window.scrollSlider = function(sliderId, direction) {
    const slider = document.querySelector(`#${sliderId} .slider-content`);
    const scrollAmount = 300; // width of a card roughly
    if (slider) {
        slider.scrollBy({ left: scrollAmount * direction, behavior: 'smooth' });
    }
}

// Inline edit toggler
window.toggleEdit = function(noteId) {
    const content = document.getElementById(`note-content-${noteId}`);
    const form = document.getElementById(`edit-form-${noteId}`);
    const actions = document.getElementById(`actions-${noteId}`);
    
    if (form.classList.contains('hidden')) {
        content.classList.add('hidden');
        actions.classList.add('hidden');
        form.classList.remove('hidden');
    } else {
        content.classList.remove('hidden');
        actions.classList.remove('hidden');
        form.classList.add('hidden');
    }
}

// Add to My List via fetch API
window.addToList = async function(subjectId) {
    try {
        const response = await fetch(`/add_to_list/${subjectId}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            alert(data.message); // Could be improved with a custom toast
        } else {
            alert(data.error || 'Please login first.');
            if(response.status === 401) {
                window.location.href = '/login';
            }
        }
    } catch (error) {
        console.error('Error adding to list:', error);
    }
}
