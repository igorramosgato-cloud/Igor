"""Testes do manifesto do pacote — fail-closed POR EVENTO, nunca pelo
pacote inteiro. Dados fictícios.
"""

from jrdp.canonico import RegistroOrigemBruto
from jrdp.cadastro_ativos import RegistroCadastro
from jrdp.conferencia import gerar_relatorio_evento
from jrdp.manifesto import gerar_manifesto
from jrdp.pipeline import construir_lancamentos_evento

CONFIG = {
    "unidades": {
        "filial": {
            "eventos": [
                {"codigo": 1524, "descricao": "Cesta", "tipo": "valor"},
                {"codigo": 1955, "descricao": "VR", "tipo": "valor"},
            ]
        },
        "matriz": {"eventos": []},
    }
}

CADASTRO = [
    RegistroCadastro(contrato="1", nome="FULANO", admissao="01/01/2020", descricao="X", cpf="0"),
    RegistroCadastro(contrato="2", nome="FULANA", admissao="01/01/2020", descricao="X", cpf="0"),
]


def _reg(nome):
    return RegistroOrigemBruto(
        unidade="filial",
        nome=nome,
        valor_bruto="10,00",
        arquivo_origem="arquivo.xlsm",
        aba_origem="Vale-refeicao",
    )


def test_manifesto_mistura_pass_e_blocked_independentemente():
    # 1524: 100% resolvido -> PASS
    lanc_1524 = construir_lancamentos_evento(
        [_reg("FULANO"), _reg("FULANA")], CADASTRO, CONFIG, "C", "08/2026", 1524
    )
    # 1955: um não encontrado -> BLOCKED
    lanc_1955 = construir_lancamentos_evento(
        [_reg("FULANO"), _reg("NOME INEXISTENTE")], CADASTRO, CONFIG, "C", "08/2026", 1955
    )
    relatorios = {
        1524: gerar_relatorio_evento(lanc_1524),
        1955: gerar_relatorio_evento(lanc_1955),
    }
    manifesto = gerar_manifesto(relatorios)

    assert manifesto.eventos_gerados == 1
    assert manifesto.eventos_bloqueados == 1
    assert manifesto.status_pacote == "PARCIALMENTE LIBERADO"

    linha_1524 = next(l for l in manifesto.linhas if l.codigo_evento == 1524)
    linha_1955 = next(l for l in manifesto.linhas if l.codigo_evento == 1955)
    assert linha_1524.status == "PASS"
    assert linha_1955.status == "BLOCKED"
    assert "1 não encontrados" in linha_1955.detalhe


def test_manifesto_totalmente_liberado():
    lanc = construir_lancamentos_evento(
        [_reg("FULANO"), _reg("FULANA")], CADASTRO, CONFIG, "C", "08/2026", 1524
    )
    manifesto = gerar_manifesto({1524: gerar_relatorio_evento(lanc)})
    assert manifesto.status_pacote == "TOTALMENTE LIBERADO"
    assert manifesto.eventos_bloqueados == 0


def test_manifesto_totalmente_bloqueado():
    lanc = construir_lancamentos_evento(
        [_reg("NOME INEXISTENTE")], CADASTRO, CONFIG, "C", "08/2026", 1524
    )
    manifesto = gerar_manifesto({1524: gerar_relatorio_evento(lanc)})
    assert manifesto.status_pacote == "TOTALMENTE BLOQUEADO"
    assert manifesto.eventos_gerados == 0


def test_manifesto_texto_segue_formato_esperado():
    lanc = construir_lancamentos_evento(
        [_reg("FULANO"), _reg("FULANA")], CADASTRO, CONFIG, "C", "08/2026", 1524
    )
    manifesto = gerar_manifesto({1524: gerar_relatorio_evento(lanc)})
    texto = manifesto.texto()
    assert "EVENTO 1524 — PASS — arquivo gerado" in texto
    assert "PACOTE: TOTALMENTE LIBERADO" in texto
    assert "0 evento(s) bloqueado(s) / 1 gerado(s)" in texto


def test_evento_100_por_cento_pass_nao_e_afetado_por_outro_bloqueado():
    """O ponto central da decisão: 1524 gera mesmo com 1955 bloqueado."""
    lanc_1524 = construir_lancamentos_evento(
        [_reg("FULANO"), _reg("FULANA")], CADASTRO, CONFIG, "C", "08/2026", 1524
    )
    lanc_1955 = construir_lancamentos_evento(
        [_reg("NOME INEXISTENTE")], CADASTRO, CONFIG, "C", "08/2026", 1955
    )
    relatorio_1524 = gerar_relatorio_evento(lanc_1524)
    relatorio_1955 = gerar_relatorio_evento(lanc_1955)
    assert relatorio_1524.pode_exportar() is True
    assert relatorio_1955.pode_exportar() is False
