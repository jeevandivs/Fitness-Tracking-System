# Generated by Django 4.2.15 on 2025-01-13 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0005_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category_id',
            field=models.IntegerField(default=1),
        ),
    ]
