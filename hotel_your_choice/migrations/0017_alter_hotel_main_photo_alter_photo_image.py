# Generated by Django 5.0.1 on 2024-01-23 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_your_choice', '0016_alter_photo_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='main_photo',
            field=models.ImageField(upload_to='hotel_your_choice/hotel_main_photos/'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(upload_to='hotel_your_choice/hotel_photos/'),
        ),
    ]