from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
# from django.contrib.auth.decorators import csrfexempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime
from billing.models import Item, Billing

import json
# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@api_view(["POST"])
@csrf_exempt
def getStatusUpdate(request):
    data = request.data.dict()
    print(type(data))
    print(data)
    x = Item.objects.get(name = data['name'])
    itemAdd = Billing.objects.filter(item = x, dateOfPurchase = datetime.now())
    if len(itemAdd)>0:
        itemX = Billing.objects.get(item = x, dateOfPurchase = datetime.now())
        itemX.quantity +=1
        itemX.totalPrice += x.price
        itemX.save()
    else:
        Billing.objects.create(
            item = x,
            quantity = data['quantity'],
            price = x.price, 
            dateOfPurchase = datetime.now())

def cartDetails(request):
    billing = Billing.objects.filter(dateOfPurchase = datetime.now())
    context = {
        'data':billing
    }
    return render(request, 'index.html', context)
