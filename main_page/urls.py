from django.urls import path
from main_page.views import main_page_view, create_news


urlpatterns = [
    path('', main_page_view, name='main_page_view'),
    path('news/create', create_news, name='create_news')
]
