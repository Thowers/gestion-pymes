from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('nuevo/', views.crear_producto, name='crear_producto'),
    path('<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('<int:pk>/movimiento/', views.registrar_movimiento, name='registrar_movimiento'),
    path('<int:pk>/historial/', views.historial_movimientos, name='historial_movimientos'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('buscar/', views.buscar_producto_ajax, name='buscar_producto_ajax'),
]
