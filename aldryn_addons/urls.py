from django.conf import settings
from django.urls import include, re_path


def patterns():
    pats = [re_path(r"^", include(url)) for url in getattr(settings, "ADDON_URLS", [])]
    last_url = getattr(settings, "ADDON_URLS_LAST", None)
    if last_url:
        pats.append(re_path(r"^", include(last_url)))
    return pats


def i18n_patterns():
    pats = [
        re_path(r"^", include(url)) for url in getattr(settings, "ADDON_URLS_I18N", [])
    ]
    last_url = getattr(settings, "ADDON_URLS_I18N_LAST", None)
    if last_url:
        pats.append(re_path(r"^", include(last_url)))
    return pats
