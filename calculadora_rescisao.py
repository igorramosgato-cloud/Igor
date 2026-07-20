"""
Calculadora de Verbas Rescisórias
=================================

Ferramenta de apoio ao cálculo de verbas rescisórias trabalhistas (CLT).
Cobre os tipos de rescisão mais comuns (sem justa causa, pedido de demissão,
justa causa, acordo Art. 484-A e término de contrato de experiência) e as
verbas típicas: saldo de salário, aviso prévio, 13º e férias proporcionais,
férias vencidas e multa do FGTS — com os descontos de INSS e IRRF.

IMPORTANTE: as tabelas de INSS e IRRF abaixo precisam ser conferidas/atualizadas
todo ano (normalmente em janeiro). Estão marcadas com "# ATUALIZAR" onde isso
importa. Este script é uma ferramenta de apoio ao cálculo, não substitui a
conferência humana antes de qualquer pagamento real, nem a legislação/convenção
coletiva aplicável a cada caso.

GAPS CONHECIDOS (não implementados neste esqueleto — evoluir conforme necessário):
  - FGTS: não modela saque-rescisão nem a guia GRRF detalhada, apenas a base
    usada para a multa de 40%/20%.
  - Seguro-desemprego (elegibilidade e valor das parcelas).
  - DSR e reflexos de horas extras habituais nas verbas rescisórias.
  - Rescisão indireta, aposentadoria e estabilidades provisórias (gestante,
    CIPA, acidentado) — cada uma tem regras próprias não cobertas aqui.
  - Art. 480 CLT (empregado que rescinde antecipadamente contrato de
    experiência) — só o Art. 479 (rescisão antecipada pelo empregador) está
    implementado.
  - Desconto simplificado de IRRF (25% do teto da tabela) como alternativa às
    deduções legais — o cálculo abaixo usa apenas dedução por dependente.
  - Geração de PDF, integração com planilha de clientes e eventos do eSocial
    (S-2299/S-2399).

Uso:
    python calculadora_rescisao.py
(ou importe a função calcular_rescisao() em outro script/planilha)
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional
from dateutil.relativedelta import relativedelta


# ---------------------------------------------------------------------------
# TABELAS (ATUALIZAR conforme legislação vigente no ano do cálculo)
# Conferido em 20/07/2026 com base no salário mínimo/teto do INSS de 2026 e na
# Lei 15.270/2025 (IRRF). Reconfirme na fonte oficial (gov.br/inss,
# gov.br/receitafederal) antes de usar em produção.
# ---------------------------------------------------------------------------

# ATUALIZAR — Tabela progressiva de INSS 2026 (faixas e alíquotas)
TABELA_INSS = [
    (1621.00, 0.075),
    (2902.84, 0.09),
    (4354.27, 0.12),
    (8475.55, 0.14),
]
TETO_INSS = 8475.55

# ATUALIZAR — Tabela progressiva de IRRF mensal (faixa, alíquota, parcela a
# deduzir). Inalterada desde a Lei 14.663/2023; a Lei 15.270/2025 não mexeu
# nestas faixas, apenas adicionou o redutor abaixo.
TABELA_IRRF = [
    (2259.20, 0.0, 0.0),
    (2826.65, 0.075, 169.44),
    (3751.05, 0.15, 381.44),
    (4664.68, 0.225, 662.77),
    (float("inf"), 0.275, 896.00),
]
DEDUCAO_POR_DEPENDENTE_IRRF = 189.59  # ATUALIZAR

# ATUALIZAR — Redutor do Art. 3º-A da Lei 9.250/95 (incluído pela Lei
# 15.270/2025), em vigor desde 01/01/2026: zera o IRRF devido para quem ganha
# até R$ 5.000,00/mês e reduz linearmente o imposto até R$ 7.350,00/mês.
REDUTOR_IRRF_LIMITE_SUPERIOR = 7350.00
REDUTOR_IRRF_CONSTANTE = 978.62
REDUTOR_IRRF_COEFICIENTE = 0.133145

ALIQUOTA_FGTS_MENSAL = 0.08


def calcular_inss(base: float) -> float:
    """Cálculo progressivo de INSS por faixa (não é alíquota única sobre o total)."""
    base = min(base, TETO_INSS)
    faixas = [0] + [f[0] for f in TABELA_INSS]
    total = 0.0
    for i, (limite, aliquota) in enumerate(TABELA_INSS):
        piso = faixas[i]
        teto_faixa = min(limite, base)
        if base > piso:
            total += (teto_faixa - piso) * aliquota
        if base <= limite:
            break
    return round(total, 2)


def calcular_redutor_irrf_lei_15270(rendimento_tributavel: float) -> float:
    """Redutor mensal do Art. 3º-A da Lei 9.250/95 (Lei 15.270/2025).

    `rendimento_tributavel` é o rendimento sujeito à incidência mensal antes
    das deduções legais/simplificadas do IRRF (ou seja, já líquido de INSS).
    """
    if rendimento_tributavel > REDUTOR_IRRF_LIMITE_SUPERIOR:
        return 0.0
    redutor = REDUTOR_IRRF_CONSTANTE - (REDUTOR_IRRF_COEFICIENTE * rendimento_tributavel)
    return round(max(redutor, 0.0), 2)


def calcular_irrf(base: float, dependentes: int = 0) -> float:
    base_ajustada = base - (dependentes * DEDUCAO_POR_DEPENDENTE_IRRF)
    for limite, aliquota, deducao in TABELA_IRRF:
        if base_ajustada <= limite:
            valor_tabela = max(base_ajustada * aliquota - deducao, 0.0)
            redutor = calcular_redutor_irrf_lei_15270(base)
            return round(max(valor_tabela - redutor, 0.0), 2)
    return 0.0


# ---------------------------------------------------------------------------
# DADOS DE ENTRADA
# ---------------------------------------------------------------------------

@dataclass
class DadosRescisao:
    salario_base: float
    data_admissao: date
    data_desligamento: date
    tipo_rescisao: str  # "sem_justa_causa" | "pedido_demissao" | "justa_causa" | "acordo_484a" | "termino_experiencia"
    aviso_previo: str = "indenizado"  # "indenizado" | "trabalhado" | "nao_aplicavel"
    ferias_vencidas: bool = False
    dependentes_irrf: int = 0
    saldo_fgts_depositado: float = 0.0  # total já depositado na conta do FGTS até o mês anterior
    # Só relevante para tipo_rescisao == "termino_experiencia": data prevista
    # de término do contrato. Se o desligamento ocorrer antes dela por
    # iniciativa do empregador, gera indenização do Art. 479 CLT.
    data_fim_contrato_experiencia: Optional[date] = None


# ---------------------------------------------------------------------------
# CÁLCULO
# ---------------------------------------------------------------------------

def calcular_rescisao(d: DadosRescisao) -> dict:
    resultado = {"tipo_rescisao": d.tipo_rescisao, "rubricas": [], "descontos": []}

    def add_provento(nome, valor):
        resultado["rubricas"].append({"rubrica": nome, "valor": round(valor, 2)})

    def add_desconto(nome, valor):
        resultado["descontos"].append({"rubrica": nome, "valor": round(valor, 2)})

    valor_dia = d.salario_base / 30

    # 1. Saldo de salário (dias trabalhados no mês do desligamento)
    dias_trabalhados_mes = d.data_desligamento.day
    add_provento("Saldo de salário", valor_dia * dias_trabalhados_mes)

    # 2. Aviso prévio (só se aplicável ao tipo de rescisão)
    tem_aviso = d.tipo_rescisao in ("sem_justa_causa", "acordo_484a")
    dias_aviso = 0
    if tem_aviso:
        anos_completos = relativedelta(d.data_desligamento, d.data_admissao).years
        dias_aviso = min(30 + (3 * anos_completos), 90)
        if d.aviso_previo == "indenizado":
            valor_aviso = valor_dia * dias_aviso
            if d.tipo_rescisao == "acordo_484a":
                valor_aviso /= 2
            add_provento(f"Aviso prévio indenizado ({dias_aviso} dias)", valor_aviso)
        # se "trabalhado", não gera verba adicional — já foi pago no salário normal

    # Súmula 371 do TST: quando o aviso é indenizado, o período projetado
    # conta para todos os efeitos (13º, férias, FGTS) como se o contrato
    # tivesse continuado até lá.
    data_projecao = d.data_desligamento
    if tem_aviso and d.aviso_previo == "indenizado":
        data_projecao = d.data_desligamento + timedelta(days=dias_aviso)

    # Em caso de justa causa o empregado perde o direito ao 13º proporcional
    # (Lei 4.090/62, Art. 3º, parágrafo único) e às férias proporcionais
    # (Art. 146, parágrafo único, CLT) — mantém apenas férias já vencidas.
    tem_direito_proporcionais = d.tipo_rescisao != "justa_causa"

    if tem_direito_proporcionais:
        # 3. 13º salário proporcional (meses com 15+ dias trabalhados contam o mês cheio)
        meses_no_ano = data_projecao.month
        if data_projecao.day >= 15:
            meses_13 = meses_no_ano
        else:
            meses_13 = meses_no_ano - 1
        add_provento(f"13º salário proporcional ({meses_13}/12)", (d.salario_base / 12) * meses_13)

        # 4. Férias proporcionais + 1/3
        meses_ferias = relativedelta(data_projecao, d.data_admissao).months
        ferias_prop = (d.salario_base / 12) * meses_ferias
        add_provento(f"Férias proporcionais ({meses_ferias}/12) + 1/3", ferias_prop * (4 / 3))

    # 5. Férias vencidas + 1/3, se houver (devidas mesmo em justa causa)
    if d.ferias_vencidas:
        add_provento("Férias vencidas + 1/3", d.salario_base * (4 / 3))

    # 6. Indenização Art. 479 CLT — rescisão antecipada de contrato de
    # experiência pelo empregador sem justa causa: metade da remuneração a
    # que o empregado teria direito até o termo do contrato.
    if (
        d.tipo_rescisao == "termino_experiencia"
        and d.data_fim_contrato_experiencia is not None
        and d.data_desligamento < d.data_fim_contrato_experiencia
    ):
        dias_restantes = (d.data_fim_contrato_experiencia - d.data_desligamento).days
        add_provento(
            f"Indenização Art. 479 CLT (metade de {dias_restantes} dias restantes)",
            (valor_dia * dias_restantes) / 2,
        )

    # --- FGTS: depósito do mês da rescisão (saldo de salário + 13º) e do
    #     período de projeção do aviso indenizado, somados ao saldo já
    #     depositado, formam a base da multa de 40%/20%.
    base_deposito_mes = sum(
        r["valor"] for r in resultado["rubricas"]
        if r["rubrica"].startswith("Saldo de salário") or r["rubrica"].startswith("13º")
    )
    fgts_mes_rescisao = round(base_deposito_mes * ALIQUOTA_FGTS_MENSAL, 2)
    fgts_periodo_aviso_projetado = 0.0
    if tem_aviso and d.aviso_previo == "indenizado":
        fgts_periodo_aviso_projetado = round(valor_dia * dias_aviso * ALIQUOTA_FGTS_MENSAL, 2)

    base_fgts_multa = d.saldo_fgts_depositado + fgts_mes_rescisao + fgts_periodo_aviso_projetado
    resultado["fgts"] = {
        "saldo_anterior_informado": round(d.saldo_fgts_depositado, 2),
        "deposito_mes_rescisao": fgts_mes_rescisao,
        "deposito_periodo_aviso_projetado": fgts_periodo_aviso_projetado,
        "base_para_multa": round(base_fgts_multa, 2),
    }

    if d.tipo_rescisao == "sem_justa_causa":
        add_provento("Multa 40% FGTS", base_fgts_multa * 0.40)
    elif d.tipo_rescisao == "acordo_484a":
        add_provento("Multa 20% FGTS (acordo Art. 484-A)", base_fgts_multa * 0.20)
    # pedido_demissao, justa_causa, término normal de experiência: sem multa

    # --- Descontos (INSS e IRRF incidem sobre saldo de salário + 13º; verbas
    #     indenizatórias como aviso, férias e multa FGTS são isentas) ---
    base_tributavel = sum(
        r["valor"] for r in resultado["rubricas"]
        if r["rubrica"].startswith("Saldo de salário") or r["rubrica"].startswith("13º")
    )
    inss = calcular_inss(base_tributavel)
    irrf = calcular_irrf(base_tributavel - inss, d.dependentes_irrf)
    add_desconto("INSS", inss)
    add_desconto("IRRF", irrf)

    total_proventos = sum(r["valor"] for r in resultado["rubricas"])
    total_descontos = sum(r["valor"] for r in resultado["descontos"])
    resultado["total_proventos"] = round(total_proventos, 2)
    resultado["total_descontos"] = round(total_descontos, 2)
    resultado["valor_liquido"] = round(total_proventos - total_descontos, 2)

    # Prazo legal de pagamento (Art. 477 CLT — 10 dias corridos do término)
    resultado["prazo_pagamento"] = d.data_desligamento + relativedelta(days=10)

    return resultado


def imprimir_resultado(r: dict):
    print(f"\n{'='*50}\nTIPO DE RESCISÃO: {r['tipo_rescisao']}\n{'='*50}")
    print("\nPROVENTOS:")
    for item in r["rubricas"]:
        print(f"  {item['rubrica']:<45} R$ {item['valor']:>10.2f}")
    print("\nDESCONTOS:")
    for item in r["descontos"]:
        print(f"  {item['rubrica']:<45} R$ {item['valor']:>10.2f}")
    print(f"\n{'-'*50}")
    print(f"  {'Total proventos':<45} R$ {r['total_proventos']:>10.2f}")
    print(f"  {'Total descontos':<45} R$ {r['total_descontos']:>10.2f}")
    print(f"  {'VALOR LÍQUIDO':<45} R$ {r['valor_liquido']:>10.2f}")
    fgts = r["fgts"]
    print(f"\nFGTS (memorando, não incluído no líquido pago em dinheiro, exceto a multa):")
    print(f"  Saldo anterior informado                     R$ {fgts['saldo_anterior_informado']:>10.2f}")
    print(f"  Depósito do mês da rescisão                  R$ {fgts['deposito_mes_rescisao']:>10.2f}")
    print(f"  Depósito período de projeção do aviso         R$ {fgts['deposito_periodo_aviso_projetado']:>10.2f}")
    print(f"  Base usada para a multa                      R$ {fgts['base_para_multa']:>10.2f}")
    print(f"\nPrazo legal de pagamento (Art. 477 CLT): {r['prazo_pagamento'].strftime('%d/%m/%Y')}")


# ---------------------------------------------------------------------------
# EXEMPLO DE USO
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    exemplo = DadosRescisao(
        salario_base=3500.00,
        data_admissao=date(2022, 3, 10),
        data_desligamento=date(2026, 7, 15),
        tipo_rescisao="sem_justa_causa",
        aviso_previo="indenizado",
        ferias_vencidas=False,
        dependentes_irrf=0,
        saldo_fgts_depositado=6200.00,
    )
    resultado = calcular_rescisao(exemplo)
    imprimir_resultado(resultado)
