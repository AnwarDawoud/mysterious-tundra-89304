# Generated by Django 3.2.23 on 2024-01-26 01:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_your_choice', '0002_remove_hotel_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='hotel',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='hotel_your_choice.hotel'),
        ),
    ]