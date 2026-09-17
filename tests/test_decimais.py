"""Testes da camada de Decimal sem artefatos de float.

Prova, com o clássico contra-exemplo de ponto flutuante (19.1), que este
módulo nunca vaza artefato binário para o valor final.
"""

from decimal import Decimal

import pytest

from jrdp.decimais import (
    DecimalContractError,
    serializar_decimal_livre,
    valor_origem_para_decimal,
)


def test_float_classico_nao_gera_artefato_binario():
    """Decimal(19.1) direto produziria um artefato de 50+ dígitos.
    valor_origem_para_decimal nunca deve fazer isso.
    """
    resultado = valor_origem_para_decimal(19.1)
    assert resultado == Decimal("19.1")
    assert str(resultado) == "19.1"
    # prova que Decimal(float) direto seria o comportamento errado a evitar
    assert Decimal(19.1) != Decimal("19.1")


def test_float_com_muitas_casas_reais_e_preservado_sem_amplificar_ruido():
    resultado = valor_origem_para_decimal(19.32084)
    assert str(resultado) == "19.32084"


def test_string_com_virgula_decimal():
    resultado = valor_origem_para_decimal("382,18378")
    assert resultado == Decimal("382.18378")


def test_string_com_ponto_decimal():
    resultado = valor_origem_para_decimal("75.5")
    assert resultado == Decimal("75.5")


def test_int_puro():
    assert valor_origem_para_decimal(75) == Decimal("75")


def test_decimal_passthrough():
    d = Decimal("4.11")
    assert valor_origem_para_decimal(d) is d


def test_bool_e_rejeitado():
    with pytest.raises(DecimalContractError):
        valor_origem_para_decimal(True)


def test_string_invalida_e_rejeitada():
    with pytest.raises(DecimalContractError):
        valor_origem_para_decimal("não é um número")


def test_tipo_nao_suportado_e_rejeitado():
    with pytest.raises(DecimalContractError):
        valor_origem_para_decimal(["75"])


# --- serialização ---


def test_serializar_zero_sempre_bare():
    assert serializar_decimal_livre(Decimal("0")) == "0"
    assert serializar_decimal_livre(Decimal("0.0")) == "0"
    assert serializar_decimal_livre(Decimal("0.00")) == "0"


def test_serializar_inteiro_sem_separador_mesmo_vindo_com_zero_decimal():
    """Evidência real: '75' aparece bare, nunca '75,0'."""
    assert serializar_decimal_livre(Decimal("75")) == "75"
    assert serializar_decimal_livre(Decimal("75.0")) == "75"
    assert serializar_decimal_livre(Decimal("75.00")) == "75"


def test_serializar_preserva_precisao_variavel_sem_arredondar():
    assert serializar_decimal_livre(Decimal("382.18378")) == "382,18378"
    assert serializar_decimal_livre(Decimal("4.11")) == "4,11"
    assert serializar_decimal_livre(Decimal("99.4")) == "99,4"


def test_serializar_nao_usa_notacao_cientifica():
    resultado = serializar_decimal_livre(Decimal("0.0000001"))
    assert "E" not in resultado.upper()


def test_serializar_nan_e_rejeitado():
    with pytest.raises(DecimalContractError):
        serializar_decimal_livre(Decimal("NaN"))


def test_serializar_infinito_e_rejeitado():
    with pytest.raises(DecimalContractError):
        serializar_decimal_livre(Decimal("Infinity"))


def test_pipeline_completo_replica_arquivo_real_evento_1889():
    """Reproduz, com valores fictícios equivalentes, os casos observados
    no arquivo real evento_1889 (ver docs/DECISIONS.md, 2026-09-17)."""
    casos = {
        "382,18378": "382,18378",
        "4,11": "4,11",
        "99,4": "99,4",
        "0": "0",
        "75": "75",
    }
    for entrada, esperado in casos.items():
        decimal_valor = valor_origem_para_decimal(entrada)
        assert serializar_decimal_livre(decimal_valor) == esperado
