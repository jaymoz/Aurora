# Generated by Django 4.0.4 on 2023-02-08 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_order_order_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_notes',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
