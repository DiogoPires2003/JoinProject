import subprocess
from django.test import SimpleTestCase


class PlaywrightE2ETest(SimpleTestCase):
    def test_run_playwright_tests(self):
        """Ejecuta los tests de Playwright como parte de manage.py test"""
        print("\nEjecutando tests de Playwright...")

        try:
            result = subprocess.run(
                ['npx', 'playwright', 'test'],
                cwd='test/e2e',
                check=True
            )
        except subprocess.CalledProcessError as e:
            self.fail(f"Playwright tests fallaron con código {e.returncode}")
