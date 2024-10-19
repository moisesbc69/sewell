from django.urls import path
from . import views
from .views import *
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('search-tours/', SearchTours.as_view(), name='search_tours'),
    path('search-tours/tour/<slug:name_search>/', TourDetail.as_view(), name='tour_details'),
    path('get-tour-data/', get_tour_data, name='get_tour_data'),
    path('webpay/iniciar/', iniciar_transaccion, name='iniciar_transaccion'),
    path('webpay/return/', retorno_webpay, name='retorno_webpay'),
    path('webpay/final/', final_webpay, name='final_webpay'),
    #path('assessment-gobierno-datos/', views.gobdatos, name='gobdatos'),
    #path('chat/', views.chat_with_gpt, name='chat_with_gpt'),
]

