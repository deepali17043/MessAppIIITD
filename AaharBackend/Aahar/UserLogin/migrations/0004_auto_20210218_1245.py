# Generated by Django 3.0.5 on 2021-02-18 12:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserLogin', '0003_auto_20210216_1144'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultMessMenu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meal', models.CharField(choices=[('Breakfast', 'Breakfast'), ('Lunch', 'Lunch'), ('Snacks', 'Snacks'), ('Dinner', 'Dinner')], max_length=10)),
                ('day', models.TextField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], max_length=15)),
                ('items', models.TextField(max_length=400)),
            ],
        ),
        migrations.AlterField(
            model_name='feedback',
            name='date',
            field=models.DateField(default=datetime.date(2021, 2, 18)),
        ),
        migrations.AlterField(
            model_name='mealdeadline',
            name='date',
            field=models.DateField(default=datetime.date(2021, 2, 18)),
        ),
        migrations.AlterField(
            model_name='messattendance',
            name='date',
            field=models.DateField(default=datetime.date(2021, 2, 18)),
        ),
        migrations.AlterField(
            model_name='messmenu',
            name='items',
            field=models.TextField(max_length=400),
        ),
    ]