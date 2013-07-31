# -*- coding: utf-8 -*-
from django.conf import settings as site_settings


DEFAULT_SETTINGS = {
    'MODEL_SETTINGS': {}
}

USER_SETTINGS = DEFAULT_SETTINGS.copy()
USER_SETTINGS.update(getattr(site_settings, 'OBJECTDUMP_SETTINGS', {}))

globals().update(USER_SETTINGS)
