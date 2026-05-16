from django.urls import path
from . import views

urlpatterns = [
    path('', views.pos, name='pos'),
    path('procesar/', views.procesar_venta, name='procesar_venta'),
    path('historial/', views.historial_ventas, name='historial_ventas'),
    path('<int:pk>/', views.detalle_venta, name='detalle_venta'),
]
