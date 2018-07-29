from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse('hello world')

def my_shares(request):
    context = {}
    return render(request, 'secret_store/my_shares.html', context)
