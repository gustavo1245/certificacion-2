-- Agregar columna edad a la tabla usuarios
USE proyecto_crud;

ALTER TABLE usuarios 
ADD COLUMN edad INT NOT NULL DEFAULT 18 AFTER apellido;
