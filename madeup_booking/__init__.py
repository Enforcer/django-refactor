import uuid
from typing import List


class MadeUpApiProviderError(Exception):
    pass


class BookingClient:

    def book_at_once(self, refs: List[str]) -> dict:
        return {'ReferenceNumber': str(uuid.uuid4())}
