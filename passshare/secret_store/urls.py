from django.urls import path
from . import views

urlpatterns = [
        path('', views.index, name='index'),
        path('my_shares', views.my_shares, name='my_shares'),
        path('recover', views.index, name='recover'),
]
