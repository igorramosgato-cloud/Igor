"""Testes de reconciliação e duplicidades do relatório de conferência.
Dados 100% fictícios.
"""

from decimal import Decimal

from jrdp.canonico import RegistroOrigemBruto
from jrdp.conferencia import gerar_relatorio_evento, reconciliar_total_fonte
from jrdp.cadastro_ativos import RegistroCadastro
from jrdp.pipeline import construir_lancamentos_evento

CONFIG = {
    "unidades": {
        "filial": {
            "eventos": [
                {"codigo": 1955, "descricao": "VR", "tipo": "valor"},
                {"codigo": 35, "descricao": "HE 50%", "tipo": "hora"},
            ]
        },
        "matriz": {"eventos": []},
    }
}


def _cadastro(contrato, nome):
    return RegistroCadastro(
        contrato=contrato, nome=nome, admissao="01/01/2020", descricao="CARGO", cpf="0"
    )


CADASTRO = [_cadastro("1", "FULANO"), _cadastro("2", "FULANA")]


def _reg(unidade, nome, valor):
    return RegistroOrigemBruto(
        unidade=unidade,
        nome=nome,
        valor_bruto=valor,
        arquivo_origem="arquivo.xlsm",
        aba_origem="Vale-refeicao",
    )


def test_duplicidade_e_contada_sem_bloquear_por_si_so():
    registros = [
        _reg("filial", "FULANO", "10,00"),
        _reg("filial", "FULANO", "10,00"),  # mesmo nome duas vezes
    ]
    lancamentos = construir_lancamentos_evento(registros, CADASTRO, CONFIG, "C", "08/2026", 1955)
    relatorio = gerar_relatorio_evento(lancamentos)
    assert relatorio.duplicidades == 1
    # duplicidade sozinha não bloqueia — só nao_encontrados/ambiguos/invalidos bloqueiam
    assert relatorio.status == "PASS"


def test_sem_duplicidade_quando_nomes_diferentes():
    registros = [_reg("filial", "FULANO", "10,00"), _reg("filial", "FULANA", "20,00")]
    lancamentos = construir_lancamentos_evento(registros, CADASTRO, CONFIG, "C", "08/2026", 1955)
    relatorio = gerar_relatorio_evento(lancamentos)
    assert relatorio.duplicidades == 0


def test_reconciliacao_valor_bate():
    registros = [_reg("filial", "FULANO", "10,00"), _reg("filial", "FULANA", "20,50")]
    lancamentos = construir_lancamentos_evento(registros, CADASTRO, CONFIG, "C", "08/2026", 1955)
    relatorio = gerar_relatorio_evento(lancamentos)
    assert reconciliar_total_fonte(relatorio, "30.50") is True


def test_reconciliacao_valor_diverge():
    registros = [_reg("filial", "FULANO", "10,00")]
    lancamentos = construir_lancamentos_evento(registros, CADASTRO, CONFIG, "C", "08/2026", 1955)
    relatorio = gerar_relatorio_evento(lancamentos)
    assert reconciliar_total_fonte(relatorio, "999.99") is False


def test_reconciliacao_horas_usa_minutos_nao_decimal():
    registros = [
        RegistroOrigemBruto(
            unidade="filial",
            nome="FULANO",
            valor_bruto="01:52",
            arquivo_origem="arquivo.xlsm",
            aba_origem="Hora-extra",
        ),
        RegistroOrigemBruto(
            unidade="filial",
            nome="FULANA",
            valor_bruto="00:32",
            arquivo_origem="arquivo.xlsm",
            aba_origem="Hora-extra",
        ),
    ]
    lancamentos = construir_lancamentos_evento(registros, CADASTRO, CONFIG, "C", "08/2026", 35)
    relatorio = gerar_relatorio_evento(lancamentos)
    # total real: 112 + 32 = 144 minutos (02:24) — nunca "1,84"
    assert relatorio.total_horas_minutos == 144
    assert reconciliar_total_fonte(relatorio, 144) is True
    assert reconciliar_total_fonte(relatorio, 184) is False  # a soma decimal errada não bate
