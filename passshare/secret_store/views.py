from django.shortcuts import render
from django.http import HttpResponse

from passshare.secret_store.models import TextSecret, UPSecret, FileSecret

def index(request):
    return HttpResponse('hello world')

def my_shares(request):
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
    return render(request, 'secret_store/my_shares.html', context)
