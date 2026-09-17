import pytest

from jrdp.serializers import InvalidTimeFormatError, serialize_hmm, serialize_valor


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("00:32", "0,32"),
        ("01:52", "1,52"),
        ("04:07", "4,07"),
        ("06:00", "6,00"),
        ("07:31", "7,31"),  # exemplo dado pelo usuário para HE 50%, 2026-09-17
    ],
)
def test_serialize_hmm_casos_confirmados(entrada, esperado):
    assert serialize_hmm(entrada) == esperado


def test_hmm_never_converts_to_decimal_hours():
    """01:30 deve virar 1,30 (formato H,MM), nunca 1,50 (hora decimal)."""
    resultado = serialize_hmm("01:30")
    assert resultado == "1,30"
    assert resultado != "1,50"


def test_serialize_hmm_minutos_invalidos_rejeitados():
    with pytest.raises(InvalidTimeFormatError):
        serialize_hmm("01:60")


def test_serialize_hmm_proibe_formato_sem_dois_pontos():
    with pytest.raises(InvalidTimeFormatError):
        serialize_hmm("0130")


def test_serialize_hmm_rejeita_valor_vazio():
    with pytest.raises(InvalidTimeFormatError):
        serialize_hmm("")


def test_serialize_valor_com_ponto():
    assert serialize_valor(1.5) == "1,50"


def test_serialize_valor_com_string_virgula():
    assert serialize_valor("12,34") == "12,34"


def test_serialize_valor_inteiro():
    assert serialize_valor(1) == "1,00"
