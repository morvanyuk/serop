CREATE TABLE `users` (
  `username` varchar(128) UNIQUE DEFAULT NULL,
  `password` varchar(128) DEFAULT NULL
) 

CREATE TABLE `items` (
  `id` bigint UNSIGNED NOT NULL,
  `name` varchar(128) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `price` float DEFAULT '1',
  `is_mods` varchar(40) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;