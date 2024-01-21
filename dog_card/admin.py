from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import DogCardModel
# Register your models here.


@admin.register(DogCardModel)
class DogCardAdmin(TranslationAdmin):
    list_display = ('name', 'ready_for_adoption', 'gender', 'age',
                    'sterilization', 'vaccination_parasite_treatment', 'size', 'description')
