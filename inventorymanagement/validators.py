from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta


def validate_two_week_checkout_limit(due_back):
    if due_back > timezone.now().date() + timedelta(weeks=2):
        raise ValidationError(
            f'{due_back} is more than two weeks into the future'
        )


def validate_due_back_not_in_past(due_back):
    if due_back < timezone.now().date():
        raise ValidationError(
            f'{due_back} is in the past'
        )


def validate_ethz_email_address(borrower_email: str):
    if not borrower_email.endswith('ethz.ch'):
        raise ValidationError(
            f'{borrower_email} is not an ETHZ email address'
        )


def validate_bottle_exists_in_db(bottle_code):
    pass
    # check if bottle_code is in db
    # TODO this could be implemented to catch "DoesNotExist" exceptions.
    #  I am currently not sure what this page will look like for DEBUG = False,
    #  so maybe implementing this validator is unnecessary
