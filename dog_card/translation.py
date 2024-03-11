from modeltranslation.translator import register, TranslationOptions
from .models import DogCardModel


@register(DogCardModel)
class DogCardTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'gender', 'age', 'size',)
