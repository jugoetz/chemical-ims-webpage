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
    - due_back
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
    - is_overdue: True if due_date is in the past
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
        auto_now=True,
    )

    due_back = models.DateField(
        null=True,
        blank=True,
        default=timezone.now,
        help_text="Enter a date between now and 2 weeks.",
        verbose_name='Anticipated return date',
        validators=[validate_two_week_checkout_limit, validate_due_back_not_in_past],
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

    def is_overdue(self):
        """Checks due_date against current date. Returns True if due_date is in the past"""
        # only evaluate object if due_back is set (otherwise datetime.date - NoneType raises error)
        if type(self.due_back) is datetime.date:
            current_date = timezone.now().date()
            due_date = self.due_back
            return (current_date - due_date) > datetime.timedelta(days=1)
        else:
            return False

    def is_checked_out(self):
        """Checks if bottle is currently checked out"""
        return self.status == 'out'

    is_overdue.boolean = True
    is_overdue.description = 'Overdue?'
    is_overdue.admin_order_field = ['due_back']
    is_checked_out.boolean = True
    is_checked_out.description = 'Checked out?'
