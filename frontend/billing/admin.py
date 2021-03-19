from django.contrib import admin
from .models import Item, Billing


admin.site.register(Billing)
admin.site.register(Item)
# Register your models here.
# from django.apps import apps


# models = apps.get_models()

# for model in models:
#     admin.site.register(model)