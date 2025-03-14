# Generated by Django 5.0.6 on 2024-12-27 00:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_products_color_products_description_products_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='user',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='shipping',
            field=models.CharField(choices=[('standard', 'Standard Delivery - $1 (3-5 business days)'), ('express', 'Express Delivery - $3 (1-2 business days)'), ('same_day', 'Same-Day Delivery - $5 (Order by 12 PM)'), ('pickup', 'In-Store Pickup - Free')], default='standard', max_length=100),
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='cartitem',
            name='cart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='shop.cart'),
        ),
    ]
