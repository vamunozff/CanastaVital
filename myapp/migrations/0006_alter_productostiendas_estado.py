# Generated by Django 5.0.6 on 2024-06-23 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_alter_productostiendas_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productostiendas',
            name='estado',
            field=models.CharField(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')], max_length=50),
        ),
    ]
