-- Script de migración para Travel Dashboard
-- Ejecutar este script para convertir la aplicación de citas a planes de viaje

USE proyecto_crud;

-- Crear tabla de planes de viaje
CREATE TABLE IF NOT EXISTS travel_plans (
  id INT NOT NULL AUTO_INCREMENT,
  destination VARCHAR(255) NOT NULL,
  description TEXT,
  travel_start_date DATE NOT NULL,
  travel_end_date DATE NOT NULL,
  plan TEXT NOT NULL,
  autor_id INT NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX fk_travel_plans_usuarios_idx (autor_id ASC),
  CONSTRAINT fk_travel_plans_usuarios
    FOREIGN KEY (autor_id)
    REFERENCES usuarios (id)
    ON DELETE CASCADE
) ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

-- Crear tabla de trip schedules (planes a los que los usuarios se unen)
CREATE TABLE IF NOT EXISTS trip_schedules (
  id INT NOT NULL AUTO_INCREMENT,
  travel_plan_id INT NOT NULL,
  usuario_id INT NOT NULL,
  joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX fk_trip_schedules_usuarios_idx (usuario_id ASC),
  INDEX fk_trip_schedules_travel_plans_idx (travel_plan_id ASC),
  CONSTRAINT fk_trip_schedules_travel_plans
    FOREIGN KEY (travel_plan_id)
    REFERENCES travel_plans (id)
    ON DELETE CASCADE,
  CONSTRAINT fk_trip_schedules_usuarios
    FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id)
    ON DELETE CASCADE
) ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

-- Insertar algunos datos de ejemplo para testing
INSERT INTO travel_plans (destination, description, travel_start_date, travel_end_date, plan, autor_id) VALUES
('París, Francia', 'Viaje cultural por la ciudad del amor', '2025-12-01', '2025-12-07', 'City Tour & Museums', 1),
('Tokyo, Japón', 'Aventura gastronómica y cultural', '2026-03-15', '2026-03-22', 'Food Tour & Temples', 1),
('Nueva York, USA', 'Explorar la gran manzana', '2026-01-10', '2026-01-15', 'Broadway & Central Park', 2);

-- Insertar algunos trip schedules de ejemplo
-- (Esto simula que el usuario 1 se unió al viaje de Nueva York creado por el usuario 2)
INSERT INTO trip_schedules (travel_plan_id, usuario_id) VALUES (3, 1);

-- Opcional: Migrar datos existentes de citas a travel_plans
-- (Descomenta las siguientes líneas si quieres migrar las citas existentes)
/*
INSERT INTO travel_plans (destination, description, travel_start_date, travel_end_date, plan, autor_id, creado_en)
SELECT 
    CONCAT('Destino de ', SUBSTRING(cita, 1, 20), '...') as destination,
    'Migrado desde reflexión anterior' as description,
    DATE_ADD(CURDATE(), INTERVAL 30 DAY) as travel_start_date,
    DATE_ADD(CURDATE(), INTERVAL 37 DAY) as travel_end_date,
    cita as plan,
    autor_id,
    creado_en
FROM citas 
WHERE LENGTH(cita) > 10;
*/

SELECT 'Migration completed successfully!' as status;
