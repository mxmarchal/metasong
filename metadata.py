
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import datetime
from lyrics import get_lyrics, get_sentiment_from_lyrics
import json
import uuid


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
    year: int | None
    duration: int
    artwork_description: str | None
    lyrics: str | None
    sentiment: Sentiment

    def __init__(self,
                 track_number: int,
                 title: str,
                 authors: list[str],
                 album: str,
                 year: int | None,
                 duration: int,
                 artwork_description: str,
                 lyrics: str, sentiment: Sentiment):
        self.uuid = str(uuid.uuid4())
        self.track_number = track_number
        self.title = title
        self.authors = authors
        self.album = album
        self.year = year
        self.duration = duration
        self.artwork_description = artwork_description
        self.lyrics = lyrics
        self.sentiment = sentiment


def get_metadata(
        audio_file_path: str,
        album_artwork_description: str | None
        ) -> Metadata:
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
        )

    # Loading metadata from audio file
    audio = MP3(audio_file_path, ID3=EasyID3)

    date = audio["date"][0] if "date" in audio else None

    # if date is 4 digits, it's a year
    if date:
        if date.isdigit() and len(date) == 4:
            metadata.year = int(date)
        else:
            # Try to parse the date
            try:
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
                print("GOT DATE", date)
                metadata.year = int(date.year)
            except ValueError:
                metadata.year = None
    else:
        metadata.year = None

    # Extracting basic info
    metadata.track_number = audio["tracknumber"][0]
    metadata.title = audio["title"][0]
    metadata.authors = audio["artist"]
    metadata.album = audio["album"][0]
    metadata.duration = int(audio.info.length)

    # Get lyrics
    if metadata.title and metadata.authors:
        metadata.lyrics = get_lyrics(metadata.authors[0], metadata.title)
        if metadata.lyrics is not None:
            sentiment_raw = get_sentiment_from_lyrics(metadata.lyrics)
            # try to json parse the sentiment
            try:
                sentiment_json = json.loads(sentiment_raw)
                # check we have the right keys
                if "themes" in sentiment_json and "keywords" in sentiment_json:
                    metadata.sentiment = Metadata.Sentiment(
                        sentiment_json["themes"],
                        sentiment_json["keywords"])
                else:
                    print("Sentiment not in the right format (missing keys)")
            except ValueError:
                print("Sentiment not in the right format (not a JSON)")
    return metadata
