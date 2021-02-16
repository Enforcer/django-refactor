import waffle
from django.db import transaction
from djmoney.contrib.django_rest_framework import MoneyField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from booking_example.commands import FinishBookingCommand
from booking_example.models import (
    Booking,
    AmusementParkPreBooking,
    MuseumPreBooking,
    RestaurantPreBooking,
)
from madeup_booking import MadeUpApiProviderError
import madeup_payment
import old_payment


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
        # in original source code, that method had 100+ LoC
        payment_card_token = validated_data.pop('payment_card_token')
        booking: Booking = super().create(validated_data)

        if not self.validate_payment_card_with_zero_auth(payment_card_token):
            booking.fail_payment()
            return booking

        if booking.pay_now_total.amount:
            with transaction.atomic():
                booking.authorize_payment_at_creation(
                    card_token=payment_card_token
                )
                if booking.status == booking.Status.FAILED_PAYMENT:
                    transaction.on_commit(
                        lambda: booking.send_email_about_failure('payment failed')
                    )
                    return booking

        return self.finish_booking(booking)

    @staticmethod
    def finish_booking(booking: Booking) -> Booking:
        command = FinishBookingCommand()
        try:
            command.finish_booking(booking)
        except MadeUpApiProviderError:
            if booking.pay_now_total.amount:
                booking.cancel_payment()
            booking.send_email_about_failure('booking failed')

        if booking.pay_now_total.amount:
            booking.capture_payment()

        booking.sync_with_crm()

        return booking

    def validate_payment_card_with_zero_auth(
        self, payment_card_token: str
    ) -> bool:
        if waffle.switch_is_active('use_new_payment'):
            try:
                madeup_payment.Charge.create(
                    amount=0,
                    currency='USD',
                    description='card validation',
                    capture=False,
                    source=payment_card_token
                )
            except madeup_payment.PaymentFailed:
                return False

            return True
        else:
            client = old_payment.Client()
            response = client.authorize(
                amount=0, currency='USD', token=payment_card_token
            )
            if response.status == old_payment.Status.SUCCESS:
                return True
            else:
                return False

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
