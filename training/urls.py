from django.urls import path

from training import views

urlpatterns = [
    path('', views.add_sample, name='add_sample')
]