# Generated by Django 5.0.6 on 2024-06-23 03:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_alter_productostiendas_estado'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='producto',
            options={},
        ),
        migrations.RenameIndex(
            model_name='producto',
            new_name='Producto_codigo_f54ff3_idx',
            old_name='Productos_codigo_04cd6d_idx',
        ),
        migrations.RenameIndex(
            model_name='producto',
            new_name='Producto_nombre_4069ed_idx',
            old_name='Productos_nombre_e60d36_idx',
        ),
        migrations.AlterModelTable(
            name='producto',
            table='Producto',
        ),
    ]
