USE coord;
CREATE TABLE IF NOT EXISTS `model` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `filename` varchar (255) NOT NULL,
  `status` varchar(255),
  `x_offset` FLOAT NOT NULL DEFAULT 0,
  `y_offset` FLOAT NOT NULL DEFAULT 0,
  `z_offset` FLOAT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `filename` (`filename`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `arc` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `model_id` int(11) unsigned NOT NULL,
  `radius` FLOAT NOT NULL,
  `cx` FLOAT NOT NULL,
  `cy` FLOAT NOT NULL,
  `cz` FLOAT NOT NULL,
  `rradius` FLOAT,
  `rcx` FLOAT,
  `rcy` FLOAT,
  `rcz` FLOAT,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`model_id`) REFERENCES `model` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `edge` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `model_id` int(11) unsigned NOT NULL,
  `side_id` int(11) unsigned,
  `arc_id` int(11) unsigned,
  `x` FLOAT NOT NULL,
  `y` FLOAT NOT NULL,
  `z` FLOAT NOT NULL,
  `rx` FLOAT,
  `ry` FLOAT,
  `rz` FLOAT,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`model_id`) REFERENCES `model` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
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
  `rlength` FLOAT,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`model_id`) REFERENCES `model` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;


CREATE TABLE IF NOT EXISTS `sensor` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `process_id` int(11) unsigned NOT NULL,
  `timestamp` TIMESTAMP(3) NOT NULL,
  `distance` FLOAT NOT NULL,
  PRIMARY KEY (`id`)
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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;


CREATE TABLE IF NOT EXISTS `process` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `model_id` int(11) unsigned NOT NULL,
  `status` varchar(255) NOT NULL,
  `error` varchar(255),
  `x_offset` FLOAT NOT NULL,
  `y_offset` FLOAT NOT NULL,
  `z_offset` FLOAT NOT NULL,
  `start` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `end` TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`model_id`) REFERENCES `model` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `machine` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `ip` varchar(255),
  `username` varchar(255),
  `password` varchar(255),
  `shared_folder` varchar(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;