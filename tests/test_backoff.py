from roster.backoff import exponential_delay,retry_delays
def test_backoff_is_exponential_and_capped():
    assert exponential_delay(0)==.5 and exponential_delay(5)==16 and exponential_delay(10,cap=5)==5
    assert retry_delays(3)==[.5,1.0,2.0]
