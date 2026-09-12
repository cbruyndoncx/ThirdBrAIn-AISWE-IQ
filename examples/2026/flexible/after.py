from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class FlightStatus(StrEnum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"


class SeatType(StrEnum):
    STANDARD = "standard"
    EXTRA_LEGROOM = "extra_legroom"


@dataclass(frozen=True)
class Money:
    amount: Decimal

    def __post_init__(self) -> None:
        if self.amount < Decimal("0"):
            raise ValueError("Money cannot be negative")

    def discounted(self, percentage: Decimal) -> "Money":
        return Money(self.amount * (Decimal("1") - percentage))


@dataclass(frozen=True)
class Passenger:
    name: str
    has_loyalty: bool = False


@dataclass(frozen=True)
class Flight:
    number: str
    price: Money
    status: FlightStatus

    def ensure_bookable(self) -> None:
        if self.status is FlightStatus.CANCELLED:
            raise ValueError("Flight cancelled")


@dataclass(frozen=True)
class BookingRequest:
    passenger: Passenger
    flight: Flight
    seat: SeatType = SeatType.STANDARD


class BookingInput(BaseModel):
    passenger_name: str
    flight_number: str
    price: Decimal = Field(gt=0)
    status: FlightStatus
    loyalty: bool = False
    seat: SeatType = SeatType.STANDARD

    def to_domain(self) -> BookingRequest:
        return BookingRequest(
            passenger=Passenger(
                name=self.passenger_name,
                has_loyalty=self.loyalty,
            ),
            flight=Flight(
                number=self.flight_number,
                price=Money(self.price),
                status=self.status,
            ),
            seat=self.seat,
        )


def create_booking(request: BookingRequest) -> None:
    request.flight.ensure_bookable()

    discount = Decimal("0.10") if request.passenger.has_loyalty else Decimal("0")
    total = request.flight.price.discounted(discount)

    print(
        f"Booked {request.flight.number} "
        f"for {request.passenger.name} "
        f"at €{total.amount} "
        f"in seat {request.seat.value}"
    )


def main() -> None:
    raw_data = {
        "passenger_name": "Ada",
        "flight_number": "AC123",
        "price": "250.00",
        "status": "scheduled",
        "loyalty": True,
        "seat": "extra_legroom",
    }

    booking = BookingInput.model_validate(raw_data).to_domain()
    create_booking(booking)


if __name__ == "__main__":
    main()
