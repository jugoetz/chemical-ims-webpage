from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django.core import exceptions
from .forms import *
from .models import *


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
            form = BottleCheckoutForm(initial={
                'checkout_date': timezone.now().date(),
            })  # return form without data from cookies
        else:
            # bind cookie data to form
            form = BottleCheckoutForm(initial={
                'checkout_date': timezone.now().date(),
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
        form = BottleCheckinForm(initial={'checkout_date': None})
    return render(request, 'inventorymanagement/checkinform.html', {'form': form})


def get_status_data(request):
    """
    This view renders the status check form, and sends the user-entered data back to the server
    """
    # if this is a POST request we need to process the form data
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


def get_user_code(request):
    """
    This view renders the 'Where are my chemicals?' code entering form, and sends the user-entered code back to the server
    """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CheckUserChemicals(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            response = HttpResponseRedirect(reverse(
                'inventorymanagement:list_detail',
                kwargs={'code': form.cleaned_data['user_code'], 'only_checked_out': form.cleaned_data['only_checked_out']}
            ))

            return response
    # if a POST (or any other method) we'll create a blank form
    else:
        form = CheckUserChemicals()

    return render(request, 'inventorymanagement/codeform.html', {'form': form})


class IndexView(generic.ListView):
    model = ChangeListEntry
    ordering = '-date'
    template_name = 'inventorymanagement/index.html'


class ChangeListView(generic.ListView):
    model = ChangeListEntry
    ordering = '-date'
    template_name = 'inventorymanagement/changelist.html'


class CheckoutView(generic.DetailView):
    """
    This view shows the user a confirmation page with bottle details after checking out a bottle
    """
    model = Bottle
    template_name = 'inventorymanagement/checkoutconfirm.html'


class CheckinView(generic.DetailView):
    """
    This view shows the user a confirmation page after checking in a bottle
    """
    model = Bottle
    template_name = 'inventorymanagement/checkinconfirm.html'


class CheckinEmptyView(generic.DetailView):
    """
    This view shows the user a confirmation page after declaring a bottle empty
    """
    model = Bottle
    template_name = 'inventorymanagement/emptyconfirm.html'


class StatusView(generic.DetailView):
    """
    This view shows the user detailed bottle information after a status request
    """
    model = Bottle
    template_name = 'inventorymanagement/status.html'


class AboutView(generic.TemplateView):
    """
    This view shows the about page
    """
    template_name = 'inventorymanagement/about.html'


class UserChemicalsView(generic.ListView):
    """
    This view shows all bottles associated to a usercode
    """

    def dispatch(self, request, *args, **kwargs):
        self.code = kwargs['code']
        self.only_checked_out = kwargs['only_checked_out']
        return super(UserChemicalsView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.only_checked_out == 'True':
            queryset = Bottle.objects.filter(code=self.code, status='out')
        else:
            queryset = Bottle.objects.filter(code=self.code)
        return queryset

    form_class = CheckUserChemicals
    model = Bottle
    template_name = 'inventorymanagement/list_detail.html'
    ordering = 'description'
