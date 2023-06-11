import subprocess
import reddit
import os
import re
import textwrap
from mutagen.mp3 import MP3
import subprocess
import wave
import contextlib
from PIL import Image, ImageDraw, ImageFont, ImageOps
import random
import time
import shutil
from pydub import AudioSegment
import ffmpeg

post_txt = "temp/post.txt"
output_path = "output/"

def get_post():
    post_txt = "temp/post.txt"
    post = reddit.get_new_post()

    Text = post.title + "\n" + post.selftext
    Text = Text.strip()
    Texts = re.split(r'[.!?]\s+', Text)

    # Filter out empty sentences
    Texts = [sentence for sentence in Texts if sentence.strip()]

    To_proccess = []

    for string in Texts:
        if len(string) <= 200:
            To_proccess.append(string)
        else:
            words = string.split()
            adjusted_string = ''
            current_length = 0

            for word in words:
                if current_length + len(word) + 1 <= 200:  # Add 1 for the space
                    adjusted_string += word + ' '
                    current_length += len(word) + 1
                else:
                    current_length = len(word) + 1
                    To_proccess.append(adjusted_string.rstrip())
                    adjusted_string = word + ' '

            To_proccess.append(adjusted_string.rstrip())

    # for line in To_proccess:
    #     print(line)

    if not os.path.exists(post_txt):
        # Create the file
        with open(post_txt, "w") as file:
            for line in To_proccess:
                file.write(line+"\n")
            print(f"File '{post_txt}' created successfully!")
    else:
        with open(post_txt, "w") as file:
            for line in To_proccess:
                file.write(line+"\n")
            print(f"File '{post_txt}' overwriten successfully!")

def create_audio():
    post_txt = "temp/post.txt"
    # Define the command to run the other Python program
    voice_command = ['python', 'TikTokTTS.py',
               '--voice','en_uk_003',
               '--file', post_txt,
               '--path','temp'
               ]

    # Run the command and capture the output
    output = subprocess.run(voice_command, universal_newlines=True)

    # Print the output
    print(output)

    mp3s = []

    # Duration to remove from the beginning of each MP3 file (in milliseconds)
    duration_to_remove = 250  # 0.1 seconds

    for root, dirs, files in os.walk("temp"):
        for file in files:
            if file.endswith(".mp3"):
                mp3s.append(os.path.join("temp", file))
            
    mp3s.sort(key=natural_sort_key)

    # Load each MP3 file using pydub and remove the specified duration
    audio_segments = []
    for mp3_file in mp3s:
        audio_segment = AudioSegment.from_mp3(mp3_file)
        audio_segment = audio_segment[:-duration_to_remove]  # Remove the specified duration
        audio_segments.append(audio_segment)

    # Concatenate the audio segments
    merged_audio = audio_segments[0]
    for segment in audio_segments[1:]:
        merged_audio += segment

    # Export the merged audio as an MP3 file
    merged_audio.export("temp/merged.mp3", format="mp3", bitrate="256k")

def natural_sort_key(s):
    """Key function for natural sorting."""
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', s)]

def create_video():
    # Input file paths
    video_file = 'input/input.mp4'
    audio_file = 'temp/merged.mp3'

    # Output file path
    output_file = 'temp/no_subs.mp4'

    # Get duration of the audio file        
    audio = MP3(audio_file)
    audio_duration = audio.info.length

    # Generate a random start time within the audio duration
    start_time = random.uniform(0, audio_duration)

    # FFmpeg command to trim the video and add the audio
    command = [
            'ffmpeg', '-y',
            '-hardacc'
            '-i', video_file, 
            '-i', audio_file,
            '-shortest',
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-map', '0:v:0',
            '-map', '1:a:0', 
            output_file
        ] 
    subprocess.call(command, shell=True)

def clear_temp():
    directory = "temp"
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))



start_time = time.time()
#get_post()
create_audio()
create_video()
#clear_temp()

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")

