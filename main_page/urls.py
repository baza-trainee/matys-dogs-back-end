from django.urls import path
from main_page.views import get_news, create_news


urlpatterns = [
    path('news', get_news, name='news'),
    path('news/create', create_news, name='create_news')
]
