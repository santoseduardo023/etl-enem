{% macro stg_participantes(year) %}

select
    nu_inscricao::bigint               as inscricao_id,
    nu_ano::smallint                   as ano,

    tp_faixa_etaria::smallint          as faixa_etaria,
    tp_sexo                            as sexo,
    tp_estado_civil::smallint          as estado_civil,
    tp_cor_raca::smallint              as cor_raca,
    tp_nacionalidade::smallint         as nacionalidade,

    tp_st_conclusao::smallint          as situacao_conclusao,
    tp_ano_concluiu::smallint          as ano_conclusao,
    tp_ensino::smallint                as tipo_ensino,
    in_treineiro::boolean              as treineiro,

    co_municipio_prova::integer        as municipio_prova_id,
    no_municipio_prova                 as municipio_prova_nome,
    co_uf_prova::smallint              as uf_prova_id,
    sg_uf_prova                        as uf_prova,

    {% for i in range(1, 24) %}
    q{{ '%03d' % i }},
    {% endfor %}

    _arquivo_origem,
    _carregado_em

from {{ source('bronze', 'participantes_' ~ year) }}

{% endmacro %}