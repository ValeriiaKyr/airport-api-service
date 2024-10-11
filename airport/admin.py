from django.contrib import admin
from airport.models import (
    Crew,
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Flight,
    Order,
    Ticket,
)


admin.site.register(Crew)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(Flight)
admin.site.register(Ticket)
admin.site.register(Order)