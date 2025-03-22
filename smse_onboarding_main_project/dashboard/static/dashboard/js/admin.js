// TODO: need to move all JavaScript from admin_tasks.html and other files here
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle
    document.querySelector('.menu-toggle').addEventListener('click', function() {
        document.querySelector('.sidebar').classList.toggle('collapsed');
    });

    // Task toggle functionality
    setupTaskToggles();
});

function setupTaskToggles() {
    // Move task toggle code from admin_tasks.html
}

// Other functions...
