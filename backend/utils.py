from datetime import datetime
import math


def calculate_distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def is_peak_hour(dt: datetime = None) -> bool:
    """Check if current time is peak hour (7-9am or 6-9pm IST)"""
    if dt is None:
        dt = datetime.now()
    hour = dt.hour
    return (7 <= hour < 9) or (18 <= hour < 21)


async def calculate_delivery_price(
    distance_km: float,
    weight_kg: float,
    timing_preference: str,
    config: dict = None
) -> float:
    """
    Calculate delivery price based on distance, weight, timing
    
    Config keys (with defaults):
    - base_fare: 25
    - per_km_rate: 4
    - flat_fee_05km: 20
    - flat_fee_1km: 25
    - flat_fee_2km: 30
    - weight_multiplier_2_5kg: 1.2
    - time_multiplier_asap: 1.15
    - peak_multiplier: 1.5
    """
    # Default config
    default_config = {
        "base_fare": 25,
        "per_km_rate": 4,
        "flat_fee_05km": 20,
        "flat_fee_1km": 25,
        "flat_fee_2km": 30,
        "weight_multiplier_2_5kg": 1.2,
        "time_multiplier_asap": 1.15,
        "peak_multiplier": 1.5
    }
    
    # Merge with provided config
    if config:
        default_config.update(config)
    cfg = default_config
    
    # Last-mile flat fees (under 2km)
    if distance_km < 0.5:
        base_price = cfg["flat_fee_05km"]
    elif distance_km < 1.0:
        base_price = cfg["flat_fee_1km"]
    elif distance_km < 2.0:
        base_price = cfg["flat_fee_2km"]
    else:
        # Standard formula (2km and above)
        base_price = cfg["base_fare"] + (cfg["per_km_rate"] * distance_km)
    
    # Weight multiplier
    weight_multiplier = 1.0
    if 2 <= weight_kg <= 5:
        weight_multiplier = cfg["weight_multiplier_2_5kg"]
    
    # Time multiplier
    time_multiplier = 1.0
    if timing_preference == "asap":
        time_multiplier = cfg["time_multiplier_asap"]
    
    # Peak hour multiplier
    peak_multiplier = 1.0
    if is_peak_hour():
        peak_multiplier = cfg["peak_multiplier"]
    
    # Calculate final price
    final_price = base_price * weight_multiplier * time_multiplier * peak_multiplier
    
    # Round to nearest rupee
    return round(final_price)


def generate_4_digit_otp() -> str:
    """Generate a random 4-digit OTP"""
    import random
    return str(random.randint(1000, 9999))
