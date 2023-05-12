import subprocess
import os
from dataclasses import dataclass

# Defines Song dataclass
@dataclass
class Song:
    file_name: str
    artist: str
    title: str
    duration: int

# Defines function to download requested song
def dl(song,id) -> Song:
    # Creates folder to store songs for specific server
    path = str(id) +'_songs'
    if os.path.isdir(path) == False:
        os.mkdir(path)

    # Uses yt-dlp to search for and downloads the song
    our_list = subprocess.check_output(["yt-dlp", "--default-search", "ytsearch", "--print", "%(channel)s_--_%(duration)s_--_%(title)s", song], encoding='utf-8').strip().split('_--_')
    subprocess.run(["yt-dlp", "-P", f"{path}", "-o", f"{our_list[2]}.%(ext)s",  "-x", "--audio-format", "wav", "--default-search", "ytsearch", song])

    # Create a Song object with information about the downloaded song
    found_song = Song(
        file_name=f"{our_list[2]}.wav",
        artist=our_list[0],
        title=our_list[2],
        duration=int(our_list[1])
    )
    found_song

    # Returns the Song object to main program
    return found_song
