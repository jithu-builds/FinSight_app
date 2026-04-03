"""
Shared holder for the CookieManager instance.

app.py creates the CookieManager once per render and stores it here.
auth.py reads it from here. No circular imports, no duplicate instantiation.
"""

_cookie_manager = None


def set_cm(cm) -> None:
    global _cookie_manager
    _cookie_manager = cm


def get_cm():
    return _cookie_manager
