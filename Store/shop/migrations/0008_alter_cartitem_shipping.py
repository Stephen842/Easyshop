# Generated by Django 5.0.6 on 2024-12-28 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_order_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='shipping',
            field=models.CharField(choices=[('standard', 'Standard Delivery - $1 (3-5 business days)')], default='standard', max_length=100),
        ),
    ]