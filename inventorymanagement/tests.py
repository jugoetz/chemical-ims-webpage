from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from .models import Bottle

# Create your tests here.


class UserInputTests(TestCase):

    def test_accepts_no_past_dates(self):
        """
        Date fields may not accepts user inputs that lie in the past
        :return:
        """
        past_time = timezone.now().date() - timedelta(days=1)
