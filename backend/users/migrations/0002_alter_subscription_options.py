# Generated by Django 3.2.3 on 2024-11-26 06:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ('subscribed_at',), 'verbose_name': 'подписка', 'verbose_name_plural': 'Подписки'},
        ),
    ]
