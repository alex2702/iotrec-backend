from django.urls import path, include
from . import views
from .views import current_user, UserList
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'api/things', views.ThingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/current-user/', current_user),
    path('api/login/', obtain_jwt_token),
    path('api/users/', UserList.as_view()),
    #path('api/things/', views.ThingListCreate.as_view())
]