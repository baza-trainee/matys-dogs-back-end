from django.urls import path
from main_page.views import main_page_view, NewsAdminView


urlpatterns = [
    path('', main_page_view.as_view(), name='main_page_view'),
    path('news', NewsAdminView.as_view(
        {
            'get': 'list',
            'post': 'create',
            'put': 'update',
            'delete': 'delete'
        }), name='create_news')
]
