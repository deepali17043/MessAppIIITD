# Generated by Django 3.1.2 on 2020-12-03 17:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserLogin', '0019_auto_20201201_1146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='messattendance',
            name='editable',
        ),
        migrations.AlterField(
            model_name='messattendance',
            name='date',
            field=models.DateField(default=datetime.date(2020, 12, 3)),
        ),
    ]
