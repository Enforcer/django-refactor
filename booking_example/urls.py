from rest_framework.routers import SimpleRouter

from booking_example.views import BookingsViewSet

router = SimpleRouter()

router.register(r'bookings', BookingsViewSet)
