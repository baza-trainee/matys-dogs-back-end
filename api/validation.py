import re
from rest_framework.validators import ValidationError


def email_validation(email):

    if email is None:
        raise ValidationError({'error': 'потрібна електронна пошта'})

    if email == '':
        raise ValidationError(
            {'error': 'Будь ласка, заповніть всі обов\'язкові поля'})

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        raise ValidationError({'error': 'Невірний формат електронної пошти'})


def password_validation(password, confirmPassword):

    password_regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!-_)(.,]).{8,12}$'
    if not re.match(password_regex, password or confirmPassword):
        raise ValidationError(
            {'error': 'Пароль повинен містити великі та малі букви, цифри та один з спеціальних символів '})
    if password != confirmPassword:
        raise ValidationError({'error': 'Паролі не співпадають'})
