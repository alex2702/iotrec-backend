from django.urls import path
from . import views
from .views import current_user, UserList

urlpatterns = [
    path('api/thing/', views.ThingListCreate.as_view()),
    path('current_user/', current_user),
    path('users/', UserList.as_view())
]