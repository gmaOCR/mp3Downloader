import os
import shutil
from io import BytesIO
from unittest import mock
from unittest.mock import patch, call

import pytest
from django.test import RequestFactory
from django.http import HttpResponse

from downloader import views

# Chemin vers le répertoire de téléchargement de test
TEST_DOWNLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "download"))

# Chemin vers le fichier de test
TEST_FILE_PATH = os.path.join(TEST_DOWNLOAD_DIR, "test_file.txt")


@pytest.fixture(params=['mp3', 'avi', 'mkv', 'mp4'])
def output_format(request):
    return request.param


@pytest.fixture(scope="session")
def video_file():
    # Crée le répertoire de téléchargement si nécessaire
    os.makedirs(TEST_DOWNLOAD_DIR, exist_ok=True)

    # Crée un fichier de test
    with open(TEST_FILE_PATH, "w") as file:
        file.write("Test content")

    yield TEST_FILE_PATH

    # Supprime le fichier de test après utilisation
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)
    shutil.rmtree(TEST_DOWNLOAD_DIR, ignore_errors=True)


@pytest.fixture(scope="session")
def audio_file():
    os.makedirs(TEST_DOWNLOAD_DIR, exist_ok=True)

    # Crée un fichier de test
    with open(TEST_FILE_PATH, "w") as file:
        file.write("Test audio file")
    yield TEST_FILE_PATH

    # Supprime le fichier de test après utilisation
    if os.path.exists(TEST_FILE_PATH):
        os.remove(TEST_FILE_PATH)
    shutil.rmtree(TEST_DOWNLOAD_DIR, ignore_errors=True)


def test_convert_to_mkv(video_file):
    video_title = "test_video"
    output_directory = TEST_DOWNLOAD_DIR
    output_file = views.convert_to_mkv(video_file, video_title, output_directory)
    assert os.path.exists(output_file)
    assert output_file.endswith(".mkv")


def test_convert_to_mp3_file(audio_file):
    audio_title = "test_audio"
    output_directory = TEST_DOWNLOAD_DIR
    # Créer un mock de la méthode `clip.write_audiofile` pour éviter la conversion réelle du
    # fichier audio
    with patch('moviepy.editor.AudioFileClip.write_audiofile') as mock_write_audiofile:
        # Appeler la méthode convert_to_mp3_file
        output_file = views.convert_to_mp3_file(audio_file, audio_title, output_directory)
        output_file = os.path.abspath(output_file)  # Obtenir le chemin absolu du fichier de sortie

        # Vérifier que le fichier de sortie a été créé avec le bon format
        assert output_file.endswith(".mp3")
        expected_path = os.path.normpath(os.path.join(output_directory, 'test_audio.mp3'))
        assert os.path.abspath(output_file) == expected_path

        # Vérifier que la méthode write_audiofile a été appelée avec les bons arguments
        mock_write_audiofile.assert_called_once_with(output_file, codec='mp3', bitrate='256k')


def test_convert_to_avi(video_file):
    video_title = "test_video"
    output_directory = TEST_DOWNLOAD_DIR
    output_file = views.convert_to_avi(video_file, video_title, output_directory)
    assert os.path.exists(output_file)
    assert output_file.endswith(".avi")


def test_convert_to_mp4(video_file):
    video_title = "test_video"
    output_directory = TEST_DOWNLOAD_DIR
    output_file = views.convert_to_mp4(video_file, video_title, output_directory)
    assert os.path.exists(output_file)
    assert output_file.endswith(".mp4")


@pytest.mark.parametrize('output_format', ['mp3', 'avi', 'mkv', 'mp4'])
def test_download_video(output_format):
    factory = RequestFactory()
    link = "https://www.example.com/video/VIDEO_ID"
    request = factory.post('/download', data={'link': link, 'output_format': output_format})

    # Mock save_video_info et download_video_file
    with patch('downloader.views.save_video_info') as mock_save_video_info, \
            patch('downloader.views.download_video_file') as mock_download_video_file, \
            patch('os.path.exists') as mock_exists, \
            patch('builtins.open', create=True) as mock_open, \
            patch('os.remove') as mock_remove:
        # Définir le comportement attendu des mocks
        mock_save_video_info.return_value = None
        mock_download_video_file.return_value = f'/path/to/output_file.{output_format}'
        mock_exists.return_value = True

        # Créer un objet BytesIO pour simuler le fichier ouvert
        mock_file_object = BytesIO(b'mock file content')
        mock_open.return_value.__enter__.return_value = mock_file_object
        mock_remove.return_value = None

        # Appeler la méthode à tester
        response = views.download_video(request)

        # Vérifier le comportement et les assertions
        assert isinstance(response, HttpResponse)
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/octet-stream'
        content_disposition = response['Content-Disposition']
        expected_disposition = f'attachment; filename="output_file.{output_format}"'
        assert content_disposition == expected_disposition

        # Vérifier que les méthodes ont été appelées avec les bons arguments
        mock_save_video_info.assert_called_once_with(link, output_format)
        mock_download_video_file.assert_called_once_with(link, output_format)
        mock_exists.assert_called_once_with(f'/path/to/output_file.{output_format}')
        mock_open.assert_called_once_with(f'/path/to/output_file.{output_format}', 'rb')
        mock_remove.assert_called_once_with(f'/path/to/output_file.{output_format}')


