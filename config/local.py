# -*- coding: utf-8 -*-
"""
Local settings for development environments
"""
import sys

from .base import *  # noqa

testing = env.bool("CI", default=False) or env.bool("TEST", default=False) or "test" in sys.argv

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=True)
if env.bool("CI", default=False):
    # Required by django_coverage_plugin
    TEMPLATES[0]["OPTIONS"]["debug"] = True
else:
    TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env("DJANGO_SECRET_KEY", default="((5)iob@s%#(3=@le*xd^hu^)4_btrz7zpq-e1=@wruddsl9+h")

# Mail settings
# ------------------------------------------------------------------------------
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_BACKEND = env("DJANGO_EMAIL_BACKEND",
                    default="django.core.mail.backends.console.EmailBackend")

# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": ""
    }
}

# django-debug-toolbar
# ------------------------------------------------------------------------------
if env.bool("DJANGO_DEBUG_TOOLBAR", default=True):
    DEBUG_TOOLBAR_ENABLED = True
    MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)
    INSTALLED_APPS += ("debug_toolbar", "debug_toolbar_user_panel")

    INTERNAL_IPS = ("127.0.0.1", "localhost")

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TEMPLATE_CONTEXT": True,
    }
    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar_user_panel.panels.UserPanel",
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ]

# RQ
# --
RQ_QUEUES["default"]["ASYNC"] = False

# The Federation
# ------------------------------------------------------------------------------
THEFEDERATION_HTTPS = False

# Extra tools for development
MIDDLEWARE += ("querycount.middleware.QueryCountMiddleware",)

# Tests
if testing:
    # Possibly wont conflict with anything..
    REDIS_DB = 15
