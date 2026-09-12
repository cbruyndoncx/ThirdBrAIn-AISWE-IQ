from decimal import Decimal

from domain import (
    Booking,
    Country,
    Destination,
    Invoice,
    Itinerary,
    Traveler,
    TripRequest,
)


class FlightAPI:
    def reserve(self, flight_id: str, traveler_country: Country) -> str:
        return f"flight-ref-{flight_id}"


class HotelAPI:
    def reserve(self, hotel_id: str, traveler_country: Country) -> str:
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


def create_invoice(booking: Booking) -> Invoice:
    return Invoice(booking_id=booking.id, total=Decimal("1299.00"))


def check_visa(traveler_country: Country, destination_country: Country) -> None:
    print(f"Checking visa from {traveler_country.code} to {destination_country.code}")


def book_trip(
    request: TripRequest,
    flight_api: FlightAPI,
    hotel_api: HotelAPI,
    db: BookingRepository,
    email: EmailSender,
    analytics: Analytics,
) -> Booking:
    itinerary = Itinerary(
        traveler=request.traveler,
        destination=request.destination,
        flight_id=request.flight_id,
        hotel_id=request.hotel_id,
    )

    flight_ref = flight_api.reserve(
        request.flight_id,
        request.traveler.passport_country,
    )

    hotel_ref = hotel_api.reserve(
        request.hotel_id,
        request.traveler.passport_country,
    )

    booking = db.save(
        itinerary=itinerary,
        flight_reference=flight_ref,
        hotel_reference=hotel_ref,
    )

    if request.traveler.passport_country != request.destination.country:
        check_visa(
            request.traveler.passport_country,
            request.destination.country,
        )

    invoice = create_invoice(booking)

    email.send_confirmation(
        request.traveler.email,
        booking.id,
        invoice.total,
        hotel_ref,
    )

    analytics.track(
        "trip_booked",
        {
            "booking_id": booking.id,
            "destination": request.destination.country.code,
            "traveler_country": request.traveler.passport_country.code,
            "hotel_ref": hotel_ref,
        },
    )

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
        flight_api=FlightAPI(),
        hotel_api=HotelAPI(),
        db=BookingRepository(),
        email=EmailSender(),
        analytics=Analytics(),
    )

    print(booking)


if __name__ == "__main__":
    main()
