-- MySQL dump 10.13  Distrib 5.5.15, for osx10.7 (i386)
--
-- Host: localhost    Database: library
-- ------------------------------------------------------
-- Server version	5.5.15

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `library`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `library` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `library`;

--
-- Table structure for table `search_records`
--

DROP TABLE IF EXISTS `search_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `search_records` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `record` varchar(1024) NOT NULL,
  `time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `search_records`
--

LOCK TABLES `search_records` WRITE;
/*!40000 ALTER TABLE `search_records` DISABLE KEYS */;
INSERT INTO `search_records` VALUES (3,1,'三国','2012-07-13 00:10:18'),(4,1,'三国','2012-07-13 00:10:20'),(6,1,'三国','2012-07-13 00:10:36'),(7,1,'三国','2012-07-13 00:10:38'),(8,1,'三国','2012-07-13 00:10:39'),(9,1,'三国','2012-07-13 00:10:46'),(10,1,'三国','2012-07-13 00:10:48'),(11,1,'三国','2012-07-13 00:10:49'),(12,1,'三国','2012-07-13 00:10:50'),(13,1,'三国','2012-07-13 00:10:52'),(14,1,'三国','2012-07-13 00:10:58'),(15,1,'三国','2012-07-13 00:11:01'),(16,1,'三国','2012-07-13 00:11:08'),(17,1,'三国','2012-07-13 00:11:13'),(18,1,'韩寒','2012-07-13 00:14:31'),(19,2,'测试','2012-07-14 12:02:12');
/*!40000 ALTER TABLE `search_records` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2012-07-29 18:54:02
