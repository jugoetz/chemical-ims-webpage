from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from django.core import exceptions
from .forms import *
from . import models


# Create your views here.

def get_checkout_data(request):
    """
    This view renders the checkout form, and sends the user-entered data back to the server
    """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        bottle_code = request.POST['id']  # get bottle_code from user input
        bottle_code_clean = bottle_code.replace('-', '')  # remove dashes that people might have placed
        try:
            instance = Bottle.objects.get(id=bottle_code_clean)  # get the Bottle instance user requested to change
            # create a form instance and populate it with data from the request + the Bottle instance to be changed
            form = BottleCheckoutForm(request.POST, instance=instance)
        except exceptions.ObjectDoesNotExist:
            # don't call the bottle instance since it will raise another error (as the bottle does not exist)
            # instead, let the validation method in the form handle it
            form = BottleCheckoutForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.cleaned_data['id'] = form.cleaned_data['id'].replace('-', '')  # remove dashes that user might have used in bottle code
            # process the data in form.cleaned_data as required
            # TODO remove following 2 comments when send_email is solved
            # if form.cleaned_data['send_confirmation'] is True:  # send an email if selected by user
            #     form.send_confirmation_email()
            # redirect to a new URL:
            form.save()
            response = HttpResponseRedirect(reverse('inventorymanagement:confirmcheckout',
                                                    kwargs={'pk': form.cleaned_data['id']}
                                                    ))
            # add cookies to the response to help fill form next time (max_age is 4 weeks...in seconds)
            response.set_cookie('email', form.cleaned_data['borrower_email'], max_age=2419200)
            response.set_cookie('fullname', form.cleaned_data['borrower_full_name'], max_age=2419200)
            response.set_cookie('group', form.cleaned_data['borrower_group'], max_age=2419200)
            return response

    # if a GET (or any other method) we'll create a blank form
    else:

        fullname = request.COOKIES.get('fullname')
        group = request.COOKIES.get('group')
        email = request.COOKIES.get('email')
        if fullname is None or group is None or email is None:
            form = BottleCheckoutForm()  # return unbound form
        else:
            # bind cookie data to form
            form = BottleCheckoutForm(initial={
                'borrower_full_name': fullname,
                'borrower_email': email,
                'borrower_group': group,
            })


    return render(request, 'inventorymanagement/checkoutform.html', {'form': form})


def get_checkin_data(request):
    """
    This view renders the checkin form, and sends the user-entered data back to the server
    """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        bottle_code = request.POST['id']  # get bottle_code from user input
        bottle_code_clean = bottle_code.replace('-', '')  # remove dashes that people might have placed
        try:
            instance = Bottle.objects.get(id=bottle_code_clean)  # get the Bottle instance user requested to change
            # create a form instance and populate it with data from the request + the Bottle instance to be changed
            form = BottleCheckinForm(request.POST, instance=instance)
        except exceptions.ObjectDoesNotExist:
            # don't call the bottle instance since it will raise another error (as the bottle does not exist)
            # instead, let the validation method in the form handle it
            form = BottleCheckinForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # remove dashes that user might have used in bottle code
            form.cleaned_data['id'] = form.cleaned_data['id'].replace('-', '')
            # form.cleaned_data['return_date'] = 'n/a'
            if form.cleaned_data['return_status'] == 'EMPTY':
                # delete the Bottle instance
                form.save()  # not sure if this call is necessary with the instance.save() afterwards
                instance.status = 'empty'
                instance.save()
                return HttpResponseRedirect(reverse('inventorymanagement:confirmempty', args=(bottle_code_clean,)))
            else:
                form.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('inventorymanagement:confirmreturn', args=(bottle_code_clean,)))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = BottleCheckinForm()
    return render(request, 'inventorymanagement/checkinform.html', {'form': form})


def get_status_data(request):
    """
    This view renders the status check form, and sends the user-entered data back to the server
    """
    # if this is a GET request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CheckStatus(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            return HttpResponseRedirect(reverse(
                'inventorymanagement:detail',
                kwargs={'pk': form.cleaned_data['bottle_code']}
            ))
    # if a POST (or any other method) we'll create a blank form
    else:
        form = CheckStatus()

    return render(request, 'inventorymanagement/statusform.html', {'form': form})


class IndexView(generic.ListView):
    models = models.Bottle
    template_name = 'inventorymanagement/index.html'

    def get_queryset(self):
        """
        Excludes any questions not published yet
        """
        return models.Bottle.objects.filter(code='GBODJG')


class CheckoutView(generic.DetailView):
    """
    This view shows the user a confirmation page with bottle details after checking out a bottle
    """
    model = models.Bottle
    template_name = 'inventorymanagement/checkoutconfirm.html'


class CheckinView(generic.DetailView):
    """
    This view shows the user a confirmation page after checking in a bottle
    """
    model = models.Bottle
    template_name = 'inventorymanagement/checkinconfirm.html'


class CheckinEmptyView(generic.DetailView):
    """
    This view shows the user a confirmation page after declaring a bottle empty
    """
    model = models.Bottle
    template_name = 'inventorymanagement/emptyconfirm.html'


class StatusView(generic.DetailView):
    """
    This view shows the user detailed bottle information after a status request
    """
    model = models.Bottle
    template_name = 'inventorymanagement/status.html'


