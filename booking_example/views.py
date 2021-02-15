from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet

from booking_example.models import Booking
from booking_example.serializers import BookingSerializer


class BookingsViewSet(CreateModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    ordering = ("id",)
