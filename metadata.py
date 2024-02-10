
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import datetime
import os
import requests
import pyquery as pq
from openai import OpenAI
import json

class Metadata:
    class Sentiment:
        themes: list[str]
        keywords: list[str]

        def __init__(self, themes: list[str], keywords: list[str]):
            self.themes = themes
            self.keywords = keywords

        def to_dict(self):
            return {
                'themes': self.themes,
                'keywords': self.keywords
            }

    uuid: str
    track_number: int
    title: str
    authors: list[str]
    album: str
    year: int
    duration: int
    artwork_description: str
    lyrics: str
    sentiment: Sentiment
    vectors: list[float]

    def __init__(self, uuid: str, track_number: int, title: str, authors: list[str], album: str, year: int, duration: int, artwork_description: str, lyrics: str, sentiment: Sentiment, vectors: list[float]):
        self.uuid = uuid if uuid else str(uuid.uuid4())
        self.track_number = track_number
        self.title = title
        self.authors = authors
        self.album = album
        self.year = year
        self.duration = duration
        self.artwork_description = artwork_description
        self.lyrics = lyrics
        self.sentiment = sentiment
        self.vectors = vectors

def _get_sentiment_from_lyrics(lyrics: str) -> str:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "I'm going to give you lyrics of a song. You'll have to ouput me the response in a JSON format, no other conversation or words, just the list. I want 2 keys - themes: a list describing the feeling, mood and themes of the lyrics (only words, no sentence) -keywords: a list of important words found in the lyrics (like in the chorus, only words, no sentence). You must give me the anwser in English."
            },
            {
                "role": "user",
                "content": lyrics
            }
        ],
        model="gpt-3.5-turbo-0125",
        response_format={"type":"json_object"}
    )
    return chat_completion.choices[0].message.content

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
        return "None"
    json_response = response.json()
    
    # Get first hit
    hit = json_response["response"]["hits"][0]

    # Get lyrics from Genius
    lyrics_url = hit['result']['url']
    response = requests.get(lyrics_url)
    if response.status_code != 200:
        return "None"
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
            lyrics="Lyrics not found",
            sentiment=Metadata.Sentiment("", ""),
            vectors=[]
        )

        # Loading metadata from audio file
        audio = MP3(audio_file_path, ID3=EasyID3)

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
            if metadata.lyrics != "None":
                sentiment_raw = _get_sentiment_from_lyrics(metadata.lyrics)
                # try to json parse the sentiment
                try:
                    sentiment_json = json.loads(sentiment_raw)
                    # check we have the right keys
                    if "themes" in sentiment_json and "keywords" in sentiment_json:
                        metadata.sentiment = Metadata.Sentiment(sentiment_json["themes"], sentiment_json["keywords"])
                    else:
                        print("Sentiment not in the right format (missing keys)")
                except:
                    print("Sentiment not in the right format (not a JSON)")
        return metadata