import os
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from django.http import HttpResponseServerError

from .models import Video
from pytube import YouTube

# Liste des formats disponibles
AVAILABLE_FORMATS = ['mp4', 'avi', 'mkv', 'mp3']


def save_video_info(link, output_format):
    # Sauvegarde le lien et le format de sortie dans la base de données
    video = Video(link=link, output_format=output_format)
    video.save()


def download_video_file(link, output_format, download_file=True):
    # Récupère la vidéo YouTube
    yt = YouTube(link)
    video_stream = yt.streams.get_highest_resolution()

    # Télécharge la vidéo dans le format choisi
    output_directory = os.path.join(settings.BASE_DIR, 'ytb_dl', 'download')
    os.makedirs(output_directory, exist_ok=True)
    video_path = video_stream.download(output_path=output_directory)

    if output_format == 'mp3':
        return convert_to_mp3_file(video_path, yt.title, output_directory)
    elif output_format == 'mkv':
        return convert_to_mkv(video_path, yt.title, output_directory)
    elif output_format == 'avi':
        return convert_to_avi(video_path, yt.title, output_directory)
    elif output_format == 'mp4':
        return convert_to_mp4(video_path, yt.title, output_directory)


def convert_to_mp3_file(video_path, audio_title, output_directory):
    # Convertit l'audio en MP3 en utilisant MoviePy
    output_file = os.path.join(output_directory, f'{audio_title}.mp3')
    clip = AudioFileClip(video_path)
    clip.write_audiofile(output_file, codec='mp3', bitrate='256k')
    return output_file


def convert_to_mkv(video_path, video_title, output_directory):
    # Convertit la vidéo en MKV en utilisant MoviePy
    output_file = os.path.join(output_directory, f'{video_title}.mkv')
    clip = VideoFileClip(video_path)

    clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
    return output_file


def convert_to_avi(video_path, video_title, output_directory):
    # Convertit la vidéo en AVI en utilisant MoviePy avec le codec MPEG-4
    output_file = os.path.join(output_directory, f'{video_title}.avi')
    clip = VideoFileClip(video_path)
    clip.write_videofile(output_file, codec='mpeg4')
    return output_file


def convert_to_mp4(video_path, video_title, output_directory):
    # Convertit la vidéo en MP4 en utilisant MoviePy avec le codec 'h264'
    output_file = os.path.join(output_directory, f'{video_title}.mp4')
    clip = VideoFileClip(video_path)
    clip.write_videofile(output_file, codec='h264', audio_codec='aac')
    return output_file


def download_video(request):
    if request.method == 'POST':
        link = request.POST.get('link')
        output_format = request.POST.get('output_format')

        if output_format in AVAILABLE_FORMATS:
            save_video_info(link, output_format)
            output_file = download_video_file(link, output_format)

            if output_file and os.path.exists(output_file):
                with open(output_file, 'rb') as file:
                    response = HttpResponse(file.read(), content_type='application/octet-stream')

                output_filename = os.path.basename(output_file)
                response['Content-Disposition'] = f'attachment; filename="{output_filename}"'
                os.remove(output_file)  # Supprimer le fichier après utilisation
                return response
            else:
                return HttpResponseServerError("An error occurred during video conversion.")
    return render(request, 'download_form.html')
