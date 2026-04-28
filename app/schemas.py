from pydantic import BaseModel, Field


class GeoPoint(BaseModel):
    type: str = "Point"
    coordinates: list[float]  # [longitude, latitude]


class LocationInput(BaseModel):
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    radius_meters: int = Field(default=5000, ge=100, le=50000)
    service_type: str | None = None


class ProviderSummary(BaseModel):
    id: str
    name: str
    service_type: str
    description: str | None
    address: str | None
    area: str | None
    distance_meters: float | None
    trust_score: float
    community_photos_count: int
    confirmations_count: int
    has_trust_badge: bool
    years_in_business: int | None
    last_verified: str | None  # ISO date
    opening_hours: list[str] = []
    services_offered: list[str] = []
    phone: str | None = None
    location: GeoPoint


class ProviderDetail(ProviderSummary):
    location: GeoPoint
    photo_urls: list[str] = []
