from datetime import date

import pytest

from calculadora_rescisao import (
    DadosRescisao,
    calcular_irrf,
    calcular_numero_parcelas_seguro_desemprego,
    calcular_rescisao,
    calcular_valor_parcela_seguro_desemprego,
    gerar_evento_esocial_s2299,
    _aplicar_tabela_irrf,
    DESCONTO_SIMPLIFICADO_IRRF_MENSAL,
)


def rubricas_por_nome(itens, trecho):
    return [i for i in itens if trecho in i["rubrica"]]


def test_exemplo_sem_justa_causa_bate_com_calculo_manual():
    d = DadosRescisao(
        salario_base=3500.00,
        data_admissao=date(2022, 3, 10),
        data_desligamento=date(2026, 7, 15),
        tipo_rescisao="sem_justa_causa",
        aviso_previo="indenizado",
        saldo_fgts_depositado=6200.00,
        media_horas_extras_mensal=10,
    )
    r = calcular_rescisao(d)

    assert rubricas_por_nome(r["rubricas"], "Saldo de salário")[0]["valor"] == 1750.00
    assert rubricas_por_nome(r["rubricas"], "Aviso prévio")[0]["valor"] == pytest.approx(5300.91, abs=0.01)
    assert rubricas_por_nome(r["rubricas"], "13º")[0]["valor"] == pytest.approx(2524.24, abs=0.01)
    assert rubricas_por_nome(r["rubricas"], "Multa 40%")[0]["valor"] == pytest.approx(2786.40, abs=0.01)
    assert r["total_descontos"] == pytest.approx(401.51, abs=0.01)
    assert r["seguro_desemprego"]["elegivel"] is True
    assert r["seguro_desemprego"]["numero_parcelas"] == 5
    assert r["fgts"]["percentual_saque_estimado"] == 1.0


def test_justa_causa_perde_13_e_ferias_proporcionais():
    d = DadosRescisao(
        salario_base=3000,
        data_admissao=date(2024, 1, 10),
        data_desligamento=date(2026, 7, 15),
        tipo_rescisao="justa_causa",
        ferias_vencidas=True,
    )
    r = calcular_rescisao(d)

    assert not rubricas_por_nome(r["rubricas"], "13º")
    assert not rubricas_por_nome(r["rubricas"], "proporcionais")
    assert rubricas_por_nome(r["rubricas"], "Férias vencidas")
    assert r["seguro_desemprego"]["elegivel"] is False
    assert r["fgts"]["percentual_saque_estimado"] == 0.0


def test_rescisao_indireta_tem_efeitos_de_sem_justa_causa():
    d = DadosRescisao(
        salario_base=4000,
        data_admissao=date(2023, 1, 10),
        data_desligamento=date(2026, 7, 10),
        tipo_rescisao="rescisao_indireta",
        saldo_fgts_depositado=5000,
    )
    r = calcular_rescisao(d)

    assert rubricas_por_nome(r["rubricas"], "Aviso prévio")
    assert rubricas_por_nome(r["rubricas"], "Multa 40%")
    assert r["seguro_desemprego"]["elegivel"] is True


def test_acordo_484a_usa_metade_do_aviso_e_20_por_cento_de_multa():
    d = DadosRescisao(
        salario_base=4000,
        data_admissao=date(2020, 6, 1),
        data_desligamento=date(2026, 7, 20),
        tipo_rescisao="acordo_484a",
        saldo_fgts_depositado=8000,
    )
    r = calcular_rescisao(d)

    assert rubricas_por_nome(r["rubricas"], "20%")
    assert r["fgts"]["percentual_saque_estimado"] == 0.80
    assert r["seguro_desemprego"]["elegivel"] is False


def test_art_479_provento_quando_empregador_antecipa_experiencia():
    d = DadosRescisao(
        salario_base=2500,
        data_admissao=date(2026, 5, 1),
        data_desligamento=date(2026, 7, 1),
        tipo_rescisao="termino_experiencia",
        aviso_previo="nao_aplicavel",
        data_fim_contrato_experiencia=date(2026, 10, 31),
        quem_antecipou_experiencia="empregador",
    )
    r = calcular_rescisao(d)
    assert rubricas_por_nome(r["rubricas"], "Art. 479")
    assert not rubricas_por_nome(r["descontos"], "Art. 480")


def test_art_480_desconto_quando_empregado_antecipa_experiencia():
    d = DadosRescisao(
        salario_base=2500,
        data_admissao=date(2026, 5, 1),
        data_desligamento=date(2026, 7, 1),
        tipo_rescisao="termino_experiencia",
        aviso_previo="nao_aplicavel",
        data_fim_contrato_experiencia=date(2026, 10, 31),
        quem_antecipou_experiencia="empregado",
    )
    r = calcular_rescisao(d)
    assert rubricas_por_nome(r["descontos"], "Art. 480")
    assert not rubricas_por_nome(r["rubricas"], "Art. 479")


