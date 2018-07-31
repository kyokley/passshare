from django.urls import path
from . import views

urlpatterns = [
        path('create', views.create, name='create'),
        path('manage', views.manage, name='manage'),
        path('recover', views.recover, name='recover'),
]
