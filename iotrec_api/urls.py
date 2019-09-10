from django.urls import path, include
from . import views
from .views import UserApiView, current_user
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
from rest_framework import routers

router = routers.DefaultRouter()
# router.register(r'venues', views.VenueViewSet)
router.register(r'things', views.ThingViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'categories-flat', views.CategoryFlatViewSet)
#router.register(r'current-user', views.CurrentUserViewSet, basename='current-user')


urlpatterns = [
    path('', include(router.urls)),
    path('current-user/', current_user),
    path('login/', obtain_jwt_token),
    path('verify-token/', verify_jwt_token),
    path('users/', UserApiView.as_view()),
    # path('api/things/', views.ThingListCreate.as_view())
]