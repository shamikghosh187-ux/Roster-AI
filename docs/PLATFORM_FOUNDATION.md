# Roster Platform Foundation

The platform foundation is a dependency-light layer for safer evolution of the assistant.

It provides request correlation, UTC timestamps, retries and exponential backoff, circuit breaking, rate limiting, bounded TTL caching, secret redaction and explicit secret access, audit records, event journaling, command envelopes, operation results, bounded sessions, action policies, execution context propagation, lifecycle management, and feature flags.

The primitives are intentionally independent of provider SDKs and desktop UI code. Focused regression tests make incremental adoption safer.
