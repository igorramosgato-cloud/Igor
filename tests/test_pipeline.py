"""Testes da camada canônica: construção de lançamentos, agrupamento por
evento, relatório de conferência e exportadores. Dados 100% fictícios —
ver .claude/rules/homologacao-dados.md.
"""

from decimal import Decimal

import pytest

from jrdp.cadastro_ativos import RegistroCadastro
from jrdp.canonico import RegistroOrigemBruto, agrupar_por_evento
from jrdp.conferencia import gerar_relatorio_evento
from jrdp.exportadores import (
    ExportacaoBlockedError,
    QuestorExporterH,
    QuestorExporterV,
)
from jrdp.pipeline import construir_lancamentos_cesta_basica, construir_lancamentos_evento

CONFIG_FICTICIA = {
    "cliente": "CLIENTE FICTICIO",
    "unidades": {
        "matriz": {
            "eventos": [
                {"codigo": 50, "descricao": "HE 100% Noturna", "tipo": "hora"},
                {"codigo": 35, "descricao": "HE 50%", "tipo": "hora"},
                {"codigo": 1524, "descricao": "Cesta Básica", "tipo": "valor"},
                {"codigo": 1955, "descricao": "VR", "tipo": "valor"},
            ]
        },
        "filial": {
            "eventos": [
                {"codigo": 35, "descricao": "HE 50%", "tipo": "hora"},
                {"codigo": 1524, "descricao": "Cesta Básica", "tipo": "valor"},
                {"codigo": 1955, "descricao": "VR", "tipo": "valor"},
                {
                    "codigo": None,
                    "descricao": "Evento Pendente",
                    "tipo": "valor",
                    "status": "PENDENTE",
                },
            ]
        },
    },
    "erros_historicos": [],
}


def _cadastro(contrato, nome, cpf="000.000.000-00"):
    return RegistroCadastro(
        contrato=contrato, nome=nome, admissao="01/01/2020", descricao="CARGO", cpf=cpf
    )


CADASTRO = [
    _cadastro("1", "FULANO DE TAL UM"),
    _cadastro("2", "FULANA DE TAL DOIS"),
    _cadastro("3", "SICRANO TRES"),
]


def _registro(unidade, nome, valor, aba="Vale-refeicao"):
    return RegistroOrigemBruto(
        unidade=unidade,
        nome=nome,
        valor_bruto=valor,
        arquivo_origem=f"planilha_{unidade}.xlsm",
        aba_origem=aba,
    )


# --- construção canônica ---


def test_lancamento_resolvido_valor_preserva_precisao_sem_arredondar():
    registros = [_registro("filial", "FULANO DE TAL UM", "19,32084")]
    lancamentos = construir_lancamentos_evento(
        registros, CADASTRO, CONFIG_FICTICIA, "CLIENTE FICTICIO", "08/2026", 1955
    )
    assert len(lancamentos) == 1
    l = lancamentos[0]
    assert l.status_matching == "resolvido"
    assert l.status_validacao == "valido"
    assert l.codigo_colaborador == "1"
    assert l.valor_normalizado == "19,32084"
    assert l.tipo == "valor"


def test_lancamento_tipo_h_usa_hmm_sem_conversao_decimal():
    registros = [_registro("filial", "FULANO DE TAL UM", "07:31", aba="Hora-extra")]
    lancamentos = construir_lancamentos_evento(
        registros, CADASTRO, CONFIG_FICTICIA, "CLIENTE FICTICIO", "08/2026", 35
    )
    assert lancamentos[0].valor_normalizado == "7,31"
    assert lancamentos[0].tipo == "hora"


def test_nome_nao_encontrado_fica_bloqueado_sem_valor():
    registros = [_registro("filial", "NOME INEXISTENTE", "10,00")]
    lancamentos = construir_lancamentos_evento(
        registros, CADASTRO, CONFIG_FICTICIA, "CLIENTE FICTICIO", "08/2026", 1955
    )
    l = lancamentos[0]
    assert l.status_matching == "nao_encontrado"
    assert l.codigo_colaborador is None
    assert l.valor_normalizado is None
    assert l.motivo_bloqueio is not None


def test_nome_ambiguo_fica_bloqueado_sem_adivinhar():
    cadastro_com_duplicata = CADASTRO + [_cadastro("4", "FULANO DE TAL UM")]
    registros = [_registro("filial", "FULANO DE TAL UM", "10,00")]
    lancamentos = construir_lancamentos_evento(
        registros, cadastro_com_duplicata, CONFIG_FICTICIA, "CLIENTE FICTICIO", "08/2026", 1955
    )
    l = lancamentos[0]
    assert l.status_matching == "ambiguo"
    assert l.codigo_colaborador is None


