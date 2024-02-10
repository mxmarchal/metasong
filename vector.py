
import os
import json
from dotenv import load_dotenv
import argparse
from metadata import Metadata
from openai import OpenAI
from multiprocessing import Pool

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
  
  def to_string(self):
    themes = ",".join(self.metadata.sentiment.themes)
    keywords = ",".join(self.metadata.sentiment.keywords)
    return f"{self.metadata.lyrics} {themes} {keywords} {self.metadata.title} {self.metadata.artwork_description} {' '.join(self.metadata.authors)}"

def vectorize(payload: VectorizePayload) -> list[float]:
  client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
  embeddings = client.embeddings.create(
      model="text-embedding-3-small",
      input=payload.to_string()
  )
  vectors = embeddings.data[0].embedding
  return vectors
   

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

def save_vector_to_json(vector: list[float], file_path: str):
  json_file_path = os.path.splitext(file_path)[0] + '_vector.json'
  with open(json_file_path, 'w') as f:
    json.dump(vector, f)

def process_json_file(json_file):
  print(f"Processing {json_file}...")
  metadata = read_metadata_from_json(json_file)
  payload = VectorizePayload(metadata)
  vectors = vectorize(payload)
  save_vector_to_json(vectors, json_file)
  print(f"Vectorized data saved to {os.path.splitext(json_file)[0]}_vector.json")
  return vectors

def main():
  load_dotenv()
  parser = argparse.ArgumentParser(description="Vectorize metadata and lyrics from an album folder (MP3)")
  parser.add_argument("path", help="Path to the album forlder (MP3)")
  args = parser.parse_args()

  # Check API key is set
  if not os.environ.get('OPENAI_API_KEY'):
      print("OpenAI API key not found")
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

  # Process json files
  with Pool() as pool:
    pool.starmap(process_json_file, [(json_file,) for json_file in json_files])

if __name__ == "__main__":
  main()