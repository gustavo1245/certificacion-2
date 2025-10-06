-- Agregar columna fecha_nacimiento a la tabla usuarios
USE proyecto_crud;

ALTER TABLE usuarios 
ADD COLUMN fecha_nacimiento DATE NOT NULL AFTER apellido;
