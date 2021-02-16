from dataclasses import dataclass

from booking_example import emails, crm
from booking_example.models import Booking
from booking_example.payments import Payments, AuthorizationFailed
from madeup_booking import MadeUpApiProviderError, BookingClient


@dataclass
class BookingService:
    _payments: Payments
    _booking_client: BookingClient

    def __call__(self, booking: Booking, payment_card_token: str) -> None:
        try:
            self._payments.perform_zero_auth(payment_card_token)
        except AuthorizationFailed:
            booking.fail_payment()
            booking.save()
            return

        if booking.needs_pay_anything_now:
            try:
                auth_handle = self._payments.authorize(
                    payment_card_token, booking.pay_now_total
                )
            except AuthorizationFailed:
                booking.fail_payment()
                booking.save()
                emails.send_information_about_failure(booking)

        references = booking.get_prebookings_references()
        try:
            booking_api_response = self._booking_client.book_at_once(references)
        except MadeUpApiProviderError:
            if booking.needs_pay_anything_now:
                self._payments.release(auth_handle)

            emails.send_information_about_failure(booking)
        else:
            booking.reference = booking_api_response['ReferenceNumber']
            if booking.needs_pay_anything_now:
                self._payments.capture(auth_handle)

            crm.sync_booking(booking)

        booking.save()
