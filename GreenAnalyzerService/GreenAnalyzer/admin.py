from django.contrib import admin

from .models import RESModel, EnergyProfile

admin.site.register(RESModel)
admin.site.register(EnergyProfile)