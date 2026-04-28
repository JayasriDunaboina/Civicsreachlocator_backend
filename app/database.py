from pymongo import MongoClient
from pymongo.collection import Collection

from app.config import settings

client: MongoClient | None = None
_db = None


def get_db():
    global client, _db
    if client is None:
        client = MongoClient(settings.mongodb_uri)
        _db = client[settings.db_name]
        _ensure_indexes(_db)
    return _db


def _ensure_indexes(db):
    """Create 2dsphere index for geospatial queries and supporting indexes."""
    providers: Collection = db["providers"]
    providers.create_index([("location", "2dsphere")])
    providers.create_index([("service_type", 1)])
    providers.create_index([("trust_score", -1)])


def close_db():
    global client
    if client:
        client.close()
        client = None
