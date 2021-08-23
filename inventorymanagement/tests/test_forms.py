from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from ..forms import BottleCheckoutForm
from ..models import Bottle


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
                              )

    def setUp(self) -> None:
        self.acceptable_data = {
            'id':                 '1',
            'borrower_full_name': 'Test Guy',
            'borrower_email':     'testguy@ethz.ch',
            'borrower_group':     'Bode',
            'checkout_date':       timezone.now().date(),
            'status':             'out'
        }
        self.bottle = Bottle.objects.get(id='1')

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
