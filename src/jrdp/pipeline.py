"""Construção de lançamentos canônicos a partir de registros brutos de
origem (Matriz/Filial), aplicando matching, regra de evento e validação.

Esta é a camada "normalização → matching → mapeamento de evento →
validação" do pipeline (ver docs/P01_ART_LATEX_QUESTOR.md, 2026-09-17).
Não inclui a extração física das planilhas `.xlsm` reais (isso depende de
acesso ao arquivo real a cada execução) nem a exportação final para o
Questor (ver `exportadores.py`).
"""

from decimal import Decimal

from .cadastro_ativos import RegistroCadastro
from .canonico import LancamentoCanonico, RegistroOrigemBruto
from .config import ClienteConfigError, get_evento, is_evento_bloqueado
from .decimais import DecimalContractError, serializar_decimal_livre, valor_origem_para_decimal
from .depara import RegistroDePara
from .origem_matching import cruzar_com_depara
from .serializers import InvalidTimeFormatError, serialize_hmm


def construir_lancamentos_evento(
    registros: list[RegistroOrigemBruto],
    cadastro: list[RegistroCadastro],
    config_cliente: dict,
    cliente: str,
    competencia: str,
    codigo_evento: int,
    depara: list[RegistroDePara] | None = None,
) -> list[LancamentoCanonico]:
    """Constrói um lançamento canônico por registro de origem, para um
    único evento (podendo combinar registros de Matriz e Filial na mesma
    chamada — a granularidade final é por evento, não por unidade).

    Cada registro passa por: matching (nome -> código, nesta ordem: match
    exato normalizado, depois de-para homologado — ver
    `origem_matching.cruzar_com_depara`), busca da regra do evento na
    unidade correspondente, serialização conforme o tipo (hora -> H,MM;
    valor -> Decimal sem arredondamento), e é marcado como
    válido/inválido/bloqueado. Nunca decide matching ambíguo sozinho, e
    nunca usa fuzzy matching automático (`sugestao_fuzzy` é só
    diagnóstico humano).
    """
    resultado_matching = cruzar_com_depara(
        [(r.nome, r.unidade) for r in registros], cadastro, depara
    )

    lancamentos = []
    for registro in registros:
        codigo_colaborador = resultado_matching.resolvidos.get(registro.nome)
        if codigo_colaborador is not None:
            status_matching = "resolvido"
        elif registro.nome in resultado_matching.ambiguos:
            status_matching = "ambiguo"
        else:
            status_matching = "nao_encontrado"

        tipo = ""
        valor_normalizado = None
        status_validacao = "bloqueado"
        motivo_bloqueio = None
        regra_aplicada = ""

        if status_matching != "resolvido":
            motivo_bloqueio = f"Matching {status_matching} para o nome de origem."
        else:
            try:
                evento = get_evento(config_cliente, registro.unidade, codigo_evento)
            except ClienteConfigError as exc:
                status_validacao = "invalido"
                motivo_bloqueio = str(exc)
                evento = None

            if evento is not None:
                tipo = evento["tipo"]
                regra_aplicada = evento["descricao"]
                if is_evento_bloqueado(evento):
                    status_validacao = "bloqueado"
                    motivo_bloqueio = (
                        f"Evento {codigo_evento} ({evento['descricao']}) está "
                        "PENDENTE de configuração."
                    )
                else:
                    try:
                        if tipo == "hora":
                            valor_normalizado = serialize_hmm(registro.valor_bruto)
                        elif tipo == "valor":
                            valor_decimal = valor_origem_para_decimal(registro.valor_bruto)
                            valor_normalizado = serializar_decimal_livre(valor_decimal)
                        else:
                            raise DecimalContractError(f"Tipo de evento desconhecido: {tipo!r}")
                        status_validacao = "valido"
                    except (InvalidTimeFormatError, DecimalContractError) as exc:
                        status_validacao = "invalido"
                        motivo_bloqueio = str(exc)

        lancamentos.append(
            LancamentoCanonico(
                cliente=cliente,
                competencia=competencia,
                unidade_origem=registro.unidade,
                codigo_colaborador=codigo_colaborador,
                nome_origem=registro.nome,
                codigo_evento=codigo_evento,
                tipo=tipo,
                valor_original=registro.valor_bruto,
                valor_normalizado=valor_normalizado,
                arquivo_origem=registro.arquivo_origem,
                aba_origem=registro.aba_origem,
                linha_origem=registro.linha_origem,
                regra_aplicada=regra_aplicada,
                status_matching=status_matching,
                status_validacao=status_validacao,
                motivo_bloqueio=motivo_bloqueio,
            )
        )

    return lancamentos


def construir_lancamentos_cesta_basica(
    nomes_matriz: list[str],
    nomes_filial: list[str],
    cadastro: list[RegistroCadastro],
    config_cliente: dict,
    cliente: str,
    competencia: str,
    codigo_evento: int,
    arquivo_matriz: str,
    arquivo_filial: str,
    valor_por_colaborador: Decimal = Decimal("1"),
    depara: list[RegistroDePara] | None = None,
) -> list[LancamentoCanonico]:
    """Cesta Básica: a aba de origem não tem coluna de valor — o valor é
    R$1,00 por colaborador listado (regra confirmada, ver
    docs/DECISIONS.md 2026-09-17). Constrói um RegistroOrigemBruto
    sintético por nome listado, com valor_bruto fixo, e delega para
    `construir_lancamentos_evento`.
    """
    valor_bruto = serializar_decimal_livre(valor_por_colaborador)
    registros = [
        RegistroOrigemBruto(
            unidade="matriz",
            nome=nome,
            valor_bruto=valor_bruto,
            arquivo_origem=arquivo_matriz,
            aba_origem="Cesta basica",
        )
        for nome in nomes_matriz
    ] + [
        RegistroOrigemBruto(
            unidade="filial",
            nome=nome,
            valor_bruto=valor_bruto,
            arquivo_origem=arquivo_filial,
            aba_origem="Cesta basica",
        )
        for nome in nomes_filial
    ]
    return construir_lancamentos_evento(
        registros, cadastro, config_cliente, cliente, competencia, codigo_evento, depara
    )
