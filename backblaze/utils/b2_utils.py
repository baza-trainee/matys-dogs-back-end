from b2sdk.v1 import B2Api, InMemoryAccountInfo
from PIL import Image
import os
from cairosvg import svg2png
from io import BytesIO
from rest_framework.exceptions import ValidationError
from backblaze.utils.validation import image_validation
# Constants for default values
DEFAULT_QUALITY = 80
DEFAULT_LOSSY_QUALITY = 50
QUALITY_STEP = 5
LOSSY_QUALITY_STEP = 6
TARGET_SIZE = 200000
MIN_DIMENSION = 100

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
        raise ValidationError({"description":f"Помилка ініціалізація B2 API: {e}"})


bucket, bucket_name = initialize_b2api()


def read_file(file_obj):
    file_obj.seek(0)
    bytes_read = file_obj.read()
    if file_obj.name.endswith('.svg'):
        # conver to png
        png_data = svg2png(bytestring=bytes_read)
        # convert to webp
        image = Image.open(BytesIO(png_data)).convert('RGB')
    else:
        image = Image.open(BytesIO(bytes_read)).convert('RGB')
    return image

# Convert to webp


def upload_to_backblaze(byte_arr, file_obj):
    if byte_arr.tell() > 2097152:
        raise ValidationError(
            detail={'description': 'Розмір зображення не повинен перевищувати 2MB'})
    webp_file_name = os.path.splitext(file_obj.name)[0] + '.webp'
    file_info = bucket.upload_bytes(
        byte_arr.getvalue(), file_name=webp_file_name)
    webp_image_name = file_info.file_name
    end_path = os.environ.get('END_BACKET_PATH')
    webp_image_id = file_info.id_
    image_url = f'https://{bucket_name}.{end_path}/{webp_image_name}'

    return webp_image_name, webp_image_id, image_url


# Convert to webp

def converter_to_webP(file_obj):
    try:
        image_validation(file_obj)
        image = read_file(file_obj)
        byte_arr = compress_image(image)
        return upload_to_backblaze(byte_arr, file_obj)
    except Exception as e:
        raise ValidationError(detail={"description": f"Помилка перетвореня у webp: {e}"})


def resize_image(image, refactor_size, min_dimension=MIN_DIMENSION):
    if image.width > min_dimension and image.height > min_dimension:
        new_width = int(image.width * refactor_size)
        new_height = int(image.height * refactor_size)
        image = image.resize((new_width, new_height))
    return image

# Compress image


def compress_image(image, quality=DEFAULT_QUALITY, lossy_quality=DEFAULT_LOSSY_QUALITY,
                   step_quality=QUALITY_STEP, step_lossy_quality=LOSSY_QUALITY_STEP,
                   target_size=TARGET_SIZE, refactor_size=0.8):
    if not isinstance(image, Image.Image):
        raise ValidationError(detail={'description': 'Недійсний об’єкт зображення'})
    byte_arr = BytesIO()
    while byte_arr.tell() < target_size and quality >= 10:
        
        byte_arr.seek(0) # Reset the pointer to the beginning of the file
        byte_arr.truncate(0) # Clear the file
        image.save(byte_arr, format='webp', optimize=True,
                   quality=quality, progressive=True, lossy=True, lossy_quality=lossy_quality)

        if byte_arr.tell() <= target_size:
            break

        image = resize_image(image, refactor_size)
        quality -= step_quality
        lossy_quality -= step_lossy_quality
        refactor_size *= 0.8
    byte_arr.seek(0)
    return byte_arr


# Delete file from backblaze


def delete_file_from_backblaze(id):
    if not id:
        raise ValidationError(detail={'description': 'Потрібен ідентифікатор файлу'})
    try:
        # Get file info by id
        file_info = bucket.get_file_info_by_id(file_id=id)
        # Delete file
        delted_file = bucket.delete_file_version(
            file_id=file_info.id_, file_name=file_info.file_name)
        # Return deleted file info
        return delted_file
    except Exception as e:
        raise ValidationError(detail={"description":f"Помилка при видалені: {e}"})
