from django.urls import path
from . import views;

urlpatterns = [
    path("",views.streamHandle),
    path('<slug:slug>/', views.startStream),
    path('video/play/<int:id>/', views.videoServe),
]