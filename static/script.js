const examples = {
    calculator: {
        task: 'beautiful-calculator',
        brief: 'Create a beautiful calculator web application with basic arithmetic operations (+, -, *, /), clear and delete buttons, keyboard support, and a modern gradient design with smooth animations',
        checks: 'responsive, keyboard-support, animations',
        nonce: `calc-${Date.now()}`
    },
    todo: {
        task: 'todo-list-app',
        brief: 'Build a todo list application with the ability to add, complete, and delete tasks. Include localStorage for persistence, task categories (work, personal, shopping), dark mode toggle, and priority levels',
        checks: 'localStorage, dark-mode, categories',
        nonce: `todo-${Date.now()}`
    },
    portfolio: {
        task: 'personal-portfolio',
        brief: 'Design a personal portfolio website with sections for About Me, Projects showcase with live demos, Skills with proficiency bars, and a Contact form. Use modern design with smooth scroll and interactive elements',
        checks: 'responsive, smooth-scroll, contact-form',
        nonce: `portfolio-${Date.now()}`
    }
};

function fillExample(type) {
    const example = examples[type];
    if (!example) return;

    document.getElementById('task').value = example.task;
    document.getElementById('brief').value = example.brief;
    document.getElementById('checks').value = example.checks;
    document.getElementById('nonce').value = example.nonce;
    
    document.getElementById('appForm').scrollIntoView({ behavior: 'smooth' });
}

document.getElementById('appForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    const responseContainer = document.getElementById('responseContainer');
    const responseContent = document.getElementById('responseContent');
    
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    
    const formData = {
        email: document.getElementById('email').value,
        secret: document.getElementById('secret').value,
        task: document.getElementById('task').value,
        round: parseInt(document.getElementById('round').value),
        nonce: document.getElementById('nonce').value,
        brief: document.getElementById('brief').value,
        checks: document.getElementById('checks').value.split(',').map(s => s.trim()).filter(s => s),
        evaluation_url: document.getElementById('evaluation_url').value,
    };
    
    const attachmentsText = document.getElementById('attachments').value.trim();
    if (attachmentsText) {
        formData.attachments = attachmentsText.split('\n').map(s => s.trim()).filter(s => s);
    }
    
    try {
        const response = await fetch('/api-endpoint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        responseContainer.style.display = 'block';
        responseContent.className = 'response-content';
        
        if (response.ok) {
            responseContent.classList.add('response-success');
            responseContent.innerHTML = `
                <div style="margin-bottom: 1.5rem;">
                    <span class="status-badge status-success">✓ Success</span>
                    <strong style="font-size: 1.1rem;">${data.message || 'Request submitted successfully!'}</strong>
                </div>
                <div style="margin-top: 1.5rem; padding: 1.5rem; background: rgba(99, 102, 241, 0.08); border-radius: 0.75rem; border: 1px solid rgba(99, 102, 241, 0.2);">
                    <p style="margin-bottom: 0.75rem;"><strong>📦 Task:</strong> <code style="background: rgba(99, 102, 241, 0.2); padding: 0.25rem 0.5rem; border-radius: 0.25rem;">${data.task}</code></p>
                    <p style="margin-bottom: 1rem;"><strong>🔄 Round:</strong> ${data.round}</p>
                    <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(16, 185, 129, 0.1); border-radius: 0.5rem; border-left: 3px solid var(--success);">
                        <p style="margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.95rem;">
                            <strong>🔄 Processing:</strong> Your app is being generated and deployed in the background.
                        </p>
                        <p style="margin-bottom: 0.5rem; color: var(--text-muted); font-size: 0.95rem;">
                            <strong>📧 Notification:</strong> Check your evaluation URL for deployment details.
                        </p>
                        <p style="color: var(--text-muted); font-size: 0.95rem;">
                            <strong>🌐 Live URL:</strong> <code style="background: rgba(99, 102, 241, 0.2); padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.85rem;">https://[username].github.io/${data.task}/</code>
                        </p>
                    </div>
                </div>
            `;
        } else {
            responseContent.classList.add('response-error');
            responseContent.innerHTML = `
                <div style="margin-bottom: 1rem;">
                    <span class="status-badge status-error">✗ Error</span>
                    <strong style="font-size: 1.1rem;">Request Failed</strong>
                </div>
                <pre style="margin-top: 1rem; white-space: pre-wrap; background: rgba(239, 68, 68, 0.1); padding: 1rem; border-radius: 0.5rem;">${JSON.stringify(data, null, 2)}</pre>
            `;
        }
        
        responseContainer.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        responseContainer.style.display = 'block';
        responseContent.className = 'response-content response-error';
        responseContent.innerHTML = `
            <div style="margin-bottom: 1rem;">
                <span class="status-badge status-error">✗ Network Error</span>
                <strong style="font-size: 1.1rem;">Connection Failed</strong>
            </div>
            <p style="margin-top: 1rem; color: var(--text-muted);">${error.message}</p>
            <div style="margin-top: 1rem; padding: 1rem; background: rgba(239, 68, 68, 0.1); border-radius: 0.5rem;">
                <p style="font-size: 0.9rem; color: var(--text-muted);">
                    <strong>💡 Tip:</strong> Make sure the server is running and accessible.
                </p>
            </div>
        `;
        responseContainer.scrollIntoView({ behavior: 'smooth' });
    } finally {
        submitBtn.disabled = false;
        btnText.style.display = 'flex';
        btnLoader.style.display = 'none';
    }
});

// Auto-generate nonce on page load
window.addEventListener('load', () => {
    const nonceField = document.getElementById('nonce');
    if (!nonceField.value) {
        nonceField.value = `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
    
    // Add smooth scroll to form on example click
    document.querySelectorAll('.example-card').forEach(card => {
        card.addEventListener('click', () => {
            setTimeout(() => {
                document.getElementById('brief').focus();
            }, 500);
        });
    });
});
