-- Create database and tables for reservation_parking
CREATE DATABASE IF NOT EXISTS reservation_parking CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE reservation_parking;

-- Users
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  is_admin TINYINT(1) NOT NULL DEFAULT 0,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Parking spots
CREATE TABLE IF NOT EXISTS parking_spots (
  id INT AUTO_INCREMENT PRIMARY KEY,
  spot_number VARCHAR(32) NOT NULL UNIQUE,
  active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Reservations
CREATE TABLE IF NOT EXISTS reservations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
  household VARCHAR(64) NOT NULL,
  phone VARCHAR(32) NOT NULL,
  spot_id INT NOT NULL,
  start_time DATETIME NOT NULL,
  end_time DATETIME NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_reservations_spot FOREIGN KEY (spot_id) REFERENCES parking_spots(id) ON DELETE CASCADE,
  INDEX idx_reservations_spot_time (spot_id, start_time, end_time)
) ENGINE=InnoDB;

-- Seed sample spots
INSERT INTO parking_spots (spot_number)
SELECT * FROM (
  SELECT 'A-01' UNION ALL SELECT 'A-02' UNION ALL SELECT 'A-03' UNION ALL SELECT 'A-04' UNION ALL SELECT 'A-05'
) AS tmp
WHERE NOT EXISTS (SELECT 1 FROM parking_spots LIMIT 1);

-- Note: Overlap prevention is handled at the application layer in FastAPI.
