from mutagen.id3 import ID3, APIC
import os
from PIL import Image
import io
from openai import OpenAI
import base64


def _get_image_description(image_data: str | None) -> str | None:
    if image_data is None:
        return None
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Describe the album cover.
                        Simple and straight to the point."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        model="gpt-4-vision-preview",
        max_tokens=300,
    )
    return chat_completion.choices[0].message.content


def get_album_artwork_description(audio_file) -> str | None:
    # Get album artwork
    id3 = ID3(audio_file)
    artwork_data = None
    for tag in id3.values():
        if isinstance(tag, APIC):
            artwork_data = tag.data
            break

    # Scale image to 512x512
    image = Image.open(io.BytesIO(artwork_data))
    image = image.resize((512, 512))
    image_base64 = io.BytesIO()
    image.save(image_base64, format="JPEG")
    image_base64 = base64.b64encode(image_base64.getvalue()).decode('utf-8')

    return _get_image_description(image_base64)
