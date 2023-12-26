from b2sdk.v1 import B2Api, InMemoryAccountInfo
from PIL import Image
import tempfile
import os

# Initialize B2 API


def initialize_b2api():
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    application_key_id = os.getenv('APPLICATION_KEY_ID')
    application_key = os.getenv('APPLICATION_KEY')
    b2_api.authorize_account(
        "production", application_key_id, application_key)
    return b2_api


def converterToWebP(file_obj):
    b2_api = initialize_b2api()
    bucket_name = os.getenv('BUCKET_NAME_IMG')
    bucket = b2_api.get_bucket_by_name(bucket_name=bucket_name)
    image = Image.open(file_obj)
    with tempfile.NamedTemporaryFile(suffix='.webp',delete=True) as temp:
        image.save(temp, "WEBP")
    image.save(temp.name, "WEBP")
    with open(temp.name, 'rb') as data: 
        bucket.upload_bytes(data.read(), file_name=os.path.basename(temp.name))
    webp_image_name = os.path.basename(temp.name)
    return webp_image_name, bucket_name
