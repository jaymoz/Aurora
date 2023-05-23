# Generated by Django 3.1.7 on 2023-05-19 02:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_auto_20230519_0447'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brand',
            options={},
        ),
        migrations.AlterModelTable(
            name='address',
            table='Address',
        ),
        migrations.AlterModelTable(
            name='brand',
            table='Brand',
        ),
        migrations.AlterModelTable(
            name='category',
            table='Category',
        ),
        migrations.AlterModelTable(
            name='contact',
            table='Contact',
        ),
        migrations.AlterModelTable(
            name='item',
            table='Item',
        ),
        migrations.AlterModelTable(
            name='itemcolor',
            table='ItemColor',
        ),
        migrations.AlterModelTable(
            name='itemimage',
            table='ItemImage',
        ),
        migrations.AlterModelTable(
            name='order',
            table='Order',
        ),
        migrations.AlterModelTable(
            name='orderitem',
            table='OrderItem',
        ),
        migrations.AlterModelTable(
            name='review',
            table='Review',
        ),
        migrations.AlterModelTable(
            name='size',
            table='Size',
        ),
        migrations.AlterModelTable(
            name='wishlist',
            table='Wishlist',
        ),
    ]