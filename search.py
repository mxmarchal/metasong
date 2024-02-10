from pinecone import Pinecone, ServerlessSpec
import os
from metadata import Metadata
from vector import get_json_files, read_metadata_from_json
from dotenv import load_dotenv
import argparse
from openai import OpenAI


def vectorize_query(query: str) -> list[float]:
  client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
  embeddings = client.embeddings.create(
      model="text-embedding-3-small",
      input=query
  )
  vectors = embeddings.data[0].embedding
  return vectors

def main():
  load_dotenv()
  parser = argparse.ArgumentParser(description="Search for a song")
  parser.add_argument("query", help="Search query")
  args = parser.parse_args()


  if not os.environ.get('OPENAI_API_KEY'):
    print("OpenAI API key not found")
    return
  if not os.environ.get('PINECONE_API_KEY'):
    print("Pinecone API key not found")
    return
  
  pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
  index = pc.Index("metasong-index")

  query_vectors = vectorize_query(args.query)
  results = index.query(vector=query_vectors, top_k=3, include_metadata=True)

  print("Results:", results)


if __name__ == "__main__":
  main()