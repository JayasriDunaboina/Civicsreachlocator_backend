# backend/scripts/seed.py

import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "civicreach")

# ============================================
# SAMPLE DATA FOR CIVIC REACH LOCATOR
# ============================================

# 1. MUNICIPALITIES / CITIES
sample_providers = [
    {
       {
  "_id": {
    "$oid": "69843562b605479aad506601"
  },
  "name": "Ramesh Tailor Shop",
  "service_type": "tailor",
  "description": "Expert in alterations and custom stitching.",
  "address": "Main Bazaar, Narasapuram",
  "phone": "+91-9876543210",
  "location": {
    "type": "Point",
    "coordinates": [
      81.684,
      16.436
    ]
  },
  "community_photos_count": 3,
  "confirmations_count": 5,
  "photo_urls": [
    "https://www.google.com/search?q=tailors+images&oq=tailors+images&gs_lcrp=EgZjaHJvbWUyCQgAEEUYORiABDIICAEQABgWGB4yCAgCEAAYFhgeMggIAxAAGBYYHjIICAQQABgWGB4yCAgFEAAYFhgeMggIBhAAGBYYHjIICAcQABgWGB4yCAgIEAAYFhgeMggICRAAGBYYHtIBCDU3MTFqMGo3qAIIsAIB8QUBRy3qDOQrKw&sourceid=chrome&ie=UTF-8"
  ]
}
    {
        "name": "Sita Electrical Works",
        "service_type": "electrician",
        "description": "House wiring, appliance repair, and installation.",
        "address": "Market Road, Narasapuram",
        "phone": "+91-9123456780",
        "location": {"type": "Point", "coordinates": [81.682, 16.435]},
        "community_photos_count": 2,
        "confirmations_count": 4,
        "photo_urls": ["https://example.com/photos/electrician1.jpg"],
        "created_at": datetime.now()
    },
    {
    "name": "Lakshmi Plumbing Works",
    "service_type": "plumber",
    "description": "Pipe repairs, leak fixing, and bathroom fittings.",
    "address": "Temple Street, Narasapuram",
    "phone": "+91-9000000001",
    "location": {
      "type": "Point",
      "coordinates": [81.685, 16.434]
    },
    "community_photos_count": 3,
    "confirmations_count": 6,
    "photo_urls": ["https://example.com/photos/plumber2.jpg"],
    "created_at": { "$date": "2026-03-25T12:00:00Z" }
  },
  {
  "_id": {
    "$oid": "69843562b605479aad506602"
  },
  "name": "Sita Electrical Works",
  "service_type": "electrician",
  "description": "House wiring, appliance repair, and installation.",
  "address": "Market Road, Narasapuram",
  "phone": "+91-9123456780",
  "location": {
    "type": "Point",
    "coordinates": [
      81.682,
      16.435
    ]
  },
  "community_photos_count": 2,
  "confirmations_count": 4,
  "photo_urls": [
    "https://example.com/photos/electrician1.jpg"
  ]
},
{
  "_id": {
    "$oid": "69843562b605479aad506603"
  },
  "name": "Lakshmi Cobbler",
  "service_type": "cobbler",
  "description": "Shoe repair and polishing services.",
  "address": "Bus Stand, Narasapuram",
  "phone": "+91-9988776655",
  "location": {
    "type": "Point",
    "coordinates": [
      81.681,
      16.437
    ]
  },
  "community_photos_count": 1,
  "confirmations_count": 2,
  "photo_urls": [
    "https://example.com/photos/cobbler1.jpg"
  ]
}
  {
    "name": "Narasapuram Sanitation Services",
    "service_type": "cleaning",
    "description": "Garbage clearing and drainage cleaning services.",
    "address": "Municipal Yard, Narasapuram",
    "phone": "+91-9000000002",
    "location": {
      "type": "Point",
      "coordinates": [81.686, 16.433]
    },
    "community_photos_count": 5,
    "confirmations_count": 10,
    "photo_urls": ["https://example.com/photos/sanitation.jpg"],
    "created_at": { "$date": "2026-03-25T12:00:00Z" }
  },
  {
    "name": "Sri Sai Water Supply",
    "service_type": "water_supply",
    "description": "Drinking water tanker and emergency water supply.",
    "address": "Old Bus Stand Road, Narasapuram",
    "phone": "+91-9000000003",
    "location": {
      "type": "Point",
      "coordinates": [81.687, 16.432]
    },
    "community_photos_count": 2,
    "confirmations_count": 7,
    "photo_urls": ["https://example.com/photos/water.jpg"],
    "created_at": { "$date": "2026-03-25T12:00:00Z" }
  },
  {
    "name": "Street Light Repair Team",
    "service_type": "electric_maintenance",
    "description": "Street light installation and repair services.",
    "address": "Electric Office, Narasapuram",
    "phone": "+91-9000000004",
    "location": {
      "type": "Point",
      "coordinates": [81.688, 16.431]
    },
    "community_photos_count": 4,
    "confirmations_count": 9,
    "photo_urls": ["https://example.com/photos/streetlight.jpg"],
    "created_at": { "$date": "2026-03-25T12:00:00Z" }
  }

]
def seed():
    """Seed all collections with sample data"""
    
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    
    # Collections
    municipalities = db.municipalities
    wards = db.wards
    departments = db.departments
    officials = db.officials
    users = db.users
    feedback = db.feedback
    interactions = db.interactions
    qr_scans = db.qr_scans
    notifications = db.notifications
    providers = db.providers  # Legacy/alternative collection
    
    # Create indexes
    print("Creating indexes...")
    wards.create_index([("location", "2dsphere")])
    officials.create_index([("phone", 1)], unique=True)
    users.create_index([("phone", 1)], unique=True)
    users.create_index([("email", 1)], unique=True, sparse=True)
    feedback.create_index([("ward_id", 1), ("status", 1)])
    interactions.create_index([("official_id", 1), ("initiated_at", -1)])
    qr_scans.create_index([("scanned_at", -1)])
    
    # Clear existing data (optional - comment out for production)
    print("Clearing existing data...")
    municipalities.delete_many({})
    wards.delete_many({})
    departments.delete_many({})
    officials.delete_many({})
    users.delete_many({})
    feedback.delete_many({})
    interactions.delete_many({})
    qr_scans.delete_many({})
    notifications.delete_many({})
    providers.delete_many({})
    
    # Insert sample data
    print("Seeding municipalities...")
    municipalities.insert_many(sample_municipalities)
    
    print("Seeding wards...")
    wards.insert_many(sample_wards)
    
    print("Seeding departments...")
    departments.insert_many(sample_departments)
    
    print("Seeding officials...")
    officials.insert_many(sample_officials)
    
    print("Seeding users...")
    users.insert_many(sample_users)
    
    print("Seeding feedback...")
    feedback.insert_many(sample_feedback)
    
    print("Seeding interactions...")
    interactions.insert_many(sample_interactions)
    
    print("Seeding QR scans...")
    qr_scans.insert_many(sample_qr_scans)
    
    print("Seeding notifications...")
    notifications.insert_many(sample_notifications)
    
    # Legacy providers collection (from original requirement)
    print("Seeding providers collection...")
    sample_providers = [
        {
            "name": "Ramesh Tailor Shop",
            "service_type": "tailor",
            "description": "Expert in alterations and custom stitching.",
            "address": "Main Bazaar, Narasapuram",
            "phone": "+91-9876543210",
            "location": {"type": "Point", "coordinates": [81.684, 16.436]},
            "community_photos_count": 3,
            "confirmations_count": 5,
            "photo_urls": ["https://example.com/photos/tailor1.jpg"],
            "created_at": datetime.now()
        },
        {
            "name": "Sita Electrical Works",
            "service_type": "electrician",
            "description": "House wiring, appliance repair, and installation.",
            "address": "Market Road, Narasapuram",
            "phone": "+91-9123456780",
            "location": {"type": "Point", "coordinates": [81.682, 16.435]},
            "community_photos_count": 2,
            "confirmations_count": 4,
            "photo_urls": ["https://example.com/photos/electrician1.jpg"],
            "created_at": datetime.now()
        },
        {
            "name": "Lakshmi Cobbler",
            "service_type": "cobbler",
            "description": "Shoe repair and polishing services.",
            "address": "Bus Stand, Narasapuram",
            "phone": "+91-9988776655",
            "location": {"type": "Point", "coordinates": [81.681, 16.437]},
            "community_photos_count": 1,
            "confirmations_count": 2,
            "photo_urls": ["https://example.com/photos/cobbler1.jpg"],
            "created_at": datetime.now()
        },
        {
            "name": "Krishna Hardware Store",
            "service_type": "hardware",
            "description": "All types of hardware tools, paint, and electrical supplies.",
            "address": "Station Road, Narasapuram",
            "phone": "+91-9345678901",
            "location": {"type": "Point", "coordinates": [81.683, 16.438]},
            "community_photos_count": 4,
            "confirmations_count": 8,
            "photo_urls": ["https://example.com/photos/hardware1.jpg"],
            "created_at": datetime.now()
        },
        {
            "name": "Sai Plumbing Services",
            "service_type": "plumber",
            "description": "All plumbing services, bathroom fittings, and pipe repairs.",
            "address": "Temple Street, Narasapuram",
            "phone": "+91-9456789012",
            "location": {"type": "Point", "coordinates": [81.685, 16.434]},
            "community_photos_count": 2,
            "confirmations_count": 6,
            "photo_urls": ["https://example.com/photos/plumber1.jpg"],
            "created_at": datetime.now()
        }
        {
  "_id": {
    "$oid": "67c8a1b2c3d4e5f6a7b8c9d2"
  },
  "ward_number": "Ward 1",
  "ward_name": "Gollapalem",
  "municipality_id": {
    "$oid": "67c8a1b2c3d4e5f6a7b8c9d0"
  },
  "population": 3540,
  "voter_count": 2850,
  "area_sqkm": 1.2,
  "qr_code": "WARD_1_NARASAPURAM_2024",
  "is_active": true,
  "created_at": {
    "$date": "2025-01-15T10:30:00.000Z"
  }
}

  {
    "ward_number": "Ward 1",
    "ward_name": "Gollapalem",
    "municipality_id": { "$oid": "67c8a1b2c3d4e5f6a7b8c9d2" },
    "population": 3540,
    "qr_code": "WARD_1_NARASAPURAM_2024",
    "is_active": true,
    "created_at": { "$date": "2025-01-15T10:30:00Z" }
  }

    ]
    providers.insert_many(sample_providers)
    
    # Print summary
    print("\n" + "="*50)
    print("SEEDING COMPLETED SUCCESSFULLY!")
    print("="*50)
    print(f"Municipalities: {len(sample_municipalities)}")
    print(f"Wards: {len(sample_wards)}")
    print(f"Departments: {len(sample_departments)}")
    print(f"Officials: {len(sample_officials)}")
    print(f"Users: {len(sample_users)}")
    print(f"Feedback: {len(sample_feedback)}")
    print(f"Interactions: {len(sample_interactions)}")
    print(f"QR Scans: {len(sample_qr_scans)}")
    print(f"Notifications: {len(sample_notifications)}")
    print(f"Providers: {len(sample_providers)}")
    print("="*50)
    
    # Example usage tips
    print("\n📌 SAMPLE QUERIES TO TEST:")
    print("-"*40)
    print("1. Get all wards: db.wards.find()")
    print("2. Get officials by ward: db.officials.find({ward_id: ObjectId('...')})")
    print("3. Get pending feedback: db.feedback.find({status: 'pending'})")
    print("4. Get interactions by official: db.interactions.find({official_id: ObjectId('...')})")
    print("5. Get QR scan count: db.qr_scans.countDocuments()")


# ============================================
# RUN SEED
# ============================================

if __name__ == "__main__":
    seed()