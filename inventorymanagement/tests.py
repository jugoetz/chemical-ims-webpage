from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .forms import BottleCheckoutForm
from .models import Bottle

# Create your tests here.


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
                              owner_group='GBOD',
                              )

    def setUp(self) -> None:
        self.bottle = Bottle.objects.get(id='1')

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


class BottleCheckoutFormTests(TestCase):

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
                              owner_group='GBOD',
                              )

    def setUp(self) -> None:
        self.acceptable_data = {
            'id':                 '1',
            'borrower_full_name': 'Test Guy',
            'borrower_email':     'testguy@ethz.ch',
            'borrower_group':     'Bode',
            'due_back':           timezone.now().date() + timedelta(days=7),
            'status':             'out'
        }
        self.bottle = Bottle.objects.get(id='1')

    def test_accepts_no_past_due_back_date(self):
        """
        'due_back' field may not accepts user inputs that lie in the past
        :return:
        """
        past_time = timezone.now().date() - timedelta(days=1)
        wrong_data = self.acceptable_data
        wrong_data['due_back'] = past_time
        form = BottleCheckoutForm(data=wrong_data, instance=self.bottle)
        self.assertFalse(form.is_valid())

    def test_accepts_no_more_than_2_week_future_due_back_date(self):
        """
        'due_back' field may not accepts user inputs that lie more than two weeks into the future
        :return:
        """
        future_time = timezone.now().date() + timedelta(days=15)
        wrong_data = self.acceptable_data
        wrong_data['due_back'] = future_time
        form = BottleCheckoutForm(data=wrong_data, instance=self.bottle)
        self.assertFalse(form.is_valid())

    def test_accepts_1_week_future_due_back_date(self):
        """
        'due_back' field must accept user inputs that lie one week into the future
        :return:
        """
        form = BottleCheckoutForm(data=self.acceptable_data, instance=self.bottle)
        self.assertTrue(form.is_valid())

    def test_accepts_ethz_email_address(self):
        """
        'borrower_email' field must accept all email addresses containing ethz.ch after the @ sign
        (there can be chars in between)
        """

        ethz_email = 'test@somestring.ethz.ch'
        acceptable_data_email_modified = self.acceptable_data
        acceptable_data_email_modified['borrower_email'] = ethz_email
        form = BottleCheckoutForm(data=acceptable_data_email_modified, instance=self.bottle)
        self.assertTrue(form.is_valid())

    def test_does_not_accept_non_ethz_email_address(self):
        """
        'borrower_email' field may not accept email addresses not ending in ethz.ch
        (there can be chars in between this and @)
        """
        non_ethz_email = 'test@eth.ch'
        wrong_data = self.acceptable_data
        wrong_data['borrower_email'] = non_ethz_email
        form = BottleCheckoutForm(data=wrong_data, instance=self.bottle)
        self.assertFalse(form.is_valid())
