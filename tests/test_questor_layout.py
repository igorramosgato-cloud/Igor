"""Testes de contrato do layout genérico de importação do Questor.

Usam exclusivamente a fixture sanitizada em
tests/fixtures/questor/layout_generico_sanitizado.csv (dados 100%
fictícios). Nenhum dado do arquivo físico real de evidência é usado aqui —
ver .claude/rules/homologacao-dados.md.
"""

from pathlib import Path

import pytest

from jrdp.questor_layout import (
    CABECALHO_ESPERADO,
    LayoutContractError,
    parse_arquivo_layout,
)

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "questor"
    / "layout_generico_sanitizado.csv"
)


@pytest.fixture
def conteudo_bruto():
    return FIXTURE.read_bytes()


def test_arquivo_fixture_e_cp850_valido(conteudo_bruto):
    # não deve levantar UnicodeDecodeError
    conteudo_bruto.decode("cp850")


def test_terminador_de_linha_e_crlf_apenas(conteudo_bruto):
    assert conteudo_bruto.count(b"\r\n") > 0
    assert conteudo_bruto.count(b"\n") == conteudo_bruto.count(b"\r\n")


def test_nao_ha_bom(conteudo_bruto):
    assert conteudo_bruto[:3] != b"\xef\xbb\xbf"


def test_nao_ha_aspas_no_arquivo(conteudo_bruto):
    assert b'"' not in conteudo_bruto
    assert b"'" not in conteudo_bruto


def test_parse_extrai_codigo_evento_e_tipo(conteudo_bruto):
    resultado = parse_arquivo_layout(conteudo_bruto)
    assert resultado.codigo_evento == "9999"
    assert resultado.tipo == "V"


def test_parse_extrai_registros_na_ordem(conteudo_bruto):
    resultado = parse_arquivo_layout(conteudo_bruto)
    assert len(resultado.registros) == 5
    assert resultado.registros[0].codigo_funcionario == "1"
    assert resultado.registros[0].nome == "FULANO DE TAL UM"


def test_valor_bruto_preserva_precisao_variavel_sem_reformatar(conteudo_bruto):
    """Regra confirmada por evidência física: o valor NÃO tem precisão fixa.

    O parser nunca deve arredondar/formatar — apenas devolver a string
    exatamente como está no arquivo.
    """
    resultado = parse_arquivo_layout(conteudo_bruto)
    valores = {r.codigo_funcionario: r.valor_bruto for r in resultado.registros}
    assert valores["1"] == "100,00001"  # 5 casas decimais
    assert valores["2"] == "0"  # sem vírgula
    assert valores["3"] == "4,11"  # 2 casas
    assert valores["4"] == "99,4"  # 1 casa
    assert valores["5"] == "75"  # inteiro, sem vírgula


def test_coluna_c_sempre_vazia_e_validada(conteudo_bruto):
    texto = conteudo_bruto.decode("cp850")
    linha_com_coluna_c_preenchida = texto.replace(
        "1;FULANO DE TAL UM;;100,00001",
        "1;FULANO DE TAL UM;X;100,00001",
    )
    with pytest.raises(LayoutContractError, match="coluna C"):
        parse_arquivo_layout(linha_com_coluna_c_preenchida.encode("cp850"))


def test_cabecalho_com_erro_de_digitacao_faz_parte_do_contrato():
    assert CABECALHO_ESPERADO == "CÓDGIO;NOME;;"


def test_cabecalho_diferente_do_contrato_e_rejeitado(conteudo_bruto):
    texto = conteudo_bruto.decode("cp850")
    texto_com_cabecalho_corrigido = texto.replace(
        "CÓDGIO;NOME;;", "CÓDIGO;NOME;;"
    )
    with pytest.raises(LayoutContractError, match="Cabeçalho"):
        parse_arquivo_layout(texto_com_cabecalho_corrigido.encode("cp850"))


def test_encoding_errado_e_rejeitado(conteudo_bruto):
    # reconstrói o mesmo texto mas grava em utf-8 (encoding incompatível
    # com o contrato confirmado, já que há acento fora da faixa ASCII)
    texto = conteudo_bruto.decode("cp850")
    conteudo_utf8 = texto.encode("utf-8")
    # só é um teste útil se o utf-8 realmente romper o parse como cp850
    # decodificado incorretamente não bate com o cabeçalho esperado
    with pytest.raises(LayoutContractError):
        resultado = parse_arquivo_layout(conteudo_utf8)
        assert resultado.registros  # não deveria chegar aqui


def test_delimitador_diferente_e_rejeitado(conteudo_bruto):
    texto = conteudo_bruto.decode("cp850")
    texto_com_virgula = texto.replace(";", ",")
    with pytest.raises(LayoutContractError):
        parse_arquivo_layout(texto_com_virgula.encode("cp850"))


def test_tipo_desconhecido_e_rejeitado():
    conteudo = (
        ";;;1234\r\n"
        ";;;X\r\n"
        "CÓDGIO;NOME;;\r\n"
        "1;FULANO;;10\r\n"
    ).encode("cp850")
    with pytest.raises(LayoutContractError, match="Tipo desconhecido"):
        parse_arquivo_layout(conteudo)


def test_linha_com_numero_de_colunas_errado_e_rejeitada():
    conteudo = (
        ";;;1234\r\n"
        ";;;V\r\n"
        "CÓDGIO;NOME;;\r\n"
        "1;FULANO;10\r\n"  # só 3 colunas
    ).encode("cp850")
    with pytest.raises(LayoutContractError, match="4 colunas"):
        parse_arquivo_layout(conteudo)
