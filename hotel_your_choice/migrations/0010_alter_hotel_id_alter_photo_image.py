# Generated by Django 5.0.1 on 2024-01-15 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_your_choice', '0009_comment_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(upload_to='hotel_photos/'),
        ),
    ]
