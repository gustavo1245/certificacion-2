-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema proyecto_crud
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `proyecto_crud` ;

-- -----------------------------------------------------
-- Schema proyecto_crud
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `proyecto_crud` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `proyecto_crud` ;

-- -----------------------------------------------------
-- Table `proyecto_crud`.`usuarios`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `proyecto_crud`.`usuarios` ;

CREATE TABLE IF NOT EXISTS `proyecto_crud`.`usuarios` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(45) NOT NULL,
  `apellido` VARCHAR(45) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `creado_en` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email` (`email` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `proyecto_crud`.`travel_plans`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `proyecto_crud`.`travel_plans` ;

CREATE TABLE IF NOT EXISTS `proyecto_crud`.`travel_plans` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `destination` VARCHAR(255) NOT NULL,
  `description` TEXT,
  `travel_start_date` DATE NOT NULL,
  `travel_end_date` DATE NOT NULL,
  `plan` TEXT NOT NULL,
  `autor_id` INT NOT NULL,
  `is_active` BOOLEAN DEFAULT TRUE,
  `creado_en` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `actualizado_en` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `fk_travel_plans_usuarios_idx` (`autor_id` ASC) VISIBLE,
  CONSTRAINT `fk_travel_plans_usuarios`
    FOREIGN KEY (`autor_id`)
    REFERENCES `proyecto_crud`.`usuarios` (`id`)
    ON DELETE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `proyecto_crud`.`trip_schedules`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `proyecto_crud`.`trip_schedules` ;

CREATE TABLE IF NOT EXISTS `proyecto_crud`.`trip_schedules` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `travel_plan_id` INT NOT NULL,
  `usuario_id` INT NOT NULL,
  `joined_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `fk_trip_schedules_usuarios_idx` (`usuario_id` ASC) VISIBLE,
  INDEX `fk_trip_schedules_travel_plans_idx` (`travel_plan_id` ASC) VISIBLE,
  CONSTRAINT `fk_trip_schedules_travel_plans`
    FOREIGN KEY (`travel_plan_id`)
    REFERENCES `proyecto_crud`.`travel_plans` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `fk_trip_schedules_usuarios`
    FOREIGN KEY (`usuario_id`)
    REFERENCES `proyecto_crud`.`usuarios` (`id`)
    ON DELETE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;