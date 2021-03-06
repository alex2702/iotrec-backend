from django.urls import path, include
from . import views
from .views import current_user
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
from rest_framework_nested import routers

router = routers.SimpleRouter()
router.register(r'things', views.ThingViewSet, base_name='thing')
router.register(r'categories', views.CategoryViewSet, base_name='category')
router.register(r'categories-flat', views.CategoryFlatViewSet, base_name='category-flat')
router.register(r'recommendations', views.RecommendationViewSet, base_name='recommendation')
router.register(r'users', views.UserViewSet, base_name='user')

# nested router for /recommendations/{recommendationId}/feedback/ and /recommendations/{recommendationId}/rating/
recommendations_router = routers.NestedSimpleRouter(router, r'recommendations', lookup='recommendation')
recommendations_router.register(r'feedback', views.FeedbackViewSet, base_name='recommendation-feedback')
recommendations_router.register(r'rating', views.RatingViewSet, base_name='recommendation-rating')

# nested router for /users/{usersId}/preferences/ and /users/{usersId}/stays/
users_router = routers.NestedSimpleRouter(router, r'users', lookup='user')
users_router.register(r'preferences', views.PreferenceViewSet, base_name='user-preference')
users_router.register(r'stays', views.StayViewSet, base_name='user-stay')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(recommendations_router.urls)),
    path('', include(users_router.urls)),
    path('current-user/', current_user),
    path('login/', obtain_jwt_token),
    path('verify-token/', verify_jwt_token),
]
