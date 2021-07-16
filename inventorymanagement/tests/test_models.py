from django.test import TestCase
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


