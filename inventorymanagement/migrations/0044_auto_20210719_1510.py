# Generated by Django 3.2.5 on 2021-07-19 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventorymanagement', '0043_alter_changelistentry_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='changelistentry',
            options={'verbose_name': 'changelist entry', 'verbose_name_plural': 'changelist entries'},
        ),
        migrations.RemoveField(
            model_name='bottle',
            name='due_back',
        ),
        migrations.AlterField(
            model_name='bottle',
            name='checkout_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
