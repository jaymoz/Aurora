# Generated by Django 4.0.4 on 2023-02-08 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_notes',
            field=models.CharField(max_length=200),
        ),
    ]
