# GestiónPyMES 🏪
**Sistema inteligente de Gestión de Inventarios y Clientes**  
Universidad Manuela Beltrán – Sistemas Transaccionales 2026

---

## 🚀 Instalación rápida

```bash
# 1. Clonar / descomprimir el proyecto
cd gestion_pymes

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Ejecutar el script de configuración
bash setup.sh

# 4. Levantar el servidor
python manage.py runserver
```

Abrir en el navegador: **http://127.0.0.1:8000**  
Usuario: `admin` | Contraseña: `admin123`

---

## 📁 Estructura del proyecto

```
gestion_pymes/
├── core/           → Autenticación y dashboard
├── inventario/     → Productos, categorías, movimientos de stock
├── ventas/         → POS (punto de venta), historial
├── cartera/        → Clientes, deudas, abonos con comprobante único
├── templates/      → Todas las vistas HTML
├── manage.py
├── requirements.txt
└── setup.sh        → Script de instalación
```

---

## ✅ Funcionalidades implementadas

### Dashboard
- Métricas del día: ventas, stock bajo, clientes con saldo
- Gráfico de ventas (últimos 7 días)
- Top 5 productos más vendidos
- Últimas transacciones

### Inventario
- CRUD de productos con código, precios, stock actual y mínimo
- Alertas automáticas de stock bajo
- Movimientos de stock: entrada, salida, ajuste (con auditoría)
- Historial de movimientos por producto
- Categorías de productos
- Búsqueda por nombre o código

### Punto de Venta (POS)
- Búsqueda de productos en tiempo real (AJAX)
- Carrito interactivo (sin recargar la página)
- Soporte para: efectivo, transferencia, crédito
- Registro atómico de ventas (propiedades ACID)
- Descuento automático del inventario al vender
- Generación automática de deuda si el pago es a crédito

### Cartera
- Registro de clientes con datos de contacto
- Visualización de saldo pendiente por cliente
- Registro de abonos con **comprobante único** (ej: AB-2026-A1B2C3)
- Historial de abonos por cliente

### Seguridad y roles
- Login/logout integrado con Django
- Roles: **Administrador** y **Cajero**
- Restricciones: solo admins pueden crear/editar/eliminar productos

---

## ☁️ Despliegue en Railway

1. Crear cuenta en [railway.app](https://railway.app)
2. Conectar el repositorio de GitHub
3. Agregar las variables de entorno:
   ```
   SECRET_KEY=tu-clave-secreta
   DEBUG=False
   ALLOWED_HOSTS=tu-dominio.railway.app
   ```
4. Railway detectará el `Procfile` automáticamente

### Persistencia de SQLite en Railway
Railway usa efímero por defecto. Para persistir la base de datos:
- Ir a **Settings → Volumes** y montar un volumen en `/app`
- O migrar a PostgreSQL añadiendo el plugin de Railway y cambiando `DATABASES` en `settings.py`

---

## 🏗️ Arquitectura técnica

- **Framework**: Django 5 (patrón MVT)
- **Base de datos**: SQLite con **WAL** habilitado (mejor concurrencia)
- **Transacciones**: `transaction.atomic()` en todas las operaciones críticas
- **Propiedades ACID**: garantizadas por el ORM de Django
- **Despliegue**: Railway (PaaS) con WhiteNoise para archivos estáticos
- **Frontend**: Bootstrap 5 + Bootstrap Icons (sin dependencias de npm)

---

## 👤 Crear cajeros adicionales

```bash
python manage.py shell
>>> from core.models import Usuario
>>> Usuario.objects.create_user(username='cajero1', password='clave123', rol='cajero')
```

O usar el panel de administración: `http://127.0.0.1:8000/admin/`
