from mutagen.id3 import ID3, APIC
import requests
import os
from PIL import Image
import io

def _get_image_description(image_data) -> str:
    if image_data is None:
        return "None"
    huggingface_api_token = os.environ.get('HUGGINGFACE_API_TOKEN')
    if huggingface_api_token is None:
        print("Huggingface API token not found")
        return "None"
    headers = {"Authorization": f"Bearer {huggingface_api_token}"}
    response = requests.post("https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base", data=image_data, headers=headers)
    if response.status_code != 200:
        print("Error getting image description from Huggingface API")
        return "None"
    response_json = response.json()
    return response_json[0]["generated_text"]

def get_album_artwork_description(audio_file) -> str:
    # Get album artwork
    id3 = ID3(audio_file)
    artwork_data = None
    for tag in id3.values():
            if isinstance(tag, APIC):
                artwork_data = tag.data
                break
            
    # Reduce image size by 3
    # This gives me a better performance on the Huggingface API
    image = Image.open(io.BytesIO(artwork_data))
    image.thumbnail((image.width // 3, image.height // 3))
    buffered = io.BytesIO()

    # Save image to a buffer
    image.save(buffered, format="JPEG")

    # Get image description
    buffered.seek(0)
    artwork_data = buffered.read()

    return _get_image_description(artwork_data)