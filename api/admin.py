from django.contrib import admin

from .models import Company, Component, Processor, Memory, Storage, GraphicsCard, Network, Computer

# Register your models here.
admin.site.register(Company)
admin.site.register(Component)
admin.site.register(Processor)
admin.site.register(Memory)
admin.site.register(Storage)
admin.site.register(GraphicsCard)
admin.site.register(Network)
admin.site.register(Computer)