def test_evento_pendente_bloqueia_mesmo_com_matching_resolvido():
    registros = [_registro("filial", "FULANO DE TAL UM", "10,00")]
    # evento com código None não existe no config lookup por código, então
    # usamos um código que aponta para o evento PENDENTE via ajuste de teste:
    config = {
        "unidades": {
            "filial": {
                "eventos": [
                    {"codigo": 999, "descricao": "Pendente", "tipo": "valor", "status": "PENDENTE"}
                ]
            }
        }
    }
    lancamentos = construir_lancamentos_evento(
        registros, CADASTRO, config, "CLIENTE FICTICIO", "08/2026", 999
    )
    l = lancamentos[0]
    assert l.status_matching == "resolvido"
    assert l.status_validacao == "bloqueado"
    assert l.valor_normalizado is None


def test_evento_desconhecido_marca_invalido():
    registros = [_registro("filial", "FULANO DE TAL UM", "10,00")]
    lancamentos = construir_lancamentos_evento(
        registros, CADASTRO, CONFIG_FICTICIA, "CLIENTE FICTICIO", "08/2026", 424242
    )
    l = lancamentos[0]
    assert l.status_matching == "resolvido"
    assert l.status_validacao == "invalido"


def test_registro_com_valor_bruto_invalido_marca_invalido():
    registros = [_registro("filial", "FULANO DE TAL UM", "não é número")]
    lancamentos = construir_lancamentos_evento(
        registros, CADASTRO, CONFIG_FICTICIA, "CLIENTE FICTICIO", "08/2026", 1955
    )
    l = lancamentos[0]
    assert l.status_validacao == "invalido"
    assert l.valor_normalizado is None


def test_rastreabilidade_origem_para_registro_canonico():
    registros = [
        RegistroOrigemBruto(
            unidade="matriz",
            nome="FULANO DE TAL UM",
            valor_bruto="1",
            arquivo_origem="planilha_matriz.xlsm",
            aba_origem="Cesta basica",
            linha_origem=42,
        )
    ]
    lancamentos = construir_lancamentos_evento(
        registros, CADASTRO, CONFIG_FICTICIA, "CLIENTE FICTICIO", "08/2026", 1524
    )
    l = lancamentos[0]
    assert l.arquivo_origem == "planilha_matriz.xlsm"
    assert l.aba_origem == "Cesta basica"
    assert l.linha_origem == 42
    assert l.cliente == "CLIENTE FICTICIO"
    assert l.competencia == "08/2026"


# --- Cesta Básica (Matriz + Filial combinadas) ---


def test_cesta_basica_matriz_e_filial_combinadas_em_um_conjunto_por_evento():
    lancamentos = construir_lancamentos_cesta_basica(
        nomes_matriz=["FULANO DE TAL UM"],
        nomes_filial=["FULANA DE TAL DOIS", "SICRANO TRES"],
        cadastro=CADASTRO,
        config_cliente=CONFIG_FICTICIA,
        cliente="CLIENTE FICTICIO",
        competencia="08/2026",
        codigo_evento=1524,
        arquivo_matriz="planilha_matriz.xlsm",
        arquivo_filial="planilha_filial.xlsm",
    )
    assert len(lancamentos) == 3
    assert all(l.valor_normalizado == "1" for l in lancamentos)
    unidades = {l.unidade_origem for l in lancamentos}
    assert unidades == {"matriz", "filial"}

    agrupado = agrupar_por_evento(lancamentos)
    assert set(agrupado.keys()) == {1524}
    assert len(agrupado[1524]) == 3


def test_cesta_basica_filial_sozinha():
    lancamentos = construir_lancamentos_cesta_basica(
        nomes_matriz=[],
        nomes_filial=["FULANA DE TAL DOIS"],
        cadastro=CADASTRO,
        config_cliente=CONFIG_FICTICIA,
        cliente="CLIENTE FICTICIO",
        competencia="08/2026",
        codigo_evento=1524,
        arquivo_matriz="planilha_matriz.xlsm",
        arquivo_filial="planilha_filial.xlsm",
    )
    assert len(lancamentos) == 1
    assert lancamentos[0].unidade_origem == "filial"


# --- relatório de conferência ---


