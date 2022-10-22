CREATE DATABASE IF NOT EXISTS `ibmsample`;
USE `ibmsample`;
CREATE TABLE IF NOT EXISTS `accounts` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
  	`username` varchar(50) NOT NULL,
  	`password` varchar(255) NOT NULL,
  	`email` varchar(100) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

INSERT INTO `accounts` (`id`, `username`, `password`, `email`) VALUES (null, 'root', 'P@ssw0rd', 'root@gmail.com');
INSERT INTO `accounts` (`id`, `username`, `password`, `email`) VALUES (6, 'Aravinth', 'Av21@@', 'av21@gmail.com');
INSERT INTO `accounts` (`id`, `username`, `password`, `email`) VALUES (null, 'Gireesh', 'Gmessi21@@', 'Messigr@gmail.com');
select * from accounts;
