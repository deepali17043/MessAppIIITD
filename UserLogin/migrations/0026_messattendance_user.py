# Generated by Django 3.1.2 on 2020-12-17 19:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('UserLogin', '0025_remove_messattendance_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='messattendance',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='mess_customer', to='UserLogin.messuser'),
            preserve_default=False,
        ),
    ]
