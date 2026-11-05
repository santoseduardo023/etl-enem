# Decisões e investigações

## Comparação de layout: ENEM 2024 × 2025

**Método:** comparação das colunas das tabelas da bronze via `information_schema.columns`, com `FULL OUTER JOIN` entre os anos ([`sql/compare_layout.sql`](../sql/compare_layout.sql)).

**Resultado:**

| Arquivo | Diferença |
|---|---|
| `PARTICIPANTES` | Colunas idênticas nos dois anos (38) |
| `ITENS_PROVA` | Colunas idênticas nos dois anos (14) |
| `RESULTADOS` | 2025 tem 28 colunas a mais (70 contra 42) |

As 28 colunas exclusivas de 2025 são as notas da redação **por avaliador**: para cada um dos 4 avaliadores, o status da redação (`tp_status_redacao_avN`), a nota total (`nu_nota_avN`) e as notas das 5 competências (`nu_nota_compK_avN`).

**Decisão:** as colunas por avaliador ficam só na bronze. A silver usa apenas as notas finais, que existem nos dois anos. Assim, a união 2024 + 2025 na silver não exige harmonização de colunas.

## Volume por ano

| Arquivo | 2024 | 2025 |
|---|---|---|
| `PARTICIPANTES` | 4.332.944 linhas | 4.810.772 linhas |
| `RESULTADOS` | 4.332.944 linhas | 4.810.772 linhas |
| `ITENS_PROVA` | 5.550 linhas | 6.105 linhas |

Nos dois anos, `PARTICIPANTES` e `RESULTADOS` têm o mesmo número de linhas (uma por inscrito), mas sem chave que ligue um arquivo ao outro (restrição da LGPD). 2025 teve cerca de 11% a mais de inscritos.

## Empacotamento dos `.zip` do INEP

O `.zip` de 2024 (~502 MB) tem cerca de metade do tamanho do de 2025 (~988 MB), embora os dados sejam proporcionais. A diferença está na compressão:

| Arquivo | 2024 | 2025 |
|---|---|---|
| `PARTICIPANTES` | Deflate (441 MB → 96 MB) | Stored, sem compressão (489 MB) |
| `RESULTADOS` | Deflate (1.605 MB → 384 MB) | Deflate64 |

O extract trata os três métodos (Stored, Deflate e Deflate64) sem distinção por ano, e localiza os CSVs por padrão de nome, ignorando entradas extras como a pasta `DADOS/` presente só no `.zip` de 2024.