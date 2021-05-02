-- MySQL dump 10.13  Distrib 8.0.23, for Win64 (x86_64)
--
-- Host: localhost    Database: hoppaq_database
-- ------------------------------------------------------
-- Server version	8.0.23

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
-- Table structure for table `brand`
--

DROP TABLE IF EXISTS `brand`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `brand` (
  `idbrand` int NOT NULL,
  `namebrand` varchar(45) NOT NULL,
  `n_productsbrand` int DEFAULT NULL,
  `categorybrand` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`idbrand`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brand`
--

LOCK TABLES `brand` WRITE;
/*!40000 ALTER TABLE `brand` DISABLE KEYS */;
INSERT INTO `brand` VALUES (1,'Parle Platinum',1,'cookies');
/*!40000 ALTER TABLE `brand` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoice`
--

DROP TABLE IF EXISTS `invoice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice` (
  `idinvoice` int NOT NULL,
  `iduser` int NOT NULL,
  `billdate` int NOT NULL,
  `billamount` int NOT NULL,
  PRIMARY KEY (`idinvoice`),
  KEY `inv-user_idx` (`iduser`),
  CONSTRAINT `inv-user` FOREIGN KEY (`iduser`) REFERENCES `user` (`iduser`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice`
--

LOCK TABLES `invoice` WRITE;
/*!40000 ALTER TABLE `invoice` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoice` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item`
--

DROP TABLE IF EXISTS `item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item` (
  `iditem` int NOT NULL,
  `idinvoice` int NOT NULL,
  `idproduct` int NOT NULL,
  `iduser` int NOT NULL,
  `date` date NOT NULL,
  PRIMARY KEY (`iditem`),
  KEY `item-user_idx` (`iduser`),
  KEY `item-prod_idx` (`idproduct`),
  KEY `item-inv_idx` (`idinvoice`),
  CONSTRAINT `item-inv` FOREIGN KEY (`idinvoice`) REFERENCES `invoice` (`idinvoice`),
  CONSTRAINT `item-prod` FOREIGN KEY (`idproduct`) REFERENCES `product` (`idproduct`),
  CONSTRAINT `item-user` FOREIGN KEY (`iduser`) REFERENCES `user` (`iduser`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item`
--

LOCK TABLES `item` WRITE;
/*!40000 ALTER TABLE `item` DISABLE KEYS */;
/*!40000 ALTER TABLE `item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product`
--

DROP TABLE IF EXISTS `product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product` (
  `idproduct` int NOT NULL,
  `idbrand` int NOT NULL,
  `nameproduct` varchar(45) NOT NULL,
  `typeproduct` varchar(45) NOT NULL,
  `quantityproduct` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`idproduct`),
  KEY `prod-brand_idx` (`idbrand`),
  CONSTRAINT `product-brand` FOREIGN KEY (`idbrand`) REFERENCES `brand` (`idbrand`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product`
--

LOCK TABLES `product` WRITE;
/*!40000 ALTER TABLE `product` DISABLE KEYS */;
INSERT INTO `product` VALUES (1,1,'Milano chocolate chip cookies','cookies',10);
/*!40000 ALTER TABLE `product` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_description`
--

DROP TABLE IF EXISTS `product_description`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_description` (
  `idproduct` int NOT NULL,
  `idbrand` int NOT NULL,
  `product_name` varchar(45) NOT NULL,
  `description` varchar(45) NOT NULL,
  `manufacture_date` date NOT NULL,
  `expiration_date` date NOT NULL,
  KEY `desc-prod_idx` (`idproduct`),
  KEY `prod-brand_idx` (`idbrand`),
  CONSTRAINT `desc-prod` FOREIGN KEY (`idproduct`) REFERENCES `product` (`idproduct`),
  CONSTRAINT `prod-brand` FOREIGN KEY (`idbrand`) REFERENCES `brand` (`idbrand`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_description`
--

LOCK TABLES `product_description` WRITE;
/*!40000 ALTER TABLE `product_description` DISABLE KEYS */;
INSERT INTO `product_description` VALUES (1,1,'Milano chocolate chip cookies','Milano chocolate chip cookie','2020-09-07','2021-04-07');
/*!40000 ALTER TABLE `product_description` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_price`
--

DROP TABLE IF EXISTS `product_price`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_price` (
  `idproduct` int NOT NULL,
  `priceproduct` float NOT NULL,
  KEY `price-prod_idx` (`idproduct`),
  CONSTRAINT `price-prod` FOREIGN KEY (`idproduct`) REFERENCES `product` (`idproduct`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_price`
--

LOCK TABLES `product_price` WRITE;
/*!40000 ALTER TABLE `product_price` DISABLE KEYS */;
INSERT INTO `product_price` VALUES (1,30);
/*!40000 ALTER TABLE `product_price` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_weights`
--

DROP TABLE IF EXISTS `product_weights`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_weights` (
  `idproduct` int NOT NULL,
  `weightproduct` int NOT NULL DEFAULT '0',
  KEY `prod-weight_idx` (`idproduct`),
  CONSTRAINT `prod-weight` FOREIGN KEY (`idproduct`) REFERENCES `product` (`idproduct`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_weights`
--

LOCK TABLES `product_weights` WRITE;
/*!40000 ALTER TABLE `product_weights` DISABLE KEYS */;
INSERT INTO `product_weights` VALUES (1,100);
/*!40000 ALTER TABLE `product_weights` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `iduser` int NOT NULL,
  `name` varchar(45) NOT NULL,
  `gender` varchar(45) NOT NULL,
  `country` varchar(45) NOT NULL,
  `email` date NOT NULL,
  PRIMARY KEY (`iduser`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_wallet`
--

DROP TABLE IF EXISTS `user_wallet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_wallet` (
  `iduser` int DEFAULT NULL,
  `amount` int DEFAULT NULL,
  `fines` int DEFAULT NULL,
  `dues` int DEFAULT NULL,
  KEY `user-wallet_idx` (`iduser`),
  CONSTRAINT `user-wallet` FOREIGN KEY (`iduser`) REFERENCES `user` (`iduser`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_wallet`
--

LOCK TABLES `user_wallet` WRITE;
/*!40000 ALTER TABLE `user_wallet` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_wallet` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-05-02 14:28:27
