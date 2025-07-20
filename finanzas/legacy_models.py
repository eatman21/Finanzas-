from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class PerfilFinanciero(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    ingreso_mensual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    otros_ingresos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    gastos_fijos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    ahorro_mensual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    ahorro_actual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    score_crediticio = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(300), MaxValueValidator(850)]
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    @property
    def ingreso_total(self):
        return self.ingreso_mensual + self.otros_ingresos

    @property
    def capacidad_ahorro(self):
        return self.ingreso_total - self.gastos_fijos

    @property
    def capacidad_endeudamiento(self):
        # Generalmente se considera el 30-35% del ingreso neto
        return self.ingreso_total * Decimal('0.35')

    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class Deuda(models.Model):
    TIPO_DEUDA_CHOICES = [
        ('TARJETA', 'Tarjeta de Crédito'),
        ('PERSONAL', 'Préstamo Personal'),
        ('ESTUDIANTIL', 'Préstamo Estudiantil'),
        ('AUTO', 'Préstamo Automotriz'),
        ('HIPOTECA', 'Hipoteca'),
        ('OTRO', 'Otro'),
    ]

    perfil = models.ForeignKey(
        PerfilFinanciero, on_delete=models.CASCADE, related_name='deudas')
    tipo = models.CharField(max_length=20, choices=TIPO_DEUDA_CHOICES)
    nombre = models.CharField(max_length=100)
    saldo_actual = models.DecimalField(max_digits=12, decimal_places=2)
    pago_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    tasa_interes = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    fecha_inicio = models.DateField()
    plazo_meses = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - ${self.saldo_actual}"


class ObjetivoFinanciero(models.Model):
    TIPO_OBJETIVO_CHOICES = [
        ('CASA', 'Compra de Casa'),
        ('AUTO', 'Compra de Auto'),
        ('OTRO', 'Otro'),
    ]

    perfil = models.ForeignKey(
        PerfilFinanciero, on_delete=models.CASCADE, related_name='objetivos')
    tipo = models.CharField(max_length=20, choices=TIPO_OBJETIVO_CHOICES)
    nombre = models.CharField(max_length=100)
    monto_objetivo = models.DecimalField(max_digits=12, decimal_places=2)
    plazo_meses = models.IntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    @property
    def ahorro_mensual_requerido(self):
        if self.plazo_meses > 0:
            return self.monto_objetivo / self.plazo_meses
        return 0

    def __str__(self):
        return f"{self.nombre} - ${self.monto_objetivo}"


class SimulacionCredito(models.Model):
    TIPO_CREDITO_CHOICES = [
        ('HIPOTECARIO', 'Crédito Hipotecario'),
        ('AUTOMOTRIZ', 'Crédito Automotriz'),
    ]

    perfil = models.ForeignKey(
        PerfilFinanciero, on_delete=models.CASCADE, related_name='simulaciones')
    tipo = models.CharField(max_length=20, choices=TIPO_CREDITO_CHOICES)
    nombre = models.CharField(max_length=100)
    valor_propiedad = models.DecimalField(max_digits=12, decimal_places=2)
    enganche_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    tasa_interes_anual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    plazo_anos = models.IntegerField(validators=[MinValueValidator(1)])
    gastos_adicionales = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Seguros, notaría, etc."
    )
    fecha_simulacion = models.DateTimeField(auto_now_add=True)

    @property
    def monto_enganche(self):
        return self.valor_propiedad * (self.enganche_porcentaje / 100)

    @property
    def monto_credito(self):
        return self.valor_propiedad - self.monto_enganche

    @property
    def plazo_meses(self):
        return self.plazo_anos * 12

    @property
    def tasa_mensual(self):
        return (self.tasa_interes_anual / 100) / 12

    @property
    def pago_mensual(self):
        if self.tasa_mensual == 0:
            return self.monto_credito / self.plazo_meses

        # Fórmula de amortización
        return self.monto_credito * (
            (self.tasa_mensual * (1 + self.tasa_mensual) ** self.plazo_meses) /
            ((1 + self.tasa_mensual) ** self.plazo_meses - 1)
        )

    @property
    def pago_total(self):
        return self.pago_mensual * self.plazo_meses + self.gastos_adicionales

    @property
    def intereses_totales(self):
        return self.pago_total - self.monto_credito - self.gastos_adicionales

    def es_viable(self):
        if not hasattr(self, 'perfil'):
            return False
        return self.pago_mensual <= self.perfil.capacidad_endeudamiento

    def tabla_amortizacion(self):
        tabla = []
        saldo = self.monto_credito

        for mes in range(1, self.plazo_meses + 1):
            interes = saldo * self.tasa_mensual
            capital = self.pago_mensual - interes
            saldo -= capital

            tabla.append({
                'mes': mes,
                'pago': self.pago_mensual,
                'capital': capital,
                'interes': interes,
                'saldo': max(0, saldo)
            })

        return tabla

    def __str__(self):
        return f"{self.nombre} - {self.tipo}"


class Recomendacion(models.Model):
    PRIORIDAD_CHOICES = [
        ('ALTA', 'Alta'),
        ('MEDIA', 'Media'),
        ('BAJA', 'Baja'),
    ]

    perfil = models.ForeignKey(
        PerfilFinanciero, on_delete=models.CASCADE, related_name='recomendaciones')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.titulo
