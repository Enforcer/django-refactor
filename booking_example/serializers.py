import itertools

import waffle
from django.db import transaction
from djmoney.contrib.django_rest_framework import MoneyField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

import madeup_booking
from booking_example import crm, emails
from booking_example.models import (
    Booking,
    AmusementParkPreBooking,
    MuseumPreBooking,
    RestaurantPreBooking,
)
import madeup_payment
import old_payment
from booking_example.payments import NewPayments, OldPayments, AuthorizationFailed


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
        if waffle.switch_is_active('use_new_payment'):
            payments = NewPayments()
        else:
            payments = OldPayments()

        # in original source code, that method had 100+ LoC
        payment_card_token = validated_data.pop('payment_card_token')
        booking: Booking = super().create(validated_data)

        try:
            payments.perform_zero_auth(payment_card_token)
        except AuthorizationFailed:
            booking.fail_payment()
            booking.save()
            return booking

        if booking.needs_pay_anything_now:
            try:
                auth_handle = payments.authorize(
                    payment_card_token, booking.pay_now_total
                )
            except AuthorizationFailed:
                booking.fail_payment()
                booking.save()
                emails.send_information_about_failure(booking)
                return booking

        madeup_client = madeup_booking.BookingClient()
        references = booking.get_prebookings_references()
        try:
            booking_api_response = madeup_client.book_at_once(references)
        except madeup_booking.MadeUpApiProviderError:
            if booking.needs_pay_anything_now:
                payments.release(auth_handle)

            emails.send_information_about_failure(booking)
        else:
            booking.reference = booking_api_response['ReferenceNumber']
            if booking.needs_pay_anything_now:
                payments.capture(auth_handle)

            crm.sync_booking(booking)

        booking.save()
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
