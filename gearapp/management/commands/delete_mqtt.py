from django.core.management.base import BaseCommand
from datetime import date, timedelta
from gearapp.models import gear_value

class Command(BaseCommand):
    help = 'Deletes all gear_value records with date before today'

    def handle(self, *args, **kwargs):
        today = date.today()
        deleted_count, _ = gear_value.objects.filter(date__lt=today).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} gear_value records before {today}."))
