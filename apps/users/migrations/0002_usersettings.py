# Generated migration for UserSettings model

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('org',   models.CharField(default='FloraCycle',           max_length=200)),
                ('email', models.EmailField(default='hello@floracycle.in', max_length=254)),
                ('phone', models.CharField(default='+91 88888 88888',      max_length=30)),
                ('city',  models.CharField(default='Pune, Maharashtra',    max_length=120)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='settings',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'User Settings',
                'db_table': 'fc_user_settings',
            },
        ),
    ]
