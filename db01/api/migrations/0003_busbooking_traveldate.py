# Generated by Django 2.1.7 on 2019-04-25 17:59

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20190425_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='busbooking',
            name='TravelDate',
            field=models.DateField(default=django.utils.timezone.now, null=True),
        ),
    ]