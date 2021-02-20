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
from billing.models import Item

import json
# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
    

@api_view(["POST"])
# @permission_classes([AllowAny])
# @method_decorator(csrfexempt)
@csrf_exempt
def getStatusUpdate(request):
    data = request.data.dict()
    print(type(data))
    print(data)
    x = Item.objects.filter(name = data['name'], purchaseDate = str(datetime.now))
    
    print(x)

    # objectX = Item.objects.create(
    #     name = data['name'],
    #     brandName = data['brandName'],
    #     price= float(data['price']),
    #     quantity = 1,
    # )

    return JsonResponse({
            'status' : "Failed",
            'message' : 'Subscription does not exist'
        })
