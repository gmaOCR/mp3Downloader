import pytest
from django.test import RequestFactory
from downloader.models import Video
from pytube import YouTube, StreamQuery, Stream
from unittest.mock import MagicMock


pytest_plugins = ['pytest_mock']

@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def sample_video():
    # Crée un objet Video de test
    video = Video(link='https://www.example.com/video', output_format='mp4')
    video.save()
    return video



@pytest.fixture
def mocked_youtube(mocker):
    # Mocke la méthode YouTube pour éviter les requêtes réseau
    mocked_yt = mocker.MagicMock(spec=YouTube)
    mocked_yt.title = 'Test Video'

    # Définir le comportement de la méthode streams pour renvoyer un objet StreamQuery
    streams_query = mocker.MagicMock(spec=StreamQuery)
    mocked_yt.streams = mocker.MagicMock(return_value=streams_query)

    # Définir le comportement de la méthode get_highest_resolution sur l'objet StreamQuery
    highest_resolution_stream = mocker.MagicMock(spec=Stream)
    streams_query.get_highest_resolution = mocker.MagicMock(return_value=highest_resolution_stream)

    return mocked_yt


@pytest.fixture
def mocked_ffmpeg(mocker):
    # Mocke les méthodes ffmpeg.input et ffmpeg.output pour éviter les appels réels
    mocked_ffmpeg = mocker.patch('downloader.views.ffmpeg')
    return mocked_ffmpeg


@pytest.fixture
def mocked_shutil(mocker):
    # Mocke la méthode shutil.move pour éviter les opérations de déplacement réelles
    mocked_shutil = mocker.patch('downloader.views.shutil.move')
    return mocked_shutil


@pytest.fixture
def mocked_open(mocker):
    # Mocke la fonction open pour éviter la lecture de fichiers réels
    mocked_file = mocker.mock_open()
    mocker.patch('downloader.views.open', mocked_file)
    return mocked_file
