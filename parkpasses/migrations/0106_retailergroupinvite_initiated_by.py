# Generated by Django 3.2.13 on 2022-10-10 02:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0105_auto_20221007_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='retailergroupinvite',
            name='initiated_by',
            field=models.CharField(choices=[('I', 'I'), ('R', 'R')], default='I', max_length=3),
        ),
    ]
