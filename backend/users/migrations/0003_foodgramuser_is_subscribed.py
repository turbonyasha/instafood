# Generated by Django 3.2.3 on 2024-11-23 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_foodgramuser_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodgramuser',
            name='is_subscribed',
            field=models.BooleanField(default=False),
        ),
    ]
