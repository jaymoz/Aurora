# Generated by Django 3.1.7 on 2023-05-07 10:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_itemimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='image',
        ),
    ]
