import logging
import itertools

from booking_example.models import Booking
import madeup_booking


logger = logging.getLogger(__name__)


class FinishBookingCommand:
    def __init__(self):
        self.madeup_booking_client = madeup_booking.BookingClient()

    def finish_booking(self, booking: Booking) -> None:
        all_prebookings = itertools.chain(
            booking.amusement_park_prebookings.all(),
            booking.restaurant_prebookings.all(),
            booking.museum_prebookings.all(),
        )
        references = []
        for prebooking in all_prebookings:
            references.append(prebooking.prebooking_ref)

        try:
            booking_response = self.madeup_booking_client.book_at_once(
                references
            )
        except madeup_booking.MadeUpApiProviderError:
            logger.error('Oh no... Anyway')
            raise

        self.update_booking(booking, booking_response)

    @staticmethod
    def update_booking(booking: Booking, booking_response: dict) -> None:
        booking.reference = booking_response['ReferenceNumber']
        booking.save()
