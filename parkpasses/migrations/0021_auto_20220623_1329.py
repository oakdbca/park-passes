# Generated by Django 3.2.13 on 2022-06-23 05:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0020_lga'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lga',
            options={'verbose_name': 'LGA', 'verbose_name_plural': 'LGAs'},
        ),
        migrations.AlterField(
            model_name='lga',
            name='park',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='parkpasses.park'),
        ),
    ]