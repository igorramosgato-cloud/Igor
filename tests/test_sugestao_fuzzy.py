"""Testes da sugestão fuzzy — SOMENTE diagnóstico, nunca decide matching.
Dados fictícios.
"""

from jrdp.cadastro_ativos import RegistroCadastro
from jrdp.sugestao_fuzzy import sugerir_candidatos


def _cadastro(contrato, nome):
    return RegistroCadastro(
        contrato=contrato, nome=nome, admissao="01/01/2020", descricao="CARGO", cpf="0"
    )


CADASTRO = [
    _cadastro("1", "JOAO DA SILVA SANTOS"),
    _cadastro("2", "MARIA APARECIDA DE SOUZA"),
    _cadastro("3", "PEDRO ALVES"),
]


def test_sugere_candidato_proximo_por_sobrenome_faltante():
    sugestoes = sugerir_candidatos("JOAO DA SILVA", CADASTRO)
    assert len(sugestoes) >= 1
    assert sugestoes[0].nome_cadastro == "JOAO DA SILVA SANTOS"
    assert sugestoes[0].contrato == "1"


def test_sem_candidato_proximo_devolve_lista_vazia():
    sugestoes = sugerir_candidatos("XYZXYZXYZ NAO PARECIDO", CADASTRO)
    assert sugestoes == []


def test_respeita_limite_de_sugestoes():
    sugestoes = sugerir_candidatos("JOAO DA SILVA", CADASTRO, limite=1)
    assert len(sugestoes) <= 1


def test_sugestao_nunca_e_aplicada_automaticamente_ao_matching():
    """Prova de arquitetura: sugerir_candidatos não tem nenhuma forma de
    alimentar ResultadoCruzamento.resolvidos — só devolve dados para o
    analista decidir manualmente (ex.: criando uma entrada no de-para)."""
    sugestoes = sugerir_candidatos("JOAO DA SILVA", CADASTRO)
    assert not hasattr(sugestoes[0], "aplicar")
    assert not hasattr(sugestoes[0], "resolver")
