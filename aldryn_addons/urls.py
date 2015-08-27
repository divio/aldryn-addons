# -*- coding: utf-8 -*-
from django.conf import settings, urls


def patterns():
    pats = [
        urls.url(r'^', urls.include(url))
        for url in getattr(settings, 'ADDON_URLS', [])
    ]
    last_url = getattr(settings, 'ADDON_URLS_LAST', None)
    if last_url:
        pats.append(
            urls.url(r'^', urls.include(last_url))
        )
    return pats


def i18n_patterns():
    pats = [
        urls.url(r'^', urls.include(url))
        for url in getattr(settings, 'ADDON_URLS_I18N', [])
    ]
    last_url = getattr(settings, 'ADDON_URLS_I18N_LAST', None)
    if last_url:
        pats.append(
            urls.url(r'^', urls.include(last_url))
        )
    return pats
