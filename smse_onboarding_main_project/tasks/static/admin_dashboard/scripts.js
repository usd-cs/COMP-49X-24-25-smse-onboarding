document.addEventListener('DOMContentLoaded', function() {
    // Handle missing images
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', function() {
            if (!this.getAttribute('data-error-handled')) {
                this.setAttribute('data-error-handled', 'true');
                // For profile image
                if (this.classList.contains('avatar')) {
                    this.src = 'https://ui-avatars.com/api/?name=Admin&background=1a237e&color=fff';
                }
                // For logo
                else if (this.classList.contains('logo')) {
                    this.src = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0iIzFhMjM3ZSIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1zaXplPSI0MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgYWxpZ25tZW50LWJhc2VsaW5lPSJtaWRkbGUiIGZpbGw9IndoaXRlIj5TTVM8L3RleHQ+PC9zdmc+';
                }
                // For flag
                else if (this.alt === 'English') {
                    this.src = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMjM1IDY1MCIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiPjxkZWZzPjxwYXRoIGlkPSJhIiBkPSJNMCAwaDEyMzV2NjUwSDB6Ii8+PC9kZWZzPjxjbGlwUGF0aCBpZD0iYiI+PHVzZSB4bGluazpocmVmPSIjYSIgb3ZlcmZsb3c9InZpc2libGUiLz48L2NsaXBQYXRoPjxwYXRoIGQ9Ik0wIDBoMTIzNXY2NTBIMHoiIGZpbGw9IiMwMDI0N2QiLz48cGF0aCBkPSJNMCAwdjcyLjlMMTEwMy40IDY1MGgxMzEuNnYtNzIuOUwyMzEuNiAwSDB6bTEyMzUgMHY3Mi45TDEzMS42IDY1MEgwdi03Mi45TDEwMDMuNCAwaDIzMS42eiIgZmlsbD0iI2ZmZiIgY2xpcC1wYXRoPSJ1cmwoI2IpIi8+PHBhdGggZD0iTTUxNC42IDBWNjUwaDIwNS44VjBINTE0LjZ6TTAgMjIyLjF2MjA1LjhoMTIzNVYyMjIuMUgweiIgZmlsbD0iI2ZmZiIgY2xpcC1wYXRoPSJ1cmwoI2IpIi8+PHBhdGggZD0iTTAgMjY0LjV2MTIxaDEyMzV2LTEyMUgwek01NTcgMHY2NTBoMTIxVjBINTU3eiIgZmlsbD0iI2NmMTQyYiIgY2xpcC1wYXRoPSJ1cmwoI2IpIi8+PHBhdGggZD0iTTAgMHY3Mi45TDEwMDMuNCAwSDB6bTAgNjUwbDEwMDMuNC02NTBIMTA2bDIuMiAxLjRMMCAxNDQuN1Y2NTB6TTEyMzUgMGwtODIuNCA1My4xTDEyMzUgODguOVYwek0xMjM1IDY1MEwyMzEuNiAwaDEwNC44TDEyMzUgNTA1LjN2MTQ0Ljd6IiBmaWxsPSIjY2YxNDJiIiBjbGlwLXBhdGg9InVybCgjYikiLz48L3N2Zz4=';
                }
            }
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