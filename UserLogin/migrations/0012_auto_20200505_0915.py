# Generated by Django 3.0.4 on 2020-05-05 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserLogin', '0011_cart_orderplaced'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='orderPlaced',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
