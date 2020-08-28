from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
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
        instance = Bottle.objects.get(id=bottle_code)  # get the Bottle instance user requested to change
        # create a form instance and populate it with data from the request + the Bottle instance to be changed:
        form = BottleCheckoutForm(request.POST, instance=instance)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # TODO remove following 2 comments when send_email is solved
            # if form.cleaned_data['send_confirmation'] is True:  # send an email if selected by user
            #     form.send_confirmation_email()
            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('inventorymanagement:confirmcheckout', kwargs={'pk': form.cleaned_data['id']}))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = BottleCheckoutForm()

    return render(request, 'inventorymanagement/checkoutform.html', {'form': form})


def get_checkin_data(request):
    """
    This view renders the checkin form, and sends the user-entered data back to the server
    """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        bottle_code = request.POST['id']
        instance = Bottle.objects.get(id=bottle_code)
        # create a form instance and populate it with data from the request:
        form = BottleCheckinForm(request.POST, instance=instance)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            if form.cleaned_data['return_status'] == 'EMPTY':
                # delete the Bottle instance
                form.save()
                instance.status = 'empty'
                instance.save()
                return HttpResponseRedirect(reverse('inventorymanagement:confirmempty', args=(bottle_code,)))
            else:
                form.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('inventorymanagement:confirmreturn', args=(bottle_code,)))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = BottleCheckinForm()

    return render(request, 'inventorymanagement/checkinform.html', {'form': form})


def get_status_data(request):
    """
    This view renders the status check form, and sends the user-entered data back to the server
    """
    # if this is a GET request we need to process the form data
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = CheckStatus(request.GET)
        # check whether it's valid:
        if form.is_valid():
            print(form.cleaned_data)
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


