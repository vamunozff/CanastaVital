# Generated by Django 5.0.6 on 2024-07-21 06:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0015_metodopago_cliente_atencioncliente_tienda_promocion_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='atencioncliente',
            table='AtencionCliente',
        ),
        migrations.AlterModelTable(
            name='cliente',
            table='Cliente',
        ),
        migrations.AlterModelTable(
            name='detalleventa',
            table='DetalleVenta',
        ),
        migrations.AlterModelTable(
            name='inventario',
            table='Inventario',
        ),
        migrations.AlterModelTable(
            name='metodopago',
            table='MetodoPago',
        ),
        migrations.AlterModelTable(
            name='promocion',
            table='Promocion',
        ),
        migrations.AlterModelTable(
            name='tienda',
            table='Tienda',
        ),
        migrations.AlterModelTable(
            name='venta',
            table='Venta',
        ),
    ]
