# Generated by Django 3.1.1 on 2021-05-27 12:47

import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import inventorymanagement.validators


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanagement', '0034_auto_20210527_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='bottle',
            name='owner_group',
            field=models.CharField(blank=True, editable=False, max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='bottle',
            name='due_back',
            field=models.DateField(blank=True, default=datetime.datetime(2021, 5, 30, 12, 47, 51, 698441, tzinfo=utc), help_text='Enter a date between now and 2 weeks (default 3 days).', null=True, validators=[inventorymanagement.validators.validate_two_week_checkout_limit, inventorymanagement.validators.validate_due_back_not_in_past], verbose_name='Anticipated return date'),
        ),
    ]
