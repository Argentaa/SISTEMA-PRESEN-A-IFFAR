from django.urls import path

from . import views

urlpatterns = [
    path('', views.detect, name='detect_barcodes'),
    path('camera_feed', views.camera_feed, name='camera_feed'),
    path('dados', views.dados, name='dados'),
    path('dados_cod', views.dados_cod, name='dados_cod')
] 
