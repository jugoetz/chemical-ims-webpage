from django.urls import reverse
from django.db import models
from django.utils import timezone
from .validators import *
import datetime


# Create your models here.


class Bottle(models.Model):

    choices_of_loc_groups = [
        ('Bode', 'Bode'),
        ('Carreira', 'Carreira'),
        ('Chen', 'Chen'),
        ('Diederich', 'Diederich'),
        ('Ebert', 'Ebert'),
        ('Hilvert', 'Hilvert'),
        ('Kast', 'Kast'),
        ('Morandi', 'Morandi'),
        ('Thilgen', 'Thilgen'),
        ('Wennemers', 'Wennemers'),
        ('Yamakoshi', 'Yamakoshi'),
        ('Zenobi', 'Zenobi'),
        ('other', 'OTHER')
    ]
    supplier = models.CharField(max_length=200)
    price = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    owner = models.CharField(max_length=200)
    id = models.CharField(
        primary_key=True,
        max_length=15,
        verbose_name='Bottle code'
    )
    location = models.CharField(max_length=200)
    code = models.CharField(max_length=200, default='n/a')
    quantity = models.CharField(max_length=200)
    status = models.CharField(
        choices=[('out', 'checked out'), ('in', 'checked in'), ('empty', 'EMPTY')],
        default='in',
        max_length=5
    )
    checkout_date = models.DateField(
        null=True,
        blank=True,
        auto_now=True
    )
    due_back = models.DateField(
        null=True,
        blank=True,
        default=timezone.now()+datetime.timedelta(days=3),
        help_text="Enter a date between now and 2 weeks (default 3 days).",
        verbose_name='Anticipated return date',
        validators=[validate_two_week_checkout_limit, validate_due_back_not_in_past]
    )
    borrower_full_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Borrower full name'
    )
    borrower_email = models.EmailField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Please use your ETH email address'
    )
    borrower_group = models.CharField(
        max_length=9,
        choices=choices_of_loc_groups,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.id

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        return reverse('inventorymanagement:status', args=[str(self.id)])

    def is_overdue(self):
        """Checks due_date against current date. Returns True if due_date is in the past"""
        # only evaluate object if due_back is set (otherwise datetime.date - NoneType raises error)
        if type(self.due_back) is datetime.date:
            current_date = timezone.now().date()
            due_date = self.due_back
            return (current_date - due_date) > datetime.timedelta(days=1)
        else:
            return False



    is_overdue.boolean = True
    is_overdue.description = 'Overdue?'
    is_overdue.admin_order_field = ['due_back']
