"""
WSGI config for forwarding_audit project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'forwarding_audit.settings')

application = get_wsgi_application() 