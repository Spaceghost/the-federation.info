# Generated by Django 2.0.3 on 2018-04-22 13:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('thefederation', '0007_remote_platform_first_release'),
    ]

    operations = [
        migrations.AddField(
            model_name='stat',
            name='platform',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='thefederation.Platform'),
        ),
    ]