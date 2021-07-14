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
