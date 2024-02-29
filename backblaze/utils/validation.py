from rest_framework.exceptions import ValidationError


def image_validation(image_obj):
    if not image_obj:
        raise ValidationError(detail={'description': 'Зображення не знайдено'})

    valid_extensions = ('.jpg', '.png', '.jpeg', '.ios', '.webp', '.svg')
    if not image_obj.name.endswith(valid_extensions):
        raise ValidationError(detail={'description': 'Недійсний формат'})



