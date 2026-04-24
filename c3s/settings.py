"""Django settings for C3s."""
#  Copyright (C) 2026 twonum.org / Celeste.
#
#  This file is part of Celeste's Custom Can Storage (C3s).
#
#  C3s is free software: you can redistribute it and/or modify it under
#  the terms of the GNU Affero General Public License as published by the
#  Free Software Foundation, either version 3 of the License, or (at your
#  option) any later version.
#
#  C3s is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
#  License for more details.
#
#  You should have received a copy of the GNU Affero General Public
#  License along with C3s. If not, see <https://www.gnu.org/licenses/>.

# Some of this was copied from twonum.org's settings.py
# copyright 2025-2026 twonum.org / Celeste
# Affero General Public License version 3
# <https://github.com/twonfi/twonum.org>

from pathlib import Path
import os

from environ import Env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environ
env = Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    STATIC_ROOT=(str, ""),
    MEDIA_ROOT=(str, ""),
    SITE_ID=(int, 1),
    SERVER=(str, ""),
    PROXY_FILE=(bool, False),
    PROXY_FILE_PATH=(str, ""),
    # Email
    EMAIL_SMTP_HOST=(str, ""),
    EMAIL_SMTP_PORT=(int, 25),
    EMAIL_SMTP_HOST_USER=(str, ""),
    EMAIL_SMTP_HOST_PASSWORD=(str, ""),
    EMAIL_SMTP_USE_TLS=(bool, False),
    EMAIL_SMTP_USE_SSL=(bool, False),
    EMAIL_SMTP_SSL_CERTFILE=(str, None),
    EMAIL_SMTP_SSL_KEYFILE=(str, None),
    EMAIL_SMTP_TIMEOUT=(int, 3),
)
Env.read_env(os.path.join(BASE_DIR, ".env"))


def _env_file(key: str) -> str:
    env_ = env(key)

    if env_[:2] == "./":
        return str(BASE_DIR / env_[2:])
    return str(Path(env_))


SILENCED_SYSTEM_CHECKS = [
    # HTTPS-related stuff (handled by proxy/balancer)
    "security.W004",
    "security.W008",
]

DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "rest_framework",
    "canstorage.apps.CanStorageConfig",
    "info.apps.InfoConfig",
    "keyblade.apps.KeybladeConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "c3s.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "c3s.wsgi.application"


# Database
DATABASES = {"default": env.db()}

# Password/auth
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Chunk of allauth
ACCOUNT_ADAPTER = "c3s.adapters.NoSignupAccountAdapter"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_EMAIL_VERIFICATION = "optional" if DEBUG else "mandatory"
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = False if DEBUG else True
ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*", "password2*"]
LOGIN_REDIRECT_URL = "/"
MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]
MFA_PASSKEY_LOGIN_ENABLED = True if not DEBUG else False
MFA_PASSKEY_SIGNUP_ENABLED = True if not DEBUG else False

if DEBUG:
    MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = True

# More security stuff
if not DEBUG:
    CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE = True

# DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "keyblade.authentication.KeyAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# HTTPS
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-ca"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

if DEBUG:
    STATIC_URL = "static/"
    STATIC_ROOT = BASE_DIR / "staticroot"

    MEDIA_ROOT = BASE_DIR / "media"
else:
    STATIC_URL = env("STATIC_URL")
    STATIC_ROOT = _env_file("STATIC_ROOT")

    MEDIA_ROOT = _env_file("MEDIA_ROOT")

MEDIA_URL = ""  # C3s handles media

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # WhiteNoise is just a compressor; Caddy usually serves files
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Email
DEFAULT_FROM_EMAIL = env("EMAIL_FROM")
SERVER_EMAIL = env("EMAIL_FROM_SERVER")
match env("EMAIL_BACKEND"):
    case "smtp":
        EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
        EMAIL_HOST = env("EMAIL_SMTP_HOST")
        EMAIL_PORT = env("EMAIL_SMTP_PORT")
        EMAIL_HOST_USER = env("EMAIL_SMTP_HOST_USER")
        EMAIL_HOST_PASSWORD = env("EMAIL_SMTP_HOST_PASSWORD")
        EMAIL_USE_TLS = env("EMAIL_SMTP_USE_TLS")
        EMAIL_USE_SSL = env("EMAIL_SMTP_USE_SSL")
        EMAIL_SSL_CERTFILE = env("EMAIL_SMTP_SSL_CERTFILE")
        EMAIL_SSL_KEYFILE = env("EMAIL_SMTP_SSL_KEYFILE")
        EMAIL_TIMEOUT = env("EMAIL_SMTP_TIMEOUT")
    case "console":
        EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    case "dummy":
        EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

# Server hostname
SERVER = env("SERVER")

# Proxy file serving (also known as X-Accel-Redirect)
PROXY_FILE = env("PROXY_FILE")
if PROXY_FILE:
    PROXY_FILE_HEADER = env("PROXY_FILE_HEADER")
    PROXY_FILE_PATH = env("PROXY_FILE_PATH")
