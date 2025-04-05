"""
WSGI config for bloodbankmanagement project.
"""

import os
import sys

# Add the current directory and parent directory to the Python path
current_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, current_dir)

# Explicitly set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodbankmanagement.settings')

# Create the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
