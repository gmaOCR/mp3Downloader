import pytest
import tempfile
from django.http import HttpResponse
from downloader.views import download_video


@pytest.mark.django_db
def test_download_video(request_factory, sample_video, mocker):
    # Crée une requête POST de test avec les données requises pour le format 'mp4'
    data_mp4 = {'link': 'https://www.example.com/video', 'output_format': 'mp4'}
    request_mp4 = request_factory.post('/download/', data_mp4)

    # Mocke les objets et méthodes nécessaires
    mocked_youtube_instance = mocker.MagicMock()
    mocked_youtube = mocker.patch('downloader.views.YouTube', return_value=mocked_youtube_instance)
    mocked_stream_query = mocker.MagicMock()
    mocked_youtube_instance.streams = mocked_stream_query
    mocked_stream = mocker.MagicMock()
    mocked_stream_query.get_highest_resolution.return_value = mocked_stream

    # Crée un fichier vidéo temporaire
    with tempfile.NamedTemporaryFile(suffix='.mp4') as temp_file:
        mocked_stream.download.return_value = temp_file.name

        # Appelle la vue de téléchargement pour le format 'mp4'
        response_mp4 = download_video(request_mp4)

        # Vérifie que la vue renvoie une réponse HttpResponse
        assert isinstance(response_mp4, HttpResponse)

        # Vérifie que les méthodes et fonctions nécessaires ont été appelées avec les bons arguments pour le format 'mp4'
        mocked_youtube.assert_called_once_with('https://www.example.com/video')
        mocked_youtube_instance.streams.get_highest_resolution.assert_called_once()
        mocked_stream.download.assert_called_once()

        # Vérifie le contenu de la réponse
        assert response_mp4.content == b'Fake video content'
