# Generated by Django 3.2.13 on 2022-08-30 08:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0076_auto_20220830_1020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passtypepricingwindowoption',
            name='pricing_window',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='parkpasses.passtypepricingwindow'),
        ),
    ]
