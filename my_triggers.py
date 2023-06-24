# define actions. all actions are called with args:
#     scope: any string or number, e.g. "1.2.3.4"
#     duration: action_duration
#     key: the lookup key for config inside self.bans, e.g. "login_failed"
#     window: time window
#     limit: max count within window
# You are not required to implement these actions, only that actions like these are callable.

from redis import Redis
import time

class Action:
    """ define actions to be executed """
    @staticmethod
    def block_local(token, duration, *args):
        '''
        This is a sample action that blocks the event locally.
        Code:
            # block the user for 1 hour
            self.redis.set(f"{token}:blocked", 1, ex=duration)
        '''
        print("blocking local")
        pass

    @staticmethod
    def report_central(token, duration, *args):
        '''
        This is a sample action that reports the event to a central server.
        Code:
            # report the user to a central server
            requests.post("https://central.server.com/report", json={"token": token, "duration": duration})
        '''
        print("reporting central")
        pass

    @staticmethod
    def record_local(token, duration, key, window, limit):
        '''
        This is a sample action that records the event locally.
        Code:
            # record the user locally
            self.redis.set(f"{token}:recorded", 1, ex=duration)
        '''
        print("recording local")
        now = time.time()
        """ r.zadd(f"{token}:{key}:{limit}", now, now)
        r.expire(f"{token}:{key}:{limit}", duration) """
    

BANS = {
    "login_failed": {
        "thresholds": [
            {
                "limit": 10,
                "window": 3600,
                "action": [Action.block_local],
                "action_duration": 3600,
            },
            {
                "limit": 100,
                "window": 3600,
                "action": [Action.report_central],
                "action_duration": 86400
            }
        ],
    },
    "login_successful": {
        "thresholds": [
            {
                "limit": 10,
                "window": 60,
                "action": [Action.record_local],
                "action_duration": 3600
            },
        ]
    }
}