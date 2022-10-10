# Generated by Django 3.2.13 on 2022-10-10 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0106_retailergroupinvite_initiated_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retailergroupinvite',
            name='initiated_by',
            field=models.CharField(choices=[('I', 'Internal User'), ('R', 'Retailer user')], default='I', max_length=3),
        ),
    ]
