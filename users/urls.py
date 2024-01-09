from django.urls import path
from . import views as users_views

urlpatterns = [
    path('login/', users_views.log_in, name='login'),
    path('logout/', users_views.log_out, name='logout'),
]