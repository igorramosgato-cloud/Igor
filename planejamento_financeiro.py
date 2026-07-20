"""
Planejamento Financeiro Pessoal — Patrimônio + Meta (casamento) + Investimento
================================================================================

Três partes:
  1. Cliente Pluggy (Open Finance) — puxa contas e investimentos reais.
     PRECISA de credenciais reais (Client ID/Secret do dashboard.pluggy.ai)
     e de você já ter conectado suas contas em meu.pluggy.ai. Não testei
     essa parte de ponta a ponta — não tenho como, sem suas credenciais.
  2. Tracker de patrimônio — guarda um histórico local (JSON) da evolução
     do patrimônio total mês a mês.
  3. Simulador de meta — divide o que sobra por mês entre uma meta de curto
     prazo (ex: casamento, precisa estar líquido, sem risco) e investimento
     de longo prazo, com projeção de crescimento composto.

IMPORTANTE: a parte 3 é matemática pura (juros compostos, divisão de meta).
NÃO é recomendação de onde investir — isso depende do seu perfil e, se o
valor for relevante, vale conversar com um profissional licenciado.

Dependências:
    pip install -r requirements.txt --break-system-packages

Uso (CLI):
    python3 planejamento_financeiro.py meta \
        --data-meta 2027-05-01 --valor-meta 30000 --ja-guardado 5000 \
        --sobra-mensal 3000 --taxa-aa 0.11

    python3 planejamento_financeiro.py snapshot --item-id SEU_ITEM_ID
        (precisa de PLUGGY_CLIENT_ID e PLUGGY_CLIENT_SECRET no ambiente)

    python3 planejamento_financeiro.py historico
"""

import argparse
import os
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path


# =============================================================================
# PARTE 1 — CLIENTE PLUGGY (Open Finance)
# =============================================================================

PLUGGY_BASE_URL = "https://api.pluggy.ai"
PLUGGY_CLIENT_ID = os.environ.get("PLUGGY_CLIENT_ID", "")
PLUGGY_CLIENT_SECRET = os.environ.get("PLUGGY_CLIENT_SECRET", "")


