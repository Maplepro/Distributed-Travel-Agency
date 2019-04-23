from django.shortcuts import render, redirect, reverse
from urllib.parse import quote, unquote
from django.views import View
from database import utils, models
from accounts.authentication import is_authenticated, get_type
from . import forms
import requests
import datetime

class BusSearchView(View):
    template_name = 'buses/search.html'

    def get(self, request):
        if is_authenticated(request) == None:
            return redirect('accounts:Login')
        else:
            form = forms.BusSearchForm()
            return render(request, self.template_name, {'form': form, 'type': get_type(request)})

    def post(self, request):
        form = forms.BusSearchForm(request.POST)
        if form.is_valid():
            From = form.cleaned_data.get('From')
            To = form.cleaned_data.get('To')
            TravelDate = form.cleaned_data.get('TravelDate')
            
            if(TravelDate):
                query_string = 'From=' + quote(str(form.cleaned_data.get('From'))) + '&To=' + quote(str(form.cleaned_data.get('To'))) + '&TravelDate=' + quote(str(form.cleaned_data.get('TravelDate'))) 
                return redirect(reverse('buses:Display') + '?' + query_string)
            else:
                return render(request, self.template_name, {'form': form, 'error': '1', 'msg': 'Incorrect Travel Date', 'type': get_type(request)})
        else:
            return render(request, self.template_name, {'form': form, 'error': '1', 'msg': 'Fill in valid details only', 'type': get_type(request)})

class BusDisplayView(View):
    template_name = 'buses/display.html'

    def get_buses(self, From, To):
        return utils.get_bus_services_city(From, To)

    def get(self, request):
        if is_authenticated(request) == None:
            return redirect('accounts:Login')
        else:
            buses = self.get_buses(request.GET.get('From'), request.GET.get('To'))
            for bus in buses:
                print(bus.get('route'))
                # bus.update({'source': bus.get('route')[0]})
                # bus.update({'destination': bus.get('route')[len(bus.get('route')) - 1]})
                # bus.update({'start_time': bus.get('timing')[0]})
                # bus.update({'end_time': bus.get('timing')[len(bus.get('timing')) - 1]})
            return render(request, self.template_name, {'buses': buses, 'type': get_type(request)})

class BusDetailsView(View):
    template_name = 'buses/details.html'

    def get_bus_details(self, id):
        return utils.get_bus_service_by_id(id)

    def get(self, request, id):
        if is_authenticated(request) == None:
            return redirect('accounts:Login')
        else:
            print(request.GET)
            #form = forms.BusBookForm(initial = {'TravelDate': })
            details = self.get_bus_details(id)
            #print(details)
            return render(request, self.template_name, {'buses': details, 'type': get_type(request)})

    def post(self, request, id):
        form = forms.BusBookForm(request.POST)
        bus = self.get_bus_details(id)
        available = request.POST.get('available')
        if form.is_valid():
            seats = int(form.cleaned_data.get('seats'))
            if seats > 0 and seats <= int(available):
                new_id = 'B' + get_random_string(15)
                while(utils.check_booking_id(id = new_id) == False):
                    new_id = 'B' + get_random_string(15)
                db_name = utils.get_database_name()
                bill = int(bus.get('price')) * int(form.cleaned_data.get('seats'))
                r = utils.new_bus_booking(db_name = db_name,
                                            id = new_id,
                                            service_id = id,
                                            email = request.session.get('email'),
                                            From = form.cleaned_data.get('From'),
                                            To = form.cleaned_data.get('To'),
                                            booking_date = datetime.date.today(),
                                            seats = form.cleaned_data.get('seats'),
                                            bill = bill)
                if r == 201:
                    print('BOOKING CONFIRMED')
                else:
                    return render(request, self.template_name, {'available': available, 'form': form, 'error': '1', 'msg': 'Internal Error. Try Again.', 'bus': bus, 'type': get_type(request)})
            else:
                return render(request, self.template_name, {'available': available, 'form': form, 'error': '1', 'msg': 'Enter Valid number of Seats', 'bus': bus, 'type': get_type(request)})
        else:
            return render(request, self.template_name, {'available': available, 'form': form, 'error': '1', 'msg': 'Invalid Submission', 'bus': bus, 'type': get_type(request)})

class BusBookingListView(View):

    template_name = 'buses/bookings.html'

    def check_provider(self, email, id):
        service = models.ServiceMetaData.objects.filter(id = id)
        if not service:
            return False
        else:
            if email in service[0].provider:
                return True
            else:
                return False

    def get_bookings(self, id, date):
        return utils.get_bus_booking_by_date(id, date)

    def get(self, request, id):
        if is_authenticated(request) == None:
            return redirect('accounts:Login')
        if self.check_provider(request.session.get('email'), id) == True:
            bookings = self.get_bookings(id, datetime.date.today())
            form = forms.DateForm(initial = {'date': datetime.date.today})
            print(form.data)
            return render(request, self.template_name, {'form': form, 'bookings': bookings, 'type': get_type(request)})
        else:
            print('NOT FOUND')

    def post(self, request, id):
        form = forms.DateForm(request.POST)
        if form.is_valid():
            bookings = self.get_bookings(id, form.cleaned_data.get('date'))
            return render(request, self.template_name, {'form': form, 'bookings': bookings, 'type': get_type(request)})
        else:
            return render(request, self.template_name, {'form': form, 'error': '1', 'msg': 'Invalid Submission', 'bookings': bookings, 'type': get_type(request)})
