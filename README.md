# ENEM Data Pipeline

Pipeline de engenharia de dados que transforma os microdados públicos do **ENEM 2024 e 2025** (INEP) em tabelas modeladas e prontas para análise, usando **arquitetura medallion** (bronze → silver → gold) no PostgreSQL.

> **Status:** em desenvolvimento. Extração e carga na bronze concluídas para 2024 e 2025: ~18,3 milhões de linhas carregadas com um único comando por ano. Próximas etapas no [roadmap](#roadmap).

## Sumário

- [Sobre o projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
- [Stack](#stack)
- [Como rodar](#como-rodar)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Decisões técnicas](#decisões-técnicas)
- [Roadmap](#roadmap)

## Sobre o projeto

O INEP publica todo ano os microdados do ENEM: arquivos CSV que chegam a **~2 GB por ano**, em `latin-1`, separados por `;` e sem tipagem. Do jeito que são distribuídos, não estão prontos para análise.

Este projeto constrói um pipeline que:

1. **Extrai** os arquivos oficiais do INEP automaticamente (download em streaming e extração seletiva, com cache)
2. **Carrega** os dados brutos no PostgreSQL com `COPY`, de forma idempotente
3. **Transforma** em camadas com dbt: limpeza e tipagem (silver) e modelo dimensional (gold)
4. **Entrega** tabelas prontas para analistas e ferramentas de BI

## Arquitetura

![Arquitetura do pipeline](docs/arquitetura.png)

| Camada | Schema | Conteúdo | Ferramenta |
|---|---|---|---|
| **Bronze** | `bronze` | Cópia fiel dos CSVs do INEP: uma tabela por arquivo/ano, todas as colunas como texto, mais colunas de linhagem | Python + `COPY` |
| **Silver** | `silver` | Dados tipados, limpos, com 2024 e 2025 unidos e colunas curadas | dbt |
| **Gold** | `gold` | Modelo dimensional (constelação) e tabelas largas (OBTs) para BI | dbt |

## Stack

| Ferramenta | Uso |
|---|---|
| **Python 3.12** | Extração e carga (camada bronze) |
| **uv** | Gerenciamento do ambiente e das dependências |
| **requests + truststore** | Download dos microdados do INEP com retry e validação de certificado pelo sistema operacional |
| **zipfile-inflate64** | Suporte a Deflate64 na extração do `.zip` do INEP |
| **psycopg 3** | Conexão com o PostgreSQL e carga via `COPY` |
| **PostgreSQL 16** | Data warehouse local (schemas bronze, silver e gold) |
| **ruff** | Lint e padronização do código |
| **dbt-core** | Transformações silver e gold, testes e documentação _(em breve)_ |

## Como rodar

### Pré-requisitos

- [uv](https://docs.astral.sh/uv/) instalado
- PostgreSQL 16 rodando localmente
- Git

### Passo a passo

```bash
# 1. Clonar o repositório
git clone https://github.com/santoseduardo023/etl-enem.git
cd etl-enem

# 2. Criar o ambiente e instalar as dependências (lê pyproject.toml + uv.lock)
uv sync

# 3. Configurar as credenciais do banco
cp .env.example .env        # no PowerShell: Copy-Item .env.example .env
# edite o .env e preencha POSTGRES_PASSWORD

# 4. Criar o database e os schemas bronze/silver/gold (idempotente)
uv run enem-pipeline setup

# 5. Rodar o pipeline para cada ano: download, extração e carga na bronze
uv run enem-pipeline run --ano 2024
uv run enem-pipeline run --ano 2025
```

Também é possível usar `uv run python -m enem_pipeline` no lugar de `uv run enem-pipeline`. Use `--help` em qualquer comando para ver as opções.

> A primeira execução de cada ano baixa o `.zip` do INEP (~0,5 a 1 GB) e leva alguns minutos a mais. As seguintes usam o cache de `data/raw/` e `data/extracted/`, e a carga completa de um ano na bronze leva de 10 a 15 minutos. Os logs ficam no terminal e em `logs/pipeline.log`.

## Estrutura do repositório

```
etl-enem/
├── src/enem_pipeline/     # código Python do pipeline
│   ├── cli.py             # comandos setup e run (ponto de entrada)
│   ├── config.py          # leitura e validação do .env, pastas e URLs do INEP
│   ├── db.py              # conexão com o PostgreSQL
│   ├── setup_db.py        # cria database e schemas
│   ├── extract.py         # download e extração dos CSVs do INEP
│   ├── load.py            # DDL e carga na bronze com COPY
│   └── logging_config.py  # logging no terminal e em arquivo
├── sql/                   # DDL dos schemas e consultas de análise
├── dbt/models/            # transformações: staging, silver e gold
├── docs/                  # diagrama e registro de decisões e investigações
├── tests/                 # testes automatizados
├── data/                  # dados do INEP, fora do Git (raw/ e extracted/)
├── logs/                  # logs de execução, fora do Git
├── .env.example           # modelo de configuração
└── pyproject.toml         # dependências e comando enem-pipeline
```

## Decisões técnicas

**Arquitetura medallion com um schema por camada.** Separa responsabilidades (dado bruto, limpo e modelado) e facilita a futura migração para o Databricks, onde cada camada vira um schema no Unity Catalog.

**Bronze como cópia fiel, tudo em texto.** A bronze não interpreta nada: guarda exatamente o que veio do INEP. A tipagem e a limpeza acontecem na silver, onde podem ser testadas e reprocessadas sem baixar os arquivos de novo.

**DDL gerado pelo cabeçalho do CSV.** As tabelas da bronze são criadas a partir da primeira linha de cada arquivo, e não do dicionário de dados: a ordem real das colunas nos CSVs difere da documentação. Os nomes são passados ao banco via `psycopg.sql.Identifier`, sem montar SQL com f-strings.

**Linhagem na bronze.** Cada linha carrega `_arquivo_origem` e `_carregado_em`, indicando de qual arquivo veio e quando entrou no banco.

**Download em streaming, com cache e escrita atômica.** O arquivo de ~1 GB é baixado em pedaços de 1 MB, sem ocupar memória. O download é gravado num `.part` e só vira `.zip` quando termina e o tamanho confere com o `Content-Length` do servidor. Assim, um `.zip` em `data/raw/` é sempre um arquivo completo, e o cache pode confiar nele.

**Conexão com o servidor do INEP.** O servidor de download só suporta até TLS 1.2, derruba conexões de forma intermitente e não envia a cadeia completa de certificados. O extract usa um adaptador HTTP específico para o INEP: limita o TLS a 1.2, valida o certificado com o repositório do sistema operacional (`truststore`) e repete as tentativas com backoff exponencial. A verificação do certificado nunca é desligada.

**Extração seletiva e independente do empacotamento.** Do `.zip` são extraídos só os 3 CSVs de dados, localizados por padrão de nome (`DADOS/<TIPO>_<ano>.csv`), e não por caminho fixo. Os `.zip` do INEP usam métodos de compressão diferentes a cada ano (Stored, Deflate e Deflate64), e o extract trata todos da mesma forma; o suporte a Deflate64, ausente no `zipfile` do Python, vem da biblioteca `zipfile-inflate64`.

**Carga com `COPY` em vez de pandas.** O `COPY` é o mecanismo nativo do PostgreSQL para carga em massa: envia o arquivo em streaming, sem montar DataFrames em memória, e é muito mais rápido que `INSERT`s gerados pelo `to_sql`. A conversão de Latin-1 para UTF-8 é feita pelo próprio Postgres.

**Carga idempotente e atômica.** Cada tabela é recarregada com `TRUNCATE` + `COPY`, e os 3 arquivos de um ano entram numa única transação. Rodar o pipeline várias vezes nunca duplica dados, e uma falha no meio desfaz tudo, sem deixar a bronze pela metade.

**Restrição da LGPD na modelagem.** Desde 2024, os arquivos `PARTICIPANTES` (perfil socioeconômico) e `RESULTADOS` (notas) **não têm chave em comum**, por decisão do INEP para proteger a identidade dos participantes. Por isso, a gold usa uma **constelação com dois fatos** (`fato_participante` e `fato_resultado`) que só se cruzam de forma agregada (por município, UF e ano), nunca linha a linha.

**Escopo 2024–2025 e layout comparado.** São as duas edições com o mesmo modelo simplificado de microdados. A comparação de colunas entre os anos mostrou uma única diferença: 28 colunas de notas da redação por avaliador, que existem só em 2025 e ficam fora da silver. Assim, a união dos anos não exige harmonização. Detalhes em [`docs/decisoes.md`](docs/decisoes.md).

**Observabilidade e códigos de saída.** O pipeline registra horário, nível e módulo de cada etapa, com progresso a cada 10% no download e na carga, no terminal e em arquivo. Erros são gravados com o traceback completo, e a CLI termina com código `1` em caso de falha (`130` se interrompida), para que um orquestrador saiba quando a execução falhou.

**Credenciais fora do código.** Configurações ficam no `.env` (ignorado pelo Git), com validação na inicialização e mensagem clara se faltar alguma variável.

## Roadmap

- [x] **M0 – Fundação:** estrutura, ambiente com uv, configuração via `.env`, database e schemas
- [x] **M1 – Extract:** download dos microdados do INEP com cache e extração seletiva dos CSVs
- [x] **M2 – Load bronze:** DDL a partir do cabeçalho, carga com `COPY` idempotente, logging e CLI única
- [x] **M3 – Inclusão de 2024:** carga do segundo ano sem mudanças no código e comparação de layout entre os anos
- [ ] **M4 – dbt silver:** tipagem, limpeza, união dos anos e testes básicos
- [ ] **M5 – dbt gold:** modelo dimensional (constelação), OBTs e testes de qualidade
- [ ] **M6 – Acabamento:** pytest, pre-commit, CI no GitHub Actions e documentação final
- [ ] **v2 – Databricks:** migração para Delta Lake com orquestração em Workflows