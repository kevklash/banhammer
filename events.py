"""
functions defined here are intended to be called at some point in the request/response lifecycle of our API
These are only samples, you're free to implement any function(s) you like in anyway you see fit
"""

from banhammer import BanHammer # from the implementation of banhammer
import redis # from the implementation of redis

r = redis.Redis(host='localhost', port=6379) # instantiate a redis client with custom params

## Assume that we're using the spec definition of the `Bans` objects in my_triggers.py
from my_triggers import BANS

# default construction
# ban = BanHammer(BANS, r)

# you can also set these params as defaults on init:
ban = BanHammer(BANS, r, return_rates=True)

def after_login_failed(token: str):
    # simply increment the counter, action(s) maybe triggered or not depending on the set thresholds
    ban.incr(token, 'login_failed')
    
def login_restricted_ip(token: str):
    # ALTERNATIVE: to override local counter. `threshold` defaults to 0
    ban.now(token, 'login_failed', threshold=1)
    
def after_login_successful(token: str):
    # simply increment the counter, action(s) maybe triggered or not depending on the set thresholds
    ban.incr(token, 'login_successful')
    
def report_login_successful(token: str):
    # get information about this event
    status = ban.status(token, 'login_successful')