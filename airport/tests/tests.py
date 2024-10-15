import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import (
    Crew,
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Flight
)
from airport.serializers import (
    CrewListSerializer,
    CrewDetailSerializer,
    AirplaneSerializer,
    AirplaneDetailSerializer,
    AirportSerializer,
    RouteSerializer,
    RouteDetailSerializer
)


def sample_crew(**params):
    defaults = {
        "first_name": "First",
        "last_name": "Last"
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


def sample_airplane(**params):
    airplane_type = AirplaneType.objects.create(
        name="Test",
    )
    defaults = {
        "name": "Test",
        "rows": 20,
        "seats_in_row": 20,
        "airplane_type": airplane_type
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def sample_airport(**params):
    defaults = {
        "name": "Test",
        "closest_big_city": "TestCity"
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


def sample_route(**params):
    source = Airport.objects.create(
        name="Test1",
        closest_big_city="TestCity1",
    )
    destination = Airport.objects.create(
        name="Test2",
        closest_big_city="TestCity2",
    )
    defaults = {
        "source": source,
        "destination": destination,
        "distance": 100,
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_flight(**params):
    source = Airport.objects.create(
        name="Test1",
        closest_big_city="TestCity1",
    )
    destination = Airport.objects.create(
        name="Test2",
        closest_big_city="TestCity2",
    )
    route = Route.objects.create(
        source=source,
        destination=destination,
        distance=100,
    )
    airplane_type = AirplaneType.objects.create(
        name="Test",
    )
    airplane = Airplane.objects.create(
        name="Test",
        rows=20,
        seats_in_row=20,
        airplane_type=airplane_type
    )
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": "2022-06-02 14:00:00",
        "arrival_time": "2022-06-02 15:00:00",
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)


User = get_user_model()
CREW_URL = reverse("airport:crew-list")
AIRPLANE_URL = reverse("airport:airplane-list")
AIRPORT_URL = reverse("airport:airport-list")
FLIGHT_URL = reverse("airport:flight-list")
ROUTE_URL = reverse("airport:route-list")


def detail_crew_url(crew_id):
    return reverse("airport:crew-detail", args=[crew_id])


def detail_flight_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


def detail_route_url(route_id):
    return reverse("airport:route-detail", args=[route_id])


def detail_airplane_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])


def image_upload_url(crew_id):
    return reverse("airport:crew-upload-image", args=[crew_id])


class CrewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpass"
        )
        self.client.force_authenticate(self.user)

    def test_crew_list(self):
        res = self.client.get(CREW_URL)
        crews = Crew.objects.all()
        serializer = CrewListSerializer(crews, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_crew_detail(self):

        crew = sample_crew()
        url = detail_crew_url(crew.id)
        res = self.client.get(url)

        serializer = CrewDetailSerializer(crew)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class CrewImageUploadTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.crew = sample_crew()

    def tearDown(self):
        self.crew.image.delete()

    def test_upload_image_to_crew(self):
        url = image_upload_url(self.crew.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.crew.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.crew.image.path))

    def test_upload_image_bad_request(self):
        url = image_upload_url(self.crew.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_crew_list(self):
        url = CREW_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "first_name": "Test1",
                    "last_name": "Test2",
                    "image": ntf
                },
                format="multipart"
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        crew = Crew.objects.get(first_name="Test1")
        self.assertFalse(crew.image)

    def test_image_url_is_shown_on_movie_detail(self):
        url = image_upload_url(self.crew.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_crew_url(self.crew.id))

        self.assertIn("image", res.data)


class AirplaneTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpass"
        )
        self.airplane_type = AirplaneType.objects.create(name="Test")

        self.client.force_authenticate(self.user)

    def test_airplane_list(self):
        res = self.client.get(AIRPLANE_URL)
        airplane = Airplane.objects.all()
        serializer = AirplaneSerializer(airplane, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_airplane_detail(self):
        airplane = sample_airplane()
        url = detail_airplane_url(airplane.id)
        res = self.client.get(url)

        serializer = AirplaneDetailSerializer(airplane)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane(self):

        payload = {
            "name": "Test",
            "rows": 20,
            "seats_in_row": 10,
            "airplane_type": self.airplane_type.id
        }
        res = self.client.post(AIRPLANE_URL, payload)
        airplane = Airplane.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            if key == "airplane_type":
                self.assertEqual(payload[key], airplane.airplane_type.id)
            else:
                self.assertEqual(payload[key], getattr(airplane, key))

    def test_delete_airplane(self):
        airplane = sample_airplane()
        url = detail_airplane_url(airplane.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Airport.objects.count(), 0)


class AirportTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpass"
        )
        self.client.force_authenticate(self.user)

    def test_airport_list(self):
        res = self.client.get(AIRPORT_URL)
        airport = Airplane.objects.all()
        serializer = AirportSerializer(airport, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airport(self):
        payload = {
            "name": "Test",
            "closest_big_city": "TestCity",
        }
        res = self.client.post(AIRPORT_URL, payload)
        airport = Airport.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(airport, key))


class RouteTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpass"
        )
        self.source = Airport.objects.create(
            name="Test1",
            closest_big_city="TestCity1"
        )
        self.destination = Airport.objects.create(
            name="Test2",
            closest_big_city="TestCity2"
        )
        self.client.force_authenticate(self.user)

    def test_route_list(self):
        res = self.client.get(ROUTE_URL)
        route = Route.objects.all()
        serializer = RouteSerializer(route, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_airplane_detail(self):
        route = sample_route()
        url = detail_route_url(route.id)
        res = self.client.get(url)

        serializer = RouteDetailSerializer(route)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route(self):
        payload = {
            "source": self.source.id,
            "destination": self.destination.id,
            "distance": 100,
        }
        res = self.client.post(ROUTE_URL, payload)
        route = Route.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            if key == "source":
                self.assertEqual(payload[key], route.source.id)
            elif key == "destination":
                self.assertEqual(payload[key], route.destination.id)
            else:
                self.assertEqual(payload[key], getattr(route, key))
