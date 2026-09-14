# Fake-backend capacity protection understood

The learner correctly identified that an over-limit request should produce a client error and that the test must assert `fake_backend.calls == []`. They understand that this proves the gateway rejected invalid work before consuming model capacity, not simply that it later reported an error.

## Evidence

The learner independently answered Lesson 3's retrieval prompt.
