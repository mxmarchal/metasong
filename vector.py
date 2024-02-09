
import os
import json
from dotenv import load_dotenv
import argparse
import requests
from metadata import Metadata
import time

class VectorizePayload:
  def __init__(self, metadata: Metadata):
    self.metadata = metadata

  def to_dict(self):
    themes = ",".join(self.metadata.sentiment.themes)
    keywords = ",".join(self.metadata.sentiment.keywords)
    additional_sentences = [
        f"Mood: {themes}",
        f"Topic: {keywords}",
        f"Title: {self.metadata.title}",
        # Include artwork description if it's concise and relevant
    ]
    return {
        "inputs": {
            "source_sentence": self.metadata.lyrics,
            "sentences": additional_sentences
        }
    }

def vectorize(payload: VectorizePayload) -> list[float]:
  API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
  headers = {
      "Authorization": f"Bearer {os.environ.get('HUGGINGFACE_API_TOKEN')}"
  }
  response = requests.post(API_URL, headers=headers, json=payload.to_dict())
  if response.status_code != 200:
      if response.status_code == 503:
          response_json = response.json()
          estimated_time = response_json.get("estimated_time", "30")
          print(f"Model is loading, retry in {estimated_time} seconds")
          time.sleep(float(estimated_time))
          return vectorize(payload)
      else:
        raise ValueError(f"Request failed with status code {response.status_code}")
  return response.json()

def get_json_files(path: str) -> list[str]:
  json_files = []
  for root, dirs, files in os.walk(path):
    for file in files:
      if file.endswith('.json'):
        json_files.append(os.path.join(root, file))
  return json_files

def is_valid_metadata(metadata_dict):
    # Check if the JSON data corresponds to the Metadata model
    required_keys = ['track_number', 'title', 'authors', 'album', 'year', 'duration', 'artwork_description', 'lyrics']
    for key in required_keys:
        if key not in metadata_dict:
            return False
    return True

def read_metadata_from_json(file_path):
    with open(file_path, 'r') as f:
        metadata_dict = json.load(f)
        if is_valid_metadata(metadata_dict):
            # Extract the Sentiment sub-dictionary and convert it to Sentiment object
            sentiment_dict = metadata_dict.pop('sentiment', {})
            sentiment = Metadata.Sentiment(**sentiment_dict)
            
            # Create a new Metadata object with the remaining data
            metadata = Metadata(**metadata_dict, sentiment=sentiment)
            return metadata
        else:
            raise ValueError("JSON data does not correspond to Metadata model")


def exec_vectorize(metadata: Metadata):
  payload = VectorizePayload(metadata)
  vectors = vectorize(payload)
  return vectors

def main():
  load_dotenv()
  parser = argparse.ArgumentParser(description="Vectorize metadata and lyrics from an album folder (MP3)")
  parser.add_argument("path", help="Path to the album forlder (MP3)")
  args = parser.parse_args()

  # Check API key is set
  if not os.environ.get('HUGGINGFACE_API_TOKEN'):
      print("Huggingface API key not set")
      return

  # Check if the path is a folder and exists
  if not os.path.isdir(args.path):
      print(f"Path {args.path} is not a folder or does not exist")
      return
  
  # Get list of json files
  json_files = get_json_files(args.path)

  if len(json_files) == 0:
      print("No json files found in the specified folder")
      return
  print(f"Found {len(json_files)} json files in the specified folder")

  # test with first file
  metadata = read_metadata_from_json(json_files[0])
  vector = exec_vectorize(metadata)
  print(vector)

  # for json_file in json_files:
  #   metadata = read_metadata_from_json(json_file)
  #   print(metadata.authors)

if __name__ == "__main__":
  main()