# Generated by Django 5.0.6 on 2024-12-12 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_gallery'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gallery',
            options={'verbose_name_plural': 'Galleries'},
        ),
        migrations.AlterField(
            model_name='gallery',
            name='caption',
            field=models.CharField(blank=True, default='', max_length=60, null=True),
        ),
    ]
