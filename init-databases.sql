-- Script de inicialización para crear ambas bases de datos
-- Se ejecuta automáticamente al iniciar el contenedor de PostgreSQL

-- Base de datos para tournaments-service
CREATE DATABASE tournaments_db;

-- Base de datos para matches-service
CREATE DATABASE matches_db;

-- Conectar a tournaments_db para verificar
\c tournaments_db;
SELECT 'tournaments_db creada exitosamente' AS status;

-- Conectar a matches_db para verificar
\c matches_db;
SELECT 'matches_db creada exitosamente' AS status;