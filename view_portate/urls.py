from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='view_portate-home'),
    path('merone1/', views.merone1, name='merone1'),
    path('merone3/', views.merone3, name='merone3'),
    path('trebisacce/', views.trebisacce, name='trebisacce'),
]