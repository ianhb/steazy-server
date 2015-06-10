from django.contrib.auth.models import User
from django.core.management import BaseCommand

__author__ = 'Ian'

class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser("admin", "admin@810labs.me", "admin")