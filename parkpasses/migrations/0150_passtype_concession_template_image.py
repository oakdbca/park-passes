# Generated by Django 3.2.16 on 2023-01-25 04:23

from django.db import migrations
import django_resized.forms
import parkpasses.components.passes.models


class Migration(migrations.Migration):

    dependencies = [
        ('parkpasses', '0149_passtype_template_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='passtype',
            name='concession_template_image',
            field=django_resized.forms.ResizedImageField(crop=None, force_format=None, help_text='Ideal dimension for image are 540px (width) x 225px (height)', keep_meta=True, null=True, quality=99, scale=None, size=[540, 225], upload_to=parkpasses.components.passes.models.pass_type_concession_template_image_path),
        ),
    ]