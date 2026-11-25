import os
from dotenv import find_dotenv, load_dotenv

load_dotenv()
mail_env_path = find_dotenv(".env.mail")
if mail_env_path:
    load_dotenv(mail_env_path, override=False)

SECRET_KEY = os.getenv("JWT_SECRET", "")
if len(SECRET_KEY) < 32:
    raise RuntimeError("JWT_SECRET must contain at least 32 characters")
DEVICE_SECRET_SALT = os.getenv("DEVICE_SECRET_SALT", "")
if len(DEVICE_SECRET_SALT) < 32:
    raise RuntimeError("DEVICE_SECRET_SALT must contain at least 32 characters")
if os.getenv("APP_ENV") == "production":
    missing = []
    if not (os.getenv("PUBLIC_APP_URL") or os.getenv("APP_URL")):
        missing.append("PUBLIC_APP_URL")
    if not os.getenv("CORS_ORIGINS"):
        missing.append("CORS_ORIGINS")
    if missing:
        raise RuntimeError("Production configuration is missing: " + ", ".join(missing))
    app_url = os.getenv("PUBLIC_APP_URL") or os.getenv("APP_URL", "")
    if not app_url.startswith("https://"):
        raise RuntimeError("PUBLIC_APP_URL or APP_URL must use HTTPS in production")
    if any(not origin.strip().startswith("https://") for origin in os.getenv("CORS_ORIGINS", "").split(",")):
        raise RuntimeError("CORS_ORIGINS must contain HTTPS origins in production")
smtp_auth = os.getenv("SMTP_AUTH", "true").strip().lower()
if smtp_auth not in {"true", "false"}:
    raise RuntimeError("SMTP_AUTH must be true or false")
if os.getenv("SMTP_HOST", "").strip():
    missing = []
    if smtp_auth == "true" and not (os.getenv("SMTP_USERNAME") or os.getenv("SMTP_USER")):
        missing.append("SMTP_USERNAME")
    if smtp_auth == "true" and not (os.getenv("SMTP_PASSWORD") or os.getenv("SMTP_PASS")):
        missing.append("SMTP_PASSWORD")
    if smtp_auth == "false" and not (os.getenv("SMTP_FROM") or os.getenv("MAIL_FROM")):
        missing.append("SMTP_FROM")
    if missing:
        raise RuntimeError("SMTP_HOST requires: " + ", ".join(missing))
    try:
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
    except ValueError as exc:
        raise RuntimeError("SMTP_PORT must be 25, 587 (STARTTLS), or 465 (SSL)") from exc
    if smtp_port not in (25, 465, 587):
        raise RuntimeError("SMTP_PORT must be 25, 587 (STARTTLS), or 465 (SSL)")
    if smtp_port == 25 and smtp_auth != "false":
        raise RuntimeError("SMTP port 25 is only supported with SMTP_AUTH=false")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

RATE_LIMIT_DB_PATH = os.getenv("RATE_LIMIT_DB_PATH", "./data/rate-limits.sqlite")
try:
    AUTH_RATE_LIMIT = int(os.getenv("AUTH_RATE_LIMIT", "10"))
except ValueError:
    AUTH_RATE_LIMIT = 10
try:
    AUTH_RATE_WINDOW_SECONDS = int(os.getenv("AUTH_RATE_WINDOW_SECONDS", "60"))
except ValueError:
    AUTH_RATE_WINDOW_SECONDS = 60
