from reservations.views import *
from django.urls import path
# Enable admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    path(r'month/(?P<month>\d*)/(?P<year>\d*)', MonthDetailView.as_view()),
    path('reservation/', Reservation.as_view(), name='reservations_reservation'),
    path('calendar/', calendar_view, name='reservations_calendar'),
    path('holidays/', get_holidays, name='reservations_holidays'),
    
]

