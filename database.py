from urllib.parse import quote_plus, urlparse, urlunparse
from pymongo import MongoClient
from pymongo.collection import Collection

from app.config import settings

client: MongoClient | None = None
_db = None


def _encode_mongo_uri(uri: str) -> str:
    try:
        parsed = urlparse(uri)
        if parsed.username and parsed.password:
            encoded_user = quote_plus(parsed.username)
            encoded_pass = quote_plus(parsed.password)
            host = parsed.hostname
            port = f":{parsed.port}" if parsed.port else ""
            netloc = f"{encoded_user}:{encoded_pass}@{host}{port}"
            fixed = parsed._replace(netloc=netloc)
            return urlunparse(fixed)
    except Exception:
        pass
    return uri


def get_db():
    global client, _db
    if client is None:
        safe_uri = _encode_mongo_uri(settings.mongodb_uri)
        client = MongoClient(safe_uri)
        _db = client[settings.db_name]
        _ensure_indexes(_db)
    return _db


def _ensure_indexes(db):
    providers: Collection = db["providers"]
    providers.create_index([("location", "2dsphere")])
    providers.create_index([("service_type", 1)])
    providers.create_index([("trust_score", -1)])


def close_db():
    global client
    if client:
        client.close()
        client = None
