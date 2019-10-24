from django.urls import path, include
from django.views.generic import TemplateView

from . import views
from .views import current_user#, ThingCreateAPIView, ThingSingleAPIView, ThingListAPIView
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
from rest_framework_nested import routers

router = routers.SimpleRouter()
# router.register(r'venues', views.VenueViewSet)
router.register(r'things', views.ThingViewSet, base_name='thing')
router.register(r'categories', views.CategoryViewSet, base_name='category')
router.register(r'categories-flat', views.CategoryFlatViewSet, base_name='category-flat')
router.register(r'recommendations', views.RecommendationViewSet, base_name='recommendation')
router.register(r'users', views.UserViewSet, base_name='user')

recommendations_router = routers.NestedSimpleRouter(router, r'recommendations', lookup='recommendation')
recommendations_router.register(r'feedback', views.FeedbackViewSet, base_name='recommendation-feedback')
recommendations_router.register(r'rating', views.RatingViewSet, base_name='recommendation-rating')
#recommendations_router.register(r'context', views.ContextViewSet, base_name='recommendation-context')


users_router = routers.NestedSimpleRouter(router, r'users', lookup='user')
users_router.register(r'preferences', views.PreferenceViewSet, base_name='user-preference')
users_router.register(r'stays', views.StayViewSet, base_name='user-stay')

#router.register(r'current-user', views.CurrentUserViewSet, basename='current-user')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(recommendations_router.urls)),
    path('', include(users_router.urls)),
    path('current-user/', current_user),
    path('login/', obtain_jwt_token),
    path('verify-token/', verify_jwt_token),
    #path('users/', UserApiView.as_view()),
    #path('things/', ThingCreateAPIView.as_view()),
    #path('things/', ThingSingleAPIView.as_view()),
    #path('things/', ThingListAPIView.as_view()),
    # path('api/things/', views.ThingListCreate.as_view())
]