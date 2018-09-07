from django.conf.urls import url, include
from django.urls import path
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'text_secret', views.TextSecretViewSet)

urlpatterns = [
        path('create', views.create, name='create'),
        path('manage', views.manage, name='manage'),
        path('recover', views.recover, name='recover'),
        url(r'^api/', include(router.urls)),
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
