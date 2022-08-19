# Generated by Django 3.2.13 on 2022-08-19 08:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0067_auto_20220812_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discountcode',
            name='discount_code_batch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='discount_codes', to='parkpasses.discountcodebatch'),
        ),
        migrations.AlterField(
            model_name='pass',
            name='sold_via',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='parkpasses.retailergroup'),
        ),
    ]
