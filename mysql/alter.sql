ALTER TABLE model
ADD COLUMN measurement_range FLOAT,
ADD COLUMN measure_feedrate FLOAT,
ADD COLUMN move_feedrate FLOAT;

ALTER TABLE process
ADD COLUMN measurement_range FLOAT,
ADD COLUMN measure_feedrate FLOAT,
ADD COLUMN move_feedrate FLOAT
ADD COLUMN mtct_latency FLOAT;

ALTER TABLE mtconnect
ADD COLUMN line_timestamp TIMESTAMP(3);
