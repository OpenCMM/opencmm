USE coord;
CREATE TABLE IF NOT EXISTS `model` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `filename` varchar (255) NOT NULL,
  `status` varchar(255),
  `x_offset` FLOAT NOT NULL DEFAULT 0,
  `y_offset` FLOAT NOT NULL DEFAULT 0,
  `z_offset` FLOAT NOT NULL DEFAULT 0,
  `measurement_range` FLOAT,
  `measure_feedrate` FLOAT,
  `move_feedrate` FLOAT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `filename` (`filename`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `process` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `model_id` int(11) unsigned NOT NULL,
  `status` varchar(255) NOT NULL,
  `error` varchar(255),
  `x_offset` FLOAT NOT NULL,
  `y_offset` FLOAT NOT NULL,
  `z_offset` FLOAT NOT NULL,
  `measurement_range` FLOAT NOT NULL,
  `measure_feedrate` FLOAT NOT NULL,
  `move_feedrate` FLOAT NOT NULL,
  `start` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `end` TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`model_id`) REFERENCES `model` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `arc` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `model_id` int(11) unsigned NOT NULL,
  `radius` FLOAT NOT NULL,
  `cx` FLOAT NOT NULL,
  `cy` FLOAT NOT NULL,
  `cz` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`model_id`) REFERENCES `model` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `arc_result` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `arc_id` int(11) unsigned NOT NULL,
  `process_id` int(11) unsigned NOT NULL,
  `radius` FLOAT NOT NULL,
  `cx` FLOAT NOT NULL,
  `cy` FLOAT NOT NULL,
  `cz` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`arc_id`) REFERENCES `arc` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (`process_id`) REFERENCES `process` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `edge` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `model_id` int(11) unsigned NOT NULL,
  `side_id` int(11) unsigned,
  `arc_id` int(11) unsigned,
  `x` FLOAT NOT NULL,
  `y` FLOAT NOT NULL,
  `z` FLOAT NOT NULL,
  `line` INTEGER,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`model_id`) REFERENCES `model` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `edge_result` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `edge_id` int(11) unsigned NOT NULL,
  `process_id` int(11) unsigned NOT NULL,
  `x` FLOAT NOT NULL,
  `y` FLOAT NOT NULL,
  `z` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`edge_id`) REFERENCES `edge` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (`process_id`) REFERENCES `process` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;


CREATE TABLE IF NOT EXISTS `side` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `model_id` int(11) unsigned NOT NULL,
  `x0` FLOAT NOT NULL,
  `y0` FLOAT NOT NULL,
  `z0` FLOAT NOT NULL,
  `x1` FLOAT NOT NULL,
  `y1` FLOAT NOT NULL,
  `z1` FLOAT NOT NULL,
  `pair_id` int(11) unsigned,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`model_id`) REFERENCES `model` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `pair` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `model_id` int(11) unsigned NOT NULL,
  `type` varchar(255) NOT NULL,
  `length` FLOAT,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`model_id`) REFERENCES `model` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `pair_result` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `pair_id` int(11) unsigned NOT NULL,
  `process_id` int(11) unsigned NOT NULL,
  `length` FLOAT,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`pair_id`) REFERENCES `pair` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (`process_id`) REFERENCES `process` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;


CREATE TABLE IF NOT EXISTS `trace` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `model_id` int(11) unsigned NOT NULL,
  `type` varchar(255) NOT NULL,
  `start` int(11) unsigned NOT NULL,
  `end` int(11) unsigned NOT NULL,
  `result` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`model_id`) REFERENCES `model` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (`start`) REFERENCES `side` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (`end`) REFERENCES `side` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `trace_line` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `trace_id` int(11) unsigned NOT NULL,
  `line` INT NOT NULL,
  `x0` FLOAT NOT NULL,
  `y0` FLOAT NOT NULL,
  `x1` FLOAT NOT NULL,
  `y1` FLOAT NOT NULL,
  `z` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`trace_id`) REFERENCES `trace` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;


CREATE TABLE IF NOT EXISTS `trace_line_result` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `trace_line_id` int(11) unsigned NOT NULL,
  `process_id` int(11) unsigned NOT NULL,
  `distance` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`trace_line_id`) REFERENCES `trace_line` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (`process_id`) REFERENCES `process` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;


CREATE TABLE IF NOT EXISTS `sensor` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `process_id` int(11) unsigned NOT NULL,
  `timestamp` TIMESTAMP(3) NOT NULL,
  `distance` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`process_id`) REFERENCES `process` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;


CREATE TABLE IF NOT EXISTS `mtconnect` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `process_id` int(11) unsigned NOT NULL,
  `timestamp` TIMESTAMP(3) NOT NULL,
  `x` FLOAT NOT NULL,
  `y` FLOAT NOT NULL,
  `z` FLOAT NOT NULL,
  `line` varchar(255) NOT NULL, 
  `feedrate` FLOAT NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`process_id`) REFERENCES `process` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;


CREATE TABLE IF NOT EXISTS `machine` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `ip` varchar(255),
  `username` varchar(255),
  `password` varchar(255),
  `shared_folder` varchar(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;