def test_relatorio_pass_quando_tudo_resolvido():
    registros = [
        _registro("matriz", "FULANO DE TAL UM", "10,00"),
        _registro("filial", "FULANA DE TAL DOIS", "20,00"),
    ]
    lancamentos = construir_lancamentos_evento(
        registros, CADASTRO, CONFIG_FICTICIA, "CLIENTE FICTICIO", "08/2026", 1955
    )
    relatorio = gerar_relatorio_evento(lancamentos)
    assert relatorio.status == "PASS"
    assert relatorio.pode_exportar() is True
    assert relatorio.quantidade_matriz == 1
    assert relatorio.quantidade_filial == 1
    assert relatorio.quantidade_total == 2
    assert relatorio.soma_valor == Decimal("30.00")


def test_relatorio_blocked_com_apenas_um_nao_encontrado():
    registros = [
        _registro("filial", "FULANO DE TAL UM", "10,00"),
        _registro("filial", "NOME INEXISTENTE", "20,00"),
    ]
    lancamentos = construir_lancamentos_evento(
        registros, CADASTRO, CONFIG_FICTICIA, "CLIENTE FICTICIO", "08/2026", 1955
    )
    relatorio = gerar_relatorio_evento(lancamentos)
    assert relatorio.status == "BLOCKED"
    assert relatorio.pode_exportar() is False
    assert relatorio.nao_encontrados == 1
    assert relatorio.encontrados == 1


def test_relatorio_blocked_com_ambiguo():
    cadastro_com_duplicata = CADASTRO + [_cadastro("4", "FULANO DE TAL UM")]
    registros = [_registro("filial", "FULANO DE TAL UM", "10,00")]
    lancamentos = construir_lancamentos_evento(
        registros, cadastro_com_duplicata, CONFIG_FICTICIA, "CLIENTE FICTICIO", "08/2026", 1955
    )
    relatorio = gerar_relatorio_evento(lancamentos)
    assert relatorio.status == "BLOCKED"
    assert relatorio.ambiguos == 1


def test_relatorio_e_sempre_gerado_mesmo_bloqueado():
    registros = [_registro("filial", "NOME INEXISTENTE", "10,00")]
    lancamentos = construir_lancamentos_evento(
        registros, CADASTRO, CONFIG_FICTICIA, "CLIENTE FICTICIO", "08/2026", 1955
    )
    relatorio = gerar_relatorio_evento(lancamentos)  # não deve levantar
    assert relatorio.status == "BLOCKED"


# --- exportadores ---


def test_exporter_v_bloqueia_com_matching_incompleto():
    registros = [
        _registro("filial", "FULANO DE TAL UM", "10,00"),
        _registro("filial", "NOME INEXISTENTE", "20,00"),
    ]
    lancamentos = construir_lancamentos_evento(
        registros, CADASTRO, CONFIG_FICTICIA, "CLIENTE FICTICIO", "08/2026", 1955
    )
    relatorio = gerar_relatorio_evento(lancamentos)
    with pytest.raises(ExportacaoBlockedError):
        QuestorExporterV().exportar(lancamentos, relatorio)


def test_exporter_v_gera_arquivo_quando_relatorio_pass():
    registros = [_registro("filial", "FULANO DE TAL UM", "19,32084")]
    lancamentos = construir_lancamentos_evento(
        registros, CADASTRO, CONFIG_FICTICIA, "CLIENTE FICTICIO", "08/2026", 1955
    )
    relatorio = gerar_relatorio_evento(lancamentos)
    conteudo = QuestorExporterV().exportar(lancamentos, relatorio)
    texto = conteudo.decode("cp850")
    linhas = texto.split("\r\n")
    assert linhas[0] == ";;;1955"
    assert linhas[1] == ";;;V"
    assert linhas[2] == "CÓDGIO;NOME;;"
    assert linhas[3] == "1;FULANO DE TAL UM;;19,32084"


def test_exporter_h_sempre_bloqueia_independente_do_relatorio():
    registros = [_registro("filial", "FULANO DE TAL UM", "07:31", aba="Hora-extra")]
    lancamentos = construir_lancamentos_evento(
        registros, CADASTRO, CONFIG_FICTICIA, "CLIENTE FICTICIO", "08/2026", 35
    )
    relatorio = gerar_relatorio_evento(lancamentos)
    assert relatorio.status == "PASS"  # matching resolvido, mas H continua bloqueado
    with pytest.raises(ExportacaoBlockedError, match="tipo=H"):
        QuestorExporterH().exportar(lancamentos, relatorio)
