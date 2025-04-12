// Sidebar toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            console.log('Sidebar toggle clicked'); // Debug log
            
            // Toggle collapsed class to switch between full and icon-only modes
            sidebar.classList.toggle('collapsed');
            
            // Adjust main content margin when sidebar is collapsed
            if (sidebar.classList.contains('collapsed')) {
                mainContent.style.marginLeft = 'var(--sidebar-collapsed-width, 70px)';
                mainContent.style.width = 'calc(100% - var(--sidebar-collapsed-width, 70px))';
            } else {
                mainContent.style.marginLeft = 'var(--sidebar-width, 280px)';
                mainContent.style.width = 'calc(100% - var(--sidebar-width, 280px))';
            }
        });
    }

    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth < 1200) {
            // On mobile view, switch to mobile behavior
            if (mainContent) {
                mainContent.style.marginLeft = '0';
                mainContent.style.width = '100%';
            }
        } else {
            // On desktop, maintain collapsed or expanded state
            if (sidebar && mainContent) {
                if (sidebar.classList.contains('collapsed')) {
                    mainContent.style.marginLeft = 'var(--sidebar-collapsed-width, 70px)';
                    mainContent.style.width = 'calc(100% - var(--sidebar-collapsed-width, 70px))';
                } else {
                    mainContent.style.marginLeft = 'var(--sidebar-width, 280px)';
                    mainContent.style.width = 'calc(100% - var(--sidebar-width, 280px))';
                }
            }
        }
    });
});

// Initialize tooltips for Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('.tt'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    } else {
        console.warn('Bootstrap tooltip not available');
    }
}); 
