from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Country:
    code: str


@dataclass(frozen=True)
class Traveler:
    name: str
    email: str
    passport_country: Country

    def needs_visa_for(self, destination: "Destination") -> bool:
        return self.passport_country != destination.country


@dataclass(frozen=True)
class Destination:
    country: Country
    city: str


@dataclass(frozen=True)
class TripRequest:
    traveler: Traveler
    destination: Destination
    flight_id: str
    hotel_id: str


@dataclass(frozen=True)
class Itinerary:
    traveler: Traveler
    destination: Destination
    flight_id: str
    hotel_id: str

    def requires_visa(self) -> bool:
        return self.traveler.needs_visa_for(self.destination)


@dataclass(frozen=True)
class Booking:
    id: str
    itinerary: Itinerary
    flight_reference: str
    hotel_reference: str

    @property
    def traveler(self) -> Traveler:
        return self.itinerary.traveler

    @property
    def destination(self) -> Destination:
        return self.itinerary.destination


@dataclass(frozen=True)
class Invoice:
    booking_id: str
    total: Decimal
