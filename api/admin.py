from django.contrib import admin

from .models import Company, Component, Computer

# Register your models here.
admin.site.register(Company)
admin.site.register(Component)
admin.site.register(Computer)
