from slowapi import Limiter
from slowapi.util import get_remote_address

# Module-level singleton so auth.py and main.py share the same instance.
limiter = Limiter(key_func=get_remote_address)