def test_save_video_info():
    link = "https://www.example.com/video/VIDEO_ID"
    output_format = "mp4"

    with patch('downloader.models.Video.save') as mock_save:
        views.save_video_info(link, output_format)

        # Vérifier que la méthode save a été appelée avec les bons arguments
        mock_save.assert_called_once()


@pytest.fixture
def expected_output():
    return "fake_output_path"


# @pytest.mark.parametrize("output_format, expected_output", [
#     ("mp3", "fake_output_path"),  # Modifier la valeur attendue en "fake_output_path"
#     ("mkv", "fake_output_path"),  # Modifier la valeur attendue en "fake_output_path"
#     ("avi", "fake_output_path"),  # Modifier la valeur attendue en "fake_output_path"
#     ("mp4", "fake_output_path"),  # Modifier la valeur attendue en "fake_output_path"
# ])
# def test_download_video_file(output_format, expected_output):
#     link = "https://www.youtube.com/watch?v=BpMp-DUOKeU"  # URL avec un format valide
#
#     with patch('pytube.YouTube') as mock_youtube, \
#             patch('downloader.views.convert_to_mp3_file') as mock_convert_to_mp3_file, \
#             patch('downloader.views.convert_to_mkv') as mock_convert_to_mkv, \
#             patch('downloader.views.convert_to_avi') as mock_convert_to_avi, \
#             patch('downloader.views.convert_to_mp4') as mock_convert_to_mp4:
#         # Définir le comportement attendu des mocks
#         mock_youtube.return_value.streams.get_highest_resolution.return_value = "mock_video_stream"
#         mock_convert_to_mp3_file.return_value = expected_output  # Utiliser la valeur attendue pour le mock
#         mock_convert_to_mkv.return_value = expected_output  # Utiliser la valeur attendue pour le mock
#         mock_convert_to_avi.return_value = expected_output  # Utiliser la valeur attendue pour le mock
#         mock_convert_to_mp4.return_value = expected_output  # Utiliser la valeur attendue pour le mock
#
#         output_file = views.download_video_file(link, output_format, download_file=False)
#
#         # Vérifier le comportement et les assertions
#         assert output_file == expected_output


@pytest.mark.parametrize("output_format, expected_output", [
    ("mp3", "fake_output_path"),  # Modifier la valeur attendue en "fake_output_path"
    ("mkv", "fake_output_path"),  # Modifier la valeur attendue en "fake_output_path"
    ("avi", "fake_output_path"),  # Modifier la valeur attendue en "fake_output_path"
    ("mp4", "fake_output_path"),  # Modifier la valeur attendue en "fake_output_path"
])
def test_download_video_file(output_format, expected_output):
    link = "https://www.youtube.com/watch?v=BpMp-DUOKeU"  # URL avec un format valide

    with patch('pytube.YouTube'), \
            patch.object(views, 'convert_to_mp3_file') as mock_convert_to_mp3_file, \
            patch.object(views, 'convert_to_mkv') as mock_convert_to_mkv, \
            patch.object(views, 'convert_to_avi') as mock_convert_to_avi, \
            patch.object(views, 'convert_to_mp4') as mock_convert_to_mp4:
        # Définir le comportement attendu des mocks
        mock_convert_to_mp3_file.return_value = "fake_output_path"
        mock_convert_to_mkv.return_value = "fake_output_path"
        mock_convert_to_avi.return_value = "fake_output_path"
        mock_convert_to_mp4.return_value = "fake_output_path"

        output_file = views.download_video_file(link, output_format, download_file=False)

        if output_format == 'mp3':
            assert mock_convert_to_mp3_file.called
        else:
            mock_convert_to_mp3_file.assert_not_called()

        if output_format == 'mkv':
            assert mock_convert_to_mkv.called
        else:
            mock_convert_to_mkv.assert_not_called()

        if output_format == 'avi':
            assert mock_convert_to_avi.called
        else:
            mock_convert_to_avi.assert_not_called()

        if output_format == 'mp4':
            assert mock_convert_to_mp4.called
        else:
            mock_convert_to_mp4.assert_not_called()

        # Vérifier le comportement et les assertions
        assert output_file == expected_output
