"""
Management command to remove the old hardcoded demo partner account
that was seeded in earlier versions of FloraCycle setup.sh.

Usage:
    python manage.py remove_demo_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

DEMO_EMAILS = ['temple@floracycle.in']

class Command(BaseCommand):
    help = 'Removes hardcoded demo partner accounts from older setup versions.'

    def handle(self, *args, **options):
        deleted = 0
        for email in DEMO_EMAILS:
            count, _ = User.objects.filter(email=email).delete()
            if count:
                self.stdout.write(self.style.SUCCESS(f'  Removed demo user: {email}'))
                deleted += count
        if deleted == 0:
            self.stdout.write('  No demo users found — nothing to remove.')
        else:
            self.stdout.write(self.style.SUCCESS(f'  Done. {deleted} demo user(s) removed.'))
