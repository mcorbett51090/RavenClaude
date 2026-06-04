# Monitor drift and define the retraining trigger up front

Models decay as the world they were trained on changes, so monitor input drift, prediction drift, and (when labels arrive) performance, and decide the retraining trigger — schedule, drift threshold, or performance drop — before launch. Drift is the early-warning signal you have before ground-truth labels arrive; a model with no monitoring rots silently until a customer or a metric review discovers it.
