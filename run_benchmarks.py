# Example usage:
# from banhammer import Banhammer
# from my_triggers import BANS
# from benchmarks import incr_benchmark, now_benchmark, status_benchmark
#
# ban = Banhammer(BANS)
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

# Path: run_benchmarks.py

from banhammer import BanHammer
from my_triggers import BANS
from benchmarks import incr_benchmark, now_benchmark, status_benchmark

ban = BanHammer(BANS)

# benchmark the incr function
result, duration = incr_benchmark(ban, '1234', 'login_failed')
print(result, duration)

# benchmark the now function
result, duration = now_benchmark(ban, '1234', 'login_failed')
print(result, duration)

# benchmark the status function
result, duration = status_benchmark(ban, '1234', 'login_failed')
print(result, duration)
