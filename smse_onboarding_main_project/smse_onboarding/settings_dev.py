from .settings import *

# Override email settings for development
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'usdsmse@gmail.com'
EMAIL_HOST_PASSWORD = 'avslwlzrooptdlbm'
DEFAULT_FROM_EMAIL = 'usdsmse@gmail.com'

# Disable SSL verification for development
import ssl
ssl._create_default_https_context = ssl._create_unverified_context 