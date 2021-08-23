from django.urls import reverse
from django.db import models
from django.utils import timezone
from .validators import *
import datetime


class Bottle(models.Model):
    """
    A model for chemical bottles.
    id: A bottle has a unique code (or id), usually printed on the bottles in XXX-XXX format. On the database level this
    formatting is disregarded and the ids are saved as strings of numbers (i.e. XXXXXX). Less digits are ok. More than
    6 digits may occur at some point in the future, so we allow up to 9.

    Properties changed by the system:
    - status
    - checkout_date
    - borrower_full_name
    - borrower_email
    - borrower_group

    Variable properties:
    - owner
    - location
    - code (?)

    Fixed properties (no change after bottle code issued):
    - supplier
    - price
    - description
    - quantity

    Calculated properties:
    - borrowed_two_weeks: True if checkout_date is more than 2 weeks in the past
    - is_checked_out: True if status == 'out'
    - owner_group
    """


    # primary key

    id = models.CharField(
        primary_key=True,
        max_length=9,
        verbose_name='Bottle code',
    )

    # fixed properties

    supplier = models.CharField(
        max_length=100,
        editable=False,
    )

    price = models.CharField(
        max_length=20,
        editable=False,
    )

    description = models.CharField(
        max_length=200,
        editable=False,
    )

    quantity = models.CharField(
        max_length=20,
        editable=False,
    )

    # variable properties

    owner = models.CharField(
        max_length=100,
    )

    location = models.CharField(
        max_length=50,
    )

    code = models.CharField(
        max_length=200,
        default='n/a',
        verbose_name='owner code'
    )

    status = models.CharField(
        choices=[('out', 'checked out'), ('in', 'checked in'), ('empty', 'EMPTY')],
        default='in',
        max_length=5,
    )

    checkout_date = models.DateField(
        null=True,
        blank=True,
    )

    borrower_full_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Borrower full name',
    )

    borrower_email = models.EmailField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Please use your ETH email address',
        validators=[validate_ethz_email_address],
    )

    borrower_group = models.CharField(
        choices=[
        ('Bode', 'Bode'),
        ('Carreira', 'Carreira'),
        ('Chen', 'Chen'),
        ('Ebert', 'Ebert'),
        ('Hilvert', 'Hilvert'),
        ('Kast', 'Kast'),
        ('Lang', 'Lang'),
        ('Lehrlabor', 'Lehrlabor'),
        ('Morandi', 'Morandi'),
        ('Thilgen', 'Thilgen'),
        ('Wennemers', 'Wennemers'),
        ('Yamakoshi', 'Yamakoshi'),
        ('Zenobi', 'Zenobi'),
        ('other', 'OTHER')
    ],
        max_length=20,
        null=True,
        blank=True,
    )

    owner_group = models.CharField(
        max_length=4,
    )
    """The owner group is given by the first 4 letters of the (owner) code"""

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        """
        We modify the save method to calculate the owner_group field at save time.
        (This way, it can be used in querysets and thus for filtering in the Django admin).
        """
        self.owner_group = self.code[:4]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns the url to access a particular instance of the model."""
        return reverse('inventorymanagement:status', args=[str(self.id)])

    def borrowed_two_weeks(self):
        """Returns True if checkout_date is more than 2 weeks in the past"""
        # only evaluate object if checkout_date is set (otherwise datetime.date - NoneType raises error)
        if type(self.checkout_date) is datetime.date:
            current_date = timezone.now().date()
            return (current_date - self.checkout_date) > datetime.timedelta(weeks=2)
        else:
            return False

    def is_checked_out(self):
        """Checks if bottle is currently checked out"""
        return self.status == 'out'

    borrowed_two_weeks.boolean = True
    borrowed_two_weeks.description = '2 weeks exceeded?'
    borrowed_two_weeks.admin_order_field = ['checkout_date']
    is_checked_out.boolean = True
    is_checked_out.description = 'Checked out?'


class ChangeListEntry(models.Model):
    """
    A model for entries in the changelist.
    A changelist entry consists of
        - id (auto-generated)
        - date
        - description
    All fields are required.
    """
    class Meta:
        verbose_name = 'changelist entry'
        verbose_name_plural = 'changelist entries'  # this fixes the plural error on the admin page

    entry_id = models.AutoField(
        primary_key=True
    )

    date = models.DateField(
        default=datetime.date.today
    )

    description = models.CharField(
        max_length=200,
        help_text='Enter a short description of the recorded change (max. 200 characters)'
    )

    def is_recent(self):
        """Recent changes are at most 30 days old"""
        return self.date >= datetime.date.today() - datetime.timedelta(days=30)

    is_recent.boolean = True
