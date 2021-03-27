from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('addproduct/', views.getStatusUpdate, name='newProduct'),
    path('refreshData/', views.cartDetails, name='cartRefresh')
]