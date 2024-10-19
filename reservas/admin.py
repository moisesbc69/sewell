from django.contrib import admin
from .models import *

class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1  # Permite añadir una foto adicional por defecto

class TourAdmin(admin.ModelAdmin):
    inlines = [TourImageInline]  
    # Indica qué campos mostrar en la lista del administrador
    #list_display = ('name', 'activation_date', 'created', 'expiration', 'spot')

    # Si deseas incluir el campo en el formulario de edición también
    fields = ('name', 'name_search', 'description', 'price', 'photo', 'activation_date', 'expiration_date')

    # Si deseas que ciertos campos sean de solo lectura (como activation_date)
    readonly_fields = ('created', 'updated')


admin.site.register(Tour, TourAdmin)
admin.site.register(Holiday)

admin.site.register(Reservation)