import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create or update the FloraCycle superuser"

    def handle(self, *args, **kwargs):

        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not email or not password:
            self.stdout.write(
                self.style.ERROR(
                    "DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD "
                    "must be configured."
                )
            )
            return

        email = email.strip().lower()

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name": "FloraCycle Admin",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        if not created:
            user.full_name = "FloraCycle Admin"
            user.role = "admin"
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True

        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser {email} created successfully."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser {email} updated successfully."
                )
            )