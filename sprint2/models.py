from django.db import models

from django.utils import timezone
import uuid


from healthApp.models import Patient as HealthAppPatient
from healthApp.models import Service as HealthAppService


# También podrías necesitar Appointment si quieres facturar basado en citas completadas
from healthApp.models import Appointment as HealthAppAppointment


class Factura(models.Model):
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('EMITIDA', 'Emitida'),
        ('PAGADA', 'Pagada'),
        ('ANULADA', 'Anulada'),
        ('VENCIDA', 'Vencida'),
    ]

    # --- CONEXIÓN AL MODELO PACIENTE DE HEALTHAPP ---
    paciente = models.ForeignKey(
        HealthAppPatient,  # Usamos el modelo importado
        on_delete=models.SET_NULL,
        # O models.PROTECT si no quieres borrar facturas si se borra un paciente con facturas
        null=True,
        blank=False,  # Hacemos que el paciente sea obligatorio para una factura
        related_name='facturas_sprint2'  # 'related_name' para evitar conflictos si Patient ya tiene 'facturas'
    )

    numero_factura = models.CharField(max_length=50, unique=True, blank=True)
    fecha_emision = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField(null=True, blank=True)

    total_bruto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    porcentaje_impuesto = models.DecimalField(max_digits=5, decimal_places=2, default=21.00,
                                              help_text="Ej. 21.00 para 21% IVA")  # Por defecto 21%
    monto_impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_neto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='BORRADOR')
    metodo_pago_sugerido = models.CharField(max_length=100, blank=True, null=True)
    notas_adicionales = models.TextField(blank=True, null=True)

    archivo_pdf = models.FileField(upload_to='facturas_pdf/', blank=True, null=True)

    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)



    def __str__(self):
        paciente_nombre = self.paciente.first_name + " " + self.paciente.last_name if self.paciente else "N/A"
        return f"Factura {self.numero_factura} - {paciente_nombre}"

    def generar_numero_factura(self):
        if not self.numero_factura:

            prefijo = "FACT"
            anio_actual = timezone.now().strftime('%Y')


            # Usando la versión anterior por simplicidad de implementación inicial:
            timestamp = timezone.now().strftime('%y%m%d')  # Año con 2 dígitos para acortar
            unique_part = str(uuid.uuid4()).split('-')[0][:4].upper()
            self.numero_factura = f"{prefijo}{timestamp}-{unique_part}"  # Ej: FACT231026-A1B2

    def calcular_totales(self):
        # Asegurarse de que las líneas existen y están cargadas
        if hasattr(self, 'lineas_factura') and self.lineas_factura.exists():
            self.total_bruto = sum(linea.subtotal for linea in self.lineas_factura.all())
        else:

            self.total_bruto = sum(lf.subtotal for lf in LineaFactura.objects.filter(factura=self))

        if self.porcentaje_impuesto > 0:
            self.monto_impuesto = (self.total_bruto * self.porcentaje_impuesto) / 100
        else:
            self.monto_impuesto = 0
        self.total_neto = self.total_bruto + self.monto_impuesto

    def save(self, *args, **kwargs):
        if not self.pk:  # Solo al crear por primera vez
            self.generar_numero_factura()

        super().save(*args, **kwargs)


class LineaFactura(models.Model):
    factura = models.ForeignKey(Factura, related_name='lineas_factura', on_delete=models.CASCADE)


    servicio = models.ForeignKey(
        HealthAppService,  # Usamos el modelo importado
        on_delete=models.SET_NULL,  # O models.PROTECT
        null=True,
        blank=True
    )
    # Descripción manual, útil si no se usa un 'servicio' o para añadir detalles
    descripcion_manual = models.CharField(max_length=255, blank=True)

    cantidad = models.PositiveIntegerField(default=1)
    # El precio unitario podría autocompletarse si se selecciona un servicio,
    # pero lo dejamos editable para flexibilidad (descuentos, precios especiales).
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def __str__(self):
        concepto = ""
        if self.servicio:
            concepto = self.servicio.name
        elif self.descripcion_manual:
            concepto = self.descripcion_manual
        else:
            concepto = "Concepto no especificado"
        return f"{self.cantidad} x {concepto} (Fact: {self.factura.numero_factura})"

    def clean(self):
        # Autocompletar precio_unitario y descripcion_manual si se selecciona un servicio y están vacíos
        if self.servicio and not self.pk:  # Solo al crear la línea y si hay servicio
            if not self.precio_unitario or self.precio_unitario == 0:
                self.precio_unitario = self.servicio.price
            if not self.descripcion_manual:
                self.descripcion_manual = self.servicio.name  # O self.servicio.description si prefieres

    def save(self, *args, **kwargs):
        # self.clean() # Llama a clean para autocompletar si es necesario, aunque Django no lo hace por defecto en save.
        # Es mejor manejar la lógica de autocompletado en el form o la vista.
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        # No recalcular totales de factura aquí para cada línea guardada,
        # es más eficiente hacerlo una vez en la vista después de todas las operaciones de líneas.