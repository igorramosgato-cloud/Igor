"""Testes dos extratores por aba. Fixtures 100% fictícias, no formato de
linhas que o openpyxl devolveria (tuplas), nunca lendo arquivo real —
ver .claude/rules/homologacao-dados.md.
"""

import pytest

from jrdp.extratores.cesta_basica import extrair_nomes_cesta_basica
from jrdp.extratores.horas import (
    ReferenciaHoraNaoSuportadaError,
    extrair_he_50,
    extrair_he_100,
)
from jrdp.extratores.valor_simples import extrair_valor_simples
from jrdp.extratores.vale_transporte import (
    ValeTransporteIndisponivelError,
    extrair_vale_transporte,
)


# --- valor_simples (Vale-refeição, Vale-compras, Convênio Farmácia, Adicional Noturno) ---


def test_extrai_registros_com_nome_e_valor():
    linhas = [
        (None, "FULANO DE TAL UM", 19.32084),
        (None, "FULANA DE TAL DOIS", 0),
        (None, None, None),  # padding no fim da aba real
    ]
    registros = extrair_valor_simples(linhas, "filial", "planilha_filial.xlsm", "Vale-refeicao")
    assert len(registros) == 2
    assert registros[0].nome == "FULANO DE TAL UM"
    assert registros[0].valor_bruto == "19.32084"
    assert registros[0].unidade == "filial"
    assert registros[0].aba_origem == "Vale-refeicao"


def test_linha_totalmente_vazia_e_ignorada():
    linhas = [(None, None, None), (None, None, None)]
    registros = extrair_valor_simples(linhas, "matriz", "arquivo.xlsm", "Vale-compras")
    assert registros == []


def test_linha_com_valor_mas_sem_nome_e_preservada_para_conferencia():
    linhas = [(None, None, 10.0)]
    registros = extrair_valor_simples(linhas, "matriz", "arquivo.xlsm", "convenio farmacia")
    assert len(registros) == 1
    assert registros[0].nome == ""


def test_rastreabilidade_linha_origem_correta():
    linhas = [
        (None, "FULANO", 1.0),
        (None, "FULANA", 2.0),
    ]
    registros = extrair_valor_simples(
        linhas, "filial", "arquivo.xlsm", "Adicional Noturno", linha_inicial=6
    )
    assert registros[0].linha_origem == 6
    assert registros[1].linha_origem == 7


# --- cesta_basica ---


def test_extrai_apenas_nomes_ignorando_outras_colunas():
    linhas = [
        (None, "FULANO DE TAL UM", "DEPTO X", "CC1", "algum CR", "assinado"),
        (None, "FULANA DE TAL DOIS", None, None, None, None),
        (None, None, None, None, None, None),
    ]
    nomes = extrair_nomes_cesta_basica(linhas)
    assert nomes == ["FULANO DE TAL UM", "FULANA DE TAL DOIS"]


def test_cesta_basica_lista_vazia():
    assert extrair_nomes_cesta_basica([]) == []


# --- horas (Hora-extra) — estrutural, não validado contra dados reais ---


def test_he50_extrai_referencia_string_hhmm():
    linhas = [(None, "FULANO", "BASE", "07:31", "VALOR", None, None, None)]
    registros = extrair_he_50(linhas, "filial", "arquivo.xlsm")
    assert len(registros) == 1
    assert registros[0].valor_bruto == "07:31"


def test_he100_extrai_coluna_diferente_da_he50():
    linhas = [(None, "FULANO", "BASE", "07:31", "VALOR1", "02:00", "VALOR2", None)]
    registros = extrair_he_100(linhas, "filial", "arquivo.xlsm")
    assert registros[0].valor_bruto == "02:00"


def test_he_ignora_linha_sem_referencia():
    linhas = [(None, "FULANO", "BASE", None, None, None, None, None)]
    assert extrair_he_50(linhas, "filial", "arquivo.xlsm") == []


def test_he_aceita_datetime_time():
    from datetime import time

    linhas = [(None, "FULANO", "BASE", time(7, 31), None, None, None, None)]
    registros = extrair_he_50(linhas, "filial", "arquivo.xlsm")
    assert registros[0].valor_bruto == "07:31"


def test_he_aceita_fracao_de_dia_float():
    # 07:31 como fração de dia: (7*60+31)/1440
    fracao = (7 * 60 + 31) / 1440
    linhas = [(None, "FULANO", "BASE", fracao, None, None, None, None)]
    registros = extrair_he_50(linhas, "filial", "arquivo.xlsm")
    assert registros[0].valor_bruto == "07:31"


def test_he_tipo_nao_suportado_e_rejeitado():
    from jrdp.canonico import RegistroOrigemBruto  # noqa: F401 (import só para clareza do teste)

    linhas_ruins = [(None, "FULANO", "BASE", ["lista inválida"], None, None, None, None)]
    with pytest.raises(ReferenciaHoraNaoSuportadaError):
        extrair_he_50(linhas_ruins, "filial", "arquivo.xlsm")


# --- vale_transporte — PENDENTE por design ---


def test_vale_transporte_sempre_bloqueia_por_falta_de_evidencia():
    with pytest.raises(ValeTransporteIndisponivelError):
        extrair_vale_transporte()
