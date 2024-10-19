from django.db import models
#from importlib.resources import path
from os import sep
import re, threading
from datetime import date, datetime, timedelta #, time
from django.utils.text import slugify
#from email.policy import default

from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.contrib.sessions.models import Session
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from django.db import models
from django.db.models import Func, F, Q
from django.db.models.manager import BaseManager
from django.db.models.signals import post_save, post_delete, m2m_changed
from reservastours.settings import STATIC_DEFAULT_LOGO

'''
OWNERSHIP_TYPE = (
    ("O0", "--"), #None
    ("O1", "Privately Held"),
    ("O2", "Individual Entrepreneurship"),
    ("O3", "Public"),
    ('O4', 'Partnership'),
    ("O5", "Educational Institution"),
    ("O6", "Government Agency"),
    ("O7", "Non-profit"),
)

PROFILE_TYPE = (
    (0, "--"),
    (1, "Buyer"),
    (2, "Seller"),
)
'''
'''
def tours_files_directory_path(instance, filename):
    import os
    from reservastours.settings import MEDIA_ROOT
    if os.path.isabs(filename): 
        path = filename.replace(MEDIA_ROOT, "") #+os.path.sep
        print("path: "+str(path))
    else: path = 'uploads/tours/{0}'.format(filename)
    return path
'''

def tours_images_tours_directory_path(instance, filename):
    # Si la instancia es de Tour, usar el ID y el nombre del tour
    if isinstance(instance, Tour):
        cleaned_name = slugify(instance.name)
        return f'uploads/tours/{cleaned_name}/{filename}'
    
    # Si la instancia es de TourImage, usar el ID y el nombre del tour asociado
    if isinstance(instance, TourImage):
        cleaned_name = slugify(instance.tour.name)
        return f'uploads/tours/{cleaned_name}/{filename}'


# Create your models here.
class Tour(models.Model):
    """
    Model for tours
    """
    name = models.CharField(max_length=250, null=True, blank=True,
        help_text="Name of Tour")
    name_search = models.CharField(max_length=250, null=False, unique = True, help_text="Tour Name Search")
    description = models.TextField(null=True, blank=True, help_text="Tour Description")
    price = models.CharField(max_length=250, null=True, default="")
    #spot = models.IntegerField(default=50, null=True, blank=True, help_text="Cupos del Tour")
    photo = models.FileField(
        upload_to=tours_images_tours_directory_path,
        storage = FileSystemStorage(location=settings.MEDIA_ROOT),
        default = STATIC_DEFAULT_LOGO,
        null=True,
        blank=True,
        help_text="Photo of Tour")
    activation_date = models.DateTimeField(null=False, default=timezone.now, help_text="Activation Date")
    expiration_date = models.DateTimeField(null=False, help_text="Expiration Date")
    is_expirated = models.BooleanField(default=False, blank=True, help_text="True if tour is expirated or cancelled")
    created = models.DateTimeField(null=True, auto_now_add=True, help_text="Creation Date")
    updated = models.DateTimeField(null=True, auto_now=True, help_text="Update Date")
    
    
    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        verbose_name = "Tour"
        verbose_name_plural = "Tour"
        constraints = [
            #models.UniqueConstraint(fields=["name"], name="name_unique_key")
        ]
    
    def save(self, *args, **kwargs):
        #if bool(self.short_name):
        #   setattr(self, "short_name", str(self.short_name).upper())
        print("--SAVING Tour: "+str(self.name))
        post_save.connect(create_tour_days, sender=Tour)

        super().save(*args, **kwargs)

class TourImage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='images')
    image = models.FileField(
        upload_to=tours_images_tours_directory_path,
        storage=FileSystemStorage(location=settings.MEDIA_ROOT),  # Usar la misma configuración de almacenamiento
        null=True,
        blank=True,
        help_text="Additional photo of the tour"
    )
    
    caption = models.CharField(max_length=255, null=True, blank=True)  # Descripción opcional

    def __str__(self):
        return f"Image for {self.tour.name}"

def create_tour_days(sender, instance, created, **kwargs):
    print(str(type(instance)).upper()+" POST MODEL TOUR SAVE: ")

    start_date = instance.activation_date.date()
    end_date = instance.expiration_date.date()

    print('start_date',start_date)
    print('end_date',end_date)

    if created:
        current_date = start_date
        while current_date <= end_date:

            if not Holiday.objects.filter(date=current_date).exists():  # Verificar si el día actual es un feriado
                # Crear la instancia diaria del tour
                DailyTour.objects.create(
                    tour=instance,
                    date=current_date
                )
            # Incrementar el día en 1
            current_date += timedelta(days=1)


class DailyTour(models.Model):
    """DailyTour model - who made a DailyTour and when"""
    tour = models.ForeignKey(Tour, null=True, blank=True, on_delete = models.CASCADE, help_text="Tour")
    date = models.DateField(null=False, blank=False)
    spot = models.IntegerField(default=10, null=True, blank=True, help_text="Cupos de la reserva diaria")
    # Timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        verbose_name = "DailyTour"
        verbose_name_plural = "DailyTour"
        constraints = [
            #models.UniqueConstraint(fields=["name"], name="name_unique_key")
        ]

    def save(self, *args, **kwargs):
        #if bool(self.short_name):
        #   setattr(self, "short_name", str(self.short_name).upper())
        print("--SAVING DailyTour: "+str(self.date)+str(self.tour))
        super().save(*args, **kwargs)

    def __unicode__(self):
        return str(self.date) + " User: " + str(self.user)

    def short_desc(self):
        """Default short description visible on TourDay button"""
        return str(self.id)

class Holiday(models.Model):
    name = models.CharField(max_length=100)  # Nombre del feriado
    date = models.DateField()  # Fecha del feriado
    active = models.BooleanField(default=True, editable=True)
    # Timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return f"{self.name} - {self.date}"

class Reservation(models.Model):
    """Reservation model - who made a reservation and when"""
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    tour_day = models.ForeignKey(DailyTour, null=True, blank=True, on_delete = models.CASCADE, help_text="Tour")
    date = models.DateTimeField(null=False, blank=False)
    # Timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservation"
        constraints = [
            #models.UniqueConstraint(fields=["name"], name="name_unique_key")
        ]

    def save(self, *args, **kwargs):
        #if bool(self.short_name):
        #   setattr(self, "short_name", str(self.short_name).upper())
        print("--SAVING Reservation: "+str(self.user)+str(self.tour))
        super().save(*args, **kwargs)

    def __unicode__(self):
        return str(self.date) + " User: " + str(self.user)

    def short_desc(self):
        """Default short description visible on reservation button"""
        return str(self.id)
    