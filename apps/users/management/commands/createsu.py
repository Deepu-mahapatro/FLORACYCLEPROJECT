import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):

    help = "Create superuser automatically"

    def handle(self, *args, **kwargs):

        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        user, created = User.objects.get_or_create(
            email=email
        )

        user.set_password(password)

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        user.save()

        print("Superuser updated successfully")