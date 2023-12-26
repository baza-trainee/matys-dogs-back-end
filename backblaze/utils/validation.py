from rest_framework.exceptions import ValidationError


def image_validation(image_obj):
    if not image_obj:
        raise ValidationError(detail={'error': 'No image found'})

    valid_extensions = ('.jpg', '.png', '.jpeg', '.ios')
    if not image_obj.name.endswith(valid_extensions):
        raise ValidationError(detail={'error': 'Incorrect file format'})

    if image_obj.size > 2097152:  # 2MB
        raise ValidationError(
            detail={'error': 'Image size should not exceed 2MB'})


def document_validation(document_obj):
    if not document_obj:
        raise ValidationError(detail={'error': 'No document found'})

    valid_extensions = ('.pdf', '.doc', '.docx', '.txt')
    if not document_obj.name.endswith(valid_extensions):
        raise ValidationError(detail={'error': 'Incorrect file format'})

    if document_obj.size > 2097152:  # 2MB
        raise ValidationError(
            detail={'error': 'Document size should not exceed 2MB'})
