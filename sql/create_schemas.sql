-- Schemas da arquitetura medallion

CREATE SCHEMA IF NOT EXISTS bronze;  -- cópia fiel dos CSVs do INEP
CREATE SCHEMA IF NOT EXISTS silver;  -- dados tipados, limpos e unidos (dbt)
CREATE SCHEMA IF NOT EXISTS gold;    -- modelo dimensional para consumo (dbt)