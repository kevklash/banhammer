# This module is used to check the values of Redis keys created by the Banhammer library.

from redis import Redis
from redis import exceptions as redis_exceptions

# Redis connection params: host='localhost', port=6379
r = Redis(host='localhost', port=6379)

try:
    r.ping()
    print("Connected to Redis")
    failed_login_key = '1234:login_failed'
    key_to_lookup = r.get("login_failed")
    print("Record: ", key_to_lookup)
except(redis_exceptions.ConnectionError):
    print("Connection to Redis failed")