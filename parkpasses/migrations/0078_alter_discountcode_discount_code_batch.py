# Generated by Django 3.2.13 on 2022-08-31 06:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0077_alter_passtypepricingwindowoption_pricing_window'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discountcode',
            name='discount_code_batch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discount_codes', to='parkpasses.discountcodebatch'),
        ),
    ]