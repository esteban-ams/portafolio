-- =============================================================================
-- Script de Inicializacion de Bases de Datos
-- =============================================================================
-- Este script se ejecuta automaticamente cuando PostgreSQL inicia por primera vez
-- Agrega aqui las bases de datos adicionales que necesites para tus proyectos
-- =============================================================================

-- Base de datos para Komercia (Django ERP)
CREATE DATABASE komercia;

-- Log de inicializacion
DO $$
BEGIN
    RAISE NOTICE 'Bases de datos creadas:';
    RAISE NOTICE '  - main (default)';
    RAISE NOTICE '  - komercia (Django ERP)';
    RAISE NOTICE 'Inicializacion completada - %', NOW();
END $$;
