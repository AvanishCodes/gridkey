from django.contrib import admin

from .models import Company, Trade

# Register your models here.
admin.site.register(Trade)
admin.site.register(Company)
