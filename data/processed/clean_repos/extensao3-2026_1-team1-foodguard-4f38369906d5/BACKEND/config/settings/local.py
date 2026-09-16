# ruff: noqa: E501
from .base import * # noqa: F403

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# APPS
# ------------------------------------------------------------------------------
INSTALLED_APPS += [
    "drf_spectacular",
    "django_browser_reload",
]

# REST FRAMEWORK
# ------------------------------------------------------------------------------
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"

# SPECTACULAR / SWAGGER SETTINGS
# ------------------------------------------------------------------------------
# https://drf-spectacular.readthedocs.io/en/latest/settings.html
SPECTACULAR_SETTINGS = {
    'TITLE': 'API FoodGuard',
    'DESCRIPTION': 'Documentação oficial dos endpoints do sistema FoodGuard.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}