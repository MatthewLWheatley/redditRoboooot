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
import string

post_txt = "temp/post.txt"
output_path = "output/"

def get_post():
    
    post = reddit.get_new_post()

    Text = post.selftext
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
                if current_length + len(word) + 1 <= 100:  # Add 1 for the space
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
            file.write(post.title + "\n")
            for line in To_proccess:
                file.write(line+"\n")
            print(f"File '{post_txt}' created successfully!")
    else:
        with open(post_txt, "w") as file:
            file.write(post.title + "\n")
            for line in To_proccess:
                file.write(line+"\n")
            print(f"File '{post_txt}' overwriten successfully!")

def create_audio():

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

def round_corners(image: Image.Image, radius: int) -> Image.Image:
    """
    Round the corners of a PIL image.
    :param image: The image to round.
    :param radius: The radius of the rounded corners.
    :return: The rounded image.
    """
    # Create a mask of the same size as the image, filled with black
    mask = Image.new('L', image.size, 0)

    # Draw a white rounded rectangle onto the mask
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), mask.size], radius=radius, fill=255)

    # Composite the mask onto the original image
    result = Image.composite(image, Image.new('RGBA', image.size), mask)

    return result

def create_picture():
    image_width = 880
    text_margin = 50
    post_txt = "temp\\post.txt"
    Lines = []
    with open(post_txt, "r") as file:
        Lines = file.readlines()

    count = 0
    for Line in Lines:
        count += 1
        font = ImageFont.truetype("arial", 56)
        chunks = textwrap.wrap(Line, width=(image_width - 2 * text_margin) // (font.getbbox('n')[2] - font.getbbox('n')[0]))
        
        # Calculate total height of all lines of text
        total_text_height = 0
        for chunk in chunks:
            total_text_height += (font.getbbox(chunk)[3] - font.getbbox(chunk)[1])

        text_height = total_text_height

        # Generate a random background color
        background_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 128)

        # Add the padding to the image height
        image = Image.new("RGBA", (image_width, text_height + 2 * text_margin), background_color)
        draw = ImageDraw.Draw(image)

        y_text = text_margin
        for chunk in chunks:
            bbox = font.getbbox(chunk)
            width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x_text = (image_width - width) // 2  # Change is here

            # Create the outline by drawing the text in black with offsets
            for adj in range(-2, 3):
                draw.text((x_text + adj, y_text - adj), chunk, font=font, fill="black")
                draw.text((x_text + adj, y_text + adj), chunk, font=font, fill="black")
            # Draw the text in white over the outline
            draw.text((x_text, y_text), chunk, font=font, fill="white")

            y_text += height

        # Round the corners of the image
        image = round_corners(image, radius=50)

        # Save the image to a file
        image.save("temp\\temp"+str(count)+".png")

def natural_sort_key(s):
    """Key function for natural sorting."""
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', s)]

def create_video():
    output_path = "output/"
    input_mp4 = "input/input.mp4"
    mp3s = []
    pngs = []
    mp4s = []
    
    for root, dirs, files in os.walk("temp"):
        for file in files:
            if file.endswith(".mp3"):
                mp3s.append(os.path.join("temp", file))
            elif file.endswith(".png"):
                pngs.append(os.path.join("temp", file))
            elif file.endswith(".mp4"):
                mp4s.append(os.path.join("temp",file))

    total_duration = 0

    mp3s.sort(key=natural_sort_key)
    pngs.sort(key=natural_sort_key)
    mp4s.sort(key=natural_sort_key)

    for i in range(len(mp3s)):
        audio = MP3(mp3s[i])
        dur = audio.info.length-0.25
        
        print(f"Mp3: {i}")
        print(f"Duration of current audio: {dur} seconds")
        print(f"Total duration so far: {total_duration} seconds")

        output_V = f"temp/video{i+1}.mp4"
        output_VA = f"temp/audio{i+1}.mp4"
        output_VAI = f"temp/temp{i+1}.mp4"
        
        Video = [
            'ffmpeg', '-y',
            '-hwaccel', 'cuda',
            '-i', input_mp4, 
            '-ss', str(total_duration), 
            '-t', str(dur),
            output_V
        ] 

        Audio = [
            'ffmpeg', '-y',
            '-hwaccel', 'cuda',
            '-i', output_V, 
            '-i', mp3s[i],
            '-shortest',
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-map', '0:v:0',
            '-map', '1:a:0', 
            output_VA
        ] 

        Image = [
            'ffmpeg', '-y',
            '-hwaccel', 'cuda',
            '-i', output_VA,
            '-i', pngs[i],
            '-filter_complex', 'overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2',
            output_VAI
        ]

        subprocess.run(Video, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(.5)
        subprocess.run(Audio, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(.5)
        subprocess.run(Image, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(.5)
        total_duration += dur
    mp4s = []

    for root, dirs, files in os.walk("temp"):
        for file in files:
            if file.endswith(".mp4"):
                if file.startswith("temp"):
                    mp4s.append(file)

    mp4s.sort(key=natural_sort_key)

    with open('temp/temp.txt', 'w') as f:
        for video in mp4s:
            f.write(f"file '{video}'\n")

    with open(post_txt, 'r') as file:
        first_line = file.readline().strip()
    # Remove punctuation from the first line
    first_line = first_line.translate(str.maketrans("", "", string.punctuation))

    output_file = os.path.join(output_path, first_line + '.mp4')

    command = [
        'ffmpeg','-y',
        '-hwaccel', 'cuda',
        '-f', 'concat',  # Specify the concat demuxer
        '-safe', '0',  # Allow unsafe file paths
        '-i', 'temp/temp.txt',  # Input file is the file we just created
        '-c', 'copy',  # Copy the streams directly, no re-encoding
        output_file  # Output file
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


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


for i in range(10):
    print("run: {i}")
    post_txt = "temp/post.txt"

    start_time = time.time()
    get_post()
    create_picture()
    create_audio()
    create_video()
    clear_temp()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")

