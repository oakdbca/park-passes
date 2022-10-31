# Generated by Django 3.2.13 on 2022-09-30 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0099_auto_20220929_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='concessionusage',
            name='concession_card_number',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='retailergroup',
            name='address_line_2',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='retailergroup',
            name='state',
            field=models.CharField(choices=[('NSW', 'Western Australia'), ('VIC', 'Victoria'), ('QLD', 'Queensland'), ('WA', 'Western Australia'), ('SA', 'South Australia'), ('TAS', 'Tasmania'), ('ACT', 'Australian Capital Territory'), ('NT', 'Western Australia')], default='WA', max_length=3, null=True),
        ),
    ]
