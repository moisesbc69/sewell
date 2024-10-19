import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
import logging
from datetime import datetime

try:
    from django.shortcuts import render, redirect
    from django.urls import reverse_lazy, reverse
    from django.views.generic import TemplateView, View, ListView, DeleteView
    try:
        from django.utils.encoding import force_text
    except Exception as e:
        from django.utils.encoding import force_str as force_text
    from django.utils.http import urlsafe_base64_decode
    from django.contrib.auth import login, logout
    from django.http import HttpResponse
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404, redirect
    from django.http import HttpResponse
    from django.contrib.auth.decorators import login_required
    from django.utils.decorators import method_decorator
    from django.conf import settings
except Exception as e: print("ERROR: ", e)

from reservas.models import Tour as TourModel
from reservas.models import DailyTour as DailyTourModel
from reservas.models import Holiday as HolidayModel

from transbank.webpay.webpay_plus.transaction import Transaction

# Create your views here.

def home(request):
    return render(request, 'index.html')

'''
def gobdatos(request):
    return render(request, 'landing/assessment.html')
'''
class LandingMain(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        
        print("final context: ", context)
        return context


class SearchTours(TemplateView):
    
    template_name = 'search-tours.html' 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context_ = self.set_context_data(self.request)
        #context.update(context_)
        print("final context: ", context)
        return context
    
    def post(self, request, *args, **kwargs):
        params = getattr(request, "POST")
        print("POST PARAMS: ", params)
        context_ = self.set_context_data(params)
        #self.save_user_search(context_, request)
        return render(request, self.template_name, context=context_)
    
    def set_context_data(self, params):
        email = params.get('email', '')
        arrival_date = datetime.strptime(params.get('arrival_date', ''),'%m/%d/%Y')
        departure_date = datetime.strptime(params.get('departure_date', ''),'%m/%d/%Y')
        #guests = params.get('guests', '')

        tours = TourModel.objects.filter(expiration_date__gte = arrival_date, is_expirated = False)
        print("tours", tours)
        context = {
            'tours': tours
        }

        '''
        context = {
            'email': params.get('email', ''),
            'arrival_date': params.get('arrival_date', ''),
            'departure_date': params.get('departure_date', ''),
            'guests': params.get('guests', 'Guests')
        }
        '''
        print("context", context)
        return context
    

class TourDetail(TemplateView):
    
    template_name = 'tour-details.html' 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context_ = self.set_context_data(self.request)
        #context.update(context_)
        print("final context: ", context)
        tour_name_search = context['name_search']
        tour = get_object_or_404(TourModel, name_search=tour_name_search)
        print("tour",tour)

        context['tour'] = tour 
        context['images'] = tour.images.all()
        print("context",context)

        return context

    
def get_tour_data(request):
    # Obtener las instancias de tours por día
    tours = DailyTourModel.objects.all()

    # Crear un diccionario donde cada día tenga un cupo
    tour_data = {
        tour.date.strftime('%Y-%m-%d'): tour.spot for tour in tours
    }

    # Obtener los días feriados
    holidays = HolidayModel.objects.values_list('date', flat=True)

    print('tour_data',tour_data)
    # Devolver los datos como JSON
    return JsonResponse({
        'tour_data': tour_data,
        'holidays': list(holidays)
    })

#TBK
def iniciar_transaccion(request):
    # Aquí configuras la transacción con los datos como monto y orden
    amount = 10000  # Monto total (por ejemplo, monto de la reserva)
    session_id = request.session.session_key
    buy_order = "orden1234"  # Número único para identificar la orden de compra
    return_url = settings.WEBPAY_RETURN_URL

    # Iniciar la transacción con Webpay
    tx = Transaction()
    response = tx.create(buy_order, session_id, amount, return_url)

    # Redirigir al usuario a Webpay
    return redirect(response['url'] + '?token_ws=' + response['token'])

def retorno_webpay(request):
    token = request.GET.get('token_ws')
    tx = Transaction()

    # Confirmar la transacción con el token
    response = tx.commit(token)

    if response['status'] == 'AUTHORIZED':
        # Transacción exitosa
        return render(request, 'transaccion_exitosa.html', {'response': response})
    else:
        # Transacción fallida
        return render(request, 'transaccion_fallida.html', {'response': response})

def final_webpay(request):
    # Aquí recibes la confirmación final de Webpay
    return render(request, 'final_webpay.html')
