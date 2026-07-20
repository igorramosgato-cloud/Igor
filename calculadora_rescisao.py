"""
Calculadora de Verbas Rescisórias
=================================

Ferramenta de apoio ao cálculo de verbas rescisórias trabalhistas (CLT).
Cobre os tipos de rescisão mais comuns (sem justa causa, pedido de demissão,
justa causa, acordo Art. 484-A, término de contrato de experiência, rescisão
indireta e aposentadoria) e as verbas típicas: saldo de salário, aviso
prévio, 13º e férias proporcionais, férias vencidas, reflexo de horas
extras habituais + DSR, multa e saque-rescisão do FGTS, estimativa de
seguro-desemprego, alertas de estabilidade provisória e os descontos de
INSS e IRRF.

IMPORTANTE: as tabelas de INSS, IRRF e Seguro-Desemprego abaixo precisam ser
conferidas/atualizadas todo ano (normalmente em janeiro). Estão marcadas com
"# ATUALIZAR" onde isso importa. Este script é uma ferramenta de apoio ao
cálculo, não substitui a conferência humana antes de qualquer pagamento real,
nem a legislação/convenção coletiva aplicável a cada caso.

GAPS CONHECIDOS (não implementados neste esqueleto — evoluir conforme necessário):
  - FGTS: o valor sacável é uma estimativa (percentual por tipo de rescisão +
    multa); não modela a guia GRRF detalhada nem substitui a homologação real
    no FGTS Digital/Conectividade Social.
  - Seguro-desemprego: a média salarial assume salário constante nos últimos
    3 meses — ajuste manualmente se o salário variou. Outros vínculos formais
    no período aquisitivo podem ser somados via
    `meses_trabalhados_outros_vinculos_periodo`, mas isso é informado pelo
    usuário, não verificado automaticamente.
  - Reflexo de horas extras: usa uma média informada pelo usuário e um
    divisor/dias úteis padrão, não o histórico real de ponto.
  - Estabilidades provisórias: a indenização estimada (dias restantes +
    13º/férias proporcionais desse período) é um piso conservador, não um
    cálculo definitivo — consulte jurídico antes de agir sobre o alerta;
    quando há mais de uma estabilidade concorrente, usa só a mais longa.
  - Geração de PDF (recibo_pdf.py) e integração com planilha de clientes
    (planilha_clientes.py) usam campos e nomes de colunas fixos — adapte ao
    layout real da sua planilha de clientes.
  - O evento S-2299 gerado é um esqueleto: `codRubr` só é preenchido se você
    passar `mapa_rubricas` (a tabela S-1010 da própria empresa) para
    `gerar_evento_esocial_s2299`; sem isso, fica `None`.
  - As tabelas de INSS/IRRF/Seguro-Desemprego foram conferidas cruzando
    várias fontes secundárias (contábeis/jurídicas) nesta sessão, pois o
    acesso direto ao gov.br (Receita Federal, INSS, MTE) ficou bloqueado
    (HTTP 403) neste ambiente — vale reconfirmar na fonte oficial antes de
    usar em produção.

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
# Conferido em 20/07/2026 com base no salário mínimo/teto do INSS de 2026, na
# Lei 15.270/2025 (IRRF) e na tabela do Seguro-Desemprego vigente desde
# 11/01/2026. Reconfirme na fonte oficial (gov.br/inss, gov.br/receitafederal,
# gov.br/trabalho-e-emprego) antes de usar em produção.
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

# ATUALIZAR — Desconto simplificado mensal de IRRF (25% do limite máximo da
# tabela progressiva mensal): substitui todas as deduções legais (dependentes,
# pensão, INSS complementar) quando for mais vantajoso para o contribuinte. A
# fonte pagadora é obrigada a aplicar o método que resultar em menor retenção.
DESCONTO_SIMPLIFICADO_IRRF_MENSAL = 607.20

# ATUALIZAR — Redutor do Art. 3º-A da Lei 9.250/95 (incluído pela Lei
# 15.270/2025), em vigor desde 01/01/2026: zera o IRRF devido para quem ganha
# até R$ 5.000,00/mês e reduz linearmente o imposto até R$ 7.350,00/mês.
REDUTOR_IRRF_LIMITE_SUPERIOR = 7350.00
REDUTOR_IRRF_CONSTANTE = 978.62
REDUTOR_IRRF_COEFICIENTE = 0.133145

ALIQUOTA_FGTS_MENSAL = 0.08

# ATUALIZAR — Tabela do Seguro-Desemprego (Resolução CODEFAT), vigente desde
# 11/01/2026: teto R$ 2.518,65, piso de um salário mínimo (R$ 1.621,00).
SALARIO_MINIMO_2026 = 1621.00
SEGURO_DESEMPREGO_FAIXA1 = 2222.17
SEGURO_DESEMPREGO_FAIXA2 = 3703.99
SEGURO_DESEMPREGO_CONSTANTE_FAIXA2 = 1777.74
SEGURO_DESEMPREGO_TETO = 2518.65

# ATUALIZAR — Códigos de motivo de desligamento da Tabela 19 do eSocial.
MOTIVO_DESLIGAMENTO_ESOCIAL = {
    "sem_justa_causa": "30",
    "pedido_demissao": "33",
    "justa_causa": "31",
    "acordo_484a": "20",
    "rescisao_indireta": "32",
    "aposentadoria": "42",
}

# Percentual do saldo do FGTS liberado para saque conforme o tipo de rescisão
# (Lei 8.036/90, Art. 20; Art. 484-A, §2º, CLT para o acordo).
PERCENTUAL_SAQUE_FGTS = {
    "sem_justa_causa": 1.0,
    "rescisao_indireta": 1.0,
    "aposentadoria": 1.0,
    "acordo_484a": 0.80,
    "pedido_demissao": 0.0,
    "justa_causa": 0.0,
    # Extinção de contrato por prazo determinado (inclusive antecipação) é uma
    # das hipóteses de movimentação do FGTS do Art. 20, Lei 8.036/90.
    "termino_experiencia": 1.0,
}


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


def _aplicar_tabela_irrf(base_ajustada: float) -> float:
    for limite, aliquota, deducao in TABELA_IRRF:
        if base_ajustada <= limite:
            return max(base_ajustada * aliquota - deducao, 0.0)
    return 0.0


def calcular_irrf(base: float, dependentes: int = 0) -> float:
    """IRRF mensal, usando o menor valor entre deduções legais (dependentes)
    e o desconto simplificado — a fonte pagadora deve aplicar o que for mais
    vantajoso ao contribuinte —, já líquido do redutor da Lei 15.270/2025.
    """
    irrf_deducoes_legais = _aplicar_tabela_irrf(base - (dependentes * DEDUCAO_POR_DEPENDENTE_IRRF))
    irrf_desconto_simplificado = _aplicar_tabela_irrf(base - DESCONTO_SIMPLIFICADO_IRRF_MENSAL)
    valor_tabela = min(irrf_deducoes_legais, irrf_desconto_simplificado)
    redutor = calcular_redutor_irrf_lei_15270(base)
    return round(max(valor_tabela - redutor, 0.0), 2)


def calcular_valor_parcela_seguro_desemprego(media_salarial: float) -> float:
    """Valor de cada parcela do seguro-desemprego a partir da média dos
    últimos 3 salários (Resolução CODEFAT vigente em 2026)."""
    if media_salarial <= SEGURO_DESEMPREGO_FAIXA1:
        valor = media_salarial * 0.8
    elif media_salarial <= SEGURO_DESEMPREGO_FAIXA2:
        valor = SEGURO_DESEMPREGO_CONSTANTE_FAIXA2 + (media_salarial - SEGURO_DESEMPREGO_FAIXA1) * 0.5
    else:
        valor = SEGURO_DESEMPREGO_TETO
    return round(max(valor, SALARIO_MINIMO_2026), 2)


def calcular_numero_parcelas_seguro_desemprego(meses_trabalhados: int, numero_solicitacoes_anteriores: int) -> int:
    """Número de parcelas conforme meses trabalhados no período aquisitivo e
    quantas vezes o benefício já foi solicitado antes (Lei 7.998/90)."""
    if numero_solicitacoes_anteriores <= 0:
        minimo_meses = 12
    elif numero_solicitacoes_anteriores == 1:
        minimo_meses = 9
    else:
        minimo_meses = 6

    if meses_trabalhados < minimo_meses:
        return 0
    if meses_trabalhados >= 24:
        return 5
    if meses_trabalhados >= 12:
        return 4
    return 3


def verificar_estabilidades(d) -> list:
    """Alerta se a dispensa (com ou sem justa causa) ocorre dentro de um
    período de estabilidade provisória. A dispensa nesse caso é, em regra,
    nula — reintegração ou indenização do período são cabíveis; não se aplica
    a acordo Art. 484-A, pedido de demissão ou término normal de experiência.
    """
    if d.tipo_rescisao not in ("sem_justa_causa", "justa_causa", "rescisao_indireta"):
        return []

    alertas = []
    estabilidades = [
        ("gestante (Art. 10, II, 'b', ADCT)", d.estabilidade_gestante_dt_fim),
        ("dirigente sindical/CIPA (Art. 10, II, 'a', ADCT)", d.estabilidade_cipa_dt_fim),
        ("acidentária (Art. 118, Lei 8.213/91)", d.estabilidade_acidentario_dt_fim),
    ]
    for nome, dt_fim in estabilidades:
        if dt_fim is not None and d.data_desligamento < dt_fim:
            alertas.append(
                f"Dispensa dentro do período de estabilidade {nome}, vigente até "
                f"{dt_fim.strftime('%d/%m/%Y')}. Dispensa sem motivo compatível com a "
                f"estabilidade é presumidamente nula — avalie reintegração antes de "
                f"homologar; a indenização abaixo é apenas uma estimativa mínima."
            )
    return alertas


# ---------------------------------------------------------------------------
# DADOS DE ENTRADA
# ---------------------------------------------------------------------------

@dataclass
class DadosRescisao:
    salario_base: float
    data_admissao: date
    data_desligamento: date
    tipo_rescisao: str  # "sem_justa_causa" | "pedido_demissao" | "justa_causa" | "acordo_484a" | "termino_experiencia" | "rescisao_indireta" | "aposentadoria"
    aviso_previo: str = "indenizado"  # "indenizado" | "trabalhado" | "nao_aplicavel"
    ferias_vencidas: bool = False
    dependentes_irrf: int = 0
    saldo_fgts_depositado: float = 0.0  # total já depositado na conta do FGTS até o mês anterior

    # Só relevante para tipo_rescisao == "termino_experiencia": data prevista
    # de término do contrato. Se o desligamento ocorrer antes dela, gera
    # indenização do Art. 479 CLT (antecipação pelo empregador, padrão) ou do
    # Art. 480 CLT (antecipação pelo empregado, se quem_antecipou_experiencia
    # == "empregado").
    data_fim_contrato_experiencia: Optional[date] = None
    quem_antecipou_experiencia: Optional[str] = None  # "empregador" | "empregado"

    # Horas extras habituais (Súmula 27 TST / OJ 394 SDI-1 TST): integram o
    # cálculo do aviso prévio, 13º e férias proporcionais/vencidas via DSR.
    media_horas_extras_mensal: float = 0.0
    valor_hora_extra: Optional[float] = None  # se None, calcula com divisor e adicional abaixo
    divisor_hora_normal: float = 220.0  # ajustável por convenção coletiva
    adicional_hora_extra: float = 0.5  # 50% (Art. 7º, XVI, CF); pode variar por CCT
    dias_uteis_mes_referencia: int = 25
    dias_repouso_mes_referencia: int = 5  # domingos + feriados no mês de referência

    # Seguro-desemprego: só relevante para tipo_rescisao == "sem_justa_causa"
    # e "rescisao_indireta". `meses_trabalhados_outros_vinculos_periodo` soma
    # meses de outros vínculos formais dentro da janela de referência (18, 12
    # ou 6 meses conforme o nº de solicitações anteriores) que não este
    # contrato — informe se o período aquisitivo não se resume a este vínculo.
    numero_solicitacoes_seguro_desemprego_anteriores: int = 0
    meses_trabalhados_outros_vinculos_periodo: int = 0

    # Estabilidades provisórias: informe a data-fim de cada uma que se aplique
    # (None se não houver). Se a dispensa (sem ou com justa causa) ocorrer
    # antes dessa data, o cálculo gera um alerta de risco e uma indenização
    # estimada mínima do período estabilitário remanescente.
    estabilidade_gestante_dt_fim: Optional[date] = None  # Art. 10, II, "b", ADCT
    estabilidade_cipa_dt_fim: Optional[date] = None  # Art. 10, II, "a", ADCT
    estabilidade_acidentario_dt_fim: Optional[date] = None  # Art. 118, Lei 8.213/91


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

    # Reflexo de horas extras habituais + DSR (Súmula 27 TST, OJ 394 SDI-1):
    # integra a base do aviso indenizado, 13º e férias — não o saldo de
    # salário, que reflete apenas os dias efetivamente trabalhados no mês.
    valor_hora_extra = d.valor_hora_extra
    if valor_hora_extra is None:
        valor_hora_extra = (d.salario_base / d.divisor_hora_normal) * (1 + d.adicional_hora_extra)
    valor_he_mensal = d.media_horas_extras_mensal * valor_hora_extra
    dsr_sobre_he = 0.0
    if valor_he_mensal and d.dias_uteis_mes_referencia:
        dsr_sobre_he = (valor_he_mensal / d.dias_uteis_mes_referencia) * d.dias_repouso_mes_referencia
    remuneracao_reflexos = d.salario_base + valor_he_mensal + dsr_sobre_he
    valor_dia_reflexos = remuneracao_reflexos / 30

    # 1. Saldo de salário (dias trabalhados no mês do desligamento)
    dias_trabalhados_mes = d.data_desligamento.day
    add_provento("Saldo de salário", valor_dia * dias_trabalhados_mes)

    # 2. Aviso prévio (só se aplicável ao tipo de rescisão). Rescisão indireta
    # (Art. 483 CLT) gera os mesmos direitos financeiros de uma dispensa sem
    # justa causa, por jurisprudência consolidada do TST.
    tem_aviso = d.tipo_rescisao in ("sem_justa_causa", "acordo_484a", "rescisao_indireta")
    dias_aviso = 0
    if tem_aviso:
        anos_completos = relativedelta(d.data_desligamento, d.data_admissao).years
        dias_aviso = min(30 + (3 * anos_completos), 90)
        if d.aviso_previo == "indenizado":
            valor_aviso = valor_dia_reflexos * dias_aviso
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
        add_provento(f"13º salário proporcional ({meses_13}/12)", (remuneracao_reflexos / 12) * meses_13)

        # 4. Férias proporcionais + 1/3
        meses_ferias = relativedelta(data_projecao, d.data_admissao).months
        ferias_prop = (remuneracao_reflexos / 12) * meses_ferias
        add_provento(f"Férias proporcionais ({meses_ferias}/12) + 1/3", ferias_prop * (4 / 3))

    # 5. Férias vencidas + 1/3, se houver (devidas mesmo em justa causa)
    if d.ferias_vencidas:
        add_provento("Férias vencidas + 1/3", remuneracao_reflexos * (4 / 3))

    # 6. Indenização por rescisão antecipada de contrato de experiência:
    # Art. 479 CLT (empregador antecipa, sem justa causa) ou Art. 480 CLT
    # (empregado antecipa — vira desconto, devido ao empregador).
    if (
        d.tipo_rescisao == "termino_experiencia"
        and d.data_fim_contrato_experiencia is not None
        and d.data_desligamento < d.data_fim_contrato_experiencia
    ):
        dias_restantes = (d.data_fim_contrato_experiencia - d.data_desligamento).days
        indenizacao = (valor_dia_reflexos * dias_restantes) / 2
        if d.quem_antecipou_experiencia == "empregado":
            add_desconto(
                f"Indenização Art. 480 CLT ao empregador (metade de {dias_restantes} dias restantes)",
                indenizacao,
            )
        else:
            add_provento(
                f"Indenização Art. 479 CLT (metade de {dias_restantes} dias restantes)",
                indenizacao,
            )

    # --- Estabilidades provisórias: alerta de risco + indenização estimada
    # mínima do período estabilitário remanescente mais longo (não soma
    # estabilidades concorrentes, nem novos reflexos de 13º/férias sobre
    # esse período — ver GAPS CONHECIDOS no cabeçalho do arquivo).
    resultado["alertas_risco"] = verificar_estabilidades(d)
    dias_estabilidade_restantes = 0
    if d.tipo_rescisao in ("sem_justa_causa", "justa_causa", "rescisao_indireta"):
        for dt_fim in (
            d.estabilidade_gestante_dt_fim,
            d.estabilidade_cipa_dt_fim,
            d.estabilidade_acidentario_dt_fim,
        ):
            if dt_fim is not None and d.data_desligamento < dt_fim:
                dias_estabilidade_restantes = max(dias_estabilidade_restantes, (dt_fim - d.data_desligamento).days)
    if dias_estabilidade_restantes > 0:
        meses_estabilidade = max(1, round(dias_estabilidade_restantes / 30))
        add_provento(
            f"Indenização estimada do período estabilitário ({dias_estabilidade_restantes} dias — ver alerta de risco)",
            valor_dia_reflexos * dias_estabilidade_restantes,
        )
        add_provento(
            f"13º proporcional estimado do período estabilitário ({meses_estabilidade}/12 — ver alerta de risco)",
            (remuneracao_reflexos / 12) * meses_estabilidade,
        )
        add_provento(
            f"Férias proporcionais estimadas do período estabilitário ({meses_estabilidade}/12 + 1/3 — ver alerta de risco)",
            (remuneracao_reflexos / 12) * meses_estabilidade * (4 / 3),
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
        fgts_periodo_aviso_projetado = round(valor_dia_reflexos * dias_aviso * ALIQUOTA_FGTS_MENSAL, 2)

    base_fgts_multa = d.saldo_fgts_depositado + fgts_mes_rescisao + fgts_periodo_aviso_projetado
    resultado["fgts"] = {
        "saldo_anterior_informado": round(d.saldo_fgts_depositado, 2),
        "deposito_mes_rescisao": fgts_mes_rescisao,
        "deposito_periodo_aviso_projetado": fgts_periodo_aviso_projetado,
        "base_para_multa": round(base_fgts_multa, 2),
    }

    valor_multa_fgts = 0.0
    if d.tipo_rescisao in ("sem_justa_causa", "rescisao_indireta"):
        valor_multa_fgts = round(base_fgts_multa * 0.40, 2)
        add_provento("Multa 40% FGTS", valor_multa_fgts)
    elif d.tipo_rescisao == "acordo_484a":
        valor_multa_fgts = round(base_fgts_multa * 0.20, 2)
        add_provento("Multa 20% FGTS (acordo Art. 484-A)", valor_multa_fgts)
    # pedido_demissao, justa_causa, término normal de experiência: sem multa

    # Saque-rescisão (Art. 20, Lei 8.036/90): estimativa do que pode ser
    # movimentado na conta — não substitui a homologação real no FGTS Digital.
    percentual_saque = PERCENTUAL_SAQUE_FGTS.get(d.tipo_rescisao, 0.0)
    resultado["fgts"]["percentual_saque_estimado"] = percentual_saque
    resultado["fgts"]["valor_sacavel_estimado"] = round(
        base_fgts_multa * percentual_saque + valor_multa_fgts, 2
    )

    # --- Seguro-desemprego (estimativa): dispensa sem justa causa ou
    # rescisão indireta. Considera apenas o vínculo desta rescisão como
    # período aquisitivo — ajuste manualmente se houver outros vínculos
    # formais no período.
    seguro_desemprego = {"elegivel": False, "numero_parcelas": 0, "valor_parcela": 0.0, "valor_total_estimado": 0.0}
    if d.tipo_rescisao in ("sem_justa_causa", "rescisao_indireta"):
        rel_vinculo = relativedelta(d.data_desligamento, d.data_admissao)
        meses_trabalhados_vinculo = (
            rel_vinculo.years * 12 + rel_vinculo.months + d.meses_trabalhados_outros_vinculos_periodo
        )
        numero_parcelas = calcular_numero_parcelas_seguro_desemprego(
            meses_trabalhados_vinculo, d.numero_solicitacoes_seguro_desemprego_anteriores
        )
        if numero_parcelas > 0:
            media_salarial = remuneracao_reflexos  # assume salário ~constante nos últimos 3 meses
            valor_parcela = calcular_valor_parcela_seguro_desemprego(media_salarial)
            seguro_desemprego = {
                "elegivel": True,
                "numero_parcelas": numero_parcelas,
                "valor_parcela": valor_parcela,
                "valor_total_estimado": round(valor_parcela * numero_parcelas, 2),
            }
    resultado["seguro_desemprego"] = seguro_desemprego

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


def _codigo_rubrica(nome: str, mapa: dict) -> Optional[str]:
    """Casa `nome` com `mapa_rubricas` — primeiro exato, depois pelo texto
    antes do parênteses (várias rubricas têm sufixos dinâmicos, como
    "Aviso prévio indenizado (42 dias)")."""
    if nome in mapa:
        return mapa[nome]
    return mapa.get(nome.split(" (")[0].strip())


def gerar_evento_esocial_s2299(d: DadosRescisao, resultado: dict, mapa_rubricas: Optional[dict] = None) -> dict:
    """Monta o esqueleto do evento S-2299 (Desligamento) do eSocial.

    Não substitui a integração real. `mapa_rubricas` é opcional: um dict
    {nome_da_rubrica: codRubr} com a tabela de rubricas (evento S-1010) da
    própria empresa — se informado, preenche `codRubr`; senão, fica `None`
    para preenchimento posterior.
    """
    mapa_rubricas = mapa_rubricas or {}
    if d.tipo_rescisao == "termino_experiencia":
        antecipacao = (
            d.data_fim_contrato_experiencia is not None
            and d.data_desligamento < d.data_fim_contrato_experiencia
        )
        if not antecipacao:
            mtv_deslig = "07"  # Término de Contrato a Termo
        elif d.quem_antecipou_experiencia == "empregado":
            mtv_deslig = "01"  # Rescisão Antecipada por Iniciativa do Empregado
        else:
            mtv_deslig = "02"  # Rescisão Antecipada por Iniciativa do Empregador, Sem Justa Causa
    else:
        mtv_deslig = MOTIVO_DESLIGAMENTO_ESOCIAL.get(d.tipo_rescisao)

    return {
        "evento": "S-2299",
        "infoDeslig": {
            "mtvDeslig": mtv_deslig,
            "dtDeslig": d.data_desligamento.isoformat(),
            "verbasRescisorias": {
                "proventos": [
                    {"descricao": r["rubrica"], "valor": r["valor"], "codRubr": _codigo_rubrica(r["rubrica"], mapa_rubricas)}
                    for r in resultado["rubricas"]
                ],
                "descontos": [
                    {"descricao": r["rubrica"], "valor": r["valor"], "codRubr": _codigo_rubrica(r["rubrica"], mapa_rubricas)}
                    for r in resultado["descontos"]
                ],
            },
        },
        "prazo_envio": "vinculado ao prazo de pagamento do Art. 477 CLT (10 dias corridos do desligamento)",
        "_atencao": (
            "codRubr sem correspondência em mapa_rubricas fica None e precisa ser preenchido "
            "conforme a tabela de rubricas (S-1010) da empresa; mtvDeslig segue a Tabela 19 do eSocial."
        ),
    }


def imprimir_resultado(r: dict):
    print(f"\n{'='*50}\nTIPO DE RESCISÃO: {r['tipo_rescisao']}\n{'='*50}")
    if r.get("alertas_risco"):
        print("\n*** ALERTAS DE RISCO ***")
        for alerta in r["alertas_risco"]:
            print(f"  - {alerta}")
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
    print("\nFGTS (memorando, não incluído no líquido pago em dinheiro, exceto a multa):")
    print(f"  Saldo anterior informado                     R$ {fgts['saldo_anterior_informado']:>10.2f}")
    print(f"  Depósito do mês da rescisão                  R$ {fgts['deposito_mes_rescisao']:>10.2f}")
    print(f"  Depósito período de projeção do aviso         R$ {fgts['deposito_periodo_aviso_projetado']:>10.2f}")
    print(f"  Base usada para a multa                      R$ {fgts['base_para_multa']:>10.2f}")
    print(f"  Saque-rescisão estimado ({fgts['percentual_saque_estimado']*100:.0f}% do saldo + multa)  "
          f"R$ {fgts['valor_sacavel_estimado']:>10.2f}")

    seguro = r["seguro_desemprego"]
    print("\nSeguro-desemprego (estimativa):")
    if seguro["elegivel"]:
        print(f"  Parcelas: {seguro['numero_parcelas']}  |  Valor por parcela: R$ {seguro['valor_parcela']:.2f}"
              f"  |  Total estimado: R$ {seguro['valor_total_estimado']:.2f}")
    else:
        print("  Não elegível (ou meses trabalhados insuficientes) para este tipo de rescisão.")

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
        media_horas_extras_mensal=10,  # 10h extras habituais por mês
    )
    resultado = calcular_rescisao(exemplo)
    imprimir_resultado(resultado)

    import json
    print("\nEvento eSocial S-2299 (esqueleto):")
    print(json.dumps(gerar_evento_esocial_s2299(exemplo, resultado), indent=2, ensure_ascii=False, default=str))
