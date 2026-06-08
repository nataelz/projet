from django.contrib import admin

from .models import Company, Component, Processor, ComputerProcessor, Memory, ComputerMemory, Storage, ComputerStorage, GraphicsCard, ComputerGraphicsCard, Network, ComputerNetwork, Computer

# Register your models here.
admin.site.register(Company)
admin.site.register(Processor)
admin.site.register(ComputerProcessor)
admin.site.register(Memory)
admin.site.register(ComputerMemory)
admin.site.register(Storage)
admin.site.register(ComputerStorage)
admin.site.register(GraphicsCard)
admin.site.register(ComputerGraphicsCard)
admin.site.register(Network)
admin.site.register(ComputerNetwork)
admin.site.register(Computer)
