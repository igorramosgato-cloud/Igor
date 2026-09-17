"""Testes do de-para manual homologado. Fixture 100% sanitizada — ver
.claude/rules/homologacao-dados.md.
"""

from pathlib import Path

import pytest

from jrdp.depara import (
    DeParaContractError,
    RegistroDePara,
    carregar_depara,
    carregar_depara_de_texto,
    resolver_depara,
)

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "questor" / "depara_sanitizado.json"
)


@pytest.fixture
def registros():
    return carregar_depara(FIXTURE)


def test_carrega_fixture_sanitizada(registros):
    assert len(registros) == 3


def test_arquivo_inexistente_devolve_lista_vazia(tmp_path):
    assert carregar_depara(tmp_path / "nao_existe.json") == []


def test_campo_obrigatorio_faltante_e_rejeitado():
    texto = '{"entradas": [{"nome_origem": "X"}]}'
    with pytest.raises(DeParaContractError):
        carregar_depara_de_texto(texto)


def test_status_invalido_e_rejeitado():
    texto = (
        '{"entradas": [{"nome_origem": "X", "unidade": "filial", '
        '"codigo_questor": "1", "nome_canonico": "X", "status": "invalido", '
        '"evidencia": "e", "aprovado_por": "a", "aprovado_em": "2026-01-01"}]}'
    )
    with pytest.raises(DeParaContractError):
        carregar_depara_de_texto(texto)


def test_resolve_por_de_para_aprovado(registros):
    status, codigos = resolver_depara("FULANO DE TAL", "filial", registros)
    assert status == "resolvido"
    assert codigos == ["101"]


def test_resolve_ignorando_espacos_e_caixa(registros):
    status, codigos = resolver_depara("  fulano   de tal  ", "filial", registros)
    assert status == "resolvido"
    assert codigos == ["101"]


def test_entrada_curinga_vale_para_qualquer_unidade(registros):
    status_matriz, codigos_matriz = resolver_depara("CICLANA DA SILVA", "matriz", registros)
    status_filial, codigos_filial = resolver_depara("CICLANA DA SILVA", "filial", registros)
    assert status_matriz == "resolvido" and codigos_matriz == ["202"]
    assert status_filial == "resolvido" and codigos_filial == ["202"]


def test_unidade_errada_nao_resolve(registros):
    status, codigos = resolver_depara("FULANO DE TAL", "matriz", registros)
    assert status == "nao_encontrado"
    assert codigos == []


def test_nome_sem_entrada_e_nao_encontrado(registros):
    status, codigos = resolver_depara("NOME QUE NAO EXISTE NO DEPARA", "filial", registros)
    assert status == "nao_encontrado"


def test_entrada_revogada_e_ignorada(registros):
    status, codigos = resolver_depara("NOME REVOGADO", "filial", registros)
    assert status == "nao_encontrado"


def test_de_para_ambiguo_com_dois_codigos_aprovados():
    registros_ambiguos = [
        RegistroDePara(
            nome_origem="FULANO",
            unidade="filial",
            codigo_questor="1",
            nome_canonico="FULANO A",
            status="aprovado",
            evidencia="e1",
            aprovado_por="a",
            aprovado_em="2026-01-01",
        ),
        RegistroDePara(
            nome_origem="FULANO",
            unidade="filial",
            codigo_questor="2",
            nome_canonico="FULANO B",
            status="aprovado",
            evidencia="e2",
            aprovado_por="a",
            aprovado_em="2026-01-02",
        ),
    ]
    status, codigos = resolver_depara("FULANO", "filial", registros_ambiguos)
    assert status == "ambiguo"
    assert codigos == ["1", "2"]


def test_reaproveitamento_seguro_do_mesmo_depara(registros):
    """Carregar e aplicar o mesmo de-para duas vezes produz o mesmo
    resultado — não há efeito colateral entre chamadas."""
    r1 = resolver_depara("FULANO DE TAL", "filial", registros)
    r2 = resolver_depara("FULANO DE TAL", "filial", registros)
    assert r1 == r2
