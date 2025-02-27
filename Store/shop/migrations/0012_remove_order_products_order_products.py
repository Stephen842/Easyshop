# Generated by Django 5.0.6 on 2025-02-25 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_remove_order_address_mycustomer_country_order_city_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='products',
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(to='shop.products'),
        ),
    ]
