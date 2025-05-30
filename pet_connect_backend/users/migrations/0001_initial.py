# Generated by Django 5.2.1 on 2025-05-08 19:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('address', models.TextField(blank=True)),
                ('has_children', models.BooleanField(default=False)),
                ('has_other_dogs', models.BooleanField(default=False)),
                ('has_other_cats', models.BooleanField(default=False)),
                ('preferred_animal_type', models.CharField(blank=True, max_length=50)),
                ('preferred_age_min', models.IntegerField(default=0)),
                ('preferred_age_max', models.IntegerField(default=240)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
