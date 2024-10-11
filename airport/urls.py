from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    AirplaneViewSet,
    RouteViewSet,
    CrewViewSet,
    FlightViewSet,
    TicketViewSet,
    AirplaneTypeViewSet,
    OrderViewSet
)

router = routers.DefaultRouter()
router.register("airport", AirportViewSet)
router.register("airplane", AirplaneViewSet)
router.register("route", RouteViewSet)
router.register("crew", CrewViewSet)
router.register("flight", FlightViewSet)
router.register("ticket", TicketViewSet)
router.register("airplane_type", AirplaneTypeViewSet)
router.register("order", OrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"