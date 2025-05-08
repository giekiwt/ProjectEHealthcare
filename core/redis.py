import redis
from django.conf import settings

# Create Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

# Cache keys
CACHE_KEYS = {
    'FAQ_CACHE_KEY': 'faq:all',
    'DOCTORS_CACHE_KEY': 'doctors:all',
    'FACILITIES_CACHE_KEY': 'facilities:all',
    'REVIEWS_CACHE_KEY': 'reviews:all',
    'APPOINTMENTS_CACHE_KEY': 'appointments:all',
}

# Cache timeouts (in seconds)
CACHE_TIMEOUTS = {
    'FAQ_CACHE_TIMEOUT': 60 * 60,  # 1 hour
    'DOCTORS_CACHE_TIMEOUT': 60 * 60,  # 1 hour
    'FACILITIES_CACHE_TIMEOUT': 60 * 60,  # 1 hour
    'REVIEWS_CACHE_TIMEOUT': 60 * 30,  # 30 minutes
    'APPOINTMENTS_CACHE_TIMEOUT': 60 * 15,  # 15 minutes
}

def get_cache_key(key_name):
    """Get cache key with prefix"""
    return f"{settings.CACHE_KEY_PREFIX}:{CACHE_KEYS[key_name]}"

def get_cache_timeout(key_name):
    """Get cache timeout for key"""
    return CACHE_TIMEOUTS[key_name] 