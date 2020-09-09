# Generated by Django 3.1.1 on 2020-09-08 14:20

import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import inventorymanagement.validators


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanagement', '0026_auto_20200831_1800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bottle',
            name='due_back',
            field=models.DateField(blank=True, default=datetime.datetime(2020, 9, 11, 14, 20, 58, 525437, tzinfo=utc), help_text='Enter a date between now and 2 weeks (default 3 days).', null=True, validators=[inventorymanagement.validators.validate_two_week_checkout_limit, inventorymanagement.validators.validate_due_back_not_in_past], verbose_name='Anticipated return date'),
        ),
    ]
