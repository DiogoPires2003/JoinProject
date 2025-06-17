from django.test import TestCase, Client

class SmokeTest(TestCase):
    def test_homepage_loads(self):
        client = Client()
        response = client.get('/')
        self.assertIn(response.status_code, [200, 302])