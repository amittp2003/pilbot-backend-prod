"""
Security middleware for production deployment
"""
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict
import re

# Simple in-memory rate limiting (use Redis in production for multi-instance)
rate_limit_store = defaultdict(list)

class RateLimiter:
    """Simple rate limiter to prevent API abuse"""
    
    def __init__(self, requests_per_minute=30, requests_per_hour=200):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
    
    def is_rate_limited(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limits"""
        now = datetime.now()
        
        # Clean old entries
        rate_limit_store[client_ip] = [
            timestamp for timestamp in rate_limit_store[client_ip]
            if now - timestamp < timedelta(hours=1)
        ]
        
        # Check minute limit
        recent_requests = [
            timestamp for timestamp in rate_limit_store[client_ip]
            if now - timestamp < timedelta(minutes=1)
        ]
        if len(recent_requests) >= self.requests_per_minute:
            return True
        
        # Check hour limit
        if len(rate_limit_store[client_ip]) >= self.requests_per_hour:
            return True
        
        # Add current request
        rate_limit_store[client_ip].append(now)
        return False

# Input sanitization
def sanitize_input(text: str, max_length: int = 2000) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    
    # Truncate to max length
    text = text[:max_length]
    
    # Remove potential XSS patterns (basic)
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'onerror\s*=',
        r'onclick\s*=',
        r'onload\s*=',
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove null bytes and control characters
    text = text.replace('\x00', '')
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    return text.strip()

def get_client_ip(request: Request) -> str:
    """Extract client IP from request (handles proxies)"""
    # Check for proxy headers (Render/Vercel add these)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection IP
    return request.client.host if request.client else "unknown"
