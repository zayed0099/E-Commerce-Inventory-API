
import os
from dotenv import load_dotenv

load_dotenv()

# TimeZone
TZ = os.environ.get("TZ", "UTC")

# Database
DATABASE_NAME = os.environ.get("DATABASE_NAME", "ecomm_manage.db")

# JWT
JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

if not JWT_SECRET:
	raise RuntimeError("JWT Cred are not set")

# Api Version
API_VERSION = os.environ.get("API_VER_STR", "/api/v1")

# Secret key for middleware
SECRET_KEY = os.environ.get("SECRET_KEY", None)

# Oauth
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", None)

# Tracking id encryption
TRACKING_ENC_KEY = os.environ.get("TRACKING_ENC_KEY", None)
ALPHABET_ENC = os.environ.get("ALPHABET_ENC", None)

if not TRACKING_ENC_KEY:
	raise RuntimeError("Tracking Encryption Cred are not set")	
