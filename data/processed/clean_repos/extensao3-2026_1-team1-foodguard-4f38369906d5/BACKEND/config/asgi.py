"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

application = get_asgi_application()

# Em desenvolvimento (uvicorn/ASGI não serve estáticos como o runserver),
# embrulha a app para servir os arquivos estáticos — necessário para o CSS do
# Django admin. Em produção, os estáticos são servidos pelo servidor web.
from django.conf import settings  # noqa: E402

if settings.DEBUG:
    from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler  # noqa: E402

    application = ASGIStaticFilesHandler(application)
