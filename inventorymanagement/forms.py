from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.forms import ModelForm, HiddenInput
from .models import Bottle
import datetime


class BottleCheckoutForm(ModelForm):
    """
    This is a form derived from the models.Bottle that records data to check out a bottle
    """
    class Meta:
        model = Bottle
        fields = ['id', 'borrower_full_name', 'borrower_email', 'borrower_group', 'due_back', 'status']
        widgets = {'status': HiddenInput, 'due_back': forms.SelectDateWidget}

    # This modification to __init__ sets the fields required in the form, but not in the model
    def __init__(self, *args, **kwargs):
        super(BottleCheckoutForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True
    # TODO find out how to send email or delete the outcommented statement below
    # send_confirmation = forms.BooleanField(label='Send confirmation e-mail?', required=False)

    def send_confirmation_email(self):

        subject = 'Confirmation: Inventory checkout'
        message = f'Dear {self.cleaned_data["borrower_full_name"]},\n' \
                  f'you checked out bottle {self.cleaned_data["id"]} from Bode group.' \
                  f'You specified the anticipated return date as {self.cleaned_data["due_back"]}.' \
                  f'Please remember to return the bottle once you are finished using it.' \
                  f'If you empty the bottle, please use the check-in form to notify us.\n' \
                  f'Thank you for using the Bode group chemical borrowing system!'
        sender = ['noreply@example.com']
        recipients = [self.cleaned_data['borrower_email']]
        send_mail(subject, message, sender, recipients)


class BottleCheckinForm(ModelForm):
    """
        This is a form derived from the models.Bottle that records data to return a bottle
    """
    class Meta:
        model = Bottle
        fields = ['id', 'status']
        widgets = {'status': HiddenInput}
    return_status = forms.ChoiceField(
        choices=[('EMPTY', 'empty'), ('OK', 'Returned to assigned shelf')],
        widget=forms.RadioSelect
    )
    status = 'in'


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


# class CheckOutForm(forms.Form):
#
#     list_of_loc_groups = [
#         ('BOD', 'Bode'),
#         ('CAR', 'Carreira'),
#         ('CHE', 'Chen'),
#         ('DIE', 'Diederich'),
#         ('EBE', 'Ebert'),
#         ('HIL', 'Hilvert'),
#         ('KAS', 'Kast'),
#         ('MOR', 'Morandi'),
#         ('THI', 'Thilgen'),
#         ('WEN', 'Wennemers'),
#         ('YAM', 'Yamakoshi'),
#         ('ZEN', 'Zenobi'),
#         ('OTH', 'OTHER')
#     ]
#     full_name = forms.CharField(label='Full Name', max_length=50)
#     email = forms.EmailField(label='ETH E-Mail Address', max_length=100)
#     send_confirmation = forms.BooleanField(label='Send confirmation e-mail?', required=False)
#     group = forms.ChoiceField(choices=list_of_loc_groups)
#     bottle_code = forms.CharField(
#         max_length=10,
#         strip=True
#     )
#     return_date = forms.DateField(
#         label='Anticipated Return Date',
#         initial=datetime.date.today() + datetime.timedelta(days=3),
#         help_text="Enter a date between now and 2 weeks (default 3 days).",
#         localize=True,
#         widget=forms.SelectDateWidget(years=return_list_with_ascending_x_values(datetime.date.today().year, 1, 1)),
#     )
#
#
# class CheckInForm(forms.Form):
#     email = forms.EmailField(label='ETH E-Mail Address', max_length=100)
#     bottle_code = forms.CharField(
#         max_length=10,
#         strip=True
#     )
#     status = forms.ChoiceField(
#         choices=[('EMPTY', 'empty'), ('OK', 'Returned to assigned shelf')],
#         widget=forms.RadioSelect
#     )
#

class CheckStatus(forms.Form):
    """
    This is a form to ask user which bottle to check.
    The purpose is to later redirect the user to the detail page of this bottle.
    """
    bottle_code = forms.CharField(
        max_length=10,
        strip=True,
        help_text='Enter the code of the bottle you would like to check (without dashes)',
        initial='123456',
        required=True
    )

    def clean_bottle_code(self):
        bottle_code = self.cleaned_data['bottle_code']
        try:
            Bottle.objects.filter(id=bottle_code)[0]
        except IndexError:
            raise ValidationError(
                message='This bottle is not listed in the database. '
                        'Please check if you used the right bottle code and try again.',
                code='not_in_db'
            )
        return bottle_code


