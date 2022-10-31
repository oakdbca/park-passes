# Generated by Django 3.2.13 on 2022-09-28 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0094_report'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='report',
            options={'ordering': ['-datetime_created', 'retailer_group']},
        ),
        migrations.AlterModelOptions(
            name='retailergroup',
            options={'ordering': ['name'], 'verbose_name': 'Retailer Group'},
        ),
        migrations.AlterField(
            model_name='report',
            name='processing_status',
            field=models.CharField(blank=True, choices=[('P', 'Paid'), ('U', 'Unpaid')], max_length=2, null=True),
        ),
    ]
