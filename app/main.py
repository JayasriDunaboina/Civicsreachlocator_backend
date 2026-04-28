import os
from contextlib import asynccontextmanager
from math import atan2, cos, radians, sin, sqrt

from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import settings
from app.database import close_db, get_db
from app.schemas import LocationInput, ProviderDetail, ProviderSummary
from app.trust import compute_trust_score, has_trust_badge


# ------------------ APP LIFECYCLE ------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        get_db()
    except Exception as e:
        import traceback
        print("STARTUP FAILED:", e, flush=True)
        traceback.print_exc()
        raise
    yield
    close_db()


app = FastAPI(
    title="CivicReach Locator API",
    description="Community-verified hyperlocal service discovery",
    version="1.0.0",
    lifespan=lifespan,
)

# ------------------ CORS ------------------
# In production set ALLOWED_ORIGIN to your Vercel URL, e.g.:
#   https://civic-reach.vercel.app
# In local dev leave it unset → allow all origins.

_allowed_origin = os.getenv("ALLOWED_ORIGIN", "")
_origins = [_allowed_origin] if _allowed_origin else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ PASSWORD CONFIG ------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ------------------ AUTH MODELS ------------------

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# ------------------ AUTH HELPERS ------------------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ------------------ ROOT ------------------

@app.get("/")
def root():
    return {"message": "CivicReach Locator API is running 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ------------------ AUTH ROUTES ------------------

@app.post("/signup")
def signup(user: SignupRequest):
    db = get_db()
    users = db["users"]

    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    users.insert_one({
        "name": user.name,
        "email": user.email,
        "password": hash_password(user.password),
    })

    return {"email": user.email, "token": "dummy-token"}


@app.post("/login")
def login(user: LoginRequest):
    db = get_db()
    users = db["users"]

    db_user = users.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect password")

    return {"email": db_user["email"], "token": "dummy-token"}

# ------------------ DISCOVER ------------------

@app.post("/discover", response_model=list[ProviderSummary])
def discover_nearby(body: LocationInput):
    """
    Geospatial search: find providers within radius of user location.
    Results sorted by distance; trust score and badge included.
    """
    db = get_db()
    coll = db["providers"]

    radius = min(body.radius_meters, settings.max_radius_meters)
    query: dict = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [body.longitude, body.latitude],
                },
                "$maxDistance": radius,
            }
        }
    }
    if body.service_type:
        query["service_type"] = body.service_type.lower()

    cursor = coll.find(query).limit(50)
    results = []

    for doc in cursor:
        photos = doc.get("community_photos_count", 0)
        confirms = doc.get("confirmations_count", 0)
        trust_score = compute_trust_score(photos, confirms)

        loc = doc.get("location", {})
        coords = loc.get("coordinates", [0, 0])

        # Haversine distance
        lon1, lat1 = radians(body.longitude), radians(body.latitude)
        lon2, lat2 = radians(coords[0]), radians(coords[1])
        dlon, dlat = lon2 - lon1, lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        distance_meters = 6_371_000 * 2 * atan2(sqrt(a), sqrt(1 - a))

        last_verified = doc.get("last_verified")
        if last_verified and hasattr(last_verified, "isoformat"):
            last_verified = last_verified.isoformat()[:10]
        elif last_verified:
            last_verified = str(last_verified)[:10]

        results.append(
            ProviderSummary(
                id=str(doc["_id"]),
                name=doc.get("name", ""),
                service_type=doc.get("service_type", ""),
                description=doc.get("description"),
                address=doc.get("address"),
                area=doc.get("area"),
                distance_meters=round(distance_meters, 0),
                trust_score=trust_score,
                community_photos_count=photos,
                confirmations_count=confirms,
                has_trust_badge=has_trust_badge(trust_score),
                years_in_business=doc.get("years_in_business"),
                last_verified=last_verified or doc.get("last_verified"),
                opening_hours=doc.get("opening_hours", []),
                services_offered=doc.get("services_offered", []),
                phone=doc.get("phone"),
                location=loc,
            )
        )

    return results

# ------------------ PROVIDER DETAIL ------------------

@app.get("/providers/{provider_id}", response_model=ProviderDetail)
def get_provider(provider_id: str):
    db = get_db()
    coll = db["providers"]

    try:
        doc = coll.find_one({"_id": ObjectId(provider_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid provider ID")

    if not doc:
        raise HTTPException(status_code=404, detail="Provider not found")

    photos = doc.get("community_photos_count", 0)
    confirms = doc.get("confirmations_count", 0)
    trust_score = compute_trust_score(photos, confirms)

    loc = doc.get("location", {})

    last_verified = doc.get("last_verified")
    if last_verified and hasattr(last_verified, "isoformat"):
        last_verified = last_verified.isoformat()[:10]
    elif last_verified is None:
        last_verified = None
    else:
        last_verified = str(last_verified)[:10]

    return ProviderDetail(
        id=str(doc["_id"]),
        name=doc.get("name", ""),
        service_type=doc.get("service_type", ""),
        description=doc.get("description"),
        address=doc.get("address"),
        area=doc.get("area"),
        distance_meters=None,
        trust_score=trust_score,
        community_photos_count=photos,
        confirmations_count=confirms,
        has_trust_badge=has_trust_badge(trust_score),
        years_in_business=doc.get("years_in_business"),
        last_verified=last_verified,
        opening_hours=doc.get("opening_hours", []),
        services_offered=doc.get("services_offered", []),
        phone=doc.get("phone"),
        location=loc,
        photo_urls=doc.get("photo_urls", []),
    )

# ------------------ SERVICE TYPES ------------------

@app.get("/service-types")
def list_service_types():
    db = get_db()
    types = db["providers"].distinct("service_type")
    return {"service_types": [t for t in types if t]}
