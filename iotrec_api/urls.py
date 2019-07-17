from django.urls import path, include
from . import views
from .views import current_user, UserApiView
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'venues', views.VenueViewSet)
router.register(r'things', views.ThingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('current-user/', current_user),
    path('login/', obtain_jwt_token),
    path('users/', UserApiView.as_view()),
    #path('api/things/', views.ThingListCreate.as_view())
]