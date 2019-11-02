from django.urls import path, include
from rest_framework_nested import routers

from evaluation import views

router = routers.SimpleRouter()
router.register(r'questionnaires', views.QuestionnaireViewSet, base_name='questionnaire')
router.register(r'experiments', views.ExperimentViewSet, base_name='experiment')
router.register(r'questions', views.QuestionViewSet, base_name='question')
router.register(r'analytics', views.AnalyticsEventViewSet, base_name='analytics')
router.register(r'scenarios', views.ScenarioViewSet, base_name='scenarios')

experiments_router = routers.NestedSimpleRouter(router, r'experiments', lookup='experiment')
experiments_router.register(r'replies', views.ReplyViewSet, base_name='experiment-reply')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(experiments_router.urls)),
]