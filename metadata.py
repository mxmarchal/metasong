
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import datetime
import os
import requests
import pyquery as pq

class Metadata:
    track_number: int
    title: str
    authors: list[str]
    album: str
    year: int
    duration: int
    artwork_description: str
    lyrics: str

    def __init__(self, track_number: int, title: str, authors: list[str], album: str, year: int, duration: int, artwork_description: str, lyrics: str):
        self.track_number = track_number
        self.title = title
        self.authors = authors
        self.album = album
        self.year = year
        self.duration = duration
        self.artwork_description = artwork_description
        self.lyrics = lyrics

def extract_lyrics_from_html(html: str) -> str:
    doc = pq.PyQuery(html)
    all_lyrics = doc("div[class^='Lyrics__Container']").text()
    return all_lyrics

def get_lyrics(author: str, title: str) -> str:
    # Seach for song on Genius
    search_url = f"https://api.genius.com/search?q={author} {title}"
    headers = {
        "Authorization": f"Bearer {os.environ.get('GENIUS_ACCESS_TOKEN')}"
    }
    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        return "None 2"
    json_response = response.json()
    
    # Get first hit
    hit = json_response["response"]["hits"][0]

    # Get lyrics from Genius
    lyrics_url = hit['result']['url']
    print(lyrics_url)
    response = requests.get(lyrics_url)
    #print(response.text)
    if response.status_code != 200:
        return "None 3"
    lyrics = extract_lyrics_from_html(response.text)
    return lyrics


def get_metadata(audio_file_path: str, album_artwork_description: str) -> Metadata:
        metadata = Metadata(
            track_number=0,
            title="",
            authors=[],
            album="",
            year=0,
            duration=0,
            artwork_description=album_artwork_description,
            lyrics="Lyrics not found"
        )

        # Loading metadata from audio file
        audio = MP3(audio_file_path, ID3=EasyID3)
        print("All tags:")
        for key, value in audio.items():
            print(f"{key}: {value}")

        # Extracting basic info
        metadata.track_number = audio["tracknumber"][0]
        metadata.title = audio["title"][0]
        metadata.authors = audio["artist"]
        metadata.album = audio["album"][0]
        metadata.year = datetime.datetime.strptime(audio["date"][0], '%Y-%m-%d').year
        metadata.duration = int(audio.info.length)

        # Get lyrics
        if metadata.title and metadata.authors:
            metadata.lyrics = get_lyrics(metadata.authors[0], metadata.title)
        
        return metadata