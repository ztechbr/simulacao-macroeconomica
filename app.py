from __future__ import annotations
import os
import secrets
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from data.brazil_2026 import SOURCES
from domain.engine import POLICY_RANGES, Policy, advance, new_state
from services.repository import SimulationRepository

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-change-me")
repo = SimulationRepository(os.getenv("DATABASE_PATH", str(BASE_DIR / "instance" / "presidente_macro.db")))


def current_id() -> str:
    if "simulation_id" not in session:
        session["simulation_id"] = secrets.token_hex(12)
    return session["simulation_id"]


def current_state() -> dict:
    sim_id = current_id()
    state = repo.get(sim_id)
    if not state:
        state = new_state(int(os.getenv("SIMULATION_SEED", "42")))
        repo.save(sim_id, state)
    return state




def build_history_table(history: list[dict]) -> list[dict]:
    """Prepara as linhas do histórico e a variação percentual vs. período anterior.

    Para indicadores que já são taxas (%), a coluna de variação mostra a mudança
    relativa do valor do indicador, e não pontos percentuais. O denominador usa
    |valor anterior| para preservar o sentido positivo/negativo da mudança.
    """
    metrics = (
        "gdp_real_growth_qoq_pct",
        "ipca_12m_pct",
        "unemployment_pct",
        "gross_debt_pct_gdp",
    )
    rows: list[dict] = []
    previous = None
    for item in history or []:
        row = {
            "period": item.get("period", ""),
            **{metric: item.get(metric) for metric in metrics},
        }
        for metric in metrics:
            delta_key = f"{metric}_change_pct"
            current = item.get(metric)
            prev = previous.get(metric) if previous else None
            if current is None or prev is None or abs(float(prev)) < 1e-12:
                row[delta_key] = None
            else:
                row[delta_key] = ((float(current) - float(prev)) / abs(float(prev))) * 100.0
        rows.append(row)
        previous = item
    return rows

def parse_policy(payload) -> Policy:
    def f(name, default):
        raw = payload.get(name, default)
        if raw in (None, ""):
            return float(default)
        return float(raw)
    return Policy(
        government_consumption_growth_pct=f("government_consumption_growth_pct", 0),
        public_investment_delta_pct_gdp=f("public_investment_delta_pct_gdp", 0),
        tax_burden_delta_pp=f("tax_burden_delta_pp", 0),
        transfers_growth_pct=f("transfers_growth_pct", 0),
        minimum_wage_growth_pct=f("minimum_wage_growth_pct", 0),
        selic_pct_aa=f("selic_pct_aa", 13.75),
        fx_intervention_usd_bn=f("fx_intervention_usd_bn", 0),
        productivity_quarterly_pct=f("productivity_quarterly_pct", 0.10),
        confidence_delta=f("confidence_delta", 0),
        world_growth_pct=f("world_growth_pct", 2.8),
        commodity_shock_pct=f("commodity_shock_pct", 0),
        risk_premium_delta=f("risk_premium_delta", 0),
        immigration_thousand=f("immigration_thousand", 0),
        random_shock=str(payload.get("random_shock", "")).lower() in {"1", "true", "on", "yes"},
    )


@app.get("/")
def index():
    state = current_state()
    return render_template(
        "dashboard.html",
        state=state,
        sources=SOURCES,
        policy_ranges=POLICY_RANGES,
        history_table=build_history_table(state.get("history", [])),
    )


@app.post("/advance")
def advance_route():
    state = current_state()
    try:
        policy = parse_policy(request.form)
        state = advance(state, policy)
        repo.save(current_id(), state)
        return redirect(url_for("index"))
    except (ValueError, TypeError) as exc:
        return render_template(
            "dashboard.html",
            state=state,
            sources=SOURCES,
            policy_ranges=POLICY_RANGES,
            history_table=build_history_table(state.get("history", [])),
            error=str(exc),
        ), 400


@app.post("/reset")
def reset_route():
    repo.delete(current_id())
    return redirect(url_for("index"))


@app.get("/api/state")
def api_state():
    return jsonify(current_state())


@app.post("/api/advance")
def api_advance():
    state = current_state()
    try:
        policy = parse_policy(request.get_json(silent=True) or {})
        state = advance(state, policy)
        repo.save(current_id(), state)
        return jsonify(state)
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/reset")
def api_reset():
    state = new_state(int(os.getenv("SIMULATION_SEED", "42")))
    repo.save(current_id(), state)
    return jsonify(state)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.getenv("FLASK_ENV") == "development")
