from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class AirplaneType(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=63)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE, related_name="airplanes")

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name

class Airport(models.Model):
    name = models.CharField(max_length=63)
    closest_big_city = models.CharField(max_length=63)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departure_routes")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrival_routes")
    distance = models.IntegerField()

    def __str__(self):
        return self.source.name + "-" + self.destination.name

    @property
    def full_route(self):
        return f"{self.source.closest_big_city}-{self.destination.closest_big_city}"

class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{str(self.route)}-{self.airplane.name}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")

    def __str__(self):
        return str(self.created_at)

class Ticket(models.Model):
    rows = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        unique_together = ("flight", "rows", "seat")

    def __str__(self):
        return f"{str(self.flight)}-{self.seat}-{self.row}"

    def clean(self):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (self.row, "row", "rows"),
            (self.seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(
                self.flight.airplane, airplane_attr_name
            )
            if not (1 <= ticket_attr_value <= count_attrs):
                raise ValidationError(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                                          f"number must be in available range: "
                                          f"(1, {airplane_attr_name}): "
                                          f"(1, {count_attrs})"
                    }
                )
    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    @staticmethod
    def validate_seat_and_row(
            seat: int,
            num_seats: int,
            row: int,
            num_rows: int,
            error_to_raise
    ):
        if not (1 <= seat <= num_seats):
            raise error_to_raise({
                "seat": f"seat must be in range [1, {num_seats}], not {seat}"
            })
        if not (1 <= row <= num_rows):
            raise error_to_raise({
                "seat": f"row must be in range [1, {num_rows}], not {row}"
            })

