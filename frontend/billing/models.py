from django.db import models
# from datetime import datetime 
from django.utils.timezone import now
# Create your models here.

class Item(models.Model):
    name = models.CharField(max_length=300)
    brandName = models.CharField(max_length=300)
    price = models.FloatField()
    quantity = models.IntegerField(default=1)
    purchaseDate = models.DateField(default=now, blank=True)
