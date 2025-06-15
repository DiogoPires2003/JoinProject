from django.test import TestCase
from sprint2.models import Factura, LineaFactura
from decimal import Decimal

class FacturaIntegrationTestCase(TestCase):
    def test_eliminar_linea_y_actualizar_totales(self):
        # Crear una factura
        factura = Factura.objects.create(estado='BORRADOR', porcentaje_impuesto=Decimal('21.00'))

        # Agregar líneas de factura
        linea1 = LineaFactura.objects.create(factura=factura, cantidad=2, precio_unitario=Decimal('50.00'))
        linea2 = LineaFactura.objects.create(factura=factura, cantidad=1, precio_unitario=Decimal('100.00'))

        # Calcular totales
        factura.calcular_totales()
        self.assertEqual(factura.total_bruto, Decimal('200.00'))

        # Eliminar una línea y recalcular
        linea1.delete()
        factura.calcular_totales()
        self.assertEqual(factura.total_bruto, Decimal('100.00'))
        self.assertEqual(factura.monto_impuesto, Decimal('21.00'))
        self.assertEqual(factura.total_neto, Decimal('121.00'))

    def test_creacion_factura_con_diferentes_impuestos(self):
        # Crear una factura con un impuesto del 10%
        factura = Factura.objects.create(estado='BORRADOR', porcentaje_impuesto=Decimal('10.00'))

        # Agregar líneas de factura
        LineaFactura.objects.create(factura=factura, cantidad=4, precio_unitario=Decimal('25.00'))

        # Calcular totales
        factura.calcular_totales()
        self.assertEqual(factura.total_bruto, Decimal('100.00'))
        self.assertEqual(factura.monto_impuesto, Decimal('10.00'))
        self.assertEqual(factura.total_neto, Decimal('110.00'))  

        # Cambiar el impuesto al 20% y recalcular
        factura.porcentaje_impuesto = Decimal('20.00')
        factura.calcular_totales()
        self.assertEqual(factura.monto_impuesto, Decimal('20.00'))
        self.assertEqual(factura.total_neto, Decimal('120.00'))