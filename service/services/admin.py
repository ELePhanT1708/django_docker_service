from django.contrib import admin

from services.models import Subscription, Plan, Service

# Register your models here.
admin.site.register(Subscription)
admin.site.register(Plan)
admin.site.register(Service)