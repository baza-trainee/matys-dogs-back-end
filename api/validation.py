import re
from rest_framework.validators import ValidationError


def email_validation(email):

    if email is None:
        raise ValidationError({'error': 'потрібна електронна пошта'})
    
    if email is '':
        raise ValidationError({'error': 'Будь ласка, заповніть всі обов\'язкові поля'})
    
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        raise ValidationError({'error': 'Невірний формат електронної пошти'})
