import itertools

from django.db import models
from django.db.models import CharField
from djmoney.models.fields import MoneyField
from moneyed import Money


class Booking(models.Model):
    class Status(models.TextChoices):
        FAILED_PAYMENT = 'FAILED_PAYMENT'
        PAID = 'PAID'
        SUCCESS = 'SUCCESS'

    reference = models.CharField(max_length=255)
    status = models.CharField(
        choices=Status.choices, null=True, blank=True, max_length=40
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def fail_payment(self):
        assert self.status is None
        self.status = self.Status.FAILED_PAYMENT

    @property
    def pay_now_total(self):
        return Money(1, 'USD')

    @property
    def total(self):
        all_prebookings = itertools.chain(
            self.amusement_park_prebookings.all(),
            self.restaurant_prebookings.all(),
            self.museum_prebookings.all(),
        )
        return sum(prebooking.total for prebooking in all_prebookings)

    def authorize_payment_at_creation(self, card_token: str):
        pass

    def sync_with_crm(self):
        pass

    def send_email_about_failure(self, reason: str) -> None:
        ...

    def cancel_payment(self):
        pass

    def capture_payment(self):
        pass


class Prebooking(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    prebooking_ref = models.CharField(max_length=255)

    class Meta:
        abstract = True

    @property
    def total(self):
        raise NotImplementedError


class AmusementParkPreBooking(Prebooking):
    booking = models.ForeignKey(
        Booking,
        related_name="amusement_park_prebookings",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    number_of_adults = models.PositiveIntegerField()
    number_of_children = models.PositiveIntegerField()
    price_per_adult = MoneyField(
        max_digits=6, decimal_places=2, default_currency='USD'
    )
    price_per_child = MoneyField(
        max_digits=6, decimal_places=2, default_currency='USD',
    )

    @property
    def total(self):
        adult_total = self.number_of_adults * self.price_per_adult
        childern_total = self.number_of_children * self.price_per_child
        return adult_total + childern_total


class MuseumPreBooking(Prebooking):
    booking = models.ForeignKey(
        Booking,
        related_name="museum_prebookings",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    number_of_adults = models.PositiveIntegerField()
    number_of_children = models.PositiveIntegerField()
    price_per_guest = MoneyField(
        max_digits=6, decimal_places=2, default_currency='USD',
    )
    provider = CharField(max_length=120)

    @property
    def total(self):
        guests_count = (self.number_of_children + self.number_of_adults)
        return guests_count * self.price_per_guest


class RestaurantPreBooking(Prebooking):
    booking = models.ForeignKey(
        Booking,
        related_name="restaurant_prebookings",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    number_of_guests = models.PositiveIntegerField()

    @property
    def total(self):
        return Money(0, 'USD')
