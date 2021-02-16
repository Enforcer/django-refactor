import abc
from typing import Any, cast

from moneyed import Money

import madeup_payment


AuthHandle = str


class Payments(abc.ABC):

    @abc.abstractmethod
    def perform_zero_auth(self, token: str) -> None:
        pass

    @abc.abstractmethod
    def authorize(self, token: str, amount: Money) -> AuthHandle:
        pass

    @abc.abstractmethod
    def capture(self, auth_handle: AuthHandle) -> None:
        pass

    @abc.abstractmethod
    def release(self, auth_handle: AuthHandle) -> None:
        pass


class AuthorizationFailed(Exception):
    pass


class CaptureFailed(Exception):
    pass


class NewPayments(Payments):
    def perform_zero_auth(self, token: str) -> None:
        try:
            madeup_payment.Charge.create(
                amount=0,
                currency='USD',
                description='card validation',
                capture=False,
                source=token,
            )
        except madeup_payment.PaymentFailed:
            raise AuthorizationFailed

    def authorize(self, token: str, amount: Money) -> AuthHandle:
        try:
            charge = madeup_payment.Charge.create(
                amount=int(amount.amount) * 100,
                currency=amount.currency.code,
                description='authorize',
                capture=False,
                source=token,
            )
        except madeup_payment.PaymentFailed:
            raise AuthorizationFailed
        else:
            return charge.charge_id

    def capture(self, auth_handle: AuthHandle) -> None:
        charge = madeup_payment.Charge.retrieve(auth_handle)
        if not charge.capture():
            raise CaptureFailed

    def release(self, auth_handle: str) -> None:
        charge = cast(auth_handle, madeup_payment.Charge)
        charge.cancel_auth()


class OldPayments(Payments):
    pass
