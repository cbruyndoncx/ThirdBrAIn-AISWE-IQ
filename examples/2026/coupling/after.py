from decimal import Decimal
from typing import Protocol

from domain import (
    Booking,
    Country,
    Destination,
    Invoice,
    Itinerary,
    Traveler,
    TripRequest,
)


class FlightAPI(Protocol):
    def reserve(self, flight_id: str) -> str: ...


class HotelAPI(Protocol):
    def reserve(self, hotel_id: str) -> str: ...


class RealFlightAPI:
    def reserve(self, flight_id: str) -> str:
        return f"flight-ref-{flight_id}"


class RealHotelAPI:
    def reserve(self, hotel_id: str) -> str:
        return f"hotel-ref-{hotel_id}"


class BookingRepository:
    def save(
        self,
        itinerary: Itinerary,
        flight_reference: str,
        hotel_reference: str,
    ) -> Booking:
        return Booking(
            id="booking-123",
            itinerary=itinerary,
            flight_reference=flight_reference,
            hotel_reference=hotel_reference,
        )


class EmailSender:
    def send_confirmation(
        self,
        recipient: str,
        booking_id: str,
        invoice_total: Decimal,
        hotel_reference: str,
    ) -> None:
        print(
            f"Sending confirmation to {recipient} for {booking_id}: "
            f"{invoice_total}, hotel: {hotel_reference}"
        )


class Analytics:
    def track(self, event: str, data: dict[str, str]) -> None:
        print(f"Tracking {event}: {data}")


def create_itinerary(request: TripRequest) -> Itinerary:
    return Itinerary(
        traveler=request.traveler,
        destination=request.destination,
        flight_id=request.flight_id,
        hotel_id=request.hotel_id,
    )


def check_visa(traveler_country: Country, destination_country: Country) -> None:
    print(f"Checking visa from {traveler_country.code} to {destination_country.code}")


def ensure_traveler_can_enter_destination(itinerary: Itinerary) -> None:
    if itinerary.requires_visa():
        check_visa(
            itinerary.traveler.passport_country,
            itinerary.destination.country,
        )


def reserve_itinerary(
    itinerary: Itinerary,
    flight_api: FlightAPI,
    hotel_api: HotelAPI,
) -> tuple[str, str]:
    flight_ref = flight_api.reserve(itinerary.flight_id)
    hotel_ref = hotel_api.reserve(itinerary.hotel_id)

    return flight_ref, hotel_ref


def create_invoice(booking: Booking) -> Invoice:
    return Invoice(booking_id=booking.id, total=Decimal("1299.00"))


def send_booking_confirmation(
    email: EmailSender,
    booking: Booking,
    invoice: Invoice,
) -> None:
    email.send_confirmation(
        recipient=booking.traveler.email,
        booking_id=booking.id,
        invoice_total=invoice.total,
        hotel_reference=booking.hotel_reference,
    )


def track_booking(analytics: Analytics, booking: Booking) -> None:
    analytics.track(
        "trip_booked",
        {
            "booking_id": booking.id,
            "destination": booking.destination.country.code,
            "traveler_country": booking.traveler.passport_country.code,
            "hotel_ref": booking.hotel_reference,
        },
    )


def book_trip(
    request: TripRequest,
    flight_api: FlightAPI,
    hotel_api: HotelAPI,
    db: BookingRepository,
    email: EmailSender,
    analytics: Analytics,
) -> Booking:
    itinerary = create_itinerary(request)

    ensure_traveler_can_enter_destination(itinerary)

    flight_ref, hotel_ref = reserve_itinerary(itinerary, flight_api, hotel_api)

    booking = db.save(
        itinerary=itinerary,
        flight_reference=flight_ref,
        hotel_reference=hotel_ref,
    )

    invoice = create_invoice(booking)

    send_booking_confirmation(email, booking, invoice)

    track_booking(analytics, booking)

    return booking


def main() -> None:
    request = TripRequest(
        traveler=Traveler(
            name="Ada Lovelace",
            email="ada@example.com",
            passport_country=Country("GB"),
        ),
        destination=Destination(country=Country("NL"), city="Amsterdam"),
        flight_id="KL100",
        hotel_id="HOTEL42",
    )

    booking = book_trip(
        request=request,
        flight_api=RealFlightAPI(),
        hotel_api=RealHotelAPI(),
        db=BookingRepository(),
        email=EmailSender(),
        analytics=Analytics(),
    )

    print(booking)


if __name__ == "__main__":
    main()
