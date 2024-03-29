# Generated by Django 3.1 on 2020-08-27 10:10

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanagement', '0011_auto_20200827_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bottle',
            name='due_back',
            field=models.DateField(blank=True, default=datetime.datetime(2020, 8, 30, 10, 10, 32, 522632, tzinfo=utc), help_text='Enter a date between now and 2 weeks (default 3 days).', null=True, verbose_name='Anticipated return date'),
        ),
        migrations.AlterField(
            model_name='bottle',
            name='status',
            field=models.CharField(choices=[('out', 'checked out'), ('in', 'checked in'), ('empty', 'EMPTY')], default='in', max_length=5),
        ),
    ]
