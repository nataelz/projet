import json

from django.http import HttpResponse,HttpRequest, Http404, JsonResponse
from django.shortcuts import render

from .models import Company, Processor, Memory, Storage, GraphicsCard, Network, Computer

# Create your views here.
def index(request):
    return HttpResponse("Hello, World!")

def company(request, company_id):
    try:
        company = Company.objects.get(pk=company_id)
    except Company.DoesNotExist:
        raise Http404()
    
    context = company.to_dict()
    return HttpResponse(json.dumps(context), content_type="application/json")

def processor(request, processor_id):
    try:
        processor = Processor.objects.get(pk=processor_id)
    except Processor.DoesNotExist:
        raise Http404()
    
    context = processor.to_dict()
    return HttpResponse(json.dumps(context), content_type="application/json")

def memory(request, memory_id):
    try:
        memory = Memory.objects.get(pk=memory_id)
    except Memory.DoesNotExist:
        raise Http404()
    
    context = memory.to_dict()
    return HttpResponse(json.dumps(context), content_type="application/json")

def storage(request, storage_id):
    try:
        storage = Storage.objects.get(pk=storage_id)
    except Storage.DoesNotExist:
        raise Http404()
    
    context = storage.to_dict()
    return HttpResponse(json.dumps(context), content_type="application/json")

def graphicscard(request, graphicscard_id):
    try:
        graphicscard = GraphicsCard.objects.get(pk=graphicscard_id)
    except GraphicsCard.DoesNotExist:
        raise Http404()
    
    context = graphicscard.to_dict()
    return HttpResponse(json.dumps(context), content_type="application/json")

def network(request, network_id):
    try:
        network = Network.objects.get(pk=network_id)
    except Network.DoesNotExist:
        raise Http404()
    
    context = network.to_dict()
    return HttpResponse(json.dumps(context), content_type="application/json")

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
