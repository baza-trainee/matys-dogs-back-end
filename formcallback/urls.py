from django.urls import path
from .views import CallBackPost, NotificationAdmin

urlpatterns = [
    path("form-callback", CallBackPost.as_view({"post": "create"})),
    path("notification-admin", NotificationAdmin.as_view({"get": "list"})),
    path(
        "notification-admin/<int:pk>",
        NotificationAdmin.as_view({"put": "update", "delete": "destroy"}),
    ),
]
