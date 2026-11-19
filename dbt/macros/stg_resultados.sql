{% macro stg_resultados(year) %}

select
    nu_sequencial::integer             as resultado_id,
    nu_ano::smallint                   as ano,

    co_escola::integer                 as escola_id,
    co_municipio_esc::integer          as municipio_escola_id,
    no_municipio_esc                   as municipio_escola_nome,
    co_uf_esc::smallint                as uf_escola_id,
    sg_uf_esc                          as uf_escola,
    tp_dependencia_adm_esc::smallint   as escola_dependencia_adm,
    tp_localizacao_esc::smallint       as escola_localizacao,
    tp_sit_func_esc::smallint          as escola_situacao_funcionamento,

    co_municipio_prova::integer        as municipio_prova_id,
    no_municipio_prova                 as municipio_prova_nome,
    co_uf_prova::smallint              as uf_prova_id,
    sg_uf_prova                        as uf_prova,

    tp_presenca_cn::smallint           as presenca_cn,
    tp_presenca_ch::smallint           as presenca_ch,
    tp_presenca_lc::smallint           as presenca_lc,
    tp_presenca_mt::smallint           as presenca_mt,

    co_prova_cn::integer               as prova_cn_id,
    co_prova_ch::integer               as prova_ch_id,
    co_prova_lc::integer               as prova_lc_id,
    co_prova_mt::integer               as prova_mt_id,
    tp_lingua::smallint                as lingua_estrangeira,

    nu_nota_cn::numeric(5, 1)          as nota_cn,
    nu_nota_ch::numeric(5, 1)          as nota_ch,
    nu_nota_lc::numeric(5, 1)          as nota_lc,
    nu_nota_mt::numeric(5, 1)          as nota_mt,

    tp_status_redacao::smallint        as redacao_status,
    nu_nota_comp1::numeric(5, 1)       as nota_redacao_comp1,
    nu_nota_comp2::numeric(5, 1)       as nota_redacao_comp2,
    nu_nota_comp3::numeric(5, 1)       as nota_redacao_comp3,
    nu_nota_comp4::numeric(5, 1)       as nota_redacao_comp4,
    nu_nota_comp5::numeric(5, 1)       as nota_redacao_comp5,
    nu_nota_redacao::numeric(5, 1)     as nota_redacao,

    _arquivo_origem,
    _carregado_em

from {{ source('bronze', 'resultados_' ~ year) }}

{% endmacro %}