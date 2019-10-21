from django.urls import path
from training import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.add_sample, name='add_sample'),
    path('statistics/', views.get_statistics, name='get_statistics'),
    path('results/', views.get_results, name='get_results')
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)