from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse

# Create your views here.
def test_view(request):
    return HttpResponse('oi')