import random
import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import timedelta


# ----------------------------
# Password helpers
# ----------------------------
def hash_password(password: str) -> str:
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters")
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)


# ----------------------------
# JWT helper
# ----------------------------
def generate_jwt(user_id: int, days: int = 1) -> str:
    return create_access_token(
        identity=str(user_id),
        expires_delta=timedelta(days=days)
    )


# ----------------------------
# OTP helpers
# ----------------------------

# ⚠️ For production: replace with Redis
_OTP_STORE = {}
_OTP_TTL = 300  # 5 minutes


def generate_otp(phone: str) -> str:
    otp = str(random.randint(100000, 999999))
    _OTP_STORE[phone] = {
        "otp": otp,
        "expires_at": time.time() + _OTP_TTL
    }
    return otp


def verify_otp(phone: str, otp: str) -> bool:
    record = _OTP_STORE.get(phone)
    if not record:
        return False

    if time.time() > record["expires_at"]:
        del _OTP_STORE[phone]
        return False

    if record["otp"] != otp:
        return False

    del _OTP_STORE[phone]
    return True
