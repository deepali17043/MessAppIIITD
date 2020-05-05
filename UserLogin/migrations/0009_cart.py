# Generated by Django 3.0.4 on 2020-05-01 20:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('UserLogin', '0008_menuitems_hidden'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.PositiveSmallIntegerField(default=1)),
                ('status', models.CharField(choices=[('Added to Cart', 'Added to Cart'), ('Order Placed', 'Order Placed'), ('Being Prepared', 'Being Prepared'), ('Prepared', 'Prepared'), ('Collected', 'Collected')], default='Added to Cart', max_length=50)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to='UserLogin.MenuItems')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item', to='UserLogin.MenuItems')),
            ],
        ),
    ]
