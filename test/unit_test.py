from django.test import TestCase
from sprint2.models import Factura, LineaFactura
from decimal import Decimal

class FacturaTestCase(TestCase):
    def test_calcular_totales(self):
        # Crear una factura en estado "BORRADOR"
        factura = Factura.objects.create(estado='BORRADOR', porcentaje_impuesto=Decimal('21.00'))

        # Crear líneas de factura asociadas
        LineaFactura.objects.create(factura=factura, cantidad=2, precio_unitario=Decimal('50.00'))
        LineaFactura.objects.create(factura=factura, cantidad=1, precio_unitario=Decimal('100.00'))

        # Calcular totales
        factura.calcular_totales()

        # Verificar los resultados esperados
        self.assertEqual(factura.total_bruto, Decimal('200.00'))
        self.assertEqual(factura.monto_impuesto, Decimal('42.00'))
        self.assertEqual(factura.total_neto, Decimal('242.00'))

    def test_estado_inicial_factura(self):
        factura = Factura.objects.create(estado='BORRADOR', porcentaje_impuesto=Decimal('21.00'))
        self.assertEqual(factura.estado, 'BORRADOR')

    def test_calcular_totales_sin_lineas(self):
        factura = Factura.objects.create(estado='BORRADOR', porcentaje_impuesto=Decimal('21.00'))
        factura.calcular_totales()
        self.assertEqual(factura.total_bruto, Decimal('0.00'))
        self.assertEqual(factura.monto_impuesto, Decimal('0.00'))
        self.assertEqual(factura.total_neto, Decimal('0.00'))

    def test_calcular_totales_diferentes_impuestos(self):
        factura = Factura.objects.create(estado='BORRADOR', porcentaje_impuesto=Decimal('10.00'))
        LineaFactura.objects.create(factura=factura, cantidad=3, precio_unitario=Decimal('30.00'))
        factura.calcular_totales()
        self.assertEqual(factura.total_bruto, Decimal('90.00'))
        self.assertEqual(factura.monto_impuesto, Decimal('9.00'))
        self.assertEqual(factura.total_neto, Decimal('99.00'))

    def test_actualizar_totales_despues_de_eliminar_linea(self):
        factura = Factura.objects.create(estado='BORRADOR', porcentaje_impuesto=Decimal('21.00'))
        linea1 = LineaFactura.objects.create(factura=factura, cantidad=2, precio_unitario=Decimal('50.00'))
        linea2 = LineaFactura.objects.create(factura=factura, cantidad=1, precio_unitario=Decimal('100.00'))
        factura.calcular_totales()
        self.assertEqual(factura.total_bruto, Decimal('200.00'))

        # Eliminar una línea y recalcular
        linea1.delete()
        factura.calcular_totales()
        self.assertEqual(factura.total_bruto, Decimal('100.00'))
        self.assertEqual(factura.monto_impuesto, Decimal('21.00'))
        self.assertEqual(factura.total_neto, Decimal('121.00'))