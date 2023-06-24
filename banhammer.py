import time
from collections import defaultdict
from typing import Dict, List, Tuple, Union

from redis import Redis

'''
This is a sample implementation of the BanHammer library.

This library is used to rate limit users based on the number of times they have performed an action.
It uses Redis to store the counters and execute actions when thresholds are met.

The library is designed to be used in a microservice architecture where each service has its own
BanHammer instance. The library is also designed to be used in a multi-threaded environment.
'''

class BanHammer:
    """ BanHammer is a rate limiting library that uses Redis to store the counters and
    execute actions when thresholds are met. """

    def __init__(self, bans: Dict[str, Dict], redis: Redis, return_rates: bool = False):
        """
        :param bans: a dictionary of metrics to track and their thresholds
        :param redis: a redis connection
        :param return_rates: whether to return the rates from the incr function
        """
        self.bans = bans
        self.redis = redis
        self.return_rates = return_rates

    def incr(self, token: str, metric: str, threshold: int = 0) -> Tuple[bool, Dict]:
        """
        This function increments the counter for the given metric and token and checks if the threshold is met.
        See the `now` function for more details.
        :param token: a unique identifier for the user
        :param metric: the metric to track
        :param threshold: the threshold to check against
        :return: a tuple of (passed, stats_dict)
        """
        if metric not in self.bans:
            raise ValueError(f"Metric '{metric}' is not defined in the bans configuration")

        # get the thresholds for this metric
        thresholds = self.bans[metric]["thresholds"]

        # get the current time
        now = time.time()

        # get the current rates for this metric
        rates = self._get_rates(token, metric, now)

        # check if the threshold is met
        passed = rates[threshold] <= thresholds[threshold]["limit"]

        # if the threshold is met, execute the action(s)
        if not passed:
            self._execute_actions(token, metric, threshold)

        # return the rates if requested
        if self.return_rates:
            return passed, rates

        return passed, {}

    def now(self, token: str, metric: str, threshold: int = 0) -> Tuple[bool, Dict]:
        """
        This function checks if the threshold is met for the given metric and token.
        See the `incr` function for more details.
        :param token: a unique identifier for the user
        :param metric: the metric to track
        :param threshold: the threshold to check against
        :return: a tuple of (passed, stats_dict)
        """
        if metric not in self.bans:
            raise ValueError(f"Metric '{metric}' is not defined in the bans configuration")

        # get the thresholds for this metric
        thresholds = self.bans[metric]["thresholds"]

        # get the current time
        now = time.time()

        # get the current rates for this metric
        rates = self._get_rates(token, metric, now)
        
        # check if the threshold is met
        passed = rates[threshold] <= thresholds[threshold]["limit"]
        
        # if the threshold is met, execute the action(s)
        if not passed:
            self._execute_actions(token, metric, threshold)
        
        # return the rates if requested
        if self.return_rates:
            return passed, rates
        
        return passed, {}

    def status(self, token: str, metric: str) -> Dict:
        """
        This function returns the current rates for the given metric and token.
        :param token: a unique identifier for the user
        :param metric: the metric to track
        :return: a dictionary of the current rates
        """
        if metric not in self.bans:
            raise ValueError(f"Metric '{metric}' is not defined in the bans configuration")

        # get the current time
        now = time.time()

        # get the current rates for this metric
        rates = self._get_rates(token, metric, now)

        return rates
    
    def _get_rates(self, token: str, metric: str, now: float) -> Dict:
        """
        This function returns the current rates for the given metric and token.
        :param token: a unique identifier for the user
        :param metric: the metric to track
        :param now: the current time
        :return: a dictionary of the current rates
        """
        # get the thresholds for this metric
        thresholds = self.bans[metric]["thresholds"]

        # get the current rates for this metric
        rates = defaultdict(int)
        for i, threshold in enumerate(thresholds):
            
            # get the key for this threshold
            key = self._get_key(token, metric, i)

            # get the window for this threshold
            window = threshold["window"]

            # get the current rate for this threshold
            rate = self.redis.zcount(key, now - window, now) if self.redis else 0

            # set the rate in the rates dictionary
            rates[i] = rate
            print("Current key is: ", key)

        return rates
    
    def _execute_actions(self, token: str, metric: str, threshold: int):
        """
        This function executes the actions for the given metric and token.
        :param token: a unique identifier for the user
        :param metric: the metric to track
        :param threshold: the threshold to check against
        """
        # get the thresholds for this metric
        thresholds = self.bans[metric]["thresholds"]

        # get the action(s) for this threshold
        actions = thresholds[threshold]["action"]

        # get the action duration for this threshold
        action_duration = thresholds[threshold]["action_duration"]

        # get the current time
        now = time.time()

        # execute the action(s)
        for action in actions:
            action(token, action_duration, metric, thresholds[threshold]["window"], thresholds[threshold]["limit"])
            
    def _get_key(self, token: str, metric: str, threshold: int) -> str:
        """
        This function returns the key for the given metric and token.
        Example: 12345:requests:0
        :param token: a unique identifier for the user
        :param metric: the metric to track
        :param threshold: the threshold to check against
        :return: the key for this metric and threshold
        """
        return f"{token}:{metric}:{threshold}"
    
    def _record_local(self, token: str, action_duration: int, metric: str, window: int, limit: int):
        """
        This method records an action for a local threshold.
        A local threshold is a threshold that is only checked against the current user.
        So, if a user exceeds the limit for a local threshold, the user will be banned.
        Example: a user can only make 10 requests per minute.
        Using a local threshold, if a user makes 11 requests in a minute, they will be banned.
        Usage: self._record_local(token, action_duration, metric, window, limit)
        :param token: a unique identifier for the user
        :param action_duration: the duration of the action
        :param metric: the metric to track
        :param window: the window for this threshold
        :param limit: the limit for this threshold
        """
        # get the current time
        now = time.time()

        # get the key for this metric and threshold
        key = self._get_key(token, metric, 0)

        # get the current rate for this threshold
        rate = self.redis.zcount(key, now - window, now)

        # if the rate is less than the limit, record the action
        if rate < limit:
            self.redis.zadd(key, now, now)
            self.redis.expire(key, action_duration)
            
    BANS = {
        "requests": {
            "thresholds": [
                {
                    "window": 60,
                    "limit": 10,
                    "action": [_record_local],
                    "action_duration": 60
                },
                {
                    "window": 3600,
                    "limit": 100,
                    "action": [_record_local],
                    "action_duration": 3600
                },
                {
                    "window": 86400,
                    "limit": 1000,
                    "action": [_record_local],
                    "action_duration": 86400
                }
            ]
        }
    }