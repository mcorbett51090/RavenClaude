# Use the transactional outbox for write-then-publish

When a state change must also emit an event, write the event to an outbox table within the same database transaction and have a relay publish it asynchronously. Publishing directly after the commit (or before it) is a dual-write that loses events when the publish fails or emits phantom events when the transaction rolls back. The outbox makes the state change and the event atomic.
