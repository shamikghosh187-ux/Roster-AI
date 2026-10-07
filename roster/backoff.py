"""Exponential backoff calculations without sleeping."""
def exponential_delay(attempt:int,base:float=.5,cap:float=30.0)->float:
    if attempt<0: raise ValueError("attempt must be non-negative")
    if base<0 or cap<0: raise ValueError("base and cap cannot be negative")
    return min(cap,base*(2**attempt))
def retry_delays(attempts:int,base:float=.5,cap:float=30.0)->list[float]:
    if attempts<0: raise ValueError("attempts cannot be negative")
    return [exponential_delay(i,base,cap) for i in range(attempts)]
