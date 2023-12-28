from rest_framework.exceptions import ValidationError


def image_validation(image_obj):
    if not image_obj:
        raise ValidationError(detail={'error': 'Зображення не знайдено'})

    valid_extensions = ('.jpg', '.png', '.jpeg', '.ios', '.webp', '.svg')
    if not image_obj.name.endswith(valid_extensions):
        raise ValidationError(detail={'error': 'Недійсний формат'})

    if image_obj.size > 2097152:  # 2MB
        raise ValidationError(
            detail={'error': 'Розмір зображення не повинен перевищувати 2MB'})


def document_validation(document_obj):
    if not document_obj:
        raise ValidationError(detail={'error': 'Документ не знайдено'})

    valid_extensions = ('.pdf', '.doc', '.docx', '.txt')
    if not document_obj.name.endswith(valid_extensions):
        raise ValidationError(detail={'error': 'Некоректний формат файлу'})

    if document_obj.size > 2097152:  # 2MB
        raise ValidationError(
            detail={'error': 'Розмір документа не повинен перевищувати 2MB'})
