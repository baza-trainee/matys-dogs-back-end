from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import NewsModel, Partners


@admin.register(NewsModel)
class NewsModelAdmin(TranslationAdmin):
    list_display = ('title', 'post_at', 'update_at', 'sub_text', 'url')


@admin.register(Partners)
class PartnersAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo')

# Register your models here.
