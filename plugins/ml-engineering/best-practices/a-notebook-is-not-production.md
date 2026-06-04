# A notebook is not production

Production ML is a pipeline — train, register, serve, monitor — not a hand-run script or notebook. The notebook is for prototyping; shipping requires reproducible, automatable, monitorable steps with a registry as the source of truth. A model that only exists as the output of a manually-run notebook cannot be reliably retrained, rolled back, or operated.
