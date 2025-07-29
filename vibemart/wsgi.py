import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vibemart.settings')

application = get_wsgi_application()

# Vercel handler function
def handler(request):
    return application(request)

# Alternative app variable
app = application
