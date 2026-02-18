from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid


# User Models
class User(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    role: Literal["sender", "carrier", "admin"] = "sender"
    phone_whatsapp: Optional[str] = None
    is_active: bool = True
    created_at: datetime


class UserCreate(BaseModel):
    email: str
    password: str
    name: str


class UserSession(BaseModel):
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime


# Carrier Profile Models
class CarrierProfile(BaseModel):
    user_id: str
    phone_whatsapp: Optional[str] = None
    vehicle_type: Optional[Literal["bike", "car", "auto", "bus", "train", "walking"]] = None
    aadhaar_photo_base64: Optional[str] = None
    selfie_photo_base64: Optional[str] = None
    verification_status: Literal["pending", "approved", "rejected"] = "pending"
    rejection_reason: Optional[str] = None
    approved_at: Optional[datetime] = None
    is_online: bool = False
    current_destination_lat: Optional[float] = None
    current_destination_lng: Optional[float] = None
    created_at: datetime


class CarrierKYCSubmit(BaseModel):
    phone_whatsapp: str
    vehicle_type: Literal["bike", "car", "auto", "bus", "train", "walking"]
    aadhaar_photo_base64: str
    selfie_photo_base64: str


# Delivery Models
class Delivery(BaseModel):
    delivery_id: str
    sender_id: str
    carrier_id: Optional[str] = None
    pickup_address: str
    pickup_lat: float
    pickup_lng: float
    dropoff_address: str
    dropoff_lat: float
    dropoff_lng: float
    parcel_category: Literal["documents", "clothing", "food", "electronics", "other"]
    weight_kg: float
    declared_value: float
    parcel_photos_base64: list[str] = []
    status: Literal["posted", "matched", "picked_up", "delivered", "cancelled"] = "posted"
    pickup_otp_hash: Optional[str] = None
    delivery_otp_hash: Optional[str] = None
    pickup_photo_base64: Optional[str] = None
    delivery_photo_base64: Optional[str] = None
    price_rs: float
    distance_km: float
    timing_preference: Literal["asap", "within_2h", "within_4h", "scheduled"]
    scheduled_time: Optional[datetime] = None
    created_at: datetime
    matched_at: Optional[datetime] = None
    picked_up_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None


class DeliveryCreate(BaseModel):
    pickup_address: str
    pickup_lat: float
    pickup_lng: float
    dropoff_address: str
    dropoff_lat: float
    dropoff_lng: float
    parcel_category: Literal["documents", "clothing", "food", "electronics", "other"]
    weight_kg: float
    declared_value: float
    parcel_photos_base64: list[str]
    timing_preference: Literal["asap", "within_2h", "within_4h", "scheduled"]
    scheduled_time: Optional[datetime] = None


# Location tracking
class LocationPing(BaseModel):
    delivery_id: str
    carrier_id: str
    lat: float
    lng: float
    recorded_at: datetime


# Chat Messages
class Message(BaseModel):
    message_id: str
    delivery_id: str
    sender_id: str
    content: str
    created_at: datetime


class MessageCreate(BaseModel):
    delivery_id: str
    content: str


# Ratings
class Rating(BaseModel):
    rating_id: str
    delivery_id: str
    rater_id: str
    ratee_id: str
    stars: int = Field(ge=1, le=5)
    review_text: Optional[str] = None
    created_at: datetime


class RatingCreate(BaseModel):
    delivery_id: str
    ratee_id: str
    stars: int = Field(ge=1, le=5)
    review_text: Optional[str] = None


# Disputes
class Dispute(BaseModel):
    dispute_id: str
    delivery_id: str
    raised_by: str
    description: str
    status: Literal["open", "resolved", "closed"] = "open"
    admin_notes: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None


class DisputeCreate(BaseModel):
    delivery_id: str
    description: str


# Config
class ConfigItem(BaseModel):
    key: str
    value: float


# OTP Verification
class OTPVerify(BaseModel):
    delivery_id: str
    otp: str
    otp_type: Literal["pickup", "delivery"]
