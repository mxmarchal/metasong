# 🎵 Metasong - Audio Metadata Extractor

This Python script extracts metadata and lyrics from audio files in an album folder (MP3 format) and saves them to JSON files. It utilizes multiprocessing for parallel processing, making it efficient for handling a large number of audio files.

## Features

- Extracts metadata such as track number, title, authors, album, year, duration, artwork description, and sentiment analysis. (Powered by OpenAI's GPT-3.5 Turbo API and GPT-4 Vision API.)
- Retrieves lyrics from audio files using the Genius API.
- Utilizes multiprocessing to process audio files in parallel, improving performance.

## Requirements

- Python 3.x
- External dependencies (check requirements.txt for details)
- OpenAI API key (GPT-3.5 Turbo and GPT-4 Vision a.k.a. you need to pay for this service.)
- Genius API access token

## Installation

Clone the repository:

```bash
git clone https://github.com/mxmarchal/metasong.git
```

### Install dependencies:

```bash
cd metasong
pip install -r requirements.txt
```

Create a .env file in the project directory and set the following environment variables:

```bash
OPENAI_API_KEY=your_openai_api_key
GENIUS_ACCESS_TOKEN=your_genius_access_token
```

## Usage

```bash
python main.py <path_to_album_folder>
```

Replace `path_to_album_folder` with the path to the folder containing the audio files (MP3 format) you want to process.

## Example

```bash
python main.py /path/to/album
```

# Contributing

I won't be accepting any pull requests for this project. This is a personal project and I'm not looking for contributions at the moment.

You are welcome to fork the project and customize it to your needs.

# License

This project is licensed under the MIT License. See the LICENSE file for details.