def test_termino_normal_de_experiencia_permite_saque_fgts_sem_multa():
    d = DadosRescisao(
        salario_base=2500,
        data_admissao=date(2026, 1, 1),
        data_desligamento=date(2026, 7, 1),
        tipo_rescisao="termino_experiencia",
        aviso_previo="nao_aplicavel",
        data_fim_contrato_experiencia=date(2026, 7, 1),
    )
    r = calcular_rescisao(d)
    assert not rubricas_por_nome(r["rubricas"], "Multa")
    assert r["fgts"]["percentual_saque_estimado"] == 1.0


def test_aposentadoria_sem_aviso_nem_multa_mas_com_proporcionais():
    d = DadosRescisao(
        salario_base=3000,
        data_admissao=date(2015, 1, 1),
        data_desligamento=date(2026, 7, 1),
        tipo_rescisao="aposentadoria",
        saldo_fgts_depositado=10000,
    )
    r = calcular_rescisao(d)
    assert not rubricas_por_nome(r["rubricas"], "Aviso")
    assert not rubricas_por_nome(r["rubricas"], "Multa")
    assert rubricas_por_nome(r["rubricas"], "13º")
    assert r["fgts"]["percentual_saque_estimado"] == 1.0
    assert r["seguro_desemprego"]["elegivel"] is False


def test_estabilidade_gestante_gera_alerta_e_indenizacao():
    d = DadosRescisao(
        salario_base=3000,
        data_admissao=date(2025, 1, 10),
        data_desligamento=date(2026, 7, 10),
        tipo_rescisao="sem_justa_causa",
        saldo_fgts_depositado=2000,
        estabilidade_gestante_dt_fim=date(2026, 12, 1),
    )
    r = calcular_rescisao(d)
    assert len(r["alertas_risco"]) == 1
    assert "gestante" in r["alertas_risco"][0]
    assert rubricas_por_nome(r["rubricas"], "estabilit")
    assert rubricas_por_nome(r["rubricas"], "13º proporcional estimado do período estabilit")


def test_sem_estabilidade_nao_gera_alerta():
    d = DadosRescisao(
        salario_base=3000,
        data_admissao=date(2025, 1, 10),
        data_desligamento=date(2026, 7, 10),
        tipo_rescisao="sem_justa_causa",
    )
    r = calcular_rescisao(d)
    assert r["alertas_risco"] == []
    assert not rubricas_por_nome(r["rubricas"], "estabilit")


def test_irrf_usa_o_menor_entre_deducao_legal_e_desconto_simplificado():
    base = 6000.0
    irrf_legal = _aplicar_tabela_irrf(base - 3 * 189.59)
    irrf_simplificado = _aplicar_tabela_irrf(base - DESCONTO_SIMPLIFICADO_IRRF_MENSAL)
    esperado_tabela = min(irrf_legal, irrf_simplificado)

    resultado = calcular_irrf(base, dependentes=3)
    assert resultado <= round(esperado_tabela, 2)


def test_seguro_desemprego_soma_outros_vinculos_do_periodo():
    d = DadosRescisao(
        salario_base=2000,
        data_admissao=date(2026, 1, 1),
        data_desligamento=date(2026, 7, 1),  # 6 meses neste vínculo
        tipo_rescisao="sem_justa_causa",
        meses_trabalhados_outros_vinculos_periodo=6,  # completa 12 meses
    )
    r = calcular_rescisao(d)
    assert r["seguro_desemprego"]["elegivel"] is True
    assert r["seguro_desemprego"]["numero_parcelas"] == 4


@pytest.mark.parametrize(
    "meses,solicitacoes,esperado",
    [
        (11, 0, 0),
        (12, 0, 4),
        (24, 0, 5),
        (9, 1, 3),
        (8, 1, 0),
        (6, 2, 3),
        (5, 2, 0),
    ],
)
def test_numero_parcelas_seguro_desemprego(meses, solicitacoes, esperado):
    assert calcular_numero_parcelas_seguro_desemprego(meses, solicitacoes) == esperado


def test_valor_parcela_seguro_desemprego_respeita_piso_e_teto():
    assert calcular_valor_parcela_seguro_desemprego(1000) == 1621.00  # piso do salário mínimo
    assert calcular_valor_parcela_seguro_desemprego(10000) == 2518.65  # teto


def test_gerar_evento_esocial_mapeia_motivo_e_usa_mapa_rubricas():
    d = DadosRescisao(
        salario_base=3000,
        data_admissao=date(2024, 1, 10),
        data_desligamento=date(2026, 7, 15),
        tipo_rescisao="sem_justa_causa",
    )
    r = calcular_rescisao(d)
    evento = gerar_evento_esocial_s2299(d, r, mapa_rubricas={"Saldo de salário": "1000"})
    assert evento["infoDeslig"]["mtvDeslig"] == "30"
    proventos = evento["infoDeslig"]["verbasRescisorias"]["proventos"]
    saldo = next(p for p in proventos if p["descricao"] == "Saldo de salário")
    assert saldo["codRubr"] == "1000"


def test_gerar_evento_esocial_codigo_rescisao_indireta():
    d = DadosRescisao(
        salario_base=3000,
        data_admissao=date(2024, 1, 10),
        data_desligamento=date(2026, 7, 15),
        tipo_rescisao="rescisao_indireta",
    )
    r = calcular_rescisao(d)
    evento = gerar_evento_esocial_s2299(d, r)
    assert evento["infoDeslig"]["mtvDeslig"] == "32"
