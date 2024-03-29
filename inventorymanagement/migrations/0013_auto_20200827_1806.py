# Generated by Django 3.1 on 2020-08-27 16:06

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanagement', '0012_auto_20200827_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bottle',
            name='due_back',
            field=models.DateField(blank=True, default=datetime.datetime(2020, 8, 30, 16, 6, 13, 697763, tzinfo=utc), help_text='Enter a date between now and 2 weeks (default 3 days).', null=True, verbose_name='Anticipated return date'),
        ),
    ]
