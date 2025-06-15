from django.test import TestCase, Client
from bs4 import BeautifulSoup


class LandingPageFunctionalTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_landing_page_elementos(self):
        """Test básico de la landing page"""
        response = self.client.get('/')

        # Verificar status HTTP
        self.assertEqual(response.status_code, 200)

        # Verificar contenido básico que existe en la página
        self.assertContains(response, "Bienvenido a Better Health")
        self.assertContains(response, "Nuestros Servicios")
        self.assertContains(response, "Consulta Médica")

        # Verificar templates usados
        self.assertTemplateUsed(response, 'home/home.html')
        self.assertTemplateUsed(response, 'base/navbar.html')
        self.assertTemplateUsed(response, 'base/footer.html')

    def test_landing_page_con_beautifulsoup(self):
        """Test más avanzado usando BeautifulSoup para verificar HTML"""
        response = self.client.get('/')
        soup = BeautifulSoup(response.content, 'html.parser')

        # Verificar el título de la página
        title = soup.find('title')
        self.assertIn("Better Health", title.text if title else "")

        # Verificar el botón de acceso
        acceder_link = soup.find('a', string='Acceder/Registrar-se')
        self.assertIsNotNone(acceder_link, "No se encontró el enlace 'Acceder/Registrar-se'")

        # Verificar elementos de navegación principales
        nav_items = ['Home', 'Nosotros', 'Centros', 'Servicios de salud', 'Contacto']
        for item in nav_items:
            nav_link = soup.find('a', string=item)
            self.assertIsNotNone(nav_link, f"No se encontró el enlace '{item}' en la navegación")

        # Verificar sección de servicios
        servicios_header = soup.find('h2', string='Nuestros Servicios')
        self.assertIsNotNone(servicios_header, "No se encontró el encabezado de servicios")