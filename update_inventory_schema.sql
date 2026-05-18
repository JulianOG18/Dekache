-- ==========================================================
-- SCRIPT DE ACTUALIZACIÓN DE BASE DE DATOS - DEKACHE
-- HU-07: GESTIÓN DE INVENTARIO Y MONITOR DE INSUMOS
-- ==========================================================

-- 1. Agregar columna para el umbral mínimo (Stock Crítico)
-- Las alertas críticas empiezan cuando el stock es menor o igual a 20 unidades.
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'Insumos' AND COLUMN_NAME = 'stock_minimo'
)
BEGIN
    ALTER TABLE Insumos ADD stock_minimo DECIMAL(10,2) NOT NULL DEFAULT 20.0;
END
GO

-- 2. Agregar columna para el stock máximo (Utilizado para calcular porcentaje de barras de progreso)
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = 'Insumos' AND COLUMN_NAME = 'stock_maximo'
)
BEGIN
    ALTER TABLE Insumos ADD stock_maximo DECIMAL(10,2) NOT NULL DEFAULT 100.0;
END
GO

-- 3. Ejemplo de actualización de insumos a valores reales (Opcional):
-- UPDATE Insumos SET stock_minimo = 20.0, stock_maximo = 120.0 WHERE nombre = 'Carne de Res';
-- UPDATE Insumos SET stock_minimo = 15.0, stock_maximo = 80.0 WHERE nombre = 'Queso Cheddar';
