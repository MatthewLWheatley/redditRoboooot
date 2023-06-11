# ╭─────────────────────────── Import ───────────────────────────╮ #
import os
import json
import base64
import re
import argparse
import textwrap
import requests
from pydub import AudioSegment

# ╭─────────────────────────── Def Text to TikTok TTS ───────────────────────────╮ #
def texttotiktoktts(text, voice="en_us_001", path="", num = 1):
     cyan = "\033[0;36m"
     green = "\033[0;32m"
     red = "\033[0;31m"
     reset = "\033[0m"

     log_statut = True
     version = True

     # ╭─── Author ───╮ #
     try:
          # ╭─── Send a request to url ───╮ #
          # print(f'{reset}[{green}>{reset}] {green}A request has been sent to https://tiktok-tts.weilnet.workers.dev/api/generation{reset}') # Log Print
          response = requests.post('https://tiktok-tts.weilnet.workers.dev/api/generation', # TikTok API Voice Generation
               json={"text":text,"voice":voice}) # Data
          if log_statut == True:print(f'{reset}[{green}<{reset}] {green}The request has been received{reset}') # Log Print


          # ╭─── Read Json ───╮ #
          jsondata = json.loads(response.text) # Get response Json Data       
          error = jsondata["error"] # Get error data

          # ╭─── Audio conversion ───╮ #
          if error == None:
               audio_base64 = jsondata["data"] # Get audio in base64

               text = re.sub(r"[^a-zA-Z0-9]+", "", text) # Filter Export name
               if len(text) > 61:text = text[61:] # Export name

               # if log_statut == True:print(f'{reset}[{green}>{reset}] {green}convert audio base 64 to .mp3{reset}') # Log Print
               audio_data = base64.b64decode(audio_base64) # Decode in Base64
               # if log_statut == True:print(f'{reset}[{green}<{reset}] {green}the audio has been converted to mp3{reset}') # Log Print

               # ╭─── Write Audio ───╮ #
               if not os.path.exists(path):os.makedirs(path, exist_ok=True) # Create export folder
               with open(f'{path}/temp{num}.mp3', "wb") as file:
                    file.write(audio_data) # Write audio in mp3
               # if log_statut == True:print(f'{reset}[{green}+{reset}] {green}the "{text}" audio file has been exported to "{path}{text}".{reset}') # Log Print
               return True, path
          else:
               # print(f'{reset}[{red}-{reset}]{red}{error}{reset}') # Log Print
               return False, error
     except:return False, "An error has occurred"

def main():
    parser = argparse.ArgumentParser(description='TikTok TTS Command Line Interface')
    parser.add_argument('--text', help='Text input for TTS')
    parser.add_argument('--file', help='Path to a text file for TTS')
    parser.add_argument('--voice', default='en_us_001', help='Voice selection (default: en_us_001)')
    parser.add_argument('--path', default='', help='Export path for the audio files (default: current directory)')

    args = parser.parse_args()
    text = args.text
    file_path = args.file
    voice = args.voice
    path = args.path

    if text is None and file_path is None:
        print('Error: You must provide either a text input or a file path.')
        return

    if file_path is not None:
        try:
            with open(file_path, 'r') as file:
                text = file.readlines()
        except FileNotFoundError:
            print('Error: The specified file could not be found.')
            return
        
    count = 0
    for line in text:
        count += 1
        texttotiktoktts(line, voice, path, num=count)
 

    # Create a silent audio segment
    silence = AudioSegment.silent(duration=1000)  # 1000 milliseconds = 1 second

    count += 1
    # Export the silent audio segment as an MP3 file
    #silence.export("temp/temp"+str(count)+".mp3", format="mp3")

if __name__ == '__main__':
    main()
