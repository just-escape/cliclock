import os

from django.core.wsgi import get_wsgi_application  # NOQA

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cliclock.settings")
application = get_wsgi_application()
