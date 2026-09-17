"""Testes do cruzamento nome -> código entre origem (Matriz/Filial) e o
cadastro de ativos. Dados 100% fictícios — ver
.claude/rules/homologacao-dados.md.
"""

import pytest

from jrdp.cadastro_ativos import RegistroCadastro
from jrdp.origem_matching import (
    MatchingBlockedError,
    assert_sem_bloqueios,
    cruzar_por_nome,
)


def _registro(contrato, nome, cpf="000.000.000-00"):
    return RegistroCadastro(
        contrato=contrato,
        nome=nome,
        admissao="01/01/2020",
        descricao="CARGO FICTICIO",
        cpf=cpf,
    )


CADASTRO_BASE = [
    _registro("1", "FULANO DE TAL UM", "111.111.111-11"),
    _registro("2", "FULANA DE TAL DOIS", "222.222.222-22"),
]


def test_resolve_nome_exato():
    resultado = cruzar_por_nome(["FULANO DE TAL UM"], CADASTRO_BASE)
    assert resultado.resolvidos == {"FULANO DE TAL UM": "1"}
    assert not resultado.tem_bloqueio()


def test_resolve_ignorando_espacos_extras_e_caixa():
    resultado = cruzar_por_nome(["  fulano   de tal   um  "], CADASTRO_BASE)
    assert resultado.resolvidos == {"  fulano   de tal   um  ": "1"}


def test_nome_nao_encontrado_fica_explicito_sem_adivinhar():
    resultado = cruzar_por_nome(["NOME QUE NAO EXISTE"], CADASTRO_BASE)
    assert resultado.resolvidos == {}
    assert resultado.nao_encontrados == ["NOME QUE NAO EXISTE"]
    assert resultado.tem_bloqueio()


def test_nome_duplicado_no_cadastro_fica_ambiguo_sem_adivinhar():
    cadastro_com_duplicata = CADASTRO_BASE + [
        _registro("3", "FULANO DE TAL UM", "333.333.333-33")
    ]
    resultado = cruzar_por_nome(["FULANO DE TAL UM"], cadastro_com_duplicata)
    assert resultado.resolvidos == {}
    assert set(resultado.ambiguos["FULANO DE TAL UM"]) == {"1", "3"}
    assert resultado.tem_bloqueio()


def test_assert_sem_bloqueios_nao_levanta_quando_tudo_resolvido():
    resultado = cruzar_por_nome(["FULANO DE TAL UM", "FULANA DE TAL DOIS"], CADASTRO_BASE)
    assert_sem_bloqueios(resultado)  # não deve levantar


def test_assert_sem_bloqueios_levanta_com_detalhe_individual():
    resultado = cruzar_por_nome(
        ["NOME QUE NAO EXISTE", "OUTRO NOME AUSENTE"], CADASTRO_BASE
    )
    with pytest.raises(MatchingBlockedError) as exc_info:
        assert_sem_bloqueios(resultado)
    mensagem = str(exc_info.value)
    assert "NOME QUE NAO EXISTE" in mensagem
    assert "OUTRO NOME AUSENTE" in mensagem


def test_assert_sem_bloqueios_lista_candidatos_do_ambiguo():
    cadastro_com_duplicata = CADASTRO_BASE + [
        _registro("3", "FULANO DE TAL UM", "333.333.333-33")
    ]
    resultado = cruzar_por_nome(["FULANO DE TAL UM"], cadastro_com_duplicata)
    with pytest.raises(MatchingBlockedError) as exc_info:
        assert_sem_bloqueios(resultado)
    mensagem = str(exc_info.value)
    assert "'1'" in mensagem
    assert "'3'" in mensagem


def test_lista_vazia_de_origem_nao_gera_bloqueio():
    resultado = cruzar_por_nome([], CADASTRO_BASE)
    assert resultado.resolvidos == {}
    assert not resultado.tem_bloqueio()


def test_multiplos_nomes_mistos_resolvido_ambiguo_e_ausente():
    cadastro = CADASTRO_BASE + [_registro("3", "FULANO DE TAL UM", "333.333.333-33")]
    resultado = cruzar_por_nome(
        ["FULANA DE TAL DOIS", "FULANO DE TAL UM", "NOME AUSENTE"], cadastro
    )
    assert resultado.resolvidos == {"FULANA DE TAL DOIS": "2"}
    assert "FULANO DE TAL UM" in resultado.ambiguos
    assert resultado.nao_encontrados == ["NOME AUSENTE"]
