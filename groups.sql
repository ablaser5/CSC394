DROP TABLE IF EXISTS `user_groups`;
DROP TABLE IF EXISTS `group`;

CREATE TABLE `group` (
  `g_id` int(11) NOT NULL AUTO_INCREMENT,
  `g_name` varchar(50) Not NULL,
  `owner` varchar (50) NOT NULL, 
  PRIMARY KEY (g_id)
)ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `user_groups` (
  `g_id` int(11),
  `email` varchar(50) DEFAULT NULL,
  FOREIGN KEY (`email`) REFERENCES `users` (`email`), 
  FOREIGN KEY (`g_id`) REFERENCES `group` (`g_id`) 
)ENGINE=InnoDB DEFAULT CHARSET=latin1;
