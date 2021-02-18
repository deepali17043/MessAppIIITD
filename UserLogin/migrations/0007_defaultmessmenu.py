# Generated by Django 3.0.5 on 2021-02-18 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserLogin', '0006_delete_defaultmessmenu'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultMessMenu',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('meal', models.CharField(choices=[('Breakfast', 'Breakfast'), ('Lunch', 'Lunch'), ('Snacks', 'Snacks'), ('Dinner', 'Dinner')], max_length=10)),
                ('day', models.TextField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], max_length=15)),
                ('items', models.TextField(max_length=400)),
            ],
        ),
    ]
