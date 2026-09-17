"""Proteção permanente: H,MM é formato de saída, nunca unidade
aritmética. Este teste existe especificamente para impedir a regressão
descrita em docs/DECISIONS.md (2026-09-17): somar '1,52' + '0,32' como
decimal dá 1,84, que não corresponde a nenhuma duração real.
"""

import pytest

from jrdp.minutos import (
    MinutosContractError,
    hhmm_para_minutos,
    minutos_para_hhmm,
    somar_horas_em_minutos,
)
from jrdp.serializers import serialize_hmm


def test_hhmm_para_minutos_casos_basicos():
    assert hhmm_para_minutos("00:32") == 32
    assert hhmm_para_minutos("01:52") == 112
    assert hhmm_para_minutos("06:00") == 360


def test_minutos_para_hhmm_ida_e_volta():
    assert minutos_para_hhmm(32) == "00:32"
    assert minutos_para_hhmm(112) == "01:52"
    assert minutos_para_hhmm(144) == "02:24"


def test_soma_correta_via_minutos_nunca_via_decimal():
    """O caso central pedido: 01:52 + 00:32 deve totalizar 144 minutos
    (02:24), nunca "1,84" (soma decimal das strings serializadas)."""
    total_minutos = somar_horas_em_minutos(["01:52", "00:32"])
    assert total_minutos == 144
    assert minutos_para_hhmm(total_minutos) == "02:24"

    # prova explícita de que a interpretação decimal ingênua é diferente
    # e portanto errada — nunca deve ser usada para QA de horas
    valor_decimal_1 = float(serialize_hmm("01:52").replace(",", "."))
    valor_decimal_2 = float(serialize_hmm("00:32").replace(",", "."))
    soma_decimal_errada = valor_decimal_1 + valor_decimal_2
    assert soma_decimal_errada == pytest.approx(1.84)
    assert soma_decimal_errada != 2.24  # 02:24 em "decimal" seria 2,24, não 1,84


def test_soma_de_varios_valores():
    total = somar_horas_em_minutos(["01:30", "01:30", "01:00"])
    assert total == 240
    assert minutos_para_hhmm(total) == "04:00"


def test_hhmm_invalido_e_rejeitado():
    with pytest.raises(MinutosContractError):
        hhmm_para_minutos("25:99")


def test_minutos_negativos_sao_rejeitados():
    with pytest.raises(MinutosContractError):
        minutos_para_hhmm(-5)


def test_lista_vazia_soma_zero():
    assert somar_horas_em_minutos([]) == 0
