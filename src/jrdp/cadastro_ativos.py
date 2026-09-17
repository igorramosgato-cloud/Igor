"""Leitor do relatório "Base de ativos" (cadastro código↔nome↔CPF).

Resolve o bloqueio de matching registrado em docs/DECISIONS.md
(2026-09-17): as planilhas de origem Matriz/Filial da ART LATEX têm a
coluna de código do funcionário vazia, só com nome livre. Este relatório,
extraído do sistema de origem do cliente, tem "Contrato" (código) + Nome +
CPF — e o usuário confirmou explicitamente que "Contrato" é o mesmo código
usado como "COD. FUNC. QUESTOR" nas planilhas de origem (ver
docs/DECISIONS.md, 2026-09-17). Isso permite montar um índice nome→código
e cpf→código para resolver o matching de forma confiável, em vez de usar
nome livre diretamente (o que violaria .claude/rules/matching.md).

Contrato físico confirmado por evidência real:
- encoding: Latin-1 (ISO-8859-1).
- delimitador: ';'.
- terminador de linha: CRLF.
- campos "Nome" e "Descrição" entre aspas duplas; "Contrato", "Admissão" e
  "CPF" não.
- é um relatório PAGINADO: a cada ~64 linhas se repete um bloco de quebra
  de página (linhas em branco, linha de cabeçalho da empresa/data/página,
  linha de título do relatório, linha separadora de sublinhados, e a
  própria linha de cabeçalho de colunas "Contrato;Nome;Admissão;
  Descrição;CPF"). Este parser descarta esse ruído e mantém só os
  registros de funcionário.
- rodapé final: '" Total Empresa: ...";"Total de Funcionários";<N>' — usado
  para validar que a contagem de registros extraídos bate com o total
  declarado pelo próprio relatório.
"""

import csv
import re
from dataclasses import dataclass

ENCODING = "latin-1"
DELIMITADOR = ";"
CABECALHO_COLUNAS = ["Contrato", "Nome", "Admissão", "Descrição", "CPF"]

_CPF_REGEX = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
_DATA_REGEX = re.compile(r"^\d{2}/\d{2}/\d{4}$")


class CadastroContractError(ValueError):
    """Levantado quando o arquivo não bate com o contrato físico confirmado."""


@dataclass(frozen=True)
class RegistroCadastro:
    contrato: str  # == "COD. FUNC. QUESTOR", confirmado pelo usuário em 2026-09-17
    nome: str
    admissao: str
    descricao: str
    cpf: str


def _decodificar(conteudo_bruto: bytes) -> str:
    try:
        return conteudo_bruto.decode(ENCODING)
    except UnicodeDecodeError as exc:
        raise CadastroContractError(
            f"Arquivo não decodifica como {ENCODING}: {exc}"
        ) from exc


def _parse_linha(linha: str) -> list[str]:
    return next(csv.reader([linha], delimiter=DELIMITADOR, quotechar='"'))


def parse_base_ativos(conteudo_bruto: bytes) -> list[RegistroCadastro]:
    """Faz o parsing do relatório de cadastro, descartando ruído de paginação.

    Levanta CadastroContractError se a contagem final não bater com o
    total declarado no rodapé do próprio relatório (nunca confia
    silenciosamente na extração).
    """
    texto = _decodificar(conteudo_bruto)
    linhas = texto.split("\r\n")

    total_declarado = None
    for linha in linhas:
        if linha.startswith('" Total Empresa'):
            campos = _parse_linha(linha)
            if len(campos) != 3:
                raise CadastroContractError(
                    f"Linha de rodapé não tem 3 campos: {linha!r}"
                )
            try:
                total_declarado = int(campos[2])
            except ValueError as exc:
                raise CadastroContractError(
                    f"Total declarado no rodapé não é numérico: {campos[2]!r}"
                ) from exc
            break

    if total_declarado is None:
        raise CadastroContractError(
            "Rodapé com 'Total Empresa' / 'Total de Funcionários' não encontrado."
        )

    cabecalho_validado = False
    registros = []
    for linha in linhas:
        if linha == "" or linha.startswith('"_') or linha.startswith('" Total Empresa'):
            continue
        if not (linha[0].isdigit() or linha.startswith('"Contrato')):
            # cabeçalho de página (empresa/data/página) ou título do relatório
            continue
        campos = _parse_linha(linha)
        if len(campos) != 5:
            continue
        contrato, nome, admissao, descricao, cpf = campos
        if contrato == "Contrato":
            if campos != CABECALHO_COLUNAS:
                raise CadastroContractError(
                    f"Cabeçalho de colunas não bate com o contrato confirmado. "
                    f"Esperado {CABECALHO_COLUNAS!r}, recebido {campos!r}."
                )
            cabecalho_validado = True
            continue  # cabeçalho de colunas repetido a cada quebra de página
        if not contrato.isdigit():
            raise CadastroContractError(
                f"Contrato não numérico: {contrato!r}"
            )
        if not _CPF_REGEX.match(cpf):
            raise CadastroContractError(
                f"CPF fora do formato 000.000.000-00: {cpf!r}"
            )
        if not _DATA_REGEX.match(admissao):
            raise CadastroContractError(
                f"Admissão fora do formato DD/MM/AAAA: {admissao!r}"
            )
        registros.append(
            RegistroCadastro(
                contrato=contrato,
                nome=nome,
                admissao=admissao,
                descricao=descricao,
                cpf=cpf,
            )
        )

    if not cabecalho_validado:
        raise CadastroContractError(
            "Nenhum cabeçalho de colunas 'Contrato;Nome;Admissão;Descrição;"
            "CPF' válido foi encontrado no arquivo."
        )

    if len(registros) != total_declarado:
        raise CadastroContractError(
            f"Contagem de registros extraídos ({len(registros)}) não bate "
            f"com o total declarado no rodapé ({total_declarado})."
        )

    contratos = [r.contrato for r in registros]
    if len(set(contratos)) != len(contratos):
        raise CadastroContractError("Contrato duplicado encontrado no cadastro.")

    return registros


def indexar_por_contrato(
    registros: list[RegistroCadastro],
) -> dict[str, RegistroCadastro]:
    return {r.contrato: r for r in registros}


def indexar_por_cpf(registros: list[RegistroCadastro]) -> dict[str, RegistroCadastro]:
    return {r.cpf: r for r in registros}
