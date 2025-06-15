from django.contrib import admin
from .models import Factura, LineaFactura

class LineaFacturaInline(admin.TabularInline): # O admin.StackedInline
    model = LineaFactura
    extra = 1 # Número de líneas vacías para añadir
    # readonly_fields = ('subtotal',) # Si quieres que el subtotal no sea editable aquí

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'paciente', 'fecha_emision', 'total_neto', 'estado', 'archivo_pdf')
    list_filter = ('estado', 'fecha_emision', 'paciente')
    search_fields = ('numero_factura', 'paciente__nombre', 'paciente__apellido') # Asume que Paciente tiene nombre y apellido
    readonly_fields = ('total_bruto', 'monto_impuesto', 'total_neto', 'creada_en', 'actualizada_en')
    inlines = [LineaFacturaInline]
    fieldsets = (
        (None, {
            'fields': ('paciente', 'numero_factura', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_emision', 'fecha_vencimiento')
        }),
        ('Detalles de Pago (Informativo)', {
            'fields': ('metodo_pago_sugerido',)
        }),
        ('Montos (Calculados)', {
            'fields': ('total_bruto', 'porcentaje_impuesto', 'monto_impuesto', 'total_neto')
        }),
        ('Documento y Notas', {
            'fields': ('archivo_pdf', 'notas_adicionales')
        }),
        ('Timestamps', {
            'fields': ('creada_en', 'actualizada_en'),
            'classes': ('collapse',) # Para ocultar por defecto
        }),
    )

    def save_model(self, request, obj, form, change):
        # Recalcular totales antes de guardar desde el admin, si es necesario
        obj.calcular_totales()
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        # Después de guardar las líneas, recalcular totales de la factura
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()
        # Acceder a la instancia de la factura desde el formset
        if formset.instance and formset.instance.pk:
            formset.instance.calcular_totales()
            formset.instance.save()
        super().save_formset(request, form, formset, change)


