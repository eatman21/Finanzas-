#!/bin/bash

echo "🚀 Configurando Finanzas Application..."
echo ""

# 1. Crear entorno virtual
echo "📦 Creando entorno virtual..."
python -m venv venv

# 2. Activar entorno virtual
echo "✅ Activando entorno virtual..."
source venv/bin/activate

# 3. Actualizar pip
echo "⬆️  Actualizando pip..."
pip install --upgrade pip

# 4. Instalar dependencias
echo "📚 Instalando dependencias (esto puede tomar unos minutos)..."
pip install -r requirements.txt

# 5. Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

# 6. Aplicar migraciones
echo "🗄️  Aplicando migraciones de base de datos..."
python manage.py makemigrations
python manage.py migrate

# 7. Crear superusuario
echo ""
echo "👤 Ahora vamos a crear un superusuario para el admin..."
python manage.py createsuperuser

# 8. Recolectar archivos estáticos
echo ""
echo "🎨 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo ""
echo "✅ ¡Configuración completada!"
echo ""
echo "Para iniciar el servidor ejecuta:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Luego abre tu navegador en: http://127.0.0.1:8000"
echo ""
