from fastapi import FastAPI, APIRouter, HTTPException, Depends, Response, Cookie, Header
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import Optional, List
import uuid
from datetime import datetime, timezone

from models import (
    User, UserCreate, CarrierProfile, CarrierKYCSubmit,
    Delivery, DeliveryCreate, LocationPing, Message, MessageCreate,
    Rating, RatingCreate, Dispute, DisputeCreate, ConfigItem, OTPVerify
)
from auth import (
    hash_password, verify_password, create_session, get_current_user_dependency,
    process_google_oauth_session, hash_otp, verify_otp
)
from utils import calculate_distance_km, calculate_delivery_price, generate_4_digit_otp


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Create the auth dependency with database access
get_current_user = get_current_user_dependency(db)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# AUTH ENDPOINTS
# ============================================

@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    """Register with email and password"""
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = await hash_password(user_data.password)
    
    # Create user
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password_hash": password_hash,
        "role": "sender",
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.users.insert_one(user_doc)
    
    # Create session
    session_token = await create_session(db, user_id)
    
    # Remove password hash from response
    user_doc.pop("password_hash")
    user_doc.pop("_id", None)
    
    return {
        "user": user_doc,
        "session_token": session_token
    }


@api_router.post("/auth/login")
async def login(email: str, password: str):
    """Login with email and password"""
    # Find user
    user_doc = await db.users.find_one({"email": email}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not await verify_password(password, user_doc["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user_doc.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    # Create session
    session_token = await create_session(db, user_doc["user_id"])
    
    # Remove password hash from response
    user_doc.pop("password_hash")
    
    return {
        "user": user_doc,
        "session_token": session_token
    }


@api_router.post("/auth/google/callback")
async def google_auth_callback(session_id: str, response: Response):
    """
    Handle Google OAuth callback from Emergent Auth
    REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    """
    # Exchange session_id for user data
    oauth_data = await process_google_oauth_session(session_id)
    
    # Check if user exists
    user_doc = await db.users.find_one({"email": oauth_data["email"]}, {"_id": 0})
    
    if user_doc:
        # Update user data if needed
        await db.users.update_one(
            {"email": oauth_data["email"]},
            {"$set": {
                "name": oauth_data["name"],
                "picture": oauth_data.get("picture")
            }}
        )
        user_id = user_doc["user_id"]
    else:
        # Create new user
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        user_doc = {
            "user_id": user_id,
            "email": oauth_data["email"],
            "name": oauth_data["name"],
            "picture": oauth_data.get("picture"),
            "role": "sender",
            "is_active": True,
            "created_at": datetime.now(timezone.utc)
        }
        await db.users.insert_one(user_doc)
    
    # Store Emergent's session token
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": oauth_data["session_token"],
        "expires_at": datetime.now(timezone.utc).replace(day=datetime.now(timezone.utc).day + 7),
        "created_at": datetime.now(timezone.utc)
    })
    
    # Set httpOnly cookie
    response.set_cookie(
        key="session_token",
        value=oauth_data["session_token"],
        httponly=True,
        secure=True,
        samesite="none",
        path="/"
    )
    
    # Get fresh user data
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    user_doc.pop("password_hash", None)
    
    return {
        "user": user_doc,
        "session_token": oauth_data["session_token"]
    }


@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return current_user


@api_router.post("/auth/logout")
async def logout(
    response: Response,
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    """Logout and delete session"""
    token = session_token
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
    
    if token:
        await db.user_sessions.delete_one({"session_token": token})
    
    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}


# ============================================
# USER & CARRIER PROFILE ENDPOINTS
# ============================================

@api_router.get("/users/{user_id}")
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user by ID"""
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0, "password_hash": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return user_doc


@api_router.put("/users/role")
async def update_role(role: str, current_user: dict = Depends(get_current_user)):
    """Switch between sender and carrier role"""
    if role not in ["sender", "carrier"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    await db.users.update_one(
        {"user_id": current_user["user_id"]},
        {"$set": {"role": role}}
    )
    
    return {"message": "Role updated", "role": role}


@api_router.post("/carrier/kyc")
async def submit_kyc(kyc_data: CarrierKYCSubmit, current_user: dict = Depends(get_current_user)):
    """Submit KYC for carrier verification"""
    # Check if profile exists
    existing = await db.carrier_profiles.find_one({"user_id": current_user["user_id"]}, {"_id": 0})
    
    profile_doc = {
        "user_id": current_user["user_id"],
        "phone_whatsapp": kyc_data.phone_whatsapp,
        "vehicle_type": kyc_data.vehicle_type,
        "aadhaar_photo_base64": kyc_data.aadhaar_photo_base64,
        "selfie_photo_base64": kyc_data.selfie_photo_base64,
        "verification_status": "pending",
        "is_online": False,
        "created_at": datetime.now(timezone.utc)
    }
    
    if existing:
        await db.carrier_profiles.update_one(
            {"user_id": current_user["user_id"]},
            {"$set": profile_doc}
        )
    else:
        await db.carrier_profiles.insert_one(profile_doc)
    
    return {"message": "KYC submitted for review", "status": "pending"}


@api_router.get("/carrier/profile")
async def get_carrier_profile(current_user: dict = Depends(get_current_user)):
    """Get carrier profile"""
    profile = await db.carrier_profiles.find_one({"user_id": current_user["user_id"]}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Carrier profile not found")
    return profile


@api_router.put("/carrier/online")
async def toggle_online(
    is_online: bool,
    destination_lat: Optional[float] = None,
    destination_lng: Optional[float] = None,
    current_user: dict = Depends(get_current_user)
):
    """Toggle carrier online status"""
    profile = await db.carrier_profiles.find_one({"user_id": current_user["user_id"]}, {"_id": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Carrier profile not found")
    
    if profile["verification_status"] != "approved":
        raise HTTPException(status_code=403, detail="KYC not approved")
    
    update_data = {"is_online": is_online}
    if is_online and destination_lat and destination_lng:
        update_data["current_destination_lat"] = destination_lat
        update_data["current_destination_lng"] = destination_lng
    
    await db.carrier_profiles.update_one(
        {"user_id": current_user["user_id"]},
        {"$set": update_data}
    )
    
    return {"message": f"Carrier is now {'online' if is_online else 'offline'}", "is_online": is_online}


# ============================================
# DELIVERY ENDPOINTS
# ============================================

@api_router.post("/deliveries")
async def create_delivery(delivery_data: DeliveryCreate, current_user: dict = Depends(get_current_user)):
    """Create a new delivery request"""
    # Calculate distance
    distance_km = calculate_distance_km(
        delivery_data.pickup_lat, delivery_data.pickup_lng,
        delivery_data.dropoff_lat, delivery_data.dropoff_lng
    )
    
    # Get pricing config
    config_docs = await db.config.find({}, {"_id": 0}).to_list(100)
    config = {doc["key"]: doc["value"] for doc in config_docs}
    
    # Calculate price
    price_rs = await calculate_delivery_price(
        distance_km,
        delivery_data.weight_kg,
        delivery_data.timing_preference,
        config
    )
    
    # Create delivery
    delivery_id = f"delivery_{uuid.uuid4().hex[:12]}"
    delivery_doc = {
        "delivery_id": delivery_id,
        "sender_id": current_user["user_id"],
        "pickup_address": delivery_data.pickup_address,
        "pickup_lat": delivery_data.pickup_lat,
        "pickup_lng": delivery_data.pickup_lng,
        "dropoff_address": delivery_data.dropoff_address,
        "dropoff_lat": delivery_data.dropoff_lat,
        "dropoff_lng": delivery_data.dropoff_lng,
        "parcel_category": delivery_data.parcel_category,
        "weight_kg": delivery_data.weight_kg,
        "declared_value": delivery_data.declared_value,
        "parcel_photos_base64": delivery_data.parcel_photos_base64,
        "status": "posted",
        "price_rs": price_rs,
        "distance_km": distance_km,
        "timing_preference": delivery_data.timing_preference,
        "scheduled_time": delivery_data.scheduled_time,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.deliveries.insert_one(delivery_doc)
    delivery_doc.pop("_id")
    
    return delivery_doc


@api_router.get("/deliveries")
async def get_deliveries(
    status: Optional[str] = None,
    role: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get deliveries for current user"""
    query = {}
    
    if role == "sender":
        query["sender_id"] = current_user["user_id"]
    elif role == "carrier":
        query["carrier_id"] = current_user["user_id"]
    else:
        # Get all deliveries for user (as sender or carrier)
        query = {
            "$or": [
                {"sender_id": current_user["user_id"]},
                {"carrier_id": current_user["user_id"]}
            ]
        }
    
    if status:
        query["status"] = status
    
    deliveries = await db.deliveries.find(query, {"_id": 0}).to_list(1000)
    return deliveries


@api_router.get("/deliveries/nearby")
async def get_nearby_deliveries(
    lat: float,
    lng: float,
    max_distance_km: float = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get nearby delivery requests for carriers"""
    # Get carrier profile
    profile = await db.carrier_profiles.find_one({"user_id": current_user["user_id"]}, {"_id": 0})
    if not profile or profile["verification_status"] != "approved":
        raise HTTPException(status_code=403, detail="Not an approved carrier")
    
    # Get all posted deliveries
    deliveries = await db.deliveries.find({"status": "posted"}, {"_id": 0}).to_list(1000)
    
    # Filter by distance
    nearby = []
    for delivery in deliveries:
        distance = calculate_distance_km(lat, lng, delivery["pickup_lat"], delivery["pickup_lng"])
        if distance <= max_distance_km:
            delivery["distance_from_carrier"] = round(distance, 2)
            nearby.append(delivery)
    
    # Sort by distance
    nearby.sort(key=lambda x: x["distance_from_carrier"])
    
    return nearby


@api_router.get("/deliveries/{delivery_id}")
async def get_delivery(delivery_id: str):
    """Get delivery by ID (public for tracking)"""
    delivery = await db.deliveries.find_one({"delivery_id": delivery_id}, {"_id": 0})
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


@api_router.put("/deliveries/{delivery_id}/accept")
async def accept_delivery(delivery_id: str, current_user: dict = Depends(get_current_user)):
    """Carrier accepts a delivery request"""
    delivery = await db.deliveries.find_one({"delivery_id": delivery_id}, {"_id": 0})
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    if delivery["status"] != "posted":
        raise HTTPException(status_code=400, detail="Delivery already matched")
    
    # Generate OTPs
    pickup_otp = generate_4_digit_otp()
    delivery_otp = generate_4_digit_otp()
    
    # Hash OTPs
    pickup_otp_hash = await hash_otp(pickup_otp)
    delivery_otp_hash = await hash_otp(delivery_otp)
    
    # Update delivery
    await db.deliveries.update_one(
        {"delivery_id": delivery_id},
        {"$set": {
            "carrier_id": current_user["user_id"],
            "status": "matched",
            "matched_at": datetime.now(timezone.utc),
            "pickup_otp_hash": pickup_otp_hash,
            "delivery_otp_hash": delivery_otp_hash
        }}
    )
    
    return {
        "message": "Delivery accepted",
        "delivery_id": delivery_id,
        "pickup_otp": pickup_otp,
        "delivery_otp": delivery_otp
    }


@api_router.post("/deliveries/{delivery_id}/verify-otp")
async def verify_delivery_otp(delivery_id: str, otp_data: OTPVerify, current_user: dict = Depends(get_current_user)):
    """Verify OTP for pickup or delivery"""
    delivery = await db.deliveries.find_one({"delivery_id": delivery_id}, {"_id": 0})
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    # Determine which OTP to verify
    if otp_data.otp_type == "pickup":
        if delivery["status"] != "matched":
            raise HTTPException(status_code=400, detail="Invalid status for pickup")
        
        # Verify pickup OTP
        if not await verify_otp(otp_data.otp, delivery["pickup_otp_hash"]):
            raise HTTPException(status_code=401, detail="Invalid OTP")
        
        # Update status
        await db.deliveries.update_one(
            {"delivery_id": delivery_id},
            {"$set": {
                "status": "picked_up",
                "picked_up_at": datetime.now(timezone.utc)
            }}
        )
        
        return {"message": "Pickup confirmed", "status": "picked_up"}
    
    elif otp_data.otp_type == "delivery":
        if delivery["status"] != "picked_up":
            raise HTTPException(status_code=400, detail="Invalid status for delivery")
        
        # Verify delivery OTP
        if not await verify_otp(otp_data.otp, delivery["delivery_otp_hash"]):
            raise HTTPException(status_code=401, detail="Invalid OTP")
        
        # Update status
        await db.deliveries.update_one(
            {"delivery_id": delivery_id},
            {"$set": {
                "status": "delivered",
                "delivered_at": datetime.now(timezone.utc)
            }}
        )
        
        return {"message": "Delivery confirmed", "status": "delivered"}


@api_router.post("/deliveries/{delivery_id}/location")
async def update_location(delivery_id: str, lat: float, lng: float, current_user: dict = Depends(get_current_user)):
    """Update carrier location during delivery"""
    delivery = await db.deliveries.find_one({"delivery_id": delivery_id}, {"_id": 0})
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    if delivery["carrier_id"] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your delivery")
    
    # Store location ping
    await db.locations.insert_one({
        "delivery_id": delivery_id,
        "carrier_id": current_user["user_id"],
        "lat": lat,
        "lng": lng,
        "recorded_at": datetime.now(timezone.utc)
    })
    
    return {"message": "Location updated"}


@api_router.get("/deliveries/{delivery_id}/locations")
async def get_delivery_locations(delivery_id: str):
    """Get location history for a delivery (public for tracking)"""
    locations = await db.locations.find(
        {"delivery_id": delivery_id},
        {"_id": 0}
    ).sort("recorded_at", -1).limit(100).to_list(100)
    
    return locations


# ============================================
# CHAT ENDPOINTS
# ============================================

@api_router.post("/messages")
async def send_message(message_data: MessageCreate, current_user: dict = Depends(get_current_user)):
    """Send a message in delivery chat"""
    # Verify user is part of delivery
    delivery = await db.deliveries.find_one({"delivery_id": message_data.delivery_id}, {"_id": 0})
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    if current_user["user_id"] not in [delivery["sender_id"], delivery.get("carrier_id")]:
        raise HTTPException(status_code=403, detail="Not part of this delivery")
    
    # Create message
    message_id = f"msg_{uuid.uuid4().hex[:12]}"
    message_doc = {
        "message_id": message_id,
        "delivery_id": message_data.delivery_id,
        "sender_id": current_user["user_id"],
        "content": message_data.content,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.messages.insert_one(message_doc)
    message_doc.pop("_id")
    
    return message_doc


@api_router.get("/messages/{delivery_id}")
async def get_messages(delivery_id: str, current_user: dict = Depends(get_current_user)):
    """Get messages for a delivery"""
    # Verify user is part of delivery
    delivery = await db.deliveries.find_one({"delivery_id": delivery_id}, {"_id": 0})
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    if current_user["user_id"] not in [delivery["sender_id"], delivery.get("carrier_id")]:
        raise HTTPException(status_code=403, detail="Not part of this delivery")
    
    messages = await db.messages.find(
        {"delivery_id": delivery_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(1000)
    
    return messages


# ============================================
# ADMIN ENDPOINTS
# ============================================

@api_router.get("/admin/kyc/pending")
async def get_pending_kyc(current_user: dict = Depends(get_current_user)):
    """Get pending KYC submissions (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    profiles = await db.carrier_profiles.find(
        {"verification_status": "pending"},
        {"_id": 0}
    ).to_list(1000)
    
    return profiles


@api_router.put("/admin/kyc/{user_id}/approve")
async def approve_kyc(user_id: str, current_user: dict = Depends(get_current_user)):
    """Approve carrier KYC (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    await db.carrier_profiles.update_one(
        {"user_id": user_id},
        {"$set": {
            "verification_status": "approved",
            "approved_at": datetime.now(timezone.utc)
        }}
    )
    
    return {"message": "KYC approved"}


@api_router.put("/admin/kyc/{user_id}/reject")
async def reject_kyc(user_id: str, reason: str, current_user: dict = Depends(get_current_user)):
    """Reject carrier KYC (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    await db.carrier_profiles.update_one(
        {"user_id": user_id},
        {"$set": {
            "verification_status": "rejected",
            "rejection_reason": reason
        }}
    )
    
    return {"message": "KYC rejected"}


@api_router.get("/admin/config")
async def get_config(current_user: dict = Depends(get_current_user)):
    """Get pricing config (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    config = await db.config.find({}, {"_id": 0}).to_list(100)
    return config


@api_router.put("/admin/config")
async def update_config(key: str, value: float, current_user: dict = Depends(get_current_user)):
    """Update pricing config (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    await db.config.update_one(
        {"key": key},
        {"$set": {"value": value}},
        upsert=True
    )
    
    return {"message": "Config updated", "key": key, "value": value}


# ============================================
# HEALTH CHECK
# ============================================

@api_router.get("/")
async def root():
    return {"message": "DELIVERGE API", "version": "1.0.0"}


@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
