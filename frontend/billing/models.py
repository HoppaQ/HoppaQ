from django.db import models
# from datetime import datetime 
from django.utils.timezone import now
# Create your models here.

class Item(models.Model):
    name = models.CharField(max_length=300)
    brandName = models.CharField(max_length=300)
    price = models.FloatField()
    manufactureDate = models.DateField(default=now, blank=True)

class Billing(models.Model):
    item = models.ForeignKey(Item, on_delete=CASCADE)
    quantity = models.IntegerField(default=1)
    totalPrice = models.FloatField()
    dateOfPurchase = models.DateField(default=now, blank=True)