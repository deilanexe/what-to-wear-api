DROP TABLE IF EXISTS `garment`;

DROP TABLE IF EXISTS `garment_brands`;

DROP TABLE IF EXISTS `garment_combo`;

DROP TABLE IF EXISTS `garment_type`;

DROP TABLE IF EXISTS `use_in_combo`;

CREATE TABLE IF NOT EXISTS `garment` (
  `garment_id` integer primary key NOT NULL AUTO_INCREMENT,
  `garment_type_id` integer NOT NULL,
  `garment_brand_id` integer DEFAULT NULL,
  `garment_color` char(10) NOT NULL DEFAULT '000000',
  `garment_secondary_color` char(10) NOT NULL DEFAULT '000000',
  `garment_image_url` char(255) NOT NULL DEFAULT 'image/default.png',
  `last_washed_on` date NOT NULL DEFAULT '2016-01-01',
  `purchased_on` date NOT NULL DEFAULT '2016-01-01',
  `size` char(200) DEFAULT NULL,
  `available` INT2 NOT NULL DEFAULT 1,
  `retire_date` date DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS `garment_brands` (
  `brand_id` integer PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `brand_name` char(200) NOT NULL DEFAULT '',
  `wiki_article` char(200) DEFAULT NULL,
  `website_url` char(200) DEFAULT NULL
);


CREATE TABLE IF NOT EXISTS `garment_combo` (
  `g_combo_id` integer PRIMARY KEY AUTO_INCREMENT,
  `upper_ext_id` integer DEFAULT NULL,
  `upper_int_id` integer DEFAULT NULL,
  `upper_cov_id` integer DEFAULT NULL,
  `lower_ext_id` integer DEFAULT NULL,
  `lower_acc_id` integer DEFAULT NULL,
  `foot_ext_id` integer DEFAULT NULL,
  `foot_int_id` integer DEFAULT NULL,
  `head_id` integer DEFAULT NULL,
  `used_on` date NOT NULL
);

CREATE TABLE IF NOT EXISTS `garment_type` (
  `type_id` integer PRIMARY KEY AUTO_INCREMENT,
  `type_name` char(200) NOT NULL DEFAULT '',
  `type_description` text,
  `use_in_combo_as` INTEGER NOT NULL DEFAULT '0'
);

CREATE TABLE IF NOT EXISTS `use_in_combo` (
  `use_in_combo_id` integer PRIMARY KEY AUTO_INCREMENT,
  `use_name` char(50) NOT NULL DEFAULT '''''',
  `use_description` char(250) DEFAULT NULL,
  `field_in_db` char(50) NOT NULL
);

INSERT INTO `use_in_combo` (`use_in_combo_id`, `use_name`, `use_description`, `field_in_db`) VALUES
	(1, 'UPPER_EXTERNAL', 'A torso garment that others can see.', 'upper_ext_id'),
	(2, 'UPPER_INTERNAL', 'A torso garment that others do not see most of the time.', 'upper_int_id'),
	(3, 'UPPER_COVER', 'A torso garment used in rain or cold.', 'upper_cov_id'),
	(4, 'LOWER_EXTERNAL', 'A garment for the legs.', 'lower_ext_id'),
	(5, 'LOWER_ACCESSORY', 'Generally a belt.', 'lower_acc_id'),
	(6, 'FOOT_EXTERNAL', 'Shoes.', 'foot_ext_id'),
	(7, 'HEAD', 'Cap or hat.', 'head_id'),
	(8, 'FOOT_INTERNAL', 'Socks.', 'foot_int_id');