class PluggyClient:
    """
    Cliente básico pra API do Pluggy. Precisa de PLUGGY_CLIENT_ID e
    PLUGGY_CLIENT_SECRET (do dashboard.pluggy.ai) como variáveis de
    ambiente — nunca hardcoded no código.
    """

    def __init__(self):
        import requests
        self._requests = requests
        self._api_key = None

    def autenticar(self):
        """Troca client_id/secret por uma API key de uso (válida por tempo limitado)."""
        resp = self._requests.post(
            f"{PLUGGY_BASE_URL}/auth",
            json={"clientId": PLUGGY_CLIENT_ID, "clientSecret": PLUGGY_CLIENT_SECRET},
        )
        resp.raise_for_status()
        self._api_key = resp.json()["apiKey"]

    def _headers(self):
        return {"X-API-KEY": self._api_key}

    def listar_contas(self, item_id: str) -> list:
        """item_id = identificador da conexão bancária feita em meu.pluggy.ai."""
        resp = self._requests.get(
            f"{PLUGGY_BASE_URL}/accounts",
            params={"itemId": item_id},
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()["results"]

    def listar_investimentos(self, item_id: str) -> list:
        resp = self._requests.get(
            f"{PLUGGY_BASE_URL}/investments",
            params={"itemId": item_id},
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()["results"]


def puxar_patrimonio_real(item_ids: list) -> dict:
    """
    Soma saldo de contas + valor de investimentos de todas as conexões
    (item_ids) configuradas no Meu Pluggy.

    TODO: preencher item_ids com os IDs reais das suas conexões bancárias
    (aparecem no dashboard depois de conectar em meu.pluggy.ai).
    """
    cliente = PluggyClient()
    cliente.autenticar()

    total_contas = 0.0
    total_investimentos = 0.0
    detalhes = []

    for item_id in item_ids:
        for conta in cliente.listar_contas(item_id):
            total_contas += conta.get("balance", 0.0)
            detalhes.append({"tipo": "conta", "nome": conta.get("name"), "valor": conta.get("balance")})
        for inv in cliente.listar_investimentos(item_id):
            valor = inv.get("balance", 0.0)
            total_investimentos += valor
            detalhes.append({"tipo": "investimento", "nome": inv.get("name"), "valor": valor})

    return {
        "data": date.today().isoformat(),
        "total_contas": round(total_contas, 2),
        "total_investimentos": round(total_investimentos, 2),
        "patrimonio_total": round(total_contas + total_investimentos, 2),
        "detalhes": detalhes,
    }


# =============================================================================
# PARTE 2 — TRACKER DE PATRIMÔNIO (histórico local)
# =============================================================================

ARQUIVO_HISTORICO = Path("historico_patrimonio.json")


def registrar_snapshot(snapshot: dict):
    """Adiciona um snapshot de patrimônio ao histórico local (JSON)."""
    historico = []
    if ARQUIVO_HISTORICO.exists():
        historico = json.loads(ARQUIVO_HISTORICO.read_text())
    historico.append(snapshot)
    ARQUIVO_HISTORICO.write_text(json.dumps(historico, indent=2, ensure_ascii=False))


def evolucao_patrimonio() -> list:
    """Retorna o histórico completo, do mais antigo pro mais recente."""
    if not ARQUIVO_HISTORICO.exists():
        return []
    return json.loads(ARQUIVO_HISTORICO.read_text())


# =============================================================================
# PARTE 3 — SIMULADOR DE META (casamento + investimento)
# =============================================================================

@dataclass
class ParametrosMeta:
    data_hoje: date
    data_meta: date              # ex: data do casamento
    valor_meta: float            # quanto falta juntar pro casamento
    ja_guardado_meta: float      # quanto já está guardado pra essa meta
    sobra_mensal_total: float    # quanto sobra por mês, no total, pra dividir
    taxa_investimento_aa: float  # taxa de retorno anual ESPERADA do investimento
                                  # (você define — não é sugestão minha; ex: 0.11 = 11% a.a.)


def calcular_meses_ate(data_hoje: date, data_meta: date) -> int:
    return (data_meta.year - data_hoje.year) * 12 + (data_meta.month - data_hoje.month)


def simular_divisao(p: ParametrosMeta) -> dict:
    meses_restantes = calcular_meses_ate(p.data_hoje, p.data_meta)
    if meses_restantes <= 0:
        raise ValueError("Data da meta precisa ser no futuro.")

    falta_para_meta = max(p.valor_meta - p.ja_guardado_meta, 0.0)
    necessario_por_mes_meta = falta_para_meta / meses_restantes

    if necessario_por_mes_meta > p.sobra_mensal_total:
        return {
            "viavel": False,
            "meses_restantes": meses_restantes,
            "necessario_por_mes_para_meta": round(necessario_por_mes_meta, 2),
            "sobra_mensal_total": p.sobra_mensal_total,
            "deficit_mensal": round(necessario_por_mes_meta - p.sobra_mensal_total, 2),
            "mensagem": (
                "A sobra mensal não cobre o necessário pra bater a meta no prazo. "
                "Aumente a sobra, estenda o prazo, ou reduza o valor da meta."
            ),
        }

    sobra_para_investir = p.sobra_mensal_total - necessario_por_mes_meta

    # Projeção de investimento com aporte mensal constante e juros compostos
    taxa_mensal = (1 + p.taxa_investimento_aa) ** (1 / 12) - 1
    saldo_investido = 0.0
    projecao = []
    for mes in range(1, meses_restantes + 1):
        saldo_investido = saldo_investido * (1 + taxa_mensal) + sobra_para_investir
        projecao.append({"mes": mes, "saldo_investido_estimado": round(saldo_investido, 2)})

    return {
        "viavel": True,
        "meses_restantes": meses_restantes,
        "necessario_por_mes_para_meta": round(necessario_por_mes_meta, 2),
        "sobra_para_investir_por_mes": round(sobra_para_investir, 2),
        "saldo_investido_projetado_no_prazo": round(saldo_investido, 2),
        "projecao_mensal": projecao,
    }


def imprimir_simulacao(r: dict):
    print(f"\n{'='*55}\nSIMULAÇÃO DE META\n{'='*55}")
    if not r["viavel"]:
        print(f"⚠️  {r['mensagem']}")
        print(f"  Necessário/mês pra meta:  R$ {r['necessario_por_mes_para_meta']:>10.2f}")
        print(f"  Sobra mensal disponível:  R$ {r['sobra_mensal_total']:>10.2f}")
        print(f"  Déficit mensal:           R$ {r['deficit_mensal']:>10.2f}")
        return
    print(f"  Meses até a meta:                 {r['meses_restantes']}")
    print(f"  Necessário guardar/mês p/ meta:   R$ {r['necessario_por_mes_para_meta']:>10.2f}")
    print(f"  Sobra pra investir/mês:           R$ {r['sobra_para_investir_por_mes']:>10.2f}")
    print(f"  Saldo investido projetado no fim: R$ {r['saldo_investido_projetado_no_prazo']:>10.2f}")
    print(f"\n  (projeção com juros compostos sobre a taxa anual que você informou —")
    print(f"   não é garantia de retorno, é só matemática sobre a taxa hipotética)")


# =============================================================================
# CLI
# =============================================================================

def cmd_meta(args):
    p = ParametrosMeta(
        data_hoje=date.today(),
        data_meta=date.fromisoformat(args.data_meta),
        valor_meta=args.valor_meta,
        ja_guardado_meta=args.ja_guardado,
        sobra_mensal_total=args.sobra_mensal,
        taxa_investimento_aa=args.taxa_aa,
    )
    resultado = simular_divisao(p)
    imprimir_simulacao(resultado)
    if args.json:
        print(json.dumps(resultado, indent=2, ensure_ascii=False))


def cmd_snapshot(args):
    if not (PLUGGY_CLIENT_ID and PLUGGY_CLIENT_SECRET):
        print(
            "Erro: defina as variáveis de ambiente PLUGGY_CLIENT_ID e "
            "PLUGGY_CLIENT_SECRET (do dashboard.pluggy.ai) antes de rodar este comando.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    snapshot = puxar_patrimonio_real(item_ids=args.item_id)
    registrar_snapshot(snapshot)
    print(f"Snapshot registrado em {ARQUIVO_HISTORICO}:")
    print(json.dumps(snapshot, indent=2, ensure_ascii=False))


def cmd_historico(args):
    historico = evolucao_patrimonio()
    if not historico:
        print("Nenhum snapshot registrado ainda. Use o comando 'snapshot' primeiro.")
        return
    print(f"{'Data':<12}{'Contas':>16}{'Investimentos':>18}{'Patrimônio total':>20}")
    for h in historico:
        print(
            f"{h['data']:<12}{h['total_contas']:>16.2f}"
            f"{h['total_investimentos']:>18.2f}{h['patrimonio_total']:>20.2f}"
        )
    variacao = historico[-1]["patrimonio_total"] - historico[0]["patrimonio_total"]
    print(f"\nVariação desde o primeiro snapshot: R$ {variacao:,.2f}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Planejamento financeiro pessoal: patrimônio, meta e investimento."
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_meta = sub.add_parser("meta", help="Simula a divisão mensal entre a meta (ex: casamento) e investimento.")
    p_meta.add_argument("--data-meta", required=True, help="Data da meta, formato AAAA-MM-DD (ex: data do casamento).")
    p_meta.add_argument("--valor-meta", required=True, type=float, help="Valor total da meta.")
    p_meta.add_argument("--ja-guardado", type=float, default=0.0, help="Quanto já está guardado pra essa meta.")
    p_meta.add_argument("--sobra-mensal", required=True, type=float, help="Quanto sobra por mês, no total, pra dividir.")
    p_meta.add_argument(
        "--taxa-aa", required=True, type=float,
        help="Taxa de retorno anual esperada do investimento, ex: 0.11 para 11%% a.a. (você define, não é sugestão).",
    )
    p_meta.add_argument("--json", action="store_true", help="Também imprime o resultado em JSON.")
    p_meta.set_defaults(func=cmd_meta)

    p_snapshot = sub.add_parser("snapshot", help="Puxa patrimônio real via Pluggy e registra no histórico local.")
    p_snapshot.add_argument(
        "--item-id", action="append", required=True, dest="item_id",
        help="ID de uma conexão bancária no Pluggy (repita a flag para mais de uma conexão).",
    )
    p_snapshot.set_defaults(func=cmd_snapshot)

    p_historico = sub.add_parser("historico", help="Mostra o histórico de patrimônio já registrado.")
    p_historico.set_defaults(func=cmd_historico)

    return parser


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
