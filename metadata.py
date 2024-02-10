
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import datetime
from lyrics import get_lyrics, get_sentiment_from_lyrics
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
    artwork_description: str | None
    lyrics: str | None
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

def get_metadata(audio_file_path: str, album_artwork_description: str | None) -> Metadata:
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
            if metadata.lyrics != None:
                sentiment_raw = get_sentiment_from_lyrics(metadata.lyrics)
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