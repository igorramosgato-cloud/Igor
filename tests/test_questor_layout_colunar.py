"""Testes de contrato do layout COLUNAR multi-evento de importação do
Questor (mais de um evento no mesmo arquivo).

Contrato certificado a partir de um arquivo real de OUTRO cliente (não
ART LATEX), já aceito pelo Questor — usado só para certificar a estrutura
física genérica (ver docs/DECISIONS.md, 2026-09-28). Usam exclusivamente a
fixture sanitizada em tests/fixtures/questor/layout_colunar_sanitizado.csv
(dados 100% fictícios) — nenhum dado do cliente de origem da evidência é
usado aqui, ver .claude/rules/homologacao-dados.md.
"""

from pathlib import Path

import pytest

from jrdp.questor_layout import (
    ColunaEvento,
    LayoutContractError,
    RegistroLayoutColunar,
    montar_arquivo_layout_colunar,
    parse_arquivo_layout_colunar,
)

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "questor"
    / "layout_colunar_sanitizado.csv"
)


@pytest.fixture
def conteudo_bruto():
    return FIXTURE.read_bytes()


def test_parse_estrutura_basica(conteudo_bruto):
    arquivo = parse_arquivo_layout_colunar(conteudo_bruto)
    assert [c.codigo for c in arquivo.colunas] == ["9001", "9002", "9003"]
    assert [c.tipo for c in arquivo.colunas] == ["V", "V", "H"]
    assert [c.rotulo for c in arquivo.colunas] == ["Evento Um", "Evento Dois", "Evento Tres"]
    assert len(arquivo.registros) == 3


def test_parse_valores_ausentes_viram_ausencia_na_chave(conteudo_bruto):
    arquivo = parse_arquivo_layout_colunar(conteudo_bruto)
    fulano = next(r for r in arquivo.registros if r.contrato == "1")
    assert fulano.valores == {"9001": "10,50"}
    fulana = next(r for r in arquivo.registros if r.contrato == "2")
    assert fulana.valores == {"9002": "5,25", "9003": "2,15"}


def test_parse_nao_arredonda_nem_reformata_valor(conteudo_bruto):
    arquivo = parse_arquivo_layout_colunar(conteudo_bruto)
    sicrano = next(r for r in arquivo.registros if r.contrato == "3")
    assert sicrano.valores["9001"] == "7,00"


def test_parse_rejeita_cabecalho_sem_duas_colunas_vazias_iniciais():
    conteudo = ("9001;;;\r\n;;;\r\nContrato;Nome;;\r\n1;X;1\r\n").encode("cp850")
    with pytest.raises(LayoutContractError):
        parse_arquivo_layout_colunar(conteudo)


def test_parse_rejeita_tipo_desconhecido():
    conteudo = (";;9001\r\n;;Z\r\nContrato;Nome;Evento\r\n1;X;5\r\n").encode("cp850")
    with pytest.raises(LayoutContractError):
        parse_arquivo_layout_colunar(conteudo)


def test_parse_rejeita_padding_nao_vazio_apos_fim_dos_eventos():
    conteudo = (
        ";;9001;;9002\r\n"
        ";;V;;V\r\n"
        "Contrato;Nome;Evento;;Outro\r\n"
        "1;X;5;;10\r\n"
    ).encode("cp850")
    with pytest.raises(LayoutContractError):
        parse_arquivo_layout_colunar(conteudo)


def test_parse_rejeita_contrato_ausente():
    conteudo = (";;9001\r\n;;V\r\nContrato;Nome;Evento\r\n;X;5\r\n").encode("cp850")
    with pytest.raises(LayoutContractError):
        parse_arquivo_layout_colunar(conteudo)


def test_parse_rejeita_linha_de_dados_com_numero_de_colunas_errado():
    conteudo = (";;9001;9002\r\n;;V;V\r\nContrato;Nome;A;B\r\n1;X;5\r\n").encode("cp850")
    with pytest.raises(LayoutContractError):
        parse_arquivo_layout_colunar(conteudo)


def test_montar_e_reparsear_produz_os_mesmos_dados():
    colunas = [
        ColunaEvento(codigo="9001", tipo="V", rotulo="Evento Um"),
        ColunaEvento(codigo="9002", tipo="V", rotulo="Evento Dois"),
    ]
    registros = [
        RegistroLayoutColunar(contrato="1", nome="FULANO DE TAL UM", valores={"9001": "10,50"}),
        RegistroLayoutColunar(
            contrato="2", nome="FULANA DE TAL DOIS", valores={"9002": "5,25"}
        ),
    ]
    conteudo = montar_arquivo_layout_colunar(colunas, registros)
    assert conteudo.endswith(b"\r\n")

    arquivo = parse_arquivo_layout_colunar(conteudo)
    assert [c.codigo for c in arquivo.colunas] == ["9001", "9002"]
    assert arquivo.registros[0].valores == {"9001": "10,50"}
    assert arquivo.registros[1].valores == {"9002": "5,25"}


def test_montar_nunca_gera_zero_para_ausencia():
    colunas = [ColunaEvento(codigo="9001", tipo="V", rotulo="Evento Um")]
    registros = [RegistroLayoutColunar(contrato="1", nome="X", valores={})]
    conteudo = montar_arquivo_layout_colunar(colunas, registros)
    texto = conteudo.decode("cp850")
    assert "1;X;\r\n" in texto
    assert ";0" not in texto


def test_montar_exige_pelo_menos_uma_coluna():
    with pytest.raises(LayoutContractError):
        montar_arquivo_layout_colunar([], [])
