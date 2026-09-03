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

def split_and_get(request, field_name):
    field = request.GET.get(field_name)
    return list(filter(None, field.split(','))) if field else None

def search(request):
    computers = Computer.objects.all()

    constructor = split_and_get(request, "constructor")
    format_ = split_and_get(request, "format")
    site = split_and_get(request, "site")
    name = request.GET.get("name")
    serial = request.GET.get("serial_number")
    model = split_and_get(request, "model_number")
    processor = split_and_get(request, "processors")
    memory = split_and_get(request, "memory")
    storage = split_and_get(request, "storage")
    graphics_card = split_and_get(request, "graphics_card")
    network = split_and_get(request, "network")

    if constructor:
        computers = computers.filter(constructor_id__in=constructor)
    
    if format_:
        computers = computers.filter(format__in=format_)
    
    if site:
        computers = computers.filter(site=site)
    
    if name:
        computers = computers.filter(name__icontains=name)

    if serial:
        computers = computers.filter(serial_number=serial)

    if model:
        computers = computers.filter(model=model)

    if processor:
        computers = computers.filter(processors__id__in=processor)

    if memory:
        computers = computers.filter(memory__id__in=processor)

    if storage:
        computers = computers.filter(storage__id__in=processor)

    if graphics_card:
        computers = computers.filter(graphics_card__id__in=processor)

    if network:
        computers = computers.filter(network__id__in=processor)

    computers = computers.distinct()

    limit = request.GET.get("limit")
    if not limit or limit > 250:
        limit = 50
    
    computers = computers[:int(limit)]

    return JsonResponse(
        [computer.to_dict() for computer in computers],
        safe=False
    )
