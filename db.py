from pinecone import Pinecone, ServerlessSpec
import os
from metadata import Metadata
from vector import get_json_files, read_metadata_from_json
from dotenv import load_dotenv
import argparse

def generate_entry(metadata: Metadata) -> dict:
  pc_metadata = {
      "title": metadata.title,
      "album": metadata.album,
      "year": metadata.year,
      "duration": metadata.duration,
      "artwork_description": metadata.artwork_description,
      "lyrics": metadata.lyrics,
      "authors": metadata.authors,
      "themes": metadata.sentiment.themes,
      "keywords": metadata.sentiment.keywords
  }
  values = metadata.vectors
  return {
      "id": metadata.uuid,
      "values": values,
      "metadata": pc_metadata
  }

def check_index_exists(pc, index):
  print("Checking if index exists...")
  list_indexes = pc.list_indexes().indexes
  names = [index.name for index in list_indexes]

  if index not in names:
    print(f"Creating index {index}...")
    pc.create_index(
      name=index,
      dimension=1536,
      metric="cosine",
      spec=ServerlessSpec(
        cloud="aws",
        region="us-west-2"
      )
    )
  else:
    print(f"Index {index} already exists")
  return pc.Index(index)

def main():
  load_dotenv()
  parser = argparse.ArgumentParser(description="Generate Pinecone index from an album folder (MP3)")
  parser.add_argument("path", help="Path to the album forlder (MP3)")
  args = parser.parse_args()


  if not os.path.isdir(args.path):
    print(f"Path {args.path} is not a folder or does not exist")
    return
  if not os.environ.get('PINECONE_API_KEY'):
    print("Pinecone API key not found")
    return

  pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

  index = check_index_exists(pc, "metasong-index")

  # Get list of JSON files
  json_files = get_json_files(args.path)

  # Process JSON files
  entries = []
  for json_file in json_files:
    metadata = read_metadata_from_json(json_file)
    entry = generate_entry(metadata)
    entries.append(entry)
  print(f"Adding {len(entries)} entries to the index...")
  index.upsert(entries)
  print("Done")


if __name__ == "__main__":
  main()
