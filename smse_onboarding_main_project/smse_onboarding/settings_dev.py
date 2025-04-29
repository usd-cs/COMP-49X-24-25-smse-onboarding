from .settings import *
import os
import certifi
import ssl
import urllib3
from django.core.mail.backends.smtp import EmailBackend

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Custom email backend that ignores SSL verification
class CustomEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False
        try:
            # Create unverified SSL context
            context = ssl._create_unverified_context()
            
            # Create SMTP connection
            self.connection = self.connection_class(
                self.host, self.port,
                timeout=self.timeout
            )
            
            # Start TLS with unverified context
            if self.use_tls:
                self.connection.starttls(context=context)
            
            # Login if credentials are provided
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception:
            if not self.fail_silently:
                raise
            return False

# Override email settings for development
EMAIL_BACKEND = 'smse_onboarding.settings_dev.CustomEmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'usdsmse@gmail.com'
EMAIL_HOST_PASSWORD = 'avslwlzrooptdlbm'
DEFAULT_FROM_EMAIL = 'usdsmse@gmail.com'

# Configure SSL settings
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['CURL_CA_BUNDLE'] = certifi.where()
os.environ['PYTHONHTTPSVERIFY'] = '0'

# Configure SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Override CSRF settings for development
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_DOMAIN = None
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://0.0.0.0:8000',
]