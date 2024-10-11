from rest_framework import serializers
from django.db import transaction

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

class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "airplane_type", "rows", "seats_in_row", "capacity")


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(
        read_only=True, slug_field="name"
    )

class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(many=False, read_only=True)

    class Meta:
        model = Airplane
        fields = ("id", "name", "airplane_type", "rows", "seats_in_row", "capacity", )


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance", "full_route")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(read_only=True, slug_field="name")
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance", "full_route")


class RouteDetailSerializer(serializers.ModelSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)
    route = RouteSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance", "route")

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "arrival_time", "departure_time", "crew")


class FlightListSerializer(FlightSerializer):
    airplane_name = serializers.CharField(source="airplane.name", read_only=True)
    airplane_capacity = serializers.IntegerField(source="airplane.capacity", read_only=True)
    route = serializers.SlugRelatedField(read_only=True, slug_field="full_route")
    crew = serializers.SlugRelatedField(many=True, read_only=True, slug_field="full_name")

    class Meta:
        model = Flight
        fields = (
            "id",
            "arrival_time",
            "departure_time",
            "airplane_name",
            "airplane_capacity",
            "route",
            "crew"
        )

class FlightDetailSerializer(FlightSerializer):
    route = RouteDetailSerializer(many=False, read_only=True)
    airplane = AirplaneDetailSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)


    class Meta:
        model = Flight
        fields = ("id", "route", "arrival_time", "departure_time", "airplane", "crew")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "rows", "seat", "flight")

    def validate(self, attrs):
        result = super().validate(attrs)

        Ticket.validate_seat_and_row(
            result["seat"],
            result["flight"].flight.seats_in_row,
            result["flight"].flight.seats_in_row,
            result["rows"],
            result["flight"].flight.rows,
            serializers.ValidationError,
        )
        return result


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)