from unittest import TestCase

import pytest
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED

from rest_framework.test import APIClient
from waffle.testutils import override_switch

from booking_example.models import RestaurantPreBooking


class TestBooking(TestCase):
    def setUp(self) -> None:
        self._client = APIClient()

    def test_empty_payload_triggers_validation_error(self) -> None:
        response = self._client.post('/api/bookings/')

        assert response.status_code == HTTP_400_BAD_REQUEST

    @override_switch('use_new_payment', True)
    @pytest.mark.usefixtures('transactional_db')
    def test_creates_booking(self) -> None:
        prebooking = RestaurantPreBooking.objects.create(number_of_guests=2)
        response = self._client.post('/api/bookings/', data={
            'payment_card_token': 'xd',
            'restaurant_prebookings': [prebooking.pk],
        })

        assert response.status_code == HTTP_201_CREATED
        json = response.json()
        assert json['total'] == '0.00'
        assert json['reference'] is not None
