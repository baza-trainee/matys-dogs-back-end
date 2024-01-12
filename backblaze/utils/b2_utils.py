from b2sdk.v1 import B2Api, InMemoryAccountInfo
from PIL import Image
import os
from cairosvg import svg2png
from io import BytesIO
from rest_framework.exceptions import ValidationError


# Initialize B2 API
def initialize_b2api():
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    application_key_id = os.getenv('APPLICATION_KEY_ID')
    application_key = os.getenv('APPLICATION_KEY')
    b2_api.authorize_account(
        "production", application_key_id, application_key)
    bucket_name = os.getenv('BUCKET_NAME_IMG')
    bucket = b2_api.get_bucket_by_name(bucket_name=bucket_name)
    return bucket, bucket_name

# Document simplify and upload


def document_simplify_upd(file_obj):
    bucket, bucket_name = initialize_b2api()
    file_info = bucket.upload_bytes(file_obj.read(), file_name=file_obj.name)
    doc_name = file_obj.name
    doc_id = file_info.id_
    return doc_name, doc_id, bucket_name


# Convert to webp
def converter_to_webP(file_obj):
    # Initialize B2 API
    bucket, bucket_name = initialize_b2api()

    if file_obj.name.endswith('.svg'):
        # conver to png
        png_data = svg2png(bytestring=file_obj.read())
        # convert to webp
        image = Image.open(BytesIO(png_data)).convert('RGB')
    else:
        image = Image.open(BytesIO(file_obj.read())).convert('RGB')

    # compress image
    byte_arr = BytesIO()
    byte_arr.seek(0)
    byte_arr.truncate(0)
    image.save(byte_arr, format='webp', optimize=True, quality=10)
    # check size
    size_kb = byte_arr.tell() / 1024
    if size_kb > 2097152:
        raise ValidationError(
            detail={'error': 'Розмір зображення не повинен перевищувати 2MB'})

    webp_file_name = os.path.splitext(file_obj.name)[0] + '.webp'
    file_info = bucket.upload_bytes(
        byte_arr.getvalue(), file_name=webp_file_name)

    webp_image_name = file_info.file_name
    webp_image_id = file_info.id_
    size = file_info.size

    return webp_image_name, webp_image_id, bucket_name, size


# Delete file from backblaze


def delete_file_from_backblaze(id):
    bucket, _ = initialize_b2api()
    # Get file info by id
    file_info = bucket.get_file_info_by_id(file_id=id)
    # Delete file
    delted_file = bucket.delete_file_version(
        file_id=file_info.id_, file_name=file_info.file_name)
    # Return deleted file info
    return delted_file
