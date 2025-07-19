import os
from .base import *

# Load environment-specific settings
environment = os.getenv('DJANGO_ENV', 'development')

if environment == 'production':
    from .production import *
else:
    from .development import *
