from modeltranslation.translator import register, TranslationOptions
from .models import NewsModel


# NewsModel
@register(NewsModel)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'sub_text',)
