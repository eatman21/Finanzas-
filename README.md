# Finansas - Sistema de Gestión Financiera Personal

Una aplicación web desarrollada en Django para la gestión financiera personal, que permite a los usuarios administrar sus perfiles financieros, deudas, objetivos financieros y realizar simulaciones de crédito.

## Características Principales

- **Perfil Financiero**: Gestión de ingresos, gastos, ahorros y score crediticio
- **Gestión de Deudas**: Registro y seguimiento de diferentes tipos de deudas
- **Objetivos Financieros**: Planificación y seguimiento de metas financieras
- **Simulaciones de Crédito**: Cálculo de pagos mensuales y tablas de amortización
- **Recomendaciones**: Sugerencias personalizadas basadas en el perfil financiero
- **Dashboard Interactivo**: Vista general de la situación financiera

## Instalación y Configuración

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**

   ```bash
   git clone <url-del-repositorio>
   cd Finansas
   ```

2. **Crear un entorno virtual**

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Crear un superusuario (opcional)**

   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecutar el servidor de desarrollo**

   ```bash
   python manage.py runserver
   ```

7. **Acceder a la aplicación**
   - Aplicación principal: <http://localhost:8000>
   - Panel de administración: <http://localhost:8000/admin>

## Estructura del Proyecto

```
Finansas/
├── finansas/                 # Configuración principal del proyecto
│   ├── __init__.py
│   ├── settings.py          # Configuración de Django
│   ├── urls.py              # URLs principales
│   ├── wsgi.py              # Configuración WSGI
│   └── asgi.py              # Configuración ASGI
├── finanzas/                # Aplicación principal
│   ├── __init__.py
│   ├── admin.py             # Configuración del admin
│   ├── apps.py              # Configuración de la app
│   ├── forms.py             # Formularios
│   ├── models.py            # Modelos de datos
│   ├── urls.py              # URLs de la app
│   └── views.py             # Vistas
├── manage.py                # Script de gestión de Django
├── requirements.txt         # Dependencias del proyecto
└── README.md               # Este archivo
```

## Modelos de Datos

### PerfilFinanciero

- Información básica del usuario (ingresos, gastos, ahorros)
- Cálculo automático de capacidad de ahorro y endeudamiento
- Score crediticio opcional

### Deuda

- Diferentes tipos de deudas (tarjetas, préstamos, hipotecas)
- Seguimiento de saldos, pagos mensuales y tasas de interés
- Fechas de inicio y plazos

### ObjetivoFinanciero

- Metas financieras con montos y plazos
- Cálculo automático del ahorro mensual requerido
- Estado activo/inactivo

### SimulacionCredito

- Simulaciones de créditos hipotecarios y automotrices
- Cálculo de pagos mensuales con fórmula de amortización
- Tabla de amortización completa
- Validación de viabilidad según capacidad de endeudamiento

### Recomendacion

- Sugerencias personalizadas para el usuario
- Sistema de prioridades (Alta, Media, Baja)
- Estado activo/inactivo

## Uso de la Aplicación

### 1. Crear Perfil Financiero

- Acceder a la aplicación y registrarse
- Completar la información financiera básica
- El sistema calculará automáticamente la capacidad de ahorro y endeudamiento

### 2. Gestionar Deudas

- Agregar todas las deudas existentes
- Especificar montos, tasas de interés y plazos
- El sistema mostrará un resumen de la situación de deuda

### 3. Establecer Objetivos

- Definir metas financieras (casa, auto, etc.)
- Especificar montos objetivo y plazos
- El sistema calculará el ahorro mensual necesario

### 4. Realizar Simulaciones

- Crear simulaciones de créditos hipotecarios o automotrices
- Ajustar parámetros (valor, enganche, tasa, plazo)
- Revisar la tabla de amortización y viabilidad

### 5. Revisar Recomendaciones

- El sistema generará recomendaciones basadas en el perfil
- Priorizar acciones según la urgencia
- Seguir las sugerencias para mejorar la salud financiera

## Funcionalidades Técnicas

### Cálculos Automáticos

- **Capacidad de Ahorro**: Ingreso total - Gastos fijos
- **Capacidad de Endeudamiento**: 35% del ingreso total
- **Pago Mensual**: Fórmula de amortización estándar
- **Ahorro Requerido**: Monto objetivo / Plazo en meses

### Validaciones

- Valores mínimos para ingresos y montos
- Rango de score crediticio (300-850)
- Tasas de interés entre 0% y 100%
- Plazos mínimos para créditos

### Seguridad

- Autenticación requerida para todas las vistas
- Validación de propiedad de datos
- Protección CSRF en formularios
- Sanitización de entradas

## Personalización

### Configuración de Capacidad de Endeudamiento

El porcentaje de capacidad de endeudamiento se puede modificar en el modelo `PerfilFinanciero`:

```python
@property
def capacidad_endeudamiento(self):
    # Cambiar 0.35 por el porcentaje deseado
    return self.ingreso_total * Decimal('0.35')
```

### Agregar Nuevos Tipos de Deuda

Modificar las opciones en el modelo `Deuda`:

```python
TIPO_DEUDA_CHOICES = [
    ('TARJETA', 'Tarjeta de Crédito'),
    ('PERSONAL', 'Préstamo Personal'),
    # Agregar nuevas opciones aquí
]
```

## Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Para soporte técnico o preguntas sobre el proyecto, por favor crear un issue en el repositorio.

## Roadmap

- [ ] Interfaz de usuario mejorada con Bootstrap
- [ ] Gráficos y visualizaciones de datos
- [ ] Exportación de reportes en PDF
- [ ] Integración con APIs bancarias
- [ ] Notificaciones por email
- [ ] Aplicación móvil
