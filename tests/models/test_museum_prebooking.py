import pytest
from moneyed import Money

from booking_example.models import MuseumPreBooking


@pytest.mark.parametrize(
    'number_of_adults, number_of_children, expected_total',
    [
        (0, 0, 0),
        (2, 1, 3),
        (3, 3, 6),
    ]
)
def test_total(number_of_adults, number_of_children, expected_total):
    model = MuseumPreBooking(
        number_of_adults=number_of_adults,
        number_of_children=number_of_children,
        price_per_guest=Money(1, 'USD'),
    )

    assert model.total == Money(expected_total, 'USD')
