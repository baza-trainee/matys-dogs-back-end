from django.urls import path
from main_page.views import main_page_view, NewsView, PartnersView


urlpatterns = [
    path('', main_page_view.as_view({'get': 'list'}), name='main_page_view'),
    path('news', NewsView.as_view(
        {
            'get': 'list',
            'post': 'create',
        }), name='news'),
    path('news/<int:pk>', NewsView.as_view(
        {
            'put': 'update',
            'delete': 'destroy'
        }), name='news'),
    path('partners', PartnersView.as_view(
        {
            'get': 'list',
            'post': 'create',
        }), name='partners'),
    path('partners/<str:pk>', PartnersView.as_view({'delete': 'destroy'}))
]
