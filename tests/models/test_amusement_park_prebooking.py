from unittest import TestCase

from moneyed import Money

from booking_example.models import AmusementParkPreBooking


class TestAmusementParkPreBooking(TestCase):
    def test_total(self):
        prebooking = AmusementParkPreBooking(
            number_of_adults=1,
            number_of_children=2,
            price_per_child=Money(10, 'USD'),
            price_per_adult=Money(15, 'USD'),
        )

        assert prebooking.total == Money(35, 'USD')
