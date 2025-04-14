// Welcome Modal Initialization
document.addEventListener('DOMContentLoaded', function() {
    // Fix for welcome modal
    const welcomeModal = document.getElementById('welcomeModal');
    if (welcomeModal) {
        try {
            // Move modal to body level to avoid stacking context issues
            if (welcomeModal.parentElement !== document.body) {
                document.body.appendChild(welcomeModal);
            }

            // Ensure Bootstrap is available
            if (typeof bootstrap !== 'undefined') {
                // Try standard Bootstrap modal initialization
                const modal = new bootstrap.Modal(welcomeModal);
                modal.show();
            } else {
                console.error("Bootstrap is not defined - using fallback solution");
                // Fallback solution if Bootstrap is not available
                welcomeModal.style.display = 'block';
                welcomeModal.classList.add('show');
                document.body.classList.add('modal-open');

                // Create backdrop
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);

                // Setup close buttons
                welcomeModal.querySelectorAll('[data-bs-dismiss="modal"]').forEach(btn => {
                    btn.addEventListener('click', function() {
                        welcomeModal.style.display = 'none';
                        welcomeModal.classList.remove('show');
                        document.body.classList.remove('modal-open');
                        document.body.style.overflow = '';
                        document.body.style.paddingRight = '';
                        backdrop.remove();
                    });
                });

                // Setup 'Got it!' button
                const gotItBtn = welcomeModal.querySelector('.modal-footer .btn-primary');
                if (gotItBtn) {
                    gotItBtn.addEventListener('click', function() {
                        // The link will handle the navigation/dismiss, but we still need to handle the modal UI
                        setTimeout(() => {
                            welcomeModal.style.display = 'none';
                            welcomeModal.classList.remove('show');
                            document.body.classList.remove('modal-open');
                            document.body.style.overflow = '';
                            document.body.style.paddingRight = '';
                            if (backdrop) backdrop.remove();
                        }, 100);
                    });
                }
            }
        } catch (error) {
            console.error("Error initializing welcome modal:", error);
        }
    }

    // For handling global click events on modal buttons
    document.body.addEventListener('click', function(e) {
        // Find the click target
        const target = e.target;

        // Check if close button was clicked
        if (target.classList.contains('btn-close') && target.closest('.modal')) {
            console.log("Close button click detected");
            const modal = target.closest('.modal');

            // Manually close modal
            modal.style.display = 'none';
            modal.classList.remove('show');
            document.body.classList.remove('modal-open');
            document.body.style.paddingRight = '';
            document.body.style.overflow = '';
            document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());

            e.stopPropagation();
            return;
        }

        // Check if Got it! button was clicked
        if (target.textContent.includes('Got it!') ||
            (target.closest('a') && target.closest('a').textContent.includes('Got it!'))) {
            console.log("'Got it!' button click detected");

            // Try to find dismiss_welcome URL
            const btn = target.tagName === 'A' ? target : target.closest('a');
            if (btn && btn.href && btn.href.includes('dismiss_welcome')) {
                // Submit dismiss request
                fetch(btn.href, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                }).then(() => {
                    console.log("Welcome banner dismissed via direct click handler");
                });

                // Manually close modal
                const modal = btn.closest('.modal');
                if (modal) {
                    modal.style.display = 'none';
                    modal.classList.remove('show');
                    document.body.classList.remove('modal-open');
                    document.body.style.paddingRight = '';
                    document.body.style.overflow = '';
                    document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
                }

                e.stopPropagation();
                return;
            }
        }
    }, true); // Use capture phase to ensure we get the event before other handlers
});
