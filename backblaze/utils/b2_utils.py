from b2sdk.v1 import B2Api, InMemoryAccountInfo
from PIL import Image
import os
from cairosvg import svg2png
from io import BytesIO
from rest_framework.exceptions import ValidationError
from backblaze.utils.validation import image_validation

# Initialize B2 API


def initialize_b2api():
    required_env_varibles = ['APPLICATION_KEY_ID', 'APPLICATION_KEY',
                             'BUCKET_NAME_IMG']
    for var in required_env_varibles:
        if not os.environ.get(var):
            raise ValueError(f'{var} is not set')
    try:
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        application_key_id = os.environ.get('APPLICATION_KEY_ID')
        application_key = os.environ.get('APPLICATION_KEY')
        b2_api.authorize_account(
            "production", application_key_id, application_key)
        bucket_name = os.environ.get('BUCKET_NAME_IMG')
        bucket = b2_api.get_bucket_by_name(bucket_name=bucket_name)
        return bucket, bucket_name
    except Exception as e:
        raise ValidationError(f"Error initializing B2 API: {e}")


# Convert to webp
def converter_to_webP(file_obj):

    try:
        image_validation(file_obj)
        bucket, bucket_name = initialize_b2api()
        file_obj.seek(0)
        if file_obj.name.endswith('.svg'):
            # conver to png
            png_data = svg2png(bytestring=file_obj.read())
            # convert to webp
            image = Image.open(BytesIO(png_data)).convert('RGB')
        else:
            image = Image.open(BytesIO(file_obj.read())).convert('RGB')

        # compress image
        byte_arr = compress_image(image)
        # check size
        if byte_arr.tell() > 2097152:
            raise ValidationError(
                detail={'error': 'Розмір зображення не повинен перевищувати 2MB'})
        # upload image to backblaze
        webp_file_name = os.path.splitext(file_obj.name)[0] + '.webp'
        file_info = bucket.upload_bytes(
            byte_arr.getvalue(), file_name=webp_file_name)

        webp_image_name = file_info.file_name
        webp_image_id = file_info.id_
        image_url = f'https://{bucket_name}.s3.us-east-005.backblazeb2.com/{webp_image_name}'
        return webp_image_name, webp_image_id, image_url
    except Exception as e:
        raise ValidationError(detail={f"Error converting to webp: {e}"})


# Compress image
def compress_image(image, quality=80, lossy_quality=50, step_quality=4, step_lossy_quality=5, refactor_size=0.5, target_size=250000, min_dimension=100):
    if not isinstance(image, Image.Image):
        raise ValidationError(detail={'error': 'Недійсний об’єкт зображення'})
    byte_arr = BytesIO()
    current_image = image
    while quality >= 10 and (current_image.width > min_dimension or current_image.height > min_dimension):
        byte_arr.seek(0)
        byte_arr.truncate(0)
        current_image.save(byte_arr, format='webp', optimize=True,
                           quality=quality, progressive=True, lossy=True, lossy_quality=lossy_quality)

        if byte_arr.tell() <= target_size:
            break
        if byte_arr.tell() > target_size and (current_image.width > min_dimension or current_image.height > min_dimension):
            new_width = int(image.width * refactor_size)
            new_height = int(image.height * refactor_size)
            current_image = current_image.resize((new_width, new_height))
        quality -= step_quality
        lossy_quality -= step_lossy_quality
        refactor_size *= 0.85
    return byte_arr


# Document simplify and upload


def document_simplify_upd(file_obj):
    try:
        bucket, bucket_name = initialize_b2api()
        file_info = bucket.upload_bytes(
            file_obj.read(), file_name=file_obj.name)
        doc_name = file_obj.name
        doc_id = file_info.id_
        return doc_name, doc_id, bucket_name
    except Exception as e:
        raise ValidationError(detail={f"Error uploading document: {e}"})


# Delete file from backblaze


def delete_file_from_backblaze(id):
    if not id:
        raise ValidationError(detail={'error': 'File id is required'})
    try:
        bucket, _ = initialize_b2api()
        # Get file info by id
        file_info = bucket.get_file_info_by_id(file_id=id)
        # Delete file
        delted_file = bucket.delete_file_version(
            file_id=file_info.id_, file_name=file_info.file_name)
        # Return deleted file info
        return delted_file
    except Exception as e:
        raise ValidationError(detail={f"Error deleting file: {e}"})
