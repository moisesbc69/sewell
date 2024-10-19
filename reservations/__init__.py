from django.contrib import admin


class DefaultReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'date')
    # list_filter = ('date',)
    date_hierarchy = 'date'


def get_form():
    from reservations.forms import TemplatedForm
    from reservations.models import SimpleReservation
    """Returns templated model form for model that is currently set as reservationModel"""
    class ReservationForm(TemplatedForm):

        class Meta:
            model = SimpleReservation
            # exclude fields from standard Reservation model (show only extra ones in form)
            exclude = ('user', 'date', 'created', 'updated', )
    return ReservationForm


def update_model(newModel, newAdmin=None):
    """Update reservationModel variable and update Django admin to include it"""
    global reservationModel
    reservationModel = newModel
    from django.contrib import admin
    if not reservationModel in admin.site._registry:
        admin.site.register(reservationModel, DefaultReservationAdmin if not newAdmin else newAdmin)
