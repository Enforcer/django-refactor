from dataclasses import dataclass


@dataclass(frozen=True)
class Charge:
    paid: bool

    @classmethod
    def create(
        cls,
        amount: int,
        currency: str,
        description: str,
        capture: bool,
        source: str,
    ) -> 'Charge':
        return Charge(paid=True)

    @classmethod
    def retrieve(cls, capture_id: str) -> 'Charge':
        return Charge(paid=True)

    def capture(self) -> bool:
        return True


class PaymentFailed(Exception):
    pass
