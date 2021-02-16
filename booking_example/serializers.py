from djmoney.contrib.django_rest_framework import MoneyField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from booking_example.models import (
    Booking,
    AmusementParkPreBooking,
    MuseumPreBooking,
    RestaurantPreBooking,
)


class BookingSerializer(ModelSerializer):

    amusement_park_prebookings = PrimaryKeyRelatedField(
        many=True,
        queryset=AmusementParkPreBooking.objects.all(),
    )
    museum_prebookings = PrimaryKeyRelatedField(
        many=True,
        queryset=MuseumPreBooking.objects.all(),
    )
    restaurant_prebookings = PrimaryKeyRelatedField(
        many=True,
        queryset=RestaurantPreBooking.objects.all()
    )
    payment_card_token = CharField(write_only=True)
    total = MoneyField(max_digits=6, decimal_places=2, read_only=True)
    reference = CharField(read_only=True)

    @staticmethod
    def validate_at_least_one_prebooking(data):
        keys = (
            'amusement_park_prebookings',
            'museum_prebookings',
            'restaurant_prebookings',
        )

        if not any(data[key] for key in keys):
            raise ValidationError('At least one prebooking is required')
        return data

    def validate(self, data):
        data = super().validate(data)
        data = self.validate_at_least_one_prebooking(data)
        return data

    def create(self, validated_data) -> Booking:
        booking: Booking = super().create(validated_data)
        return booking

    class Meta:
        model = Booking
        read_only_fields = (
            'total',
            'reference',
        )
        fields = read_only_fields + (
            'amusement_park_prebookings',
            'museum_prebookings',
            'restaurant_prebookings',
            'payment_card_token',
        )
