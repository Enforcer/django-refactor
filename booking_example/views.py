import waffle
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from booking_example.models import Booking
from booking_example.payments import NewPayments, OldPayments
from booking_example.serializers import BookingSerializer
from booking_example.services import BookingService
from madeup_booking import BookingClient


class BookingsViewSet(CreateModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    ordering = ("id",)

    def perform_create(self, serializer):
        card_token = serializer.validated_data.pop('payment_card_token')
        booking: Booking = serializer.save()

        booking_client = BookingClient()
        if waffle.switch_is_active('use_new_payment'):
            payments = NewPayments()
        else:
            payments = OldPayments()

        service = BookingService(payments, booking_client)
        service(booking, card_token)
