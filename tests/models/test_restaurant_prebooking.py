import pytest
from moneyed import Money

from booking_example.models import RestaurantPreBooking


@pytest.mark.parametrize('number_of_guests', [2, 5, 10])
def test_total_is_0(number_of_guests):
    model = RestaurantPreBooking(number_of_guests=number_of_guests)

    assert model.total == Money(0, 'USD')
