#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Script de configuración inicial – GestiónPyMES
# Ejecutar una sola vez después de clonar el proyecto.
# ─────────────────────────────────────────────────────────────────────────────

set -e

echo "==> Instalando dependencias..."
pip install -r requirements.txt

echo "==> Creando archivo .env (si no existe)..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "    ✓ Archivo .env creado. Puedes editarlo con tu SECRET_KEY real."
fi

echo "==> Ejecutando migraciones..."
python manage.py makemigrations core inventario ventas cartera
python manage.py migrate

echo "==> Creando superusuario administrador..."
python manage.py shell << 'PYEOF'
from core.models import Usuario
if not Usuario.objects.filter(username='admin').exists():
    Usuario.objects.create_superuser(
        username='admin',
        password='admin123',
        email='admin@gestionpymes.com',
        rol='admin',
        first_name='Administrador',
    )
    print("    ✓ Superusuario creado: admin / admin123")
else:
    print("    ✓ El superusuario 'admin' ya existe.")
PYEOF

echo "==> Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

echo ""
echo "────────────────────────────────────────────"
echo " ✅ Proyecto listo. Ejecuta:"
echo "    python manage.py runserver"
echo ""
echo " Usuario: admin"
echo " Contraseña: admin123"
echo " URL: http://127.0.0.1:8000"
echo "────────────────────────────────────────────"
