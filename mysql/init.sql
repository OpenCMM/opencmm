USE coord;
CREATE TABLE IF NOT EXISTS `point` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `x` FLOAT NOT NULL,
  `y` FLOAT NOT NULL,
  `z` FLOAT NOT NULL,
  `point_id` varchar(255) NOT NULL,
  `rx` FLOAT,
  `ry` FLOAT,
  `rz` FLOAT,
  `img_path` varchar(255),
  `is_checked` TINYINT(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `point_id` (`point_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `line` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `a` varchar(255) NOT NULL,
  `b` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `arc` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `a` varchar(255) NOT NULL,
  `b` varchar(255) NOT NULL,
  `c` varchar(255) NOT NULL,
  `d` varchar(255) NOT NULL,
  `e` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;