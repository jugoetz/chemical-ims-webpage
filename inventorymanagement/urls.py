"""checkout URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from . import views
from django.urls import path

app_name = 'inventorymanagement'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('take/', views.get_checkout_data, name='borrow'),
    path('take/confirmation/<pk>', views.CheckoutView.as_view(), name='confirmcheckout'),
    path('bring/', views.get_checkin_data, name='return'),
    path('bring/confirmation/<pk>', views.CheckinView.as_view(), name='confirmreturn'),
    path('bring/confirmation_empty/<pk>', views.CheckinEmptyView.as_view(), name='confirmempty'),
    path('status/', views.get_status_data, name='status'),
    path('status/<pk>', views.StatusView.as_view(), name='detail'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('changelist/', views.ChangeListView.as_view(), name='changelist'),
    path('list/', views.get_user_code, name='list'),
    path('list/<code>/<only_checked_out>', views.UserChemicalsView.as_view(), name='list_detail'),
]
