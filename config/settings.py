import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass


class Settings:
    """Configuración centralizada. Los secretos se leen desde variables de entorno."""
    API_BASE_URL = os.getenv("API_BASE_URL", "https://api.fda.gov/drug/label.json")
    API_KEY = os.getenv("API_KEY", "")
    REQUEST_TIMEOUT = max(2, min(int(os.getenv("REQUEST_TIMEOUT", "8")), 30))
    ENABLE_OFFLINE_FALLBACK = os.getenv("ENABLE_OFFLINE_FALLBACK", "True").lower() in ("true", "1", "yes")
    ADMIN_INITIAL_USER = os.getenv("ADMIN_INITIAL_USER", "admin")
    ADMIN_INITIAL_CLAVE = os.getenv("ADMIN_INITIAL_CLAVE", "")
    MAX_LOGIN_ATTEMPTS = max(1, min(int(os.getenv("MAX_LOGIN_ATTEMPTS", "3")), 10))
    OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
    FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"
