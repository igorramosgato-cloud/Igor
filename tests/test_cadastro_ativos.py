"""Testes de contrato do relatório "Base de ativos" (cadastro código↔nome↔CPF).

Usam exclusivamente a fixture sanitizada em
tests/fixtures/questor/cadastro_ativos_sanitizado.csv (dados 100%
fictícios). Nenhum dado do arquivo físico real de evidência é usado aqui —
ver .claude/rules/homologacao-dados.md.
"""

from pathlib import Path

import pytest

from jrdp.cadastro_ativos import (
    CadastroContractError,
    indexar_por_contrato,
    indexar_por_cpf,
    parse_base_ativos,
)

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "questor"
    / "cadastro_ativos_sanitizado.csv"
)


@pytest.fixture
def conteudo_bruto():
    return FIXTURE.read_bytes()


def test_parse_extrai_apenas_registros_reais_ignorando_paginacao(conteudo_bruto):
    registros = parse_base_ativos(conteudo_bruto)
    assert len(registros) == 3
    assert [r.contrato for r in registros] == ["1", "2", "3"]


def test_parse_ignora_cabecalhos_de_pagina_repetidos(conteudo_bruto):
    registros = parse_base_ativos(conteudo_bruto)
    nomes = [r.nome for r in registros]
    assert "Contrato" not in nomes
    assert all(n not in ("Nome", "CPF") for n in nomes)


def test_contagem_bate_com_total_declarado_no_rodape(conteudo_bruto):
    # a fixture declara "Total de Funcionários";3 — bate com os 3 registros
    registros = parse_base_ativos(conteudo_bruto)
    assert len(registros) == 3


def test_contagem_divergente_do_rodape_e_rejeitada(conteudo_bruto):
    texto = conteudo_bruto.decode("latin-1")
    texto_com_total_errado = texto.replace(
        '"Total de Funcionários";3', '"Total de Funcionários";99'
    )
    with pytest.raises(CadastroContractError, match="não bate"):
        parse_base_ativos(texto_com_total_errado.encode("latin-1"))


def test_contrato_duplicado_e_rejeitado(conteudo_bruto):
    texto = conteudo_bruto.decode("latin-1")
    texto_com_duplicata = texto.replace(
        '2;"FULANA DE TAL DOIS"', '1;"FULANA DE TAL DOIS"'
    ).replace('"Total de Funcionários";3', '"Total de Funcionários";3')
    with pytest.raises(CadastroContractError):
        parse_base_ativos(texto_com_duplicata.encode("latin-1"))


def test_cpf_fora_do_formato_e_rejeitado(conteudo_bruto):
    texto = conteudo_bruto.decode("latin-1")
    texto_com_cpf_invalido = texto.replace("111.111.111-11", "11111111111")
    with pytest.raises(CadastroContractError, match="CPF"):
        parse_base_ativos(texto_com_cpf_invalido.encode("latin-1"))


def test_data_fora_do_formato_e_rejeitada(conteudo_bruto):
    texto = conteudo_bruto.decode("latin-1")
    texto_com_data_invalida = texto.replace("01/01/2020", "2020-01-01")
    with pytest.raises(CadastroContractError, match="Admiss"):
        parse_base_ativos(texto_com_data_invalida.encode("latin-1"))


def test_rodape_ausente_e_rejeitado(conteudo_bruto):
    texto = conteudo_bruto.decode("latin-1")
    linhas = [
        linha for linha in texto.split("\r\n") if not linha.startswith('" Total Empresa')
    ]
    texto_sem_rodape = "\r\n".join(linhas)
    with pytest.raises(CadastroContractError, match="[Rr]odap"):
        parse_base_ativos(texto_sem_rodape.encode("latin-1"))


def test_indexar_por_contrato(conteudo_bruto):
    registros = parse_base_ativos(conteudo_bruto)
    indice = indexar_por_contrato(registros)
    assert indice["2"].nome == "FULANA DE TAL DOIS"


def test_indexar_por_cpf(conteudo_bruto):
    registros = parse_base_ativos(conteudo_bruto)
    indice = indexar_por_cpf(registros)
    assert indice["333.333.333-33"].contrato == "3"


def test_encoding_errado_e_rejeitado(conteudo_bruto):
    # o arquivo tem acentos fora da faixa ASCII; UTF-8 não deveria bater
    # com o contrato de rodapé/estrutura esperado
    with pytest.raises(CadastroContractError):
        parse_base_ativos(conteudo_bruto.decode("latin-1").encode("utf-8"))
