-- =============================================================
-- schema.sql
-- Script de criação do banco e da tabela 'clientes'.
--
-- Uso alternativo ao SQLModel.metadata.create_all(): execute este script
-- manualmente caso prefira provisionar o banco de forma explícita/versionada
-- (recomendado em pipelines de CI/CD e ambientes de produção).
-- =============================================================

CREATE DATABASE IF NOT EXISTS cadastro_clientes
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE cadastro_clientes;

CREATE TABLE IF NOT EXISTS clientes (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(150) NOT NULL,
    email           VARCHAR(150) NOT NULL,
    telefone        VARCHAR(20)  NOT NULL,
    cidade          VARCHAR(100) NOT NULL,
    criado_em       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em   DATETIME     NULL,

    -- Garante, no nível do banco, que não existam nomes duplicados
    CONSTRAINT uq_clientes_nome UNIQUE (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Índice adicional para buscas por nome (a constraint UNIQUE já cria um
-- índice implícito, mas fica explícito aqui para documentação)
CREATE INDEX idx_clientes_nome ON clientes (nome);
