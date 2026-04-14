import redis
import os
from fastapi import HTTPException, Request

# الاتصال بحاوية Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def rate_limiter(request: Request):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    # الحد الأقصى: 5 طلبات في الدقيقة
    limit = 80
    window = 60
    
    current_requests = r.get(key)
    
    if current_requests and int(current_requests) >= limit:
        raise HTTPException(
            status_code=429, 
            detail="Too many requests. Slow down, hacker!"
        )
    
    # إذا كان أول طلب، ننشئ المفتاح ونضبط وقت انتهاء الصلاحية
    if not current_requests:
        r.set(key, 1, ex=window)
    else:
        r.incr(key)
    
    return True