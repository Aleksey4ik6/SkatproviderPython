-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: isp_database
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `billing`
--

DROP TABLE IF EXISTS `billing`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `billing` (
  `bill_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `due_date` date NOT NULL,
  `paid` tinyint(1) DEFAULT '0',
  `payment_date` datetime DEFAULT NULL,
  PRIMARY KEY (`bill_id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `billing_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `billing`
--

LOCK TABLES `billing` WRITE;
/*!40000 ALTER TABLE `billing` DISABLE KEYS */;
INSERT INTO `billing` VALUES (1,1,650.00,'2026-03-07',1,'2026-03-05 14:10:08'),(2,3,890.00,'2026-03-12',1,'2026-03-10 14:10:08'),(3,6,450.00,'2026-03-15',1,'2026-03-15 14:10:08'),(4,7,1200.00,'2026-03-02',1,'2026-03-01 14:10:08'),(5,2,450.00,'2026-03-22',0,NULL),(6,4,1200.00,'2026-03-16',1,'2026-04-14 15:25:21'),(7,5,650.00,'2026-03-27',1,'2026-04-10 21:11:57'),(8,5,650.00,'2026-05-10',1,'2026-04-10 21:23:41'),(9,5,1000.00,'2026-05-10',1,'2026-04-10 21:30:39'),(10,5,10000.00,'2026-05-10',1,'2026-04-14 15:20:59'),(11,4,12323.00,'2026-05-14',0,NULL),(12,1,1000.00,'2026-05-29',0,NULL);
/*!40000 ALTER TABLE `billing` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `city_houses`
--

DROP TABLE IF EXISTS `city_houses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `city_houses` (
  `house_id` int NOT NULL AUTO_INCREMENT,
  `city` varchar(80) NOT NULL DEFAULT 'Абакан',
  `street` varchar(255) DEFAULT NULL,
  `house_number` varchar(60) DEFAULT NULL,
  `full_address` varchar(255) NOT NULL,
  `latitude` decimal(10,7) DEFAULT NULL,
  `longitude` decimal(10,7) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`house_id`),
  UNIQUE KEY `uq_city_houses_full_address` (`full_address`),
  KEY `idx_city_houses_latlon` (`latitude`,`longitude`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `city_houses`
--

LOCK TABLES `city_houses` WRITE;
/*!40000 ALTER TABLE `city_houses` DISABLE KEYS */;
INSERT INTO `city_houses` VALUES (1,'Абакан','проспект Ленина','12','12, проспект Ленина, Абакан, городской округ Абакан, Республика Хакасия, Сибирский федеральный округ, 655012, Россия',53.7255473,91.4689770,'2026-04-15 18:14:45'),(2,'Абакан','улица Пушкина','30','Хакасский Политехнический Колледж, 30, улица Пушкина, Абакан, городской округ Абакан, Республика Хакасия, Сибирский федеральный округ, 655012, Россия',53.7197299,91.4669501,'2026-04-15 19:44:57'),(3,'Абакан','улица Мира','21','21, улица Мира, Кулацкий, Усть-Абакан, Усть-Абаканский поссовет, Усть-Абаканский район, Республика Хакасия, Сибирский федеральный округ, 655163, Россия',53.8479812,91.3737632,'2026-04-15 19:44:59'),(4,'Абакан','улица Пушкина','1','1, улица Пушкина, Абакан, городской округ Абакан, Республика Хакасия, Сибирский федеральный округ, 655012, Россия',53.7166374,91.4789394,'2026-04-15 19:45:03'),(5,'Абакан','улица Маршала Жукова','','улица Маршала Жукова, Абакан, городской округ Абакан, Республика Хакасия, Сибирский федеральный округ, 655003, Россия',53.7408842,91.4563633,'2026-04-15 19:45:05'),(7,'Абакан','проспект Ленина','21','21, проспект Ленина, Абакан, городской округ Абакан, Республика Хакасия, Сибирский федеральный округ, 655012, Россия',53.7248110,91.4674675,'2026-04-15 19:45:09'),(8,'Абакан','улица Ленина','5','5, улица Ленина, Рынок, Усть-Абакан, Усть-Абаканский поссовет, Усть-Абаканский район, Республика Хакасия, Сибирский федеральный округ, 655102, Россия',53.8293521,91.3946377,'2026-04-15 19:59:09'),(9,'Абакан','проспект Ленина','3','3, проспект Ленина, Абакан, городской округ Абакан, Республика Хакасия, Сибирский федеральный округ, 655012, Россия',53.7251604,91.4701806,'2026-04-15 19:59:13'),(10,'Абакан','улица Некрасова','2','2, улица Некрасова, Сахарный, Усть-Абакан, Усть-Абаканский поссовет, Усть-Абаканский район, Республика Хакасия, Сибирский федеральный округ, 655102, Россия',53.8537304,91.3837481,'2026-04-15 19:59:29');
/*!40000 ALTER TABLE `city_houses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `complaints`
--

DROP TABLE IF EXISTS `complaints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `complaints` (
  `complaint_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `description` text NOT NULL,
  `date` datetime NOT NULL,
  `status` varchar(50) NOT NULL,
  `resolution` text,
  PRIMARY KEY (`complaint_id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `complaints_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaints`
--

LOCK TABLES `complaints` WRITE;
/*!40000 ALTER TABLE `complaints` DISABLE KEYS */;
INSERT INTO `complaints` VALUES (1,4,'Горит красная лампочка LOS на оптическом терминале','2026-03-17 12:10:08','Открыто',NULL),(2,5,'Очень низкая скорость вечером, не грузит видео','2026-03-16 14:10:08','В работе',NULL),(3,1,'Нужно настроить новый Wi-Fi роутерd','2026-03-12 14:10:08','Открыто',NULL),(4,2,'Случайно перерезали кабель при ремонте','2026-03-17 09:10:08','Открыто',NULL),(5,7,'Нет пинга до корпоративного сервера','2026-03-17 13:40:08','В работе',NULL),(6,2,'vbc','2026-04-10 12:10:25','Открыто',NULL),(7,1,'павва','2026-04-10 21:32:52','Открыто',NULL);
/*!40000 ALTER TABLE `complaints` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_addons`
--

DROP TABLE IF EXISTS `customer_addons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_addons` (
  `addon_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `service_name` varchar(255) NOT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'Активна',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `activated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`addon_id`),
  KEY `customer_id` (`customer_id`,`created_at`),
  CONSTRAINT `customer_addons_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_addons`
--

LOCK TABLES `customer_addons` WRITE;
/*!40000 ALTER TABLE `customer_addons` DISABLE KEYS */;
INSERT INTO `customer_addons` VALUES (1,1,'123','Активна','2026-04-14 21:33:38','2026-04-14 21:33:38'),(2,1,'Белый IP','Активна','2026-04-14 21:34:28','2026-04-14 21:34:28'),(3,1,'dd','Активна','2026-04-15 11:20:20','2026-04-15 11:20:20');
/*!40000 ALTER TABLE `customer_addons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_autopay_settings`
--

DROP TABLE IF EXISTS `customer_autopay_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_autopay_settings` (
  `customer_id` int NOT NULL,
  `enabled` tinyint(1) NOT NULL DEFAULT '0',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`customer_id`),
  CONSTRAINT `customer_autopay_settings_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_autopay_settings`
--

LOCK TABLES `customer_autopay_settings` WRITE;
/*!40000 ALTER TABLE `customer_autopay_settings` DISABLE KEYS */;
INSERT INTO `customer_autopay_settings` VALUES (1,1,'2026-04-15 11:20:45');
/*!40000 ALTER TABLE `customer_autopay_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_events`
--

DROP TABLE IF EXISTS `customer_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_events` (
  `event_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `event_type` varchar(50) NOT NULL,
  `details` text NOT NULL,
  `actor` varchar(255) DEFAULT NULL,
  `event_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`event_id`),
  KEY `customer_id` (`customer_id`,`event_time`),
  CONSTRAINT `customer_events_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_events`
--

LOCK TABLES `customer_events` WRITE;
/*!40000 ALTER TABLE `customer_events` DISABLE KEYS */;
INSERT INTO `customer_events` VALUES (1,1,'Счет','Выставлен счет #12 на 1000 ₽','Главный Администратор','2026-04-14 21:10:02'),(2,1,'Профиль','Self-service заявка #1: promised_payment','Иванов Алексей Викторович','2026-04-14 21:10:39'),(3,1,'Профиль','Self-service заявка #2: autopay','Иванов Алексей Викторович','2026-04-14 21:12:06'),(4,1,'Профиль','Self-service заявка #3: addon','Иванов Алексей Викторович','2026-04-14 21:12:34'),(5,1,'Профиль','Self-service заявка #4: plan_change','Иванов Алексей Викторович','2026-04-14 21:13:32'),(6,1,'Профиль','Self-service заявка #5: promised_payment','Иванов Алексей Викторович','2026-04-14 21:21:13'),(7,1,'Профиль','Self-service заявка #6: autopay','Иванов Алексей Викторович','2026-04-14 21:21:39'),(8,1,'Профиль','Self-service заявка #7: plan_change','Иванов Алексей Викторович','2026-04-14 21:21:46'),(9,1,'Профиль','Self-service заявка #8: addon','Иванов Алексей Викторович','2026-04-14 21:21:54'),(10,1,'Профиль','Self-service заявка #9: autopay','Иванов Алексей Викторович','2026-04-14 21:23:13'),(11,1,'Профиль','Self-service #9: статус \'В работе\' (autopay)','Главный Администратор','2026-04-14 21:33:07'),(12,1,'Профиль','Self-service #9 выполнена (autopay)','Главный Администратор','2026-04-14 21:33:22'),(13,1,'Профиль','Self-service #8 выполнена (addon)','Главный Администратор','2026-04-14 21:33:38'),(14,1,'Профиль','Self-service #7 выполнена (plan_change)','Главный Администратор','2026-04-14 21:33:40'),(15,1,'Профиль','Self-service #6 выполнена (autopay)','Главный Администратор','2026-04-14 21:33:51'),(16,1,'Профиль','Self-service #5 выполнена (promised_payment)','Главный Администратор','2026-04-14 21:34:06'),(17,1,'Профиль','Self-service #4 выполнена (plan_change)','Главный Администратор','2026-04-14 21:34:20'),(18,1,'Профиль','Self-service #3 выполнена (addon)','Главный Администратор','2026-04-14 21:34:28'),(19,1,'Профиль','Self-service #2 выполнена (autopay)','Главный Администратор','2026-04-14 21:34:34'),(20,1,'Профиль','Self-service #1 выполнена (promised_payment)','Главный Администратор','2026-04-14 21:34:41'),(21,1,'Профиль','Self-service заявка #10: autopay','Иванов Алексей Викторович','2026-04-14 21:34:47'),(22,1,'Профиль','Self-service #10: статус \'Отклонена\' (autopay)','Главный Администратор','2026-04-14 21:34:56'),(23,1,'Профиль','Клиент привязан к узлу #2','Главный Администратор','2026-04-14 21:41:34'),(24,1,'Профиль','Клиент привязан к узлу #2','Главный Администратор','2026-04-14 21:41:49'),(25,9,'Профиль','Клиент привязан к узлу #1','Главный Администратор','2026-04-14 21:41:54'),(26,1,'Диагностика','Авария закрыта: Потеря связи','Главный Администратор','2026-04-14 21:42:53'),(27,9,'Диагностика','Авария: Потеря связи','Главный Администратор','2026-04-14 21:44:31'),(28,9,'Диагностика','Авария закрыта: Потеря связи','Главный Администратор','2026-04-14 21:52:10'),(29,5,'Профиль','Клиент привязан к узлу #1','Главный Администратор','2026-04-14 21:52:19'),(30,1,'Диагностика','Авария: Потеря связи. sedsdf','Главный Администратор','2026-04-14 21:54:25'),(31,1,'Диагностика','Авария закрыта: Потеря связи','Главный Администратор','2026-04-14 21:54:38'),(32,1,'Диагностика','Авария закрыта: Потеря связи','Главный Администратор','2026-04-14 21:54:50'),(33,1,'Профиль','Self-service заявка #11: promised_payment','Иванов Алексей Викторович','2026-04-15 11:18:52'),(34,1,'Профиль','Self-service заявка #12: autopay','Иванов Алексей Викторович','2026-04-15 11:19:27'),(35,1,'Профиль','Self-service заявка #13: plan_change','Иванов Алексей Викторович','2026-04-15 11:19:33'),(36,1,'Профиль','Self-service заявка #14: addon','Иванов Алексей Викторович','2026-04-15 11:19:37'),(37,1,'Профиль','Self-service #14 выполнена (addon)','Главный Администратор','2026-04-15 11:20:20'),(38,1,'Профиль','Self-service #13 выполнена (plan_change)','Главный Администратор','2026-04-15 11:20:32'),(39,1,'Профиль','Self-service #12 выполнена (autopay)','Главный Администратор','2026-04-15 11:20:45'),(40,1,'Профиль','Self-service #11 выполнена (promised_payment)','Главный Администратор','2026-04-15 11:20:53'),(41,5,'Диагностика','Авария: Потеря связи. ','Главный Администратор','2026-04-15 11:21:41'),(42,9,'Диагностика','Авария: Потеря связи. ','Главный Администратор','2026-04-15 11:21:41'),(43,5,'Диагностика','Авария закрыта: Потеря связи','Главный Администратор','2026-04-15 11:21:52'),(44,9,'Диагностика','Авария закрыта: Потеря связи','Главный Администратор','2026-04-15 11:21:52'),(45,1,'Диагностика','Авария: Потеря связи. взрыв','Главный Администратор','2026-04-15 11:22:07'),(46,1,'Диагностика','Авария закрыта: Потеря связи','Главный Администратор','2026-04-15 11:22:15'),(47,2,'Профиль','Клиент привязан к узлу #1','Главный Администратор','2026-04-15 11:22:20'),(48,10,'Профиль','Создан клиент Соломатин Дмитрий Александрович','Главный Администратор','2026-04-15 18:15:18'),(49,10,'Диагностика','Авария дома: Нет связи в доме','Главный Администратор','2026-04-15 19:36:38'),(50,1,'Профиль','Обновлены данные клиента','Главный Администратор','2026-04-15 19:43:22'),(51,2,'Профиль','Обновлены данные клиента','Главный Администратор','2026-04-15 19:43:31'),(52,3,'Профиль','Обновлены данные клиента','Главный Администратор','2026-04-15 19:43:48'),(53,4,'Профиль','Обновлены данные клиента','Главный Администратор','2026-04-15 19:43:59'),(54,5,'Профиль','Обновлены данные клиента','Главный Администратор','2026-04-15 19:44:11'),(55,6,'Профиль','Обновлены данные клиента','Главный Администратор','2026-04-15 19:44:20'),(56,7,'Профиль','Обновлены данные клиента','Главный Администратор','2026-04-15 19:44:35'),(57,8,'Профиль','Обновлены данные клиента','Главный Администратор','2026-04-15 19:44:50'),(58,3,'Профиль','Обновлены данные клиента','Главный Администратор','2026-04-15 19:58:32'),(59,5,'Профиль','Обновлены данные клиента','Главный Администратор','2026-04-15 19:58:44'),(60,6,'Профиль','Обновлены данные клиента','Главный Администратор','2026-04-15 19:58:52'),(61,9,'Профиль','Обновлены данные клиента','Главный Администратор','2026-04-15 19:59:02'),(62,8,'Профиль','Обновлены данные клиента','Главный Администратор','2026-04-15 19:59:25');
/*!40000 ALTER TABLE `customer_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_node_links`
--

DROP TABLE IF EXISTS `customer_node_links`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_node_links` (
  `customer_id` int NOT NULL,
  `node_id` int NOT NULL,
  `linked_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`customer_id`),
  KEY `node_id` (`node_id`),
  CONSTRAINT `customer_node_links_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `customer_node_links_ibfk_2` FOREIGN KEY (`node_id`) REFERENCES `network_nodes` (`node_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_node_links`
--

LOCK TABLES `customer_node_links` WRITE;
/*!40000 ALTER TABLE `customer_node_links` DISABLE KEYS */;
INSERT INTO `customer_node_links` VALUES (1,2,'2026-04-14 21:41:49'),(2,1,'2026-04-15 11:22:20'),(5,1,'2026-04-14 21:52:19'),(9,1,'2026-04-14 21:41:54');
/*!40000 ALTER TABLE `customer_node_links` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_promised_payments`
--

DROP TABLE IF EXISTS `customer_promised_payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_promised_payments` (
  `promised_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `amount` decimal(10,2) NOT NULL DEFAULT '0.00',
  `delay_days` int NOT NULL DEFAULT '0',
  `approved_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `approved_by` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`promised_id`),
  KEY `customer_id` (`customer_id`,`approved_at`),
  CONSTRAINT `customer_promised_payments_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_promised_payments`
--

LOCK TABLES `customer_promised_payments` WRITE;
/*!40000 ALTER TABLE `customer_promised_payments` DISABLE KEYS */;
INSERT INTO `customer_promised_payments` VALUES (1,1,1000.00,1,'2026-04-14 21:34:06','Главный Администратор'),(2,1,1000.00,4,'2026-04-14 21:34:41','Главный Администратор'),(3,1,1000.00,10,'2026-04-15 11:20:53','Главный Администратор');
/*!40000 ALTER TABLE `customer_promised_payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer_self_service_requests`
--

DROP TABLE IF EXISTS `customer_self_service_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer_self_service_requests` (
  `request_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `request_type` enum('promised_payment','plan_change','addon','autopay') NOT NULL,
  `payload` text,
  `status` varchar(50) NOT NULL DEFAULT 'Новая',
  `comment` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `processed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`request_id`),
  KEY `customer_id` (`customer_id`,`created_at`),
  KEY `status` (`status`),
  CONSTRAINT `customer_self_service_requests_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer_self_service_requests`
--

LOCK TABLES `customer_self_service_requests` WRITE;
/*!40000 ALTER TABLE `customer_self_service_requests` DISABLE KEYS */;
INSERT INTO `customer_self_service_requests` VALUES (1,1,'promised_payment','{\"amount\": \"1000\", \"days\": \"4\"}','Выполнена','Заявка выполнена','2026-04-14 21:10:39','2026-04-14 21:34:41'),(2,1,'autopay','{\"enabled\": 1}','Выполнена','Заявка выполнена','2026-04-14 21:12:06','2026-04-14 21:34:34'),(3,1,'addon','{\"service\": \"Белый IP\"}','Выполнена','Заявка выполнена','2026-04-14 21:12:34','2026-04-14 21:34:28'),(4,1,'plan_change','{\"target_plan_id\": 2, \"selected\": \"2 - Оптимальный (Оптика) (300 Мбит/с, 650.00 ₽)\"}','Выполнена','Заявка выполнена','2026-04-14 21:13:32','2026-04-14 21:34:20'),(5,1,'promised_payment','{\"amount\": \"1000\", \"days\": \"1\"}','Выполнена','Заявка выполнена','2026-04-14 21:21:13','2026-04-14 21:34:06'),(6,1,'autopay','{\"enabled\": 0}','Выполнена','Заявка выполнена','2026-04-14 21:21:39','2026-04-14 21:33:51'),(7,1,'plan_change','{\"target_plan_id\": 4, \"selected\": \"4 - Гигабит PRO (1000 Мбит/с, 1200.00 ₽)\"}','Выполнена','Заявка выполнена','2026-04-14 21:21:46','2026-04-14 21:33:40'),(8,1,'addon','{\"service\": \"123\"}','Выполнена','Заявка выполнена','2026-04-14 21:21:54','2026-04-14 21:33:38'),(9,1,'autopay','{\"enabled\": 1}','Выполнена','Заявка выполнена','2026-04-14 21:23:13','2026-04-14 21:33:22'),(10,1,'autopay','{\"enabled\": 0}','Отклонена','Недостаточно данных','2026-04-14 21:34:47','2026-04-14 21:34:56'),(11,1,'promised_payment','{\"amount\": \"1000\", \"days\": \"10\"}','Выполнена','Заявка выполнена','2026-04-15 11:18:52','2026-04-15 11:20:53'),(12,1,'autopay','{\"enabled\": 1}','Выполнена','Заявка выполнена','2026-04-15 11:19:27','2026-04-15 11:20:45'),(13,1,'plan_change','{\"target_plan_id\": 3, \"selected\": \"3 - Игровой+ (500 Мбит/с, 890.00 ₽)\"}','Выполнена','Заявка выполнена','2026-04-15 11:19:33','2026-04-15 11:20:32'),(14,1,'addon','{\"service\": \"dd\"}','Выполнена','Заявка выполнена','2026-04-15 11:19:37','2026-04-15 11:20:20');
/*!40000 ALTER TABLE `customer_self_service_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `customer_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `address` varchar(255) NOT NULL,
  `phone` varchar(50) NOT NULL,
  `email` varchar(255) NOT NULL,
  `plan_id` int DEFAULT NULL,
  `registration_date` datetime DEFAULT NULL,
  `ip_address` varchar(15) DEFAULT '192.168.1.1',
  `house_id` int DEFAULT NULL,
  `latitude` decimal(10,7) DEFAULT NULL,
  `longitude` decimal(10,7) DEFAULT NULL,
  PRIMARY KEY (`customer_id`),
  KEY `plan_id` (`plan_id`),
  KEY `idx_customers_house_id` (`house_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (1,'Иванов Алексей Викторович','Хакасский Политехнический Колледж, 30, улица Пушкина, Абакан, городской округ Абакан, Республика Хакасия, Сибирский федеральный округ, 655012, Россия','+7(999)123-45-67','ivanov.a@mail.ru',3,'2025-11-17 14:10:08','8.8.8.8',2,53.7197299,91.4669501),(2,'Смирнова Елена Олеговна','21, улица Мира, Кулацкий, Усть-Абакан, Усть-Абаканский поссовет, Усть-Абаканский район, Республика Хакасия, Сибирский федеральный округ, 655163, Россия','+7(916)987-65-43','smirnova.e@yandex.ru',1,'2026-01-31 14:10:08','77.88.8.8',3,53.8479812,91.3737632),(3,'Соколов Дмитрий Иванович','5, улица Ленина, Рынок, Усть-Абакан, Усть-Абаканский поссовет, Усть-Абаканский район, Республика Хакасия, Сибирский федеральный округ, 655102, Россия','+7(926)555-44-33','sokol_d@gmail.com',3,'2025-08-29 14:10:08','1.1.1.1',8,53.8293521,91.3946377),(4,'Попова Мария Сергеевна','1, улица Пушкина, Абакан, городской округ Абакан, Республика Хакасия, Сибирский федеральный округ, 655012, Россия','+7(905)111-22-33','popova_m@mail.ru',4,'2026-03-07 14:10:08','192.168.255.10',4,53.7166374,91.4789394),(5,'Морозов Константин Юрьевич','улица Маршала Жукова, Абакан 5','+7(985)444-55-66','morozov_k@bk.ru',2,'2025-05-21 14:10:08','10.0.55.200',5,53.7350542,91.4581427),(6,'Волкова Анастасия Петровна','улица Маршала Жукова, Абакан 6','+7(999)888-77-66','volk_a@inbox.ru',1,'2026-03-12 14:10:08','8.8.4.4',5,53.7408842,91.4563633),(7,'ООО \"Вектор-Плюс\" (Юр. лицо)','21, проспект Ленина, Абакан, городской округ Абакан, Республика Хакасия, Сибирский федеральный округ, 655012, Россия','+7(495)123-00-00','info@vector-plus.ru',4,'2025-02-10 14:10:08','9.9.9.9',7,53.7248110,91.4674675),(8,'Соломатин Алексей Дмитриевич','2, улица Некрасова, Сахарный, Усть-Абакан, Усть-Абаканский поссовет, Усть-Абаканский район, Республика Хакасия, Сибирский федеральный округ, 655102, Россия','23432423423','вфцвфцвфцв@safaw.xom',4,'2026-03-17 14:23:59','192.0.2.1',10,53.8537304,91.3837481),(9,'awedawdawd','3, проспект Ленина, Абакан, городской округ Абакан, Республика Хакасия, Сибирский федеральный округ, 655012, Россия','435435345','dawdawd',4,'2026-03-17 14:25:21','10.255.255.254',9,53.7251604,91.4701806),(10,'Соломатин Дмитрий Александрович','12, проспект Ленина, Абакан, городской округ Абакан, Республика Хакасия, Сибирский федеральный округ, 655012, Россия','3243423','фцвфцв',3,'2026-04-15 18:15:18','1.1.1.1',1,53.7255473,91.4689770);
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `house_incidents`
--

DROP TABLE IF EXISTS `house_incidents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `house_incidents` (
  `incident_id` int NOT NULL AUTO_INCREMENT,
  `house_id` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `severity` varchar(20) NOT NULL DEFAULT 'Средняя',
  `status` varchar(20) NOT NULL DEFAULT 'Активна',
  `description` text,
  `started_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `resolved_at` datetime DEFAULT NULL,
  PRIMARY KEY (`incident_id`),
  KEY `idx_house_incidents_status` (`house_id`,`status`),
  KEY `idx_house_incidents_started` (`started_at`),
  CONSTRAINT `house_incidents_ibfk_1` FOREIGN KEY (`house_id`) REFERENCES `city_houses` (`house_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `house_incidents`
--

LOCK TABLES `house_incidents` WRITE;
/*!40000 ALTER TABLE `house_incidents` DISABLE KEYS */;
INSERT INTO `house_incidents` VALUES (1,1,'Нет связи в доме','Средняя','Активна','','2026-04-15 19:36:38',NULL);
/*!40000 ALTER TABLE `house_incidents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `message_id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `sender_type` enum('client','support') NOT NULL,
  `sender_name` varchar(255) DEFAULT NULL,
  `text` text NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_read` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`message_id`),
  KEY `customer_id` (`customer_id`,`created_at`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES (1,5,'client','Морозов Константин Юрьевич','c','2026-04-10 21:10:16',1),(2,5,'support','Главный Администратор','p','2026-04-10 21:10:25',1),(3,5,'support','Главный Администратор','cs','2026-04-10 21:10:32',1),(4,5,'client','Морозов Константин Юрьевич','dsvd','2026-04-10 21:24:01',1),(5,5,'client','Морозов Константин Юрьевич','123','2026-04-10 21:31:08',1),(6,4,'client','Попова Мария Сергеевна','салам','2026-04-14 15:23:35',1),(7,4,'support','Главный Администратор','ывфаыфуа','2026-04-14 15:23:47',1);
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `network_incidents`
--

DROP TABLE IF EXISTS `network_incidents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `network_incidents` (
  `incident_id` int NOT NULL AUTO_INCREMENT,
  `node_id` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `severity` varchar(20) NOT NULL DEFAULT 'Средняя',
  `status` varchar(20) NOT NULL DEFAULT 'Активна',
  `description` text,
  `started_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `resolved_at` datetime DEFAULT NULL,
  PRIMARY KEY (`incident_id`),
  KEY `node_id` (`node_id`,`status`),
  KEY `started_at` (`started_at`),
  CONSTRAINT `network_incidents_ibfk_1` FOREIGN KEY (`node_id`) REFERENCES `network_nodes` (`node_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `network_incidents`
--

LOCK TABLES `network_incidents` WRITE;
/*!40000 ALTER TABLE `network_incidents` DISABLE KEYS */;
INSERT INTO `network_incidents` VALUES (1,2,'Потеря связи','Средняя','Закрыта','взрыв\n[Закрытие] Восстановлено\n[Закрытие] Восстановлено','2026-04-14 21:41:02','2026-04-14 21:54:50'),(2,1,'Потеря связи','Средняя','Закрыта','Взрыв\n[Закрытие] Восстановлено','2026-04-14 21:44:31','2026-04-14 21:52:10'),(3,2,'Потеря связи','Критическая','Закрыта','sedsdf\n[Закрытие] Восстановлено','2026-04-14 21:54:25','2026-04-14 21:54:38'),(4,1,'Потеря связи','Критическая','Закрыта','\n[Закрытие] Восстановлено','2026-04-15 11:21:41','2026-04-15 11:21:52'),(5,2,'Потеря связи','Средняя','Закрыта','взрыв\n[Закрытие] Восстановлено','2026-04-15 11:22:07','2026-04-15 11:22:15');
/*!40000 ALTER TABLE `network_incidents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `network_nodes`
--

DROP TABLE IF EXISTS `network_nodes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `network_nodes` (
  `node_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `node_type` varchar(50) NOT NULL DEFAULT 'Роутер',
  `location` varchar(255) DEFAULT NULL,
  `x_pos` int DEFAULT '0',
  `y_pos` int DEFAULT '0',
  `status` varchar(30) NOT NULL DEFAULT 'OK',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`node_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `network_nodes`
--

LOCK TABLES `network_nodes` WRITE;
/*!40000 ALTER TABLE `network_nodes` DISABLE KEYS */;
INSERT INTO `network_nodes` VALUES (1,'1','Роутер','Центральный узел',0,0,'OK','2026-04-14 21:40:23'),(2,'2','Роутер','Центральный узел',0,0,'OK','2026-04-14 21:40:37'),(3,'edd','Роутер','Центральный узел',0,0,'OK','2026-04-14 21:50:59');
/*!40000 ALTER TABLE `network_nodes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `operators`
--

DROP TABLE IF EXISTS `operators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `operators` (
  `operator_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  PRIMARY KEY (`operator_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `operators`
--

LOCK TABLES `operators` WRITE;
/*!40000 ALTER TABLE `operators` DISABLE KEYS */;
INSERT INTO `operators` VALUES (1,'admin','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','Главный Администратор'),(2,'smirnov_p','5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5','Смирнов Петр (1 Линия)'),(3,'kuznetsova_a','5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5','Кузнецова Анна (Инженер)');
/*!40000 ALTER TABLE `operators` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plans`
--

DROP TABLE IF EXISTS `plans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plans` (
  `plan_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `speed` varchar(50) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `data_limit` varchar(50) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`plan_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plans`
--

LOCK TABLES `plans` WRITE;
/*!40000 ALTER TABLE `plans` DISABLE KEYS */;
INSERT INTO `plans` VALUES (1,'Базовый (Медь)','100 Мбит/с',450.00,NULL,NULL),(2,'Оптимальный (Оптика)','300 Мбит/с',650.00,'1000','dssdf'),(3,'Игровой+','500 Мбит/с',890.00,NULL,NULL),(4,'Гигабит PRO','1000 Мбит/с',1200.00,NULL,NULL);
/*!40000 ALTER TABLE `plans` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-16 11:14:27
