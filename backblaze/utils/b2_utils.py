from b2sdk.v1 import B2Api, InMemoryAccountInfo
from PIL import Image
import os
import tempfile
from cairosvg import svg2png
from io import BytesIO
import shutil

# Initialize B2 API


def initialize_b2api():
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    application_key_id = os.getenv('APPLICATION_KEY_ID')
    application_key = os.getenv('APPLICATION_KEY')
    b2_api.authorize_account(
        "production", application_key_id, application_key)
    return b2_api


def document_simplify_upd(file_obj):
    b2_api = initialize_b2api()
    bucket_name = os.getenv('BUCKET_NAME_IMG')
    bucket = b2_api.get_bucket_by_name(bucket_name=bucket_name)
    file_info = bucket.upload_bytes(file_obj.read(), file_name=file_obj.name)
    doc_name = file_obj.name
    doc_id = file_info.id_
    return doc_name, doc_id, bucket_name


# def convert_svg_to_png(svg_file):
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_png:
#         png_image = svg2png(bytestring=svg_file.read())
#         image = Image.open(BytesIO(png_image))
#         image.save(temp_png.name, 'PNG')
#         return temp_png.name


def converter_to_webP(file_obj):
    b2_api = initialize_b2api()
    bucket_name = os.getenv('BUCKET_NAME_IMG')
    bucket = b2_api.get_bucket_by_name(bucket_name=bucket_name)
    if file_obj.name.endswith('.svg'):
        # conver to png
        png_data = svg2png(bytestring=file_obj.read())
        # convert to webp
        png_image = Image.open(BytesIO(png_data)).convert('RGB')
        byte_arr = BytesIO()
        png_image.save(byte_arr, format='webp')
        byte_arr.seek(0)
    else:
        image = Image.open(BytesIO(file_obj.read())).convert('RGB')
        byte_arr = BytesIO()
        image.save(byte_arr, format='webp')
        byte_arr.seek(0)

    webp_file_name = os.path.splitext(file_obj.name)[0] + '.webp'
    file_info = bucket.upload_bytes(
        byte_arr.read(), file_name=webp_file_name)

    webp_image_name = file_info.file_name
    webp_image_id = file_info.id_
    return webp_image_name, webp_image_id, bucket_name


def delete_file_from_backblaze(id):
    b2_api = initialize_b2api()
    bucket_name = os.getenv('BUCKET_NAME_IMG')
    bucket = b2_api.get_bucket_by_name(bucket_name=bucket_name)
    bucket.delete_file_version(file_name='', file_id=id)
