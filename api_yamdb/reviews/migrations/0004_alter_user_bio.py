# Generated by Django 3.2 on 2024-01-20 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_auto_20240119_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=models.CharField(blank=True, max_length=255, verbose_name='Биография'),
        ),
    ]
