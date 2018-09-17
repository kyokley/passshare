from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from passshare.secret_store.models import TextSecret, UPSecret, FileSecret, COUNTDOWN_CHOICES, COUNTDOWN_DEFAULT
from passshare.secret_store import serializers
from passshare.secret_store.permissions import IsOwnerOrSharedWith

@ensure_csrf_cookie
def create(request):
    user = request.user

    # TODO: Make this raise a 403
    if not user.is_authenticated:
        raise Exception('User not authenticated')

    text_shares = TextSecret.objects.filter(owner=user)
    up_shares = UPSecret.objects.filter(owner=user)
    file_shares = FileSecret.objects.filter(owner=user)

    context = {'user': request.user,
               'text_shares': text_shares,
               'up_shares': up_shares,
               'file_shares': file_shares,
               'countdown_options': COUNTDOWN_CHOICES,
               'countdown_default': COUNTDOWN_DEFAULT,
            }
    return render(request, 'secret_store/create.html', context)

def manage(request):
    user = request.user

    # TODO: Make this raise a 403
    if not user.is_authenticated:
        raise Exception('User not authenticated')

    text_shares = TextSecret.objects.filter(owner=user)
    up_shares = UPSecret.objects.filter(owner=user)
    file_shares = FileSecret.objects.filter(owner=user)

    context = {'user': request.user,
               'text_shares': text_shares,
               'up_shares': up_shares,
               'file_shares': file_shares,
            }
    return render(request, 'secret_store/manage.html', context)

def recover(request):
    user = request.user

    # TODO: Make this raise a 403
    if not user.is_authenticated:
        raise Exception('User not authenticated')

    text_shares = TextSecret.objects.filter(owner=user)
    up_shares = UPSecret.objects.filter(owner=user)
    file_shares = FileSecret.objects.filter(owner=user)

    context = {'user': request.user,
               'text_shares': text_shares,
               'up_shares': up_shares,
               'file_shares': file_shares,
            }
    return render(request, 'secret_store/recover.html', context)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAdminUser,)

class TextSecretViewSet(viewsets.ModelViewSet):
    queryset = TextSecret.objects.all()
    serializer_class = serializers.TextSecretSerializer
    permission_classes = (IsOwnerOrSharedWith,)

    def create(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.validated_data['owner'] = request.user
            serializer.save()
            return Response(serializer.data)
        else:
            # TODO: Make failures return something useful
            pass

    def destroy(self, request, pk=None):
        obj = get_object_or_404(self.queryset, pk=pk)

        if obj.owner != self.request.user:
            raise Exception('User is not the owner of this object')
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
