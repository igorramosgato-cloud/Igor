"""Testes do cruzamento em duas etapas: match exato normalizado, depois
de-para homologado — nunca fuzzy automático. Dados fictícios.
"""

from jrdp.cadastro_ativos import RegistroCadastro
from jrdp.depara import RegistroDePara
from jrdp.origem_matching import cruzar_com_depara

CLIENTE = "CLIENTE_A"


def _cadastro(contrato, nome):
    return RegistroCadastro(
        contrato=contrato, nome=nome, admissao="01/01/2020", descricao="CARGO", cpf="0"
    )


def _depara(nome_origem, unidade, codigo, cliente=CLIENTE, status="aprovado"):
    return RegistroDePara(
        nome_origem=nome_origem,
        unidade=unidade,
        cliente=cliente,
        codigo_questor=codigo,
        nome_canonico=nome_origem,
        status=status,
        evidencia="teste",
        aprovado_por="teste",
        aprovado_em="2026-09-17",
    )


CADASTRO = [_cadastro("1", "FULANO DE TAL UM"), _cadastro("2", "FULANA DE TAL DOIS")]


def test_match_exato_nao_precisa_de_depara():
    resultado = cruzar_com_depara([("FULANO DE TAL UM", "filial")], CADASTRO, CLIENTE)
    assert resultado.resolvidos == {"FULANO DE TAL UM": "1"}


def test_nao_encontrado_no_exato_e_resolvido_pelo_depara():
    depara = [_depara("SICRANO", "filial", "99")]
    resultado = cruzar_com_depara([("SICRANO", "filial")], CADASTRO, CLIENTE, depara)
    assert resultado.resolvidos == {"SICRANO": "99"}
    assert resultado.nao_encontrados == []


def test_sem_depara_e_sem_match_exato_fica_nao_encontrado():
    resultado = cruzar_com_depara([("SICRANO", "filial")], CADASTRO, CLIENTE, depara=None)
    assert resultado.nao_encontrados == ["SICRANO"]


def test_depara_com_unidade_errada_nao_resolve():
    depara = [_depara("SICRANO", "matriz", "99")]
    resultado = cruzar_com_depara([("SICRANO", "filial")], CADASTRO, CLIENTE, depara)
    assert resultado.nao_encontrados == ["SICRANO"]


def test_depara_com_cliente_errado_nao_resolve():
    """Ponto central: de-para do cliente A nunca resolve para o cliente B."""
    depara = [_depara("SICRANO", "filial", "99", cliente="CLIENTE_A")]
    resultado = cruzar_com_depara([("SICRANO", "filial")], CADASTRO, "CLIENTE_B", depara)
    assert resultado.nao_encontrados == ["SICRANO"]


def test_depara_ambiguo_fica_ambiguo_nunca_resolvido_por_adivinhacao():
    depara = [
        _depara("SICRANO", "filial", "99"),
        _depara("SICRANO", "filial", "88"),
    ]
    resultado = cruzar_com_depara([("SICRANO", "filial")], CADASTRO, CLIENTE, depara)
    assert resultado.nao_encontrados == []
    assert set(resultado.ambiguos["SICRANO"]) == {"99", "88"}


def test_ordem_e_sempre_exato_antes_de_depara():
    """Se o exato já resolveu, o de-para (mesmo com um código diferente)
    nunca é consultado para esse nome — a ordem exato -> de-para não deve
    ser invertida nem misturada."""
    depara = [_depara("FULANO DE TAL UM", "filial", "999")]
    resultado = cruzar_com_depara([("FULANO DE TAL UM", "filial")], CADASTRO, CLIENTE, depara)
    assert resultado.resolvidos == {"FULANO DE TAL UM": "1"}  # do cadastro, não do de-para


def test_depara_revogado_nao_resolve():
    depara = [_depara("SICRANO", "filial", "99", status="revogado")]
    resultado = cruzar_com_depara([("SICRANO", "filial")], CADASTRO, CLIENTE, depara)
    assert resultado.nao_encontrados == ["SICRANO"]


def test_mistura_exato_depara_e_nao_encontrado():
    depara = [_depara("SICRANO", "filial", "99")]
    resultado = cruzar_com_depara(
        [
            ("FULANO DE TAL UM", "filial"),  # exato
            ("SICRANO", "filial"),  # de-para
            ("NINGUEM", "filial"),  # nenhum dos dois
        ],
        CADASTRO,
        CLIENTE,
        depara,
    )
    assert resultado.resolvidos == {"FULANO DE TAL UM": "1", "SICRANO": "99"}
    assert resultado.nao_encontrados == ["NINGUEM"]
