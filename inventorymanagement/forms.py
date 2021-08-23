from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, HiddenInput
from .models import Bottle


class BottleCheckoutForm(ModelForm):
    """
    This is a form derived from the models.Bottle that records data to check out a bottle
    """

    class Meta:
        model = Bottle
        fields = ['id', 'borrower_full_name', 'borrower_email', 'borrower_group', 'checkout_date', 'status']
        widgets = {'status': HiddenInput, 'checkout_date': HiddenInput}

    # This modification to __init__ sets the fields required in the form, but not in the model
    def __init__(self, *args, **kwargs):
        super(BottleCheckoutForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True

    def clean_id(self):
        """
        Validate that the user-entered bottle code exists in the database
        """
        id = ''.join(self.cleaned_data['id'].split('-'))
        if not Bottle.objects.filter(id=id).exists():
            raise ValidationError(
                message='This bottle is not listed in the database. '
                        'Please check if you used the right bottle code and try again.',
                code='not_in_db'
            )
        return id


class BottleCheckinForm(ModelForm):
    """
    This is a form derived from the models.Bottle that records data to return a bottle
    """
    class Meta:
        model = Bottle
        fields = ['id', 'status', 'checkout_date']
        widgets = {'status': HiddenInput, 'checkout_date': HiddenInput}
    return_status = forms.ChoiceField(
        choices=[('EMPTY', 'empty'), ('OK', 'Returned to assigned shelf')],
        widget=forms.RadioSelect
    )
    status = 'in'

    def clean_id(self):
        """
        Validate that the user-entered bottle code exists in the database
        """
        id = ''.join(self.cleaned_data['id'].split('-'))
        try:
            Bottle.objects.filter(id=id)[0]
        except IndexError:
            raise ValidationError(
                message='This bottle is not listed in the database. '
                        'Please check if you used the right bottle code and try again.',
                code='not_in_db'
            )
        return id


def return_list_with_ascending_x_values(start, interval, steps):
    """
    Takes any integer <start> and returns a list starting with this integer,
    ascending by <interval> for every element, until the number of elements is equal to <steps>.
    Raises TypeError if anything but int or float is given for <start> or <interval>,
    or anything but int for <steps>
    """
    if type(start) not in (int, float) or type(interval) not in (int, float) or type(steps) is not int:
        raise TypeError
    new_list = [start]
    for i in range(1, steps+1):
        new_list.append(start + i * interval)
    return new_list


class CheckStatus(forms.Form):
    """
    This is a form to ask user which bottle to check.
    The purpose is to later redirect the user to the detail page of this bottle.
    """
    bottle_code = forms.CharField(
        max_length=10,
        strip=True,
        required=True
    )

    def clean_bottle_code(self):
        """
        Validate that the user-entered bottle code exists in the database
        """
        bottle_code = ''.join(self.cleaned_data['bottle_code'].split('-'))
        try:
            Bottle.objects.filter(id=bottle_code)[0]
        except IndexError:
            raise ValidationError(
                message='This bottle is not listed in the database. '
                        'Please check if you used the right bottle code and try again.',
                code='not_in_db'
            )
        return bottle_code


class CheckUserChemicals(forms.Form):
    """
    This is a form to ask user which bottle to check.
    The purpose is to later redirect the user to the detail page of this bottle.
    """
    class Meta:
        model = Bottle
        fields = ['code', 'status']

    user_code = forms.CharField(
        max_length=6,
        strip=True,
        required=True
    )
    only_checked_out = forms.BooleanField(
        required=False,
        label='Display only checked-out bottles?'
    )

    def clean_user_code(self):
        """
        Validate that the user-entered user code exists in the database
        """
        user_code = self.cleaned_data['user_code']
        user_code = user_code.upper()
        try:
            Bottle.objects.filter(code=user_code)[0]
        except IndexError:
            raise ValidationError(
                message='This user is not listed in the database. '
                        'If you wish to add your group chemicals, '
                        'consult the About page to learn more.',
                code='not_in_db'
            )
        return user_code
