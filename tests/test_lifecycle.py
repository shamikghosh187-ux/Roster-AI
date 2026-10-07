from roster.lifecycle import Lifecycle,LifecycleState
def test_lifecycle_is_idempotent():
    l=Lifecycle(); assert l.state==LifecycleState.CREATED; assert l.start(); assert not l.start(); assert l.stop(); assert l.state==LifecycleState.STOPPED; assert not l.stop()
