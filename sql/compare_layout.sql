-- Colunas presentes em só um dos anos, por arquivo do INEP
WITH cols AS (
    SELECT
        regexp_replace(table_name, '_\d{4}$', '') AS arquivo,
        right(table_name, 4) AS ano,
        column_name
    FROM information_schema.columns
    WHERE table_schema = 'bronze'
      AND column_name NOT LIKE '\_%'
),
c24 AS (SELECT * FROM cols WHERE ano = '2024'),
c25 AS (SELECT * FROM cols WHERE ano = '2025')
SELECT
    coalesce(c24.arquivo, c25.arquivo) AS arquivo,
    coalesce(c24.column_name, c25.column_name) AS coluna,
    CASE WHEN c24.column_name IS NULL THEN 'só em 2025' ELSE 'só em 2024' END AS diferenca
FROM c24
FULL OUTER JOIN c25
    ON c24.arquivo = c25.arquivo
   AND c24.column_name = c25.column_name
WHERE c24.column_name IS NULL OR c25.column_name IS NULL
ORDER BY arquivo, diferenca, coluna;