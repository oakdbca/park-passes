# Generated by Django 3.2.13 on 2022-09-29 03:25

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0097_auto_20220928_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='invoice',
            field=models.FileField(blank=True, max_length=500, null=True, storage=django.core.files.storage.FileSystemStorage(base_url='/protected_media', location='/home/oak/dev/parkpasses/park-passes/protected_media'), upload_to=''),
        ),
        migrations.AlterField(
            model_name='report',
            name='report',
            field=models.FileField(blank=True, max_length=500, null=True, storage=django.core.files.storage.FileSystemStorage(base_url='/protected_media', location='/home/oak/dev/parkpasses/park-passes/protected_media'), upload_to=''),
        ),
    ]
