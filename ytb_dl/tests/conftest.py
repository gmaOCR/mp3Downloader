import pytest
from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup():
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'profiles',
            'downloader',
            'captcha',
            'django.contrib.sites',
        ],
    )
    settings.BASE_DIR = 'your_base_dir'  # Remplacez par le chemin de votre répertoire de base Django

    # Effectuez d'autres configurations spécifiques à votre projet si nécessaire

    # Laissez Django initialiser la base de données
    pytest_configure = pytest.importorskip("django").pytest_configure
    pytest_configure()

    yield

    # Fermez la base de données après les tests
    pytest_unconfigure = pytest.importorskip("django").pytest_unconfigure
    pytest_unconfigure()

