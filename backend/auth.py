import bcrypt
import httpx
from fastapi import HTTPException, Cookie, Header
from typing import Optional
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid


async def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


async def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


async def create_session(db: AsyncIOMotorDatabase, user_id: str) -> str:
    """Create a new session for a user"""
    session_token = f"session_{uuid.uuid4().hex}"
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at,
        "created_at": datetime.now(timezone.utc)
    })
    
    return session_token


def get_current_user_dependency(db):
    """Create a dependency function with database access"""
    async def get_current_user(
        session_token: Optional[str] = Cookie(None),
        authorization: Optional[str] = Header(None)
    ):
        """
        Get the current user from session token (cookie or Authorization header)
        REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
        """
        # Try cookie first, then Authorization header
        token = session_token
        if not token and authorization:
            if authorization.startswith("Bearer "):
                token = authorization.replace("Bearer ", "")
        
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Find session
        session_doc = await db.user_sessions.find_one(
            {"session_token": token},
            {"_id": 0}
        )
        
        if not session_doc:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        # Check expiry (ensure timezone-aware comparison)
        expires_at = session_doc["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if expires_at < datetime.now(timezone.utc):
            # Delete expired session
            await db.user_sessions.delete_one({"session_token": token})
            raise HTTPException(status_code=401, detail="Session expired")
        
        # Get user
        user_doc = await db.users.find_one(
            {"user_id": session_doc["user_id"]},
            {"_id": 0}
        )
        
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user_doc.get("is_active", True):
            raise HTTPException(status_code=403, detail="User account is inactive")
        
        return user_doc
    
    return get_current_user


async def process_google_oauth_session(session_id: str) -> dict:
    """
    Exchange session_id from Emergent Auth for user data
    REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": session_id},
            timeout=10.0
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session_id")
        
        data = response.json()
        return {
            "email": data["email"],
            "name": data["name"],
            "picture": data.get("picture"),
            "session_token": data["session_token"]
        }


async def hash_otp(otp: str) -> str:
    """Hash an OTP using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(otp.encode('utf-8'), salt)
    return hashed.decode('utf-8')


async def verify_otp(otp: str, hashed: str) -> bool:
    """Verify an OTP against a hash"""
    return bcrypt.checkpw(otp.encode('utf-8'), hashed.encode('utf-8'))
