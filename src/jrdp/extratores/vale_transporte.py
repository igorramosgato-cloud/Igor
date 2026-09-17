"""Vale-transporte — PENDENTE, propositalmente sem extração funcional.

Inventariado em 2026-09-17: a aba `Vale-transporte` existe nos dois
arquivos reais (Matriz e Filial), mas **não tem nenhum registro de
funcionário** — as únicas linhas preenchidas (30 em cada arquivo) são uma
tabela de totalizadores por centro de custo/departamento (colunas O/P do
Excel), não lançamentos individuais.

Além disso, mesmo se houvesse registros, não está confirmado qual coluna
do cabeçalho (`TOTAL`, `DESCONTO`, `ACRÉSCIMO` ou `VALOR DA CARGA`)
alimenta o valor do evento 815 no Questor — o cabeçalho tem todas essas
colunas e nenhuma evidência aponta qual é a certa.

Por isso este módulo não implementa extração de valores: fica PENDENTE
até haver (a) registros reais de funcionário na aba, e (b) confirmação de
qual coluna usar. Ver docs/P01_ART_LATEX_QUESTOR.md.
"""


class ValeTransporteIndisponivelError(NotImplementedError):
    pass


def extrair_vale_transporte(*args, **kwargs):
    raise ValeTransporteIndisponivelError(
        "Extração de Vale-transporte PENDENTE: sem registros reais de "
        "funcionário nos arquivos disponíveis, e sem confirmação de qual "
        "coluna alimenta o valor do evento 815. Ver "
        "docs/P01_ART_LATEX_QUESTOR.md."
    )
