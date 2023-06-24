'''
This module contains the benchmark functions used in the Banhammer class.
'''

import time

def benchmark(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        return result, end - start
    return wrapper

'''
This function is used to benchmark the incr function.
'''

@benchmark
def incr_benchmark(ban, token, key, count=1):
    ban.incr(token, key, count)

'''
This function is used to benchmark the now function.
'''

@benchmark
def now_benchmark(ban, token, key, threshold=0):
    ban.now(token, key, threshold)
    
'''
This function is used to benchmark the status function.
'''

@benchmark
def status_benchmark(ban, token, key):
    ban.status(token, key)


# Example usage:
# from banhammer import BanHammer
# from my_triggers import BANS
# from benchmarks import incr_benchmark, now_benchmark, status_benchmark
#
# ban = BanHammer(BANS)
#
# # benchmark the incr function
# result, duration = incr_benchmark(ban, '
# 1234', 'login_failed')
# print(result, duration)
#
# # benchmark the now function
# result, duration = now_benchmark(ban, '
# 1234', 'login_failed')
# print(result, duration)
#
# # benchmark the status function
# result, duration = status_benchmark(ban, '
# 1234', 'login_failed')
# print(result, duration)
