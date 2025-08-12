from .base import *
DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["danidorco.com"])
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
