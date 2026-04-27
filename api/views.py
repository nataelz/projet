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
    
    context = computer.to_dict()
    return HttpResponse(json.dumps(context), content_type="application/json")

def search(request):
    context = { "computers": [{"name": "test"}, {"name": "test2"}] }
    return HttpResponse(json.dumps(context), content_type="application/json")
