import argparse
import json
import os
from dotenv import load_dotenv
from artwork import get_album_artwork_description
from metadata import get_metadata, Metadata
from multiprocessing import Pool


def save_metadata_to_json(metadata: Metadata, file_path) -> str:
    output = os.environ.get("OUTPUT_PATH", "./output")
    filename = os.path.splitext(os.path.basename(file_path))[0] + ".json"
    json_file_path = os.path.join(output, filename)
    with open(json_file_path, 'w') as f:
        metadata_dict = metadata.__dict__
        metadata_dict['sentiment'] = metadata.sentiment.to_dict()
        json.dump(metadata_dict, f, indent=4)
    return json_file_path


def _get_list_of_audio_files(path):
    audio_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.mp3'):
                audio_files.append(os.path.join(root, file))
    return audio_files


def process_audio_file(audio_file: str, album_artwork_description: str | None):
    print(f"Processing {audio_file}...")
    metadata = get_metadata(audio_file, album_artwork_description)
    output_file_path = save_metadata_to_json(metadata, audio_file)
    print(f"Metadata and lyrics saved to {output_file_path}")


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Extract metadata and lyrics from an album folder (MP3)"
    )
    parser.add_argument("path", help="Path to the album forlder (MP3)")
    args = parser.parse_args()

    # Check if the path is a folder and exists
    if not os.path.isdir(args.path):
        print(f"Path {args.path} is not a folder or does not exist")
        return

    # Get list of audio files
    audio_files = _get_list_of_audio_files(args.path)

    if len(audio_files) == 0:
        print("No audio files found in the specified folder")
        return
    print(f"Found {len(audio_files)} audio files in the specified folder")

    # Create output folder if it does not exist
    output = os.environ.get("OUTPUT_PATH", "./output")
    if not os.path.exists(output):
        os.makedirs(output)

    # Get album artwork description
    album_artwork_description = get_album_artwork_description(audio_files[0])
    if album_artwork_description is None:
        print("Album artwork description not found")

    # Process audio files
    with Pool() as pool:
        pool.starmap(process_audio_file,
                     [
                         (audio_file, album_artwork_description)
                         for audio_file in audio_files
                        ])


if __name__ == "__main__":
    main()
