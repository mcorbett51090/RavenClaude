# Aggregate on event-time with watermarks

Events arrive late and out of order over real networks, so window and aggregate on each event's own timestamp and use watermarks to decide when a window is complete. Processing-time aggregations — bucketing by when the processor happened to see the event — produce wrong answers the moment there is any network delay or replay, and the error is invisible until someone reconciles against the source.
