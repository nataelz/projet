import json

from django.http import HttpResponse,HttpRequest, Http404, JsonResponse
from django.shortcuts import render

from .models import Company, Processor, Memory, Storage, GraphicsCard, Network, PowerSupply, Computer

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

def powersupply(request, powersupply_id):
    try:
        powersupply = Network.objects.get(pk=powersupply_id)
    except PowerSupply.DoesNotExist:
        raise Http404()

    context = powersupply.to_dict()
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

    # direct search
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
    power_supply = split_and_get(request, "power_supply")

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

    if power_supply:
        computers = computers.filter(power_supply__id__in=power_supply)

    # value search
    price_min =                   requests.GET.get("price_min")
    price_max =                   requests.GET.get("price_max")
    processors_constructor =      split_and_get("processors_constructor")
    processors_arch =             split_and_get("processors_arch")
    processors_freq_min =         requests.GET.get("processors_freq_min")
    processors_freq_max =         requests.GET.get("processors_freq_max")
    processors_core_min =         requests.GET.get("processors_core_min")
    processors_core_max =         requests.GET.get("processors_core_max")
    memory_constructor =          split_and_get("memory_constructor")
    memory_type =                 split_and_get("memory_type")
    memory_size_min =             requests.GET.get("memory_size_min")
    memory_size_max =             requests.GET.get("memory_size_max")
    memory_freq_min =             requests.GET.get("memory_freq_min")
    memory_freq_max =             requests.GET.get("memory_freq_max")
    storage_constructor =         split_and_get("storage_constructor")
    storage_type =                split_and_get("memory_type")
    storage_size_min =            requests.GET.get("memory_size_min")
    storage_size_max =            requests.GET.get("memory_size_max")
    graphics_card_constructor =   split_and_get("graphics_card_constructor")
    graphics_card_vram_size_min = requests.GET.get("graphics_card_vram_size_min")
    graphics_card_vram_size_max = requests.GET.get("graphics_card_vram_size_max")
    network_constructor =         split_and_get("network_constructor")
    network_type =                split_and_get("network_type")
    network_speed_min =           requests.GET.get("network_speed_min")
    network_speed_max =           requests.GET.get("network_speed_max")
    power_supply_constructor =    split_and_get("power_supply_constructor")
    power_supply_form_factor =    split_and_get("power_supply_form_factor")
    power_supply_wattage_min =    requests.GET.get("power_supply_wattage_min")
    power_supply_wattage_max =    requests.GET.get("power_supply_wattage_max")
    power_supply_rating =         split_and_get("power_supply_rating")

    if prince_min:
        computers = computers.filter(price__gte=price_min)

    if prince_max:
        computers = computers.filter(price__lte=price_max)

    if processors_constructor:
        computers = computers.filter(processors__constructor__in=processors_constructor)
    
    if processors_arch:
        computers = computers.filter(processors__architecture__in=processors_arch)
    
    if processors_freq_min:
        computers = computers.filter(processors__frequency__gte=processors_freq_min)

    if processors_freq_max:
        computers = computers.filter(processors__frequency__lte=processors_freq_max)

    if processors_core_min:
        computers = computers.filter(processors__core__gte=processors_core_min)

    if processors_core_max:
        computers = computers.filter(processors__core__lte=processors_core_max)

    if memory_constructor:
        computers = computers.filter(memory__constructor__in=memory_constructor)
    
    if memory_type:
        computers = computers.filter(memory__type__in=memory_type)
    
    if memory_size_min:
        computers = computers.filter(memory__size__gte=memory_size_min)

    if memory_size_max:
        computers = computers.filter(memory__size__lte=memory_size_max)

    if memory_freq_min:
        computers = computers.filter(memory__frequency__gte=memory_freq_min)

    if memory_freq_max:
        computers = computers.filter(memory__frequency__lte=memory_freq_max)
    
    if storage_constructor:
        computers = computers.filter(storage__constructor__in=storage_constructor)
    
    if storage_type:
        computers = computers.filter(storage__type__in=storage_type)
    
    if storage_size_min:
        computers = computers.filter(storage__size__gte=storage_size_min)

    if storage_size_max:
        computers = computers.filter(storage__size__lte=storage_size_max)
    
    if graphics_card_constructor:
        computers = computers.filter(graphics_card__constructor__in=graphics_card_constructor)
        
    if graphics_card_vram_size_min:
        computers = computers.filter(graphics_card__vram_size__gte=graphics_card_vram_size_min)

    if graphics_card_vram_size_max:
        computers = computers.filter(graphics_card__vram_size__lte=graphics_card_vram_size_max)

    if network_constructor:
        computers = computers.filter(network__constructor__in=network_constructor)
    
    if network_type:
        computers = computers.filter(network__type__in=network_type)
    
    if network_speed_min:
        computers = computers.filter(network__speed__gte=network_speed_min)

    if network_speed_max:
        computers = computers.filter(network__speed__lte=network_speed_max)

    if power_supply_constructor:
        computers = computers.filter(power_supply__constructor__in=power_supply_constructor)
    
    if power_supply_form_factor:
        computers = computers.filter(power_supply__form_factor__in=power_supply_form_factor)
    
    if power_supply_wattage_min:
        computers = computers.filter(power_supply__wattage__gte=power_supply_wattage_min)

    if power_supply_wattage_max:
        computers = computers.filter(power_supply__wattage__lte=power_supply_wattage_max)

    if power_supply_rating:
        computers = computers.filter(power_supply__rating__in=power_supply_rating)
    
    computers = computers.distinct()

    limit = request.GET.get("limit")
    if not limit or limit > 250:
        limit = 50
    
    computers = computers[:int(limit)]

    return JsonResponse(
        [computer.to_dict() for computer in computers],
        safe=False
    )
