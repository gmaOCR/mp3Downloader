import os
import shutil
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .models import Video
from pytube import YouTube
import subprocess

# Liste des formats disponibles
AVAILABLE_FORMATS = ['mp4', 'avi', 'mkv', 'mp3']


def save_video_info(link, output_format):
    # Sauvegarde le lien et le format de sortie dans la base de données
    video = Video(link=link, output_format=output_format)
    video.save()


def download_video_file(link, output_format):
    # Récupère la vidéo YouTube
    yt = YouTube(link)
    video_stream = yt.streams.get_highest_resolution()

    # Télécharge la vidéo dans le format choisi
    output_directory = os.path.join(settings.BASE_DIR, 'ytb_dl', 'download')
    os.makedirs(output_directory, exist_ok=True)
    video_path = video_stream.download(output_path=output_directory)

    if output_format == 'mp3':
        return convert_to_mp3_file(video_path, yt.title, output_directory)
    else:
        return rename_video_file(video_path, yt.title, output_directory)


def convert_to_mp3_file(video_path, video_title, output_directory):
    # Convertit la vidéo en MP3 256 kbps
    ffmpeg_path = os.path.join('..', 'ffmpeg', 'ffmpeg.exe')
    output_file = os.path.join(output_directory, f'{video_title}.mp3')
    command = [ffmpeg_path, '-i', video_path, '-vn', '-ab', '256k', output_file]
    subprocess.run(command)

    return output_file


def convert_to_specific_format(video_path, video_title, output_directory, output_format):
    # Convertit la vidéo dans le format spécifié en utilisant FFmpeg
    ffmpeg_path = os.path.join('..', 'ffmpeg', 'ffmpeg.exe')
    output_file = os.path.join(output_directory, f'{video_title}.{output_format}')
    command = [ffmpeg_path, '-i', video_path, '-c:v', 'copy', '-c:a', 'copy', output_file]
    subprocess.run(command)

    return output_file


def rename_video_file(video_path, video_title, output_directory):
    # Renomme la vidéo en conservant l'extension de fichier d'origine
    filename, file_extension = os.path.splitext(video_path)
    output_file = os.path.join(output_directory, f'{video_title}{file_extension}')
    shutil.move(video_path, output_file)

    return output_file

def download_video(request):
    if request.method == 'POST':
        link = request.POST['link']
        output_format = request.POST['output_format']

        if output_format in AVAILABLE_FORMATS:
            save_video_info(link, output_format)
            output_file = download_video_file(link, output_format)

            # Renvoie le fichier en tant que téléchargement dans le navigateur du client
            with open(output_file, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/octet-stream')
                response[
                    'Content-Disposition'] = f'attachment; filename="{os.path.basename(output_file)}"'

            # Supprime le fichier de sortie après l'envoi
            os.remove(output_file)

            return response
        else:
            return HttpResponse('Format de sortie non pris en charge')

    return render(request, 'download_form.html')