"""Testes da consolidação de identidade — a mesma pessoa não pode ser
contada duas vezes só porque aparece em vários eventos. Dados fictícios.
"""

from jrdp.canonico import RegistroOrigemBruto
from jrdp.cadastro_ativos import RegistroCadastro
from jrdp.identidade import (
    coletar_ocorrencias_nao_encontradas,
    consolidar_nao_encontrados,
    contar_pessoas_unicas_nao_encontradas,
)
from jrdp.pipeline import construir_lancamentos_evento

CONFIG = {
    "unidades": {
        "filial": {
            "eventos": [
                {"codigo": 1955, "descricao": "VR", "tipo": "valor"},
                {"codigo": 813, "descricao": "Compras", "tipo": "valor"},
            ]
        },
        "matriz": {"eventos": []},
    }
}

CADASTRO = [
    RegistroCadastro(
        contrato="1", nome="FULANO CONHECIDO", admissao="01/01/2020", descricao="X", cpf="0"
    )
]


def _reg(nome, aba):
    return RegistroOrigemBruto(
        unidade="filial",
        nome=nome,
        valor_bruto="10,00",
        arquivo_origem="arquivo.xlsm",
        aba_origem=aba,
    )


def test_mesma_pessoa_em_dois_eventos_conta_como_uma():
    lancamentos_1955 = construir_lancamentos_evento(
        [_reg("PESSOA SEM CADASTRO", "Vale-refeicao")], CADASTRO, CONFIG, "C", "08/2026", 1955
    )
    lancamentos_813 = construir_lancamentos_evento(
        [_reg("PESSOA SEM CADASTRO", "Vale-compras")], CADASTRO, CONFIG, "C", "08/2026", 813
    )
    consolidado = consolidar_nao_encontrados({1955: lancamentos_1955, 813: lancamentos_813})
    assert len(consolidado) == 1
    assert contar_pessoas_unicas_nao_encontradas({1955: lancamentos_1955, 813: lancamentos_813}) == 1
    assert consolidado["PESSOA SEM CADASTRO"] == [813, 1955]


def test_pessoas_diferentes_contam_separadamente():
    lancamentos_1955 = construir_lancamentos_evento(
        [_reg("PESSOA UM", "Vale-refeicao")], CADASTRO, CONFIG, "C", "08/2026", 1955
    )
    lancamentos_813 = construir_lancamentos_evento(
        [_reg("PESSOA DOIS", "Vale-compras")], CADASTRO, CONFIG, "C", "08/2026", 813
    )
    total = contar_pessoas_unicas_nao_encontradas({1955: lancamentos_1955, 813: lancamentos_813})
    assert total == 2


def test_normalizacao_espacos_e_caixa_consolida_como_a_mesma_pessoa():
    lancamentos_1955 = construir_lancamentos_evento(
        [_reg("pessoa   sem cadastro", "Vale-refeicao")], CADASTRO, CONFIG, "C", "08/2026", 1955
    )
    lancamentos_813 = construir_lancamentos_evento(
        [_reg("PESSOA SEM CADASTRO", "Vale-compras")], CADASTRO, CONFIG, "C", "08/2026", 813
    )
    total = contar_pessoas_unicas_nao_encontradas({1955: lancamentos_1955, 813: lancamentos_813})
    assert total == 1


def test_pessoa_resolvida_nao_entra_na_consolidacao():
    lancamentos = construir_lancamentos_evento(
        [_reg("FULANO CONHECIDO", "Vale-refeicao")], CADASTRO, CONFIG, "C", "08/2026", 1955
    )
    assert consolidar_nao_encontrados({1955: lancamentos}) == {}


def test_evento_sem_nao_encontrados_nao_aparece():
    lancamentos = construir_lancamentos_evento(
        [_reg("FULANO CONHECIDO", "Vale-refeicao")], CADASTRO, CONFIG, "C", "08/2026", 1955
    )
    assert contar_pessoas_unicas_nao_encontradas({1955: lancamentos}) == 0


def test_coletar_ocorrencias_agrega_eventos_da_mesma_pessoa_unidade():
    lancamentos_1955 = construir_lancamentos_evento(
        [_reg("PESSOA SEM CADASTRO", "Vale-refeicao")], CADASTRO, CONFIG, "C", "08/2026", 1955
    )
    lancamentos_813 = construir_lancamentos_evento(
        [_reg("PESSOA SEM CADASTRO", "Vale-compras")], CADASTRO, CONFIG, "C", "08/2026", 813
    )
    ocorrencias = coletar_ocorrencias_nao_encontradas(
        {1955: lancamentos_1955, 813: lancamentos_813}
    )
    assert len(ocorrencias) == 1
    assert ocorrencias[0]["nome_origem"] == "PESSOA SEM CADASTRO"
    assert ocorrencias[0]["unidade"] == "filial"
    assert ocorrencias[0]["eventos"] == [813, 1955]


def test_coletar_ocorrencias_separa_por_unidade():
    lancamentos_matriz = construir_lancamentos_evento(
        [
            RegistroOrigemBruto(
                unidade="matriz",
                nome="PESSOA SEM CADASTRO",
                valor_bruto="10,00",
                arquivo_origem="arquivo.xlsm",
                aba_origem="Cesta basica",
            )
        ],
        CADASTRO,
        CONFIG,
        "C",
        "08/2026",
        1955,
    )
    lancamentos_filial = construir_lancamentos_evento(
        [_reg("PESSOA SEM CADASTRO", "Vale-refeicao")], CADASTRO, CONFIG, "C", "08/2026", 1955
    )
    ocorrencias = coletar_ocorrencias_nao_encontradas(
        {1955: lancamentos_matriz + lancamentos_filial}
    )
    # mesma pessoa, unidades diferentes -> duas ocorrências separadas
    assert len(ocorrencias) == 2
    unidades = {o["unidade"] for o in ocorrencias}
    assert unidades == {"matriz", "filial"}
