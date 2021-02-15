import enum
from dataclasses import dataclass


class Status(enum.Enum):
    SUCCESS = enum.auto()
    FAILED = enum.auto()


@dataclass
class Response:
    status: Status


class Client:
    def authorize(self, amount: int, currency: str, token: str) -> Response:
        return Response(Status.SUCCESS)
