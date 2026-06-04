# Choose materialization by the trade, not habit

Use a view for cheap or rarely-read logic, a table for fast reads where a full rebuild is acceptable, and incremental for large append-mostly facts — and only go incremental with a reliable unique key and a correct load-window filter. The wrong choice either wastes warehouse compute on needless rebuilds or serves slow/stale data, and a broken incremental model silently drops or duplicates rows.
