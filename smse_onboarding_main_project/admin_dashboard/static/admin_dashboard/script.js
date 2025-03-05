document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar on mobile
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show-sidebar');
        });
    }
    
    // Handle checkbox selection
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    const mainCheckboxes = document.querySelectorAll('thead input[type="checkbox"]');
    
    mainCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const table = this.closest('table');
            const bodyCheckboxes = table.querySelectorAll('tbody input[type="checkbox"]');
            
            bodyCheckboxes.forEach(box => {
                box.checked = this.checked;
            });
        });
    });
    
    // Handle notification clicks
    const notifyButtons = document.querySelectorAll('.notify-btn');
    
    notifyButtons.forEach(button => {
        button.addEventListener('click', function() {
            // In a real application, this would trigger a notification
            alert('Notification sent!');
        });
    });
    
    // Handle edit buttons
    const editButtons = document.querySelectorAll('.edit-btn');
    
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const name = row.querySelector('td:nth-child(2)').textContent;
            
            // In a real application, this would open an edit form
            alert(`Edit ${name}'s information`);
        });
    });
    
    // Progress bar animation
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0';
        
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = width;
        }, 100);
    });
}); 