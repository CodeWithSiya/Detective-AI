import pytest
import django
from django.conf import settings
from django.test.utils import get_runner

def pytest_configure(config):
    """Configure Django settings for pytest."""
    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        SITE_ID=1,
        SECRET_KEY='test-secret-key-for-testing-only',
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL='/static/',
        ROOT_URLCONF='config.urls',
        TEMPLATE_LOADERS=(
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ),
        TEMPLATE_CONTEXT_PROCESSORS=(
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ),
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ],
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'app',
        ],
        AUTH_USER_MODEL='app.User',
        PASSWORD_HASHERS=(
            'django.contrib.auth.hashers.MD5PasswordHasher',
        ),
    )
    django.setup()

@pytest.fixture(scope='session')
def django_db_setup():
    """Set up the test database."""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }