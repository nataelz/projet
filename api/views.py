import json

from django.http import HttpResponse,HttpRequest, Http404, JsonResponse
from django.shortcuts import render

from .models import Computer

# Create your views here.
def index(request):
    return HttpResponse("Hello, World!")

def computer(request, computer_id):
    try:
        computer = Computer.objects.get(pk=computer_id)
    except Computer.DoesNotExist:
        raise Http404()
    
    context = {"computer": computer}
    return render(request, "api/computer.html", context)

def search(request):
    context = { "computers": [{"name": "test"}, {"name": "test2"}] }
    return render(request, "api/search.html", context)
