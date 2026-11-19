{% macro stg_itens_prova(year) %}

select
    {{ year }}::smallint               as ano,
    co_prova::integer                  as prova_id,
    tx_cor                             as prova_cor,
    tp_lingua::smallint                as lingua_estrangeira,
    sg_area                            as area,

    co_item::integer                   as item_id,
    co_posicao::smallint               as posicao,
    co_habilidade::smallint            as habilidade,
    tx_gabarito                        as gabarito,

    in_item_adaptado::boolean          as item_adaptado,
    in_item_aban::boolean              as item_abandonado,
    tx_motivo_aban                     as motivo_abandono,

    nu_param_a::numeric                as tri_param_a,
    nu_param_b::numeric                as tri_param_b,
    nu_param_c::numeric                as tri_param_c,

    _arquivo_origem,
    _carregado_em

from {{ source('bronze', 'itens_prova_' ~ year) }}

{% endmacro %}