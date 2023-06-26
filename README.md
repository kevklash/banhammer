<h1 align="center">BanHammer Project: ban or allow incoming API requests</h1>


## Overview
Create a system that enables generic, hierarchical, metrics-driven action triggers, according to the spec below. 

#### Requirements
The goal of this little project is a simple prototype library that is intended to run fast, scale, and designed for execution safety: it is expected to run in the critical path of a production application with high reliability.  

### Including
- Clear documentation
- Testing
- Future scalability and development

#### Usage in a backend API
For demonstration purposes, there is a simple HTTP API that uses the BanHammer implementation as we would in a real world case to protect against users breaking our service.

----

<h1 align="center">Spec and Example</h1>

> Track tokens (generally IP's) based on certain configurable metrics and timeframes such that we can perform user-defined "actions" upon them in a hierarchical way

## API

### `BanHammer` class

```python
BanHammer(bans, return_rates=False)
```

Constructor arguments:
- `bans`: a `dict` object matching the `bans` object specified below. It is the main source of configuration for the instantiation of the BanHammer object.
```python
bans = {
    # arbitrary metric name to be used in banhammer arguments i.e the event to be tracked
    "login_failed": {
        # hierarchical threshold triggers
        "thresholds": [
            {
                # how many calls of this metric(event) to allow within a defined window of time?
                "limit": 10,
                # how long in seconds should the window be?
                # i.e in this case 10 login_failed events in the last 3600 secs (1hr)
                "window": 3600,

                # what action to take (if any) when user fails login 10x in 1hr
                "action": [Action.block_local],

                # how long that "block" should persist
                # for example: if another event occurs during this window (different from the above window)
                # instantly run action
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
    # local metric only
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
```
- `return_rates`: boolean flag indicating weather function calls should return `stats_dict`

Functions:
- `incr(token, metric)`: Increments a counter for the given `metric` in concordance with the `bans` configurations
    - Arguments:
        - `token`: Caller token address to track against (typically an IP address)
        - `metric`: User-defined `bans` configuration metric that we want to increment. i.e the activity you want to 
          increment the counter against
    - Returns: a `(passed, stats_dict)` tuple where:
        - `passed` indicates true/false based on whether it should be blocked or not based on the configuration
        - `stats_dict` is a dict of showing a count of how many times a metric has been seen in a predefined time window
    - **NOTE:** This will only return a tuple containing `stats_dict` if `return_rates` is true (otherwise will just return 
      `passed`). i.e
      ```python
      ban = BanHammer(bans, return_rates=True)
      ban.incr('127.0.0.1', 'login_failed')
      >>> (True, {'token_rate_1m': 15, 'token_rate_10m': 22, 'token_rate_60m': 22})

      ban2 = BanHammer(bans, return_rates=False)  # by default return_rates is false
      ban2.incr('127.0.0.1', 'login_failed')
      >>> True  # indicates that the user has passed the check
      ```

- `now(token, metric)`: immediately bans a given token and stores for future use
    - Returns:
        - `stats_dict`: See definition below
- `status_all()`: Returns a list of all the current tokens, metrics, and their seen rates
    - Returns:
        - `stats_aggregate_dict`: A slightly modified version of the `stats_dict` (defined below) where each key will be a `metric` name, and each value would be the `stats_dict` for that metric.


### Tracking `stats_dict` object


BanHammer functions return a tuple of `(passed, stats_dict)`, where `stats_dict` is a dictionary defined below:
```python
{
    "token_rate_1m": rate_1m,   # how many times has the metric been seen in the last 1 minutes from now
    "token_rate_10m": rate_10m, # how many times has the metric been seen in the last 10 minutes from now
    "token_rate_60m": rate_60m  # how many times has the metric been seen in the last 60 minutes from now
}
```
These values generally increment every time the function is called.

# Example

Here we're going to configure and use `banhammer` to protect our app against bad logins as follows:

1. Define a metric name which represents a count of failed logins (`login_failed`)
2. Set some threshold(s) to enforce: (0: "10 in 1 hr", 1: "100 in 1 hr")
3. Define an action to perform when those trigger ("set data source key", "call reporting endpoint")

We will then call the `banhammer` library functions on each event that occurs based on the flow of the behavior of the app (details below)


### Example Usage

Below is an example of how we would use the `banhammer` library to protect API endpoints.

- in `my_triggers.py`:

```python
# define actions. all actions are called with args:
#     scope: any string or number, e.g. "1.2.3.4"
#     duration: action_duration
#     key: the lookup key for config inside self.bans, e.g. "login_failed"
#     window: time window
#     limit: max count within window
# not required to implement these actions, only that actions like these are callable.
class Action:
    """ define actions to be executed """
    @staticmethod
    def block_local(token, duration, *args):
        pass

    @staticmethod
    def report_central(token, duration, *args):
        pass

    @staticmethod
    def record_local(token, duration, key, window, limit):
        pass

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
```

- In `events.py`
```python
"""
functions defined here are intended to be called at some point in the request/response lifecycle of our API
These are only samples, we're free to implement any function(s) we like in anyway we see fit
"""

from banhammer import BanHammer  # from the implementation of the library

# Assume that we're using the spec definition of the `Bans` objects above
from my_triggers import BANS

# default construction
ban = BanHammer(BANS)

# you can also set these params as defaults on init:
ban = BanHammer(BANS, return_rates=True)

def after_login_failed(token: str):
    # simply increment the counter, action(s) maybe triggered or not depending on the set thresholds
    ban.incr(token, 'login_failed')

def login_from_restriced_ip(token: str):
    # ALTERNATIVE: to override local counter. `threshold` defaults to 0
    ban.now(token, "login_failed", threshold=1)

def after_login_successful(token: str):
    # simply increment the counter, action(s) maybe triggered or not depending on the set thresholds
    ban.incr(token, 'login_successful')

def report_login_successful(token: str):
    # get information about this event
    status = ban.status(token, 'login_successful')
```

## References

- [Rate limiting algorithms using redis](https://dev.to/astagi/rate-limiting-using-python-and-redis-58gk)