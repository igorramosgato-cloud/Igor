"""
App web do Planejamento Financeiro Pessoal
===========================================

Interface Flask simples pra usar o `planejamento_financeiro.py` sem linha
de comando: formulário do simulador de meta, histórico de patrimônio e um
botão pra puxar snapshot via Pluggy.

Rodar:
    pip install -r requirements.txt --break-system-packages
    python3 app.py
    (abre em http://127.0.0.1:5000)
"""

from datetime import date

from flask import Flask, redirect, render_template, request, url_for

from planejamento_financeiro import (
    PLUGGY_CLIENT_ID,
    PLUGGY_CLIENT_SECRET,
    ParametrosMeta,
    evolucao_patrimonio,
    puxar_patrimonio_real,
    registrar_snapshot,
    simular_divisao,
)

app = Flask(__name__)


@app.route("/")
def index():
    return redirect(url_for("meta"))


@app.route("/meta", methods=["GET", "POST"])
def meta():
    resultado = None
    erro = None
    valores = {
        "data_meta": "",
        "valor_meta": "",
        "ja_guardado": "0",
        "sobra_mensal": "",
        "taxa_aa": "",
    }

    if request.method == "POST":
        valores.update({k: request.form.get(k, v) for k, v in valores.items()})
        try:
            p = ParametrosMeta(
                data_hoje=date.today(),
                data_meta=date.fromisoformat(valores["data_meta"]),
                valor_meta=float(valores["valor_meta"]),
                ja_guardado_meta=float(valores["ja_guardado"]),
                sobra_mensal_total=float(valores["sobra_mensal"]),
                taxa_investimento_aa=float(valores["taxa_aa"]),
            )
            resultado = simular_divisao(p)
        except ValueError as exc:
            erro = str(exc)

    return render_template("meta.html", resultado=resultado, erro=erro, valores=valores)


@app.route("/historico")
def historico():
    return render_template("historico.html", historico=evolucao_patrimonio())


@app.route("/snapshot", methods=["POST"])
def snapshot():
    if not (PLUGGY_CLIENT_ID and PLUGGY_CLIENT_SECRET):
        return render_template(
            "historico.html",
            historico=evolucao_patrimonio(),
            erro=(
                "Defina as variáveis de ambiente PLUGGY_CLIENT_ID e "
                "PLUGGY_CLIENT_SECRET (do dashboard.pluggy.ai) antes de puxar um snapshot."
            ),
        )

    item_ids = [v.strip() for v in request.form.get("item_ids", "").split(",") if v.strip()]
    if not item_ids:
        return render_template(
            "historico.html",
            historico=evolucao_patrimonio(),
            erro="Informe ao menos um item_id do Pluggy (separados por vírgula).",
        )

    try:
        snap = puxar_patrimonio_real(item_ids=item_ids)
        registrar_snapshot(snap)
    except Exception as exc:  # erro de rede/API do Pluggy — mostra na tela em vez de quebrar
        return render_template(
            "historico.html",
            historico=evolucao_patrimonio(),
            erro=f"Falha ao puxar dados do Pluggy: {exc}",
        )

    return redirect(url_for("historico"))


if __name__ == "__main__":
    app.run(debug=True)
