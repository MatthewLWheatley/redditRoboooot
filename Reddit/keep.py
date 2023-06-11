def create_video():
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
        dur = audio.info.length
        
        print(f"Mp3: {i}")
        print(f"Duration of current audio: {dur} seconds")
        print(f"Total duration so far: {total_duration} seconds")

        output_V = f"temp/video{i+1}.mp4"
        output_VA = f"temp/audio{i+1}.mp4"
        output_VAI = f"temp/temp{i+1}.mp4"
        
        Video = [
            'ffmpeg', '-y',
            '-i', input_mp4, 
            '-ss', str(total_duration), 
            '-t', str(dur),
            output_VAI
        ] 

        Audio = [
            'ffmpeg', '-y',
            '-i', output_V, 
            '-i', mp3s[i],
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-map', '0:v:0',
            '-map', '1:a:0', 
            output_VA
        ] 

        Image = [
            'ffmpeg', '-y',
            '-i', output_VA,
            '-i', pngs[i],
            '-filter_complex', 'overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2',
            output_VAI
        ] 
        subprocess.run(Video, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(.5)
        #subprocess.run(Audio, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(.5)
        #subprocess.run(Image, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(.5)
        total_duration += dur

    time.sleep(4)
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

    command = [
        'ffmpeg','-y',
        '-f', 'concat',  # Specify the concat demuxer
        '-safe', '0',  # Allow unsafe file paths
        '-i', 'temp/temp.txt',  # Input file is the file we just created
        '-c', 'copy',  # Copy the streams directly, no re-encoding
        'output/output.mp4'  # Output file
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)