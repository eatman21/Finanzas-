# 🚀 Inicio Rápido - Finanzas en Cursor

## Opción 1: Setup Automático (Recomendado)

```bash
# Dale permisos al script y ejecútalo
chmod +x setup.sh
./setup.sh
```

Esto configurará todo automáticamente: entorno virtual, dependencias, base de datos y superusuario.

---

## Opción 2: Setup Manual

### 1. Crear y Activar Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar en Linux/Mac
source venv/bin/activate

# Activar en Windows
venv\Scripts\activate
```

### 2. Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configurar Base de Datos

```bash
# Crear directorios necesarios
mkdir -p logs media staticfiles

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate
```

### 4. Crear Superusuario

```bash
python manage.py createsuperuser
```

Ingresa:
- Username: `admin` (o el que prefieras)
- Email: tu email
- Password: contraseña segura

### 5. Recolectar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### 6. Iniciar Servidor

```bash
python manage.py runserver
```

---

## 🌐 Acceder a la Aplicación

Una vez iniciado el servidor:

**Aplicación Principal:**
- URL: http://127.0.0.1:8000
- Login: http://127.0.0.1:8000/login/

**Panel de Administración:**
- URL: http://127.0.0.1:8000/admin/
- User: admin (el que creaste)
- Password: tu contraseña

**API REST:**
- URL: http://127.0.0.1:8000/api/
- Documentación: http://127.0.0.1:8000/api/swagger/ (si configuras drf-yasg)

---

## 📂 Estructura de la Aplicación

```
Finanzas/
├── 🏠 Dashboard          → http://127.0.0.1:8000/dashboard/
├── 💰 Perfil Financiero  → Gestiona tus ingresos y gastos
├── 💳 Deudas            → Tracking de préstamos y tarjetas
├── 🎯 Objetivos         → Metas de ahorro
├── 🏦 Simulador Crédito → Calculadora hipotecaria
├── 📊 Cuentas (Nuevo)   → Sistema moderno de cuentas
├── 💸 Transacciones     → Registro de movimientos
└── 📈 Presupuestos      → Control de gastos
```

---

## 🔧 Comandos Útiles en Cursor

### Terminal en Cursor
Presiona `Ctrl+` ` (backtick) o `Cmd+` ` para abrir/cerrar la terminal integrada

### Comandos Django Comunes

```bash
# Ver todas las URLs disponibles
python manage.py show_urls

# Crear nueva migración
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Abrir shell de Django
python manage.py shell

# Crear datos de prueba
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user('test', 'test@test.com', 'test123')

# Limpiar base de datos (cuidado!)
python manage.py flush

# Ejecutar servidor en puerto diferente
python manage.py runserver 8080

# Ejecutar servidor para acceso externo
python manage.py runserver 0.0.0.0:8000
```

---

## 🐛 Troubleshooting

### Error: "No module named 'finanzas'"

Asegúrate de que el entorno virtual esté activado:
```bash
source venv/bin/activate
```

### Error: "OperationalError: no such table"

Ejecuta las migraciones:
```bash
python manage.py migrate
```

### Error: Port 8000 already in use

Cambia el puerto:
```bash
python manage.py runserver 8080
```

O mata el proceso:
```bash
# En Linux/Mac
lsof -ti:8000 | xargs kill -9

# En Windows
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

### Error: "ModuleNotFoundError"

Reinstala dependencias:
```bash
pip install -r requirements.txt
```

### Base de datos SQLite bloqueada

```bash
# Eliminar base de datos y recrear
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 🎨 Personalización

### Cambiar Tema/Colores

Edita: `finanzas/static/css/`

### Agregar Nueva Funcionalidad

1. Crea modelo en `finanzas/models/`
2. Crea formulario en `finanzas/forms.py`
3. Crea vista en `finanzas/views.py`
4. Agrega URL en `finanzas/urls.py`
5. Crea template en `templates/finanzas/`

### Configurar Email

Edita `.env`:
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
```

---

## 🔒 Seguridad

**⚠️ IMPORTANTE:**
- ✅ `.env` ya está configurado con SECRET_KEY segura
- ✅ No subas `.env` a Git (ya está en .gitignore)
- ⚠️ En producción, cambia `DEBUG=False`
- ⚠️ Lee `IMPROVEMENTS.md` para más recomendaciones de seguridad

---

## 📚 Siguientes Pasos

1. ✅ Completa tu perfil financiero
2. ✅ Agrega tus cuentas bancarias
3. ✅ Registra tus transacciones
4. ✅ Crea objetivos de ahorro
5. ✅ Simula créditos hipotecarios
6. ✅ Configura presupuestos mensuales

---

## 🆘 Ayuda

- **Documentación:** Ver `README.md`
- **Mejoras:** Ver `IMPROVEMENTS.md`
- **Issues:** Reporta en GitHub
- **API:** Visita `/api/` cuando el servidor esté corriendo

---

¡Disfruta gestionando tus finanzas! 💰📊
