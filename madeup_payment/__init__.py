from dataclasses import dataclass


@dataclass(frozen=True)
class Charge:
    charge_id: str
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
        return Charge(charge_id='irrelevant', paid=True)

    @classmethod
    def retrieve(cls, charge_id: str) -> 'Charge':
        return Charge(charge_id=charge_id, paid=True)

    def capture(self) -> bool:
        return True

    def cancel_auth(self) -> bool:
        return True


class PaymentFailed(Exception):
    pass
