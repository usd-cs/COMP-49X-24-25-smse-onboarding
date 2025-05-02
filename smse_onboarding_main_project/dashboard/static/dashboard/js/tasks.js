document.addEventListener('DOMContentLoaded', function() {
    // Task completion functionality for old forms
    const taskForms = document.querySelectorAll('.task-completion-form');
    taskForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            const taskItem = form.closest('.task-item') || form.closest('li');
            const isCompletingTask = form.action.includes('complete_task');

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateCircularProgress();
                    // If we're completing or uncompleting a task, refresh the page
                    // This ensures both tables are updated correctly
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });

    // New task checkboxes functionality
    const taskCheckboxes = document.querySelectorAll('.form-check-input[data-is-task="true"]');
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const taskId = this.id.split('-')[1];
            const action = this.checked ? 'complete_task' : 'continue_task';
            const url = `/dashboard/${action}/${taskId}/`;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateCircularProgress();
                    // Refresh the page to update the UI
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Revert checkbox state on error
                this.checked = !this.checked;
            });
        });
    });

    // Task action buttons (three dots menu)
    const taskActionButtons = document.querySelectorAll('.dropdown-item');
    taskActionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            if (this.textContent.includes('Mark as Complete')) {
                const checkbox = this.closest('tr').querySelector('.form-check-input[data-is-task="true"]');
                if (checkbox) {
                    checkbox.checked = true;
                    checkbox.dispatchEvent(new Event('change'));
                }
            } else if (this.textContent.includes('Mark as Incomplete')) {
                const checkbox = this.closest('tr').querySelector('.form-check-input[data-is-task="true"]');
                if (checkbox) {
                    checkbox.checked = false;
                    checkbox.dispatchEvent(new Event('change'));
                }
            }

            // Handle View Details action here if needed
        });
    });

    // Initial progress update
    updateCircularProgress();
});

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to update circular progress
function updateCircularProgress() {
    // If forceUpdateProgressCircle exists, use it (it's defined in status_card.html)
    if (window.forceUpdateProgressCircle) {
        window.forceUpdateProgressCircle();
    } else {
        // Fallback if the primary progress update function isn't available
        const circle = document.querySelector('#progressCircle');
        if (!circle) return;

        // Try to get server-provided data if available
        const progressText = document.querySelector('.progress-text div:last-child');
        const textMatch = progressText ? progressText.textContent.match(/(\d+)\s+of\s+(\d+)/) : null;
        
        if (textMatch && textMatch.length === 3) {
            // Use the values from the server-rendered text
            const completedTasks = parseInt(textMatch[1], 10);
            const totalTasks = parseInt(textMatch[2], 10);
            
            if (totalTasks > 0) {
                const percentage = (completedTasks / totalTasks);
                const circumference = 2 * Math.PI * 65; // 65 is the radius of the circle
                const offset = circumference * (1 - percentage);

                // Update the circle
                circle.style.strokeDasharray = circumference;
                circle.style.strokeDashoffset = offset;
            }
        }
    }
}
