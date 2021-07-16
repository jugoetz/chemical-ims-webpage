from django.test import TestCase
import datetime
from ..models import Bottle, ChangeListEntry


class BottleModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        Bottle.objects.create(id='1',
                              supplier='Sial',
                              price=50.50,
                              description='acetone',
                              owner='Django User',
                              location='F312-SHELF1',
                              code='GBODDU',
                              quantity='1000 mL',
                              status='in',
                              # owner_group='GBOD',
                              )

    def setUp(self) -> None:
        self.bottle = Bottle.objects.get(id='1')

    def test_bottle_is_checked_out_returns_false_for_empty_bottle(self):
        """
        Bottle.is_checked_out() must return False for an empty bottle
        """
        self.bottle.status = 'empty'
        self.assertFalse(self.bottle.is_checked_out())

    def test_bottle_is_checked_out_returns_false_for_checked_in_bottle(self):
        """
        Bottle.is_checked_out() must return False for a checked in bottle
        """
        self.assertFalse(self.bottle.is_checked_out())

    def test_bottle_is_checked_out_returns_true_for_checked_out_bottle(self):
        """
        Bottle.is_checked_out() must return True for a checked out bottle
        """
        self.bottle.status = 'out'
        self.assertTrue(self.bottle.is_checked_out())

    def test_bottle_owner_group_calculated_in_queryset(self):
        """Filtering a queryset by the owner_group must return the correct number (1) of hits."""
        self.assertEqual(len(Bottle.objects.filter(owner_group='GBOD')), 1)


class ChangeListEntryTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        ChangeListEntry.objects.create(description='Removed a bug')

    def test_description_max_length(self):
        changelistentry = ChangeListEntry.objects.get(entry_id=1)
        max_length = changelistentry._meta.get_field('description').max_length
        self.assertEqual(max_length, 200)

    def test_date_field_default_is_current_date(self):
        changelistentry = ChangeListEntry.objects.get(entry_id=1)
        date = changelistentry.date
        self.assertEqual(date, datetime.date.today())

    def test_is_recent_is_true_for_recent_change(self):
        changelistentry = ChangeListEntry.objects.get(entry_id=1)
        changelistentry.date = datetime.date.today() - datetime.timedelta(days=30)
        self.assertTrue(changelistentry.is_recent())

    def test_is_recent_is_false_for_old_change(self):
        changelistentry = ChangeListEntry.objects.get(entry_id=1)
        changelistentry.date = datetime.date.today() - datetime.timedelta(days=31)
        self.assertFalse(changelistentry.is_recent())
