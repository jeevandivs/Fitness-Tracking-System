# Generated by Django 4.2.15 on 2025-01-20 04:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0011_wishlist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='address_line2',
        ),
    ]
