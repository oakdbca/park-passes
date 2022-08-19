# Generated by Django 3.2.13 on 2022-07-12 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0040_voucher_uuid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voucher',
            name='uuid',
        ),
        migrations.AddField(
            model_name='cart',
            name='uuid',
            field=models.CharField(blank=True, max_length=36, null=True),
        ),
    ]
