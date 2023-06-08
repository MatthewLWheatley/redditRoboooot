import subprocess

post_txt = "temp/post.txt"

# Define the command to run the other Python program
command = ['python', 'TikTokTTS.py',
           '--voice','en_uk_003',
           '--file',post_txt,
           '--path','temp'
           ]

# Run the command and capture the output
output = subprocess.run(command, universal_newlines=True)

# Print the output
print(output)