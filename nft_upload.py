import requests
import os
from config import PINATA_API_KEY, PINATA_SECRET_API_KEY

def upload_to_pinata(filepath, name, description):
    # 上傳圖片
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY
    }

    filename = os.path.basename(filepath)  # 只取檔名
    with open(filepath, "rb") as file:
        files = {
            'file': (filename, file)
        }
        response = requests.post(url, files=files, headers=headers)

    if response.status_code != 200:
        raise Exception("Image upload failed:", response.text)

    image_hash = response.json()["IpfsHash"]
    image_url = f"https://gateway.pinata.cloud/ipfs/{image_hash}"

    # 上傳 metadata
    metadata = {
        "name": name,
        "description": description,
        "image": image_url
    }

    metadata_url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    response2 = requests.post(metadata_url, headers=headers, json=metadata)

    if response2.status_code != 200:
        raise Exception("Metadata upload failed:", response2.text)

    metadata_hash = response2.json()["IpfsHash"]
    metadata_uri = f"https://gateway.pinata.cloud/ipfs/{metadata_hash}"

    return metadata_uri
