
import pyquery as pq
import requests
import os
from openai import OpenAI

def get_sentiment_from_lyrics(lyrics: str) -> str:
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
        return None
    json_response = response.json()
    
    # Get first hit
    hit = json_response["response"]["hits"][0]

    # Get lyrics from Genius
    lyrics_url = hit['result']['url']
    response = requests.get(lyrics_url)
    if response.status_code != 200:
        return None
    lyrics = extract_lyrics_from_html(response.text)
    return lyrics
