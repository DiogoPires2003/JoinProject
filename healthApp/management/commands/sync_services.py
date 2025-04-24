# yourapp/management/commands/sync_services.py
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from decouple import config # Assuming you use python-decouple

# Make sure to import your Service model correctly
from healthApp.models import Service # <--- ADJUST THIS IMPORT

class Command(BaseCommand):
    help = 'Fetches services from the external API and syncs them with the local Service model'

    def handle(self, *args, **options):
        self.stdout.write("Starting service synchronization...")

        token_url = "https://example-mutua.onrender.com/token"
        services_url = "https://example-mutua.onrender.com/servicios-clinica/"
        payload = {
            "username": config("API_USERNAME"),
            "password": config("API_PASSWORD"),
        }

        try:
            # Get Token
            token_response = requests.post(token_url, data=payload, timeout=15)
            token_response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            access_token = token_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {access_token}"}

            # Get Services
            services_response = requests.get(services_url, headers=headers, timeout=15)
            services_response.raise_for_status()
            api_services = services_response.json()

            # Sync with local DB
            synced_count = 0
            created_count = 0
            api_service_ids = set()

            for api_service in api_services:
                service_id = api_service.get("id")
                service_name = api_service.get("nombre")
                service_desc = api_service.get("descripcion", "") # Provide default

                if not service_id or not service_name:
                    self.stdout.write(self.style.WARNING(f"Skipping service with missing ID or name: {api_service}"))
                    continue

                api_service_ids.add(service_id)

                # Use update_or_create for efficiency
                obj, created = Service.objects.update_or_create(
                    id=service_id, # Match based on the API's ID
                    defaults={
                        'name': service_name,
                        'description': service_desc
                        # Add other fields from API if needed in your model
                    }
                )

                if created:
                    created_count += 1
                else:
                    synced_count += 1
                # self.stdout.write(f"Synced/Created: ID={service_id}, Name={service_name}")


            # Optional: Delete local services that are no longer in the API
            # deleted_count, _ = Service.objects.exclude(id__in=api_service_ids).delete()

            self.stdout.write(self.style.SUCCESS(
                f"Synchronization complete. "
                f"Created: {created_count}, Updated: {synced_count}."
                # f" Deleted: {deleted_count}." # Uncomment if using delete step
            ))

        except requests.exceptions.RequestException as e:
            self.stderr.write(self.style.ERROR(f"API request failed: {e}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))