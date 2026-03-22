CREATE DATABASE  IF NOT EXISTS `ledgerpro` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `ledgerpro`;
-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: ledgerpro
-- ------------------------------------------------------
-- Server version	8.0.45

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
-- Table structure for table `bill_items`
--

DROP TABLE IF EXISTS `bill_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bill_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bill_id` int NOT NULL,
  `item_id` int NOT NULL,
  `quantity` double NOT NULL,
  `rate` double NOT NULL,
  `gst_percent` double DEFAULT '0',
  `amount` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bill_id` (`bill_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `bill_items_ibfk_1` FOREIGN KEY (`bill_id`) REFERENCES `bills` (`id`),
  CONSTRAINT `bill_items_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bills`
--

DROP TABLE IF EXISTS `bills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bills` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bill_number` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `vendor_id` int NOT NULL,
  `date` date NOT NULL,
  `due_date` date DEFAULT NULL,
  `subtotal` double DEFAULT '0',
  `tax_amount` double DEFAULT '0',
  `grand_total` double DEFAULT '0',
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'Draft',
  `order_number` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `payment_terms` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reverse_charge` tinyint DEFAULT '0',
  `adjustment` double DEFAULT '0',
  `tds_amount` double DEFAULT '0',
  `tcs_amount` double DEFAULT '0',
  `attachment_path` text COLLATE utf8mb4_unicode_ci,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `discount_amount` double DEFAULT '0',
  `custom_fields` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `vendor_id` (`vendor_id`),
  CONSTRAINT `bills_ibfk_1` FOREIGN KEY (`vendor_id`) REFERENCES `vendors` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `customer_balance`
--

DROP TABLE IF EXISTS `customer_balance`;
/*!50001 DROP VIEW IF EXISTS `customer_balance`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `customer_balance` AS SELECT 
 1 AS `id`,
 1 AS `name`,
 1 AS `balance`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` text COLLATE utf8mb4_unicode_ci,
  `gstin` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'Type 1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `inventory_status`
--

DROP TABLE IF EXISTS `inventory_status`;
/*!50001 DROP VIEW IF EXISTS `inventory_status`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `inventory_status` AS SELECT 
 1 AS `name`,
 1 AS `stock_on_hand`,
 1 AS `purchase_price`,
 1 AS `selling_price`,
 1 AS `stock_value`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `invoice_details`
--

DROP TABLE IF EXISTS `invoice_details`;
/*!50001 DROP VIEW IF EXISTS `invoice_details`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `invoice_details` AS SELECT 
 1 AS `invoice_number`,
 1 AS `customer_name`,
 1 AS `item_name`,
 1 AS `quantity`,
 1 AS `rate`,
 1 AS `amount`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `invoice_items`
--

DROP TABLE IF EXISTS `invoice_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_id` int NOT NULL,
  `item_id` int NOT NULL,
  `quantity` double NOT NULL,
  `rate` double NOT NULL,
  `discount_percent` double DEFAULT '0',
  `gst_percent` double DEFAULT '0',
  `amount` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `invoice_id` (`invoice_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `invoice_items_ibfk_1` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`),
  CONSTRAINT `invoice_items_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `invoice_summary`
--

DROP TABLE IF EXISTS `invoice_summary`;
/*!50001 DROP VIEW IF EXISTS `invoice_summary`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `invoice_summary` AS SELECT 
 1 AS `id`,
 1 AS `invoice_number`,
 1 AS `customer_name`,
 1 AS `date`,
 1 AS `due_date`,
 1 AS `grand_total`,
 1 AS `status`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `invoices`
--

DROP TABLE IF EXISTS `invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_number` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_id` int NOT NULL,
  `date` date NOT NULL,
  `due_date` date DEFAULT NULL,
  `subtotal` double DEFAULT '0',
  `tax_amount` double DEFAULT '0',
  `discount_amount` double DEFAULT '0',
  `grand_total` double DEFAULT '0',
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'Draft',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `order_number` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `terms` text COLLATE utf8mb4_unicode_ci,
  `salesperson` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `subject` text COLLATE utf8mb4_unicode_ci,
  `customer_notes` text COLLATE utf8mb4_unicode_ci,
  `terms_conditions` text COLLATE utf8mb4_unicode_ci,
  `round_off` double DEFAULT '0',
  `tds_amount` double DEFAULT '0',
  `tcs_amount` double DEFAULT '0',
  `attachment_path` text COLLATE utf8mb4_unicode_ci,
  `custom_fields` text COLLATE utf8mb4_unicode_ci,
  `adjustment` double DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `invoice_number` (`invoice_number`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `invoices_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sku` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `hsn_sac` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gst_rate` double DEFAULT '0',
  `description` text COLLATE utf8mb4_unicode_ci,
  `unit` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'pcs',
  `selling_price` double DEFAULT '0',
  `sp1` double DEFAULT '0',
  `sp2` double DEFAULT '0',
  `sp3` double DEFAULT '0',
  `purchase_price` double DEFAULT '0',
  `reorder_point` double DEFAULT '0',
  `stock_on_hand` double DEFAULT '0',
  `opening_stock` double DEFAULT '0',
  `opening_stock_value` double DEFAULT '0',
  `account_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `purchase_account_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `inventory_account_code` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `taxable` tinyint DEFAULT '1',
  `exemption_reason` text COLLATE utf8mb4_unicode_ci,
  `taxability_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `intra_state_tax_rate` double DEFAULT '0',
  `inter_state_tax_rate` double DEFAULT '0',
  `purchase_description` text COLLATE utf8mb4_unicode_ci,
  `inventory_valuation_method` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `item_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'Goods',
  `is_sellable` tinyint DEFAULT '1',
  `is_purchasable` tinyint DEFAULT '1',
  `track_inventory` tinyint DEFAULT '1',
  `vendor_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sku` (`sku`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ledger`
--

DROP TABLE IF EXISTS `ledger`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ledger` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `account_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `account_id` int DEFAULT NULL,
  `reference_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reference_id` int DEFAULT NULL,
  `debit` double DEFAULT '0',
  `credit` double DEFAULT '0',
  `description` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `ledger_view`
--

DROP TABLE IF EXISTS `ledger_view`;
/*!50001 DROP VIEW IF EXISTS `ledger_view`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `ledger_view` AS SELECT 
 1 AS `date`,
 1 AS `account_type`,
 1 AS `account_id`,
 1 AS `reference_type`,
 1 AS `reference_id`,
 1 AS `debit`,
 1 AS `credit`,
 1 AS `balance_effect`,
 1 AS `description`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `monthly_profit`
--

DROP TABLE IF EXISTS `monthly_profit`;
/*!50001 DROP VIEW IF EXISTS `monthly_profit`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `monthly_profit` AS SELECT 
 1 AS `month`,
 1 AS `total_sales`,
 1 AS `total_cost`,
 1 AS `profit`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `monthly_revenue`
--

DROP TABLE IF EXISTS `monthly_revenue`;
/*!50001 DROP VIEW IF EXISTS `monthly_revenue`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `monthly_revenue` AS SELECT 
 1 AS `month`,
 1 AS `total_invoices`,
 1 AS `total_revenue`,
 1 AS `total_tax`,
 1 AS `total_discount`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `payment_history`
--

DROP TABLE IF EXISTS `payment_history`;
/*!50001 DROP VIEW IF EXISTS `payment_history`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `payment_history` AS SELECT 
 1 AS `id`,
 1 AS `amount`,
 1 AS `date`,
 1 AS `customer_name`,
 1 AS `vendor_name`,
 1 AS `method`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_id` int DEFAULT NULL,
  `bill_id` int DEFAULT NULL,
  `customer_id` int DEFAULT NULL,
  `vendor_id` int DEFAULT NULL,
  `amount` double NOT NULL,
  `date` date NOT NULL,
  `method` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `payment_number` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `deposit_to` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bank_charges` double DEFAULT '0',
  `tax_deducted` double DEFAULT '0',
  `tax_account` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `attachment_path` text COLLATE utf8mb4_unicode_ci,
  `reference` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `send_thank_you` tinyint DEFAULT '0',
  `custom_fields` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `invoice_id` (`invoice_id`),
  KEY `bill_id` (`bill_id`),
  KEY `customer_id` (`customer_id`),
  KEY `vendor_id` (`vendor_id`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`),
  CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`bill_id`) REFERENCES `bills` (`id`),
  CONSTRAINT `payments_ibfk_3` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `payments_ibfk_4` FOREIGN KEY (`vendor_id`) REFERENCES `vendors` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `profit_report`
--

DROP TABLE IF EXISTS `profit_report`;
/*!50001 DROP VIEW IF EXISTS `profit_report`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `profit_report` AS SELECT 
 1 AS `total_sales`,
 1 AS `total_cost`,
 1 AS `profit`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `settings` (
  `key` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stock_batches`
--

DROP TABLE IF EXISTS `stock_batches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stock_batches` (
  `id` int NOT NULL AUTO_INCREMENT,
  `item_id` int NOT NULL,
  `quantity_remaining` double NOT NULL,
  `purchase_rate` double NOT NULL,
  `purchase_date` date NOT NULL,
  `vendor_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `item_id` (`item_id`),
  KEY `vendor_id` (`vendor_id`),
  CONSTRAINT `stock_batches_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`id`),
  CONSTRAINT `stock_batches_ibfk_2` FOREIGN KEY (`vendor_id`) REFERENCES `vendors` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `vendor_summary`
--

DROP TABLE IF EXISTS `vendor_summary`;
/*!50001 DROP VIEW IF EXISTS `vendor_summary`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vendor_summary` AS SELECT 
 1 AS `id`,
 1 AS `name`,
 1 AS `total_purchases`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `vendors`
--

DROP TABLE IF EXISTS `vendors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vendors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` text COLLATE utf8mb4_unicode_ci,
  `gstin` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `customer_balance`
--

/*!50001 DROP VIEW IF EXISTS `customer_balance`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `customer_balance` AS select `c`.`id` AS `id`,`c`.`name` AS `name`,(ifnull(sum(`i`.`grand_total`),0) - ifnull(sum(`p`.`amount`),0)) AS `balance` from ((`customers` `c` left join `invoices` `i` on((`c`.`id` = `i`.`customer_id`))) left join `payments` `p` on((`c`.`id` = `p`.`customer_id`))) group by `c`.`id`,`c`.`name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `inventory_status`
--

/*!50001 DROP VIEW IF EXISTS `inventory_status`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `inventory_status` AS select `items`.`name` AS `name`,`items`.`stock_on_hand` AS `stock_on_hand`,`items`.`purchase_price` AS `purchase_price`,`items`.`selling_price` AS `selling_price`,(`items`.`stock_on_hand` * `items`.`purchase_price`) AS `stock_value` from `items` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `invoice_details`
--

/*!50001 DROP VIEW IF EXISTS `invoice_details`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `invoice_details` AS select `i`.`invoice_number` AS `invoice_number`,`c`.`name` AS `customer_name`,`it`.`name` AS `item_name`,`ii`.`quantity` AS `quantity`,`ii`.`rate` AS `rate`,`ii`.`amount` AS `amount` from (((`invoice_items` `ii` join `invoices` `i` on((`ii`.`invoice_id` = `i`.`id`))) join `items` `it` on((`ii`.`item_id` = `it`.`id`))) join `customers` `c` on((`i`.`customer_id` = `c`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `invoice_summary`
--

/*!50001 DROP VIEW IF EXISTS `invoice_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `invoice_summary` AS select `i`.`id` AS `id`,`i`.`invoice_number` AS `invoice_number`,`c`.`name` AS `customer_name`,`i`.`date` AS `date`,`i`.`due_date` AS `due_date`,`i`.`grand_total` AS `grand_total`,`i`.`status` AS `status` from (`invoices` `i` join `customers` `c` on((`i`.`customer_id` = `c`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `ledger_view`
--

/*!50001 DROP VIEW IF EXISTS `ledger_view`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `ledger_view` AS select `l`.`date` AS `date`,`l`.`account_type` AS `account_type`,`l`.`account_id` AS `account_id`,`l`.`reference_type` AS `reference_type`,`l`.`reference_id` AS `reference_id`,`l`.`debit` AS `debit`,`l`.`credit` AS `credit`,(`l`.`debit` - `l`.`credit`) AS `balance_effect`,`l`.`description` AS `description` from `ledger` `l` order by `l`.`date` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `monthly_profit`
--

/*!50001 DROP VIEW IF EXISTS `monthly_profit`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `monthly_profit` AS select date_format(`i`.`date`,'%Y-%m') AS `month`,sum(`ii`.`amount`) AS `total_sales`,sum((`ii`.`quantity` * `it`.`purchase_price`)) AS `total_cost`,(sum(`ii`.`amount`) - sum((`ii`.`quantity` * `it`.`purchase_price`))) AS `profit` from ((`invoice_items` `ii` join `invoices` `i` on((`ii`.`invoice_id` = `i`.`id`))) join `items` `it` on((`ii`.`item_id` = `it`.`id`))) where (`i`.`status` <> 'Draft') group by date_format(`i`.`date`,'%Y-%m') order by `month` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `monthly_revenue`
--

/*!50001 DROP VIEW IF EXISTS `monthly_revenue`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `monthly_revenue` AS select date_format(`invoices`.`date`,'%Y-%m') AS `month`,count(`invoices`.`id`) AS `total_invoices`,sum(`invoices`.`grand_total`) AS `total_revenue`,sum(`invoices`.`tax_amount`) AS `total_tax`,sum(`invoices`.`discount_amount`) AS `total_discount` from `invoices` where (`invoices`.`status` <> 'Draft') group by date_format(`invoices`.`date`,'%Y-%m') order by `month` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `payment_history`
--

/*!50001 DROP VIEW IF EXISTS `payment_history`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `payment_history` AS select `p`.`id` AS `id`,`p`.`amount` AS `amount`,`p`.`date` AS `date`,`c`.`name` AS `customer_name`,`v`.`name` AS `vendor_name`,`p`.`method` AS `method` from ((`payments` `p` left join `customers` `c` on((`p`.`customer_id` = `c`.`id`))) left join `vendors` `v` on((`p`.`vendor_id` = `v`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `profit_report`
--

/*!50001 DROP VIEW IF EXISTS `profit_report`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `profit_report` AS select sum(`ii`.`amount`) AS `total_sales`,sum((`ii`.`quantity` * `it`.`purchase_price`)) AS `total_cost`,(sum(`ii`.`amount`) - sum((`ii`.`quantity` * `it`.`purchase_price`))) AS `profit` from (`invoice_items` `ii` join `items` `it` on((`ii`.`item_id` = `it`.`id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vendor_summary`
--

/*!50001 DROP VIEW IF EXISTS `vendor_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vendor_summary` AS select `v`.`id` AS `id`,`v`.`name` AS `name`,sum(`b`.`grand_total`) AS `total_purchases` from (`vendors` `v` left join `bills` `b` on((`v`.`id` = `b`.`vendor_id`))) group by `v`.`id`,`v`.`name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-22 20:21:01
