import argparse
import base64
import json
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import os
from openai import OpenAI
import datetime
from dotenv import load_dotenv
import requests
import pyquery as pq

class Metadata:
    track_number: int
    title: str
    authors: list[str]
    album: str
    year: int
    duration: int
    artwork: str
    lyrics: str

def extract_lyrics_from_html(html: str) -> str:
    doc = pq.PyQuery(html)
    all_lyrics = doc("div[class^='Lyrics__Container']").text()
    return all_lyrics

def get_lyrics(author: str, title: str) -> str:
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    if client is None:
        return "None 1"
    
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

def get_metadata(audio_file_path):
    # Initial metadata dictionary
    metadata: Metadata = {
        "track_number": None,
        "title": None,
        "authors": None,
        "album": None,
        "year": None,
        "duration": None,
        "artwork": None,
        "lyrics": "Lyrics not found"  # Placeholder for lyrics
    }
    
    # Loading metadata from audio file
    if audio_file_path.endswith('.mp3'):
        audio = MP3(audio_file_path, ID3=EasyID3)
        id3 = ID3(audio_file_path)

         # Print all tags
        print("All tags:")
        for key, value in audio.items():
            print(f"{key}: {value}")

        # Extracting basic info
        metadata["track_number"] = audio["tracknumber"][0]
        metadata["title"] = audio["title"][0]
        metadata["authors"] = audio["artist"]
        metadata["album"] = audio["album"][0]
        metadata["year"] = datetime.datetime.strptime(audio["date"][0], '%Y-%m-%d').year
        metadata["duration"] = int(audio.info.length)
        
        # Extracting artwork
        for tag in id3.values():
            if isinstance(tag, APIC):
                artwork_data = tag.data
                metadata["artwork"] = base64.b64encode(artwork_data).decode('utf-8')
                break
            
    # Get lyrics
    if metadata["title"] and metadata["authors"]:
        metadata["lyrics"] = get_lyrics(metadata["authors"][0], metadata["title"])
    
    return metadata

def save_metadata_to_json(metadata, file_path):
    json_file_path = os.path.splitext(file_path)[0] + '.json'
    with open(json_file_path, 'w') as f:
        json.dump(metadata, f, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Extract metadata and lyrics from an audio file.")
    parser.add_argument("path", help="Path to the audio file (MP3/WAV)")
    args = parser.parse_args()
    
    # Extract metadata
    metadata = get_metadata(args.path)
    
    # Here you would add your logic to find and add lyrics to the metadata dictionary
    
    # Save metadata to a JSON file
    save_metadata_to_json(metadata, args.path)
    
    print(f"Metadata and lyrics saved to {os.path.splitext(args.path)[0] + '.json'}")


if __name__ == "__main__":
    load_dotenv()
    main()
