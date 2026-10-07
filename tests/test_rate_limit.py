from roster.rate_limit import RateLimiter
def test_rate_limiter_enforces_window():
    limiter=RateLimiter(2,60)
    assert limiter.allow() and limiter.allow()
    assert not limiter.allow()
    assert limiter.remaining()==0
