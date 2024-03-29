# Generated by Django 3.2.5 on 2021-07-12 12:50

from django.db import migrations, models
import django.utils.timezone
import inventorymanagement.validators


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanagement', '0035_auto_20210527_1447'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bottle',
            name='due_back',
            field=models.DateField(blank=True, default=django.utils.timezone.now, help_text='Enter a date between now and 2 weeks.', null=True, validators=[inventorymanagement.validators.validate_two_week_checkout_limit, inventorymanagement.validators.validate_due_back_not_in_past], verbose_name='Anticipated return date'),
        ),
    ]
