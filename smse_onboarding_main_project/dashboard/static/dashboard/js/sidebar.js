// Sidebar toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    const navbar = document.querySelector('.navbar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            console.log('Sidebar toggle clicked'); // Debug log

            // Toggle collapsed class to switch between full and icon-only modes
            sidebar.classList.toggle('collapsed');

            // Adjust main content margin when sidebar is collapsed
            if (sidebar.classList.contains('collapsed')) {
                // Collapsed state - use narrower sidebar
                mainContent.style.marginLeft = 'var(--sidebar-collapsed-width, 70px)';
                mainContent.style.width = 'calc(100% - var(--sidebar-collapsed-width, 70px))';

                // Also adjust the navbar
                if (navbar) {
                    navbar.style.left = 'var(--sidebar-collapsed-width, 70px)';
                    navbar.style.width = 'calc(100% - var(--sidebar-collapsed-width, 70px))';
                }
            } else {
                // Expanded state - use full width sidebar
                mainContent.style.marginLeft = 'var(--sidebar-width, 280px)';
                mainContent.style.width = 'calc(100% - var(--sidebar-width, 280px))';

                // Also adjust the navbar
                if (navbar) {
                    navbar.style.left = 'var(--sidebar-width, 280px)';
                    navbar.style.width = 'calc(100% - var(--sidebar-width, 280px))';
                }
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

            // Also adjust the navbar for mobile
            if (navbar) {
                navbar.style.left = '0';
                navbar.style.width = '100%';
            }
        } else {
            // On desktop, maintain collapsed or expanded state
            if (sidebar && mainContent) {
                if (sidebar.classList.contains('collapsed')) {
                    mainContent.style.marginLeft = 'var(--sidebar-collapsed-width, 70px)';
                    mainContent.style.width = 'calc(100% - var(--sidebar-collapsed-width, 70px))';

                    // Also adjust the navbar for collapsed state
                    if (navbar) {
                        navbar.style.left = 'var(--sidebar-collapsed-width, 70px)';
                        navbar.style.width = 'calc(100% - var(--sidebar-collapsed-width, 70px))';
                    }
                } else {
                    mainContent.style.marginLeft = 'var(--sidebar-width, 280px)';
                    mainContent.style.width = 'calc(100% - var(--sidebar-width, 280px))';

                    // Also adjust the navbar for expanded state
                    if (navbar) {
                        navbar.style.left = 'var(--sidebar-width, 280px)';
                        navbar.style.width = 'calc(100% - var(--sidebar-width, 280px))';
                    }
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
