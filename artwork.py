from mutagen.id3 import ID3, APIC
import requests

def _get_image_description(image_data) -> str:
    if image_data is None:
        return "None"
    response = requests.post("https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base", data=image_data)
    response_json = response.json()
    print(response_json)
    return "Not implemented"

def get_album_artwork_description(audio_file) -> str:
    # Get album artwork
    id3 = ID3(audio_file)
    artwork_data = None
    for tag in id3.values():
            if isinstance(tag, APIC):
                artwork_data = tag.data
                break

    return _get_image_description(artwork_data)



# import requests

# API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
# headers = {"Authorization": f"Bearer {API_TOKEN}"}

# def query(filename):
#     with open(filename, "rb") as f:
#         data = f.read()
#     response = requests.post(API_URL, headers=headers, data=data)
#     return response.json()

# output = query("cats.jpg")