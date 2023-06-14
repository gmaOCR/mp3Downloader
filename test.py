import os
import subprocess


def convert_to_mp3(input_file, output_file, bitrate='256k'):
    ffmpeg_path = os.path.join('ffmpeg', 'ffmpeg.exe')
    command = [ffmpeg_path, '-i', input_file, '-vn', '-ab', bitrate, output_file]
    subprocess.run(command)


# Exemple d'utilisation
input_file = 'Retreat.mp4'
output_file = 'audio.mp3'

convert_to_mp3(input_file, output_file)
