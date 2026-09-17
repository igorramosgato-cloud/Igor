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
    mesclar_depara,
    resolver_depara,
    salvar_depara,
)

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "questor" / "depara_sanitizado.json"
)

CLIENTE = "CLIENTE_FICTICIO"


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
        '{"entradas": [{"nome_origem": "X", "unidade": "filial", "cliente": "C", '
        '"codigo_questor": "1", "nome_canonico": "X", "status": "invalido", '
        '"evidencia": "e", "aprovado_por": "a", "aprovado_em": "2026-01-01"}]}'
    )
    with pytest.raises(DeParaContractError):
        carregar_depara_de_texto(texto)


def test_cliente_curinga_e_rejeitado():
    texto = (
        '{"entradas": [{"nome_origem": "X", "unidade": "filial", "cliente": "*", '
        '"codigo_questor": "1", "nome_canonico": "X", "status": "aprovado", '
        '"evidencia": "e", "aprovado_por": "a", "aprovado_em": "2026-01-01"}]}'
    )
    with pytest.raises(DeParaContractError):
        carregar_depara_de_texto(texto)


def test_resolve_por_de_para_aprovado(registros):
    status, codigos = resolver_depara("FULANO DE TAL", "filial", CLIENTE, registros)
    assert status == "resolvido"
    assert codigos == ["101"]


def test_resolve_ignorando_espacos_e_caixa(registros):
    status, codigos = resolver_depara("  fulano   de tal  ", "filial", CLIENTE, registros)
    assert status == "resolvido"
    assert codigos == ["101"]


def test_entrada_curinga_vale_para_qualquer_unidade(registros):
    status_matriz, codigos_matriz = resolver_depara("CICLANA DA SILVA", "matriz", CLIENTE, registros)
    status_filial, codigos_filial = resolver_depara("CICLANA DA SILVA", "filial", CLIENTE, registros)
    assert status_matriz == "resolvido" and codigos_matriz == ["202"]
    assert status_filial == "resolvido" and codigos_filial == ["202"]


def test_unidade_errada_nao_resolve(registros):
    status, codigos = resolver_depara("FULANO DE TAL", "matriz", CLIENTE, registros)
    assert status == "nao_encontrado"
    assert codigos == []


def test_cliente_errado_nunca_reaproveita_correspondencia(registros):
    """Ponto central da decisão de 2026-09-17: de-para é por cliente,
    não só por nome+unidade. Um nome igual em outro cliente nunca deve
    resolver por acidente."""
    status, codigos = resolver_depara("FULANO DE TAL", "filial", "OUTRO_CLIENTE", registros)
    assert status == "nao_encontrado"
    assert codigos == []


def test_nome_sem_entrada_e_nao_encontrado(registros):
    status, codigos = resolver_depara("NOME QUE NAO EXISTE NO DEPARA", "filial", CLIENTE, registros)
    assert status == "nao_encontrado"


def test_entrada_revogada_e_ignorada(registros):
    status, codigos = resolver_depara("NOME REVOGADO", "filial", CLIENTE, registros)
    assert status == "nao_encontrado"


def test_de_para_ambiguo_com_dois_codigos_aprovados():
    registros_ambiguos = [
        RegistroDePara(
            nome_origem="FULANO",
            unidade="filial",
            cliente=CLIENTE,
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
            cliente=CLIENTE,
            codigo_questor="2",
            nome_canonico="FULANO B",
            status="aprovado",
            evidencia="e2",
            aprovado_por="a",
            aprovado_em="2026-01-02",
        ),
    ]
    status, codigos = resolver_depara("FULANO", "filial", CLIENTE, registros_ambiguos)
    assert status == "ambiguo"
    assert codigos == ["1", "2"]


def test_reaproveitamento_seguro_do_mesmo_depara(registros):
    """Carregar e aplicar o mesmo de-para duas vezes produz o mesmo
    resultado — não há efeito colateral entre chamadas."""
    r1 = resolver_depara("FULANO DE TAL", "filial", CLIENTE, registros)
    r2 = resolver_depara("FULANO DE TAL", "filial", CLIENTE, registros)
    assert r1 == r2


def test_salvar_e_recarregar_produz_os_mesmos_registros(registros, tmp_path):
    caminho = tmp_path / "depara_salvo.json"
    salvar_depara(caminho, registros)
    recarregados = carregar_depara(caminho)
    assert recarregados == registros


def test_mesclar_nao_duplica_entradas_iguais(registros):
    mesclado = mesclar_depara(registros, registros)
    assert len(mesclado) == len(registros)


def test_mesclar_adiciona_entradas_novas(registros):
    nova = RegistroDePara(
        nome_origem="NOVO NOME",
        unidade="filial",
        cliente=CLIENTE,
        codigo_questor="999",
        nome_canonico="NOVO NOME COMPLETO",
        status="aprovado",
        evidencia="e",
        aprovado_por="a",
        aprovado_em="2026-09-17",
    )
    mesclado = mesclar_depara(registros, [nova])
    assert len(mesclado) == len(registros) + 1
    assert nova in mesclado


def test_mesclar_nunca_sobrescreve_entrada_existente(registros):
    """Uma tentativa de reintroduzir a mesma chave não deve duplicar nem
    substituir — o histórico original prevalece."""
    duplicata_com_evidencia_diferente = RegistroDePara(
        nome_origem="FULANO DE TAL",
        unidade="filial",
        cliente=CLIENTE,
        codigo_questor="101",
        nome_canonico="OUTRO NOME QUALQUER",
        status="aprovado",
        evidencia="evidencia diferente",
        aprovado_por="outro analista",
        aprovado_em="2026-09-18",
    )
    mesclado = mesclar_depara(registros, [duplicata_com_evidencia_diferente])
    assert len(mesclado) == len(registros)
