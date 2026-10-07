from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from math import exp
from random import Random
from typing import Any

from data.brazil_2026 import BASELINE


@dataclass
class Policy:
    government_consumption_growth_pct: float = 0.0
    public_investment_delta_pct_gdp: float = 0.0
    tax_burden_delta_pp: float = 0.0
    transfers_growth_pct: float = 0.0
    minimum_wage_growth_pct: float = 0.0
    selic_pct_aa: float = 13.75
    fx_intervention_usd_bn: float = 0.0
    productivity_quarterly_pct: float = 0.10
    confidence_delta: float = 0.0
    world_growth_pct: float = 2.8
    commodity_shock_pct: float = 0.0
    risk_premium_delta: float = 0.0
    immigration_thousand: float = 0.0
    random_shock: bool = False


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _logistic_score(x: float) -> float:
    return 100.0 / (1.0 + exp(-x))


def new_state(seed: int = 42) -> dict[str, Any]:
    b = deepcopy(BASELINE)
    gdp = b["gdp_nominal_q_brl_bn"]
    state = {
        "quarter": 0,
        "period": "2026-T3",
        "seed": seed,
        **b,
        "real_gdp_index": 100.0,
        "nominal_gdp_index": 100.0,
        "price_level_index": 100.0,
        "aggregate_income_brl_bn": gdp,
        "aggregate_expenditure_brl_bn": gdp,
        "consumption_brl_bn": gdp * b["consumption_share_pct"] / 100,
        "government_consumption_brl_bn": gdp * b["government_consumption_share_pct"] / 100,
        "investment_brl_bn": gdp * b["investment_share_pct"] / 100,
        "exports_brl_bn": gdp * b["exports_share_pct"] / 100,
        "imports_brl_bn": gdp * b["imports_share_pct"] / 100,
        "inventory_change_brl_bn": gdp * b["inventory_share_pct"] / 100,
        "net_exports_brl_bn": gdp * (b["exports_share_pct"] - b["imports_share_pct"]) / 100,
        "taxes_brl_bn": gdp * b["tax_burden_pct_gdp"] / 100 / 4,
        "savings_brl_bn": gdp * b["gross_savings_share_pct"] / 100,
        "depreciation_brl_bn": gdp * b["depreciation_share_pct"] / 100,
        "net_domestic_product_brl_bn": gdp * (1 - b["depreciation_share_pct"] / 100),
        "gnp_brl_bn": gdp * (1 + b["net_factor_income_abroad_pct_gdp"] / 100),
        "gdp_at_factor_cost_brl_bn": gdp * (1 - (b["tax_burden_pct_gdp"] - b["subsidies_pct_gdp"]) / 100 / 4),
        "labor_force_m": b["labor_force_m"],
        "unemployed_m": b["labor_force_m"] * b["unemployment_pct"] / 100,
        "employed_m": b["labor_force_m"] * (1 - b["unemployment_pct"] / 100),
        "real_wage_index": 100.0,
        "potential_growth_annual_pct": 2.2,
        "output_gap_pct": 0.0,
        "approval_pct": 52.0,
        "quality_of_life_index": 100.0,
        "fiscal_space_index": 50.0,
        "external_vulnerability_index": 35.0,
        "status": "Em andamento",
        "alerts": [],
        "history": [],
        "last_policy": asdict(Policy()),
    }
    state["history"].append(snapshot(state))
    return state


def _period_label(q: int) -> str:
    base_year, base_q = 2026, 3
    idx = (base_q - 1) + q
    return f"{base_year + idx // 4}-T{idx % 4 + 1}"


def snapshot(s: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "quarter", "period", "gdp_nominal_q_brl_bn", "gdp_real_growth_qoq_pct",
        "gdp_real_growth_yoy_pct", "real_gdp_index", "ipca_12m_pct", "unemployment_pct",
        "selic_pct_aa", "fx_brl_usd", "gross_debt_pct_gdp", "net_debt_pct_gdp",
        "primary_balance_pct_gdp", "nominal_balance_pct_gdp", "current_account_pct_gdp",
        "reserves_usd_bn", "investment_share_pct", "gross_savings_share_pct",
        "avg_real_income_brl", "minimum_wage_brl", "productivity_index", "confidence_index",
        "approval_pct", "quality_of_life_index", "fiscal_space_index",
        "external_vulnerability_index", "aggregate_income_brl_bn", "aggregate_expenditure_brl_bn",
        "consumption_brl_bn", "government_consumption_brl_bn", "investment_brl_bn",
        "exports_brl_bn", "imports_brl_bn", "net_exports_brl_bn", "taxes_brl_bn",
        "savings_brl_bn", "depreciation_brl_bn", "net_domestic_product_brl_bn", "gnp_brl_bn",
        "gdp_at_factor_cost_brl_bn", "output_gap_pct", "risk_premium_index", "status"
    ]
    out = {k: s.get(k) for k in keys}
    out["alerts"] = list(s.get("alerts", []))
    return out


# Faixas didáticas usadas tanto no backend quanto nos controles da interface.
# A intenção é impedir entradas extremas acidentais e manter cada decisão
# dentro de uma ordem de grandeza plausível para um único trimestre.
POLICY_RANGES: dict[str, tuple[float, float]] = {
    "government_consumption_growth_pct": (-10.0, 10.0),
    "public_investment_delta_pct_gdp": (-1.0, 1.0),
    "tax_burden_delta_pp": (-2.0, 2.0),
    "transfers_growth_pct": (-10.0, 15.0),
    "minimum_wage_growth_pct": (-5.0, 15.0),
    "selic_pct_aa": (2.0, 20.0),
    "fx_intervention_usd_bn": (-20.0, 20.0),
    "productivity_quarterly_pct": (-0.5, 1.0),
    "confidence_delta": (-10.0, 10.0),
    "world_growth_pct": (-2.0, 6.0),
    "commodity_shock_pct": (-20.0, 20.0),
    "risk_premium_delta": (-15.0, 15.0),
    "immigration_thousand": (-500.0, 500.0),
}


def validate_policy(p: Policy) -> None:
    for field, (lo, hi) in POLICY_RANGES.items():
        v = float(getattr(p, field))
        if not lo <= v <= hi:
            raise ValueError(f"{field} deve estar entre {lo} e {hi}.")


def advance(state: dict[str, Any], policy: Policy) -> dict[str, Any]:
    validate_policy(policy)
    s = deepcopy(state)
    if s.get("status") != "Em andamento":
        return s

    rng = Random(int(s.get("seed", 42)) + int(s["quarter"]) * 7919)
    shock = rng.gauss(0, 0.20) if policy.random_shock else 0.0

    prev_gdp = s["gdp_nominal_q_brl_bn"]
    prev_real_income = s["avg_real_income_brl"]
    prev_min_wage = s["minimum_wage_brl"]
    prev_debt = s["gross_debt_pct_gdp"]

    # 1) Política, expectativas e preços relativos
    s["selic_pct_aa"] = policy.selic_pct_aa
    s["confidence_index"] = _clamp(s["confidence_index"] + policy.confidence_delta, 50, 150)
    s["risk_premium_index"] = _clamp(s["risk_premium_index"] + policy.risk_premium_delta, 50, 180)
    s["productivity_index"] *= 1 + policy.productivity_quarterly_pct / 100
    s["population_m"] += policy.immigration_thousand / 1000

    # Câmbio: diferencial real de juros, risco, conta corrente, intervenção e choque externo.
    real_rate = s["selic_pct_aa"] - s["ipca_12m_pct"]
    fx_change = (
        0.003 * (5.0 - real_rate)
        + 0.0025 * policy.risk_premium_delta
        - 0.0015 * policy.fx_intervention_usd_bn
        - 0.0010 * (policy.world_growth_pct - 2.8)
        - 0.0008 * policy.commodity_shock_pct
        + shock * 0.01
    )
    s["fx_brl_usd"] = _clamp(s["fx_brl_usd"] * (1 + fx_change), 2.5, 12.0)

    # 2) Blocos de demanda. As elasticidades são hipóteses didáticas calibradas para estabilidade.
    fiscal_impulse = 0.10 * policy.government_consumption_growth_pct + 0.45 * policy.public_investment_delta_pct_gdp
    tax_drag = -0.18 * policy.tax_burden_delta_pp
    transfers_impulse = 0.035 * policy.transfers_growth_pct
    real_rate_gap = real_rate - s["neutral_real_rate_pct"]
    monetary_drag = -0.055 * real_rate_gap
    confidence_impulse = 0.025 * policy.confidence_delta
    productivity_impulse = 0.55 * policy.productivity_quarterly_pct
    external_impulse = 0.10 * (policy.world_growth_pct - 2.8) + 0.018 * policy.commodity_shock_pct

    growth_q = 0.45 + fiscal_impulse + tax_drag + transfers_impulse + monetary_drag + confidence_impulse + productivity_impulse + external_impulse + shock
    growth_q = _clamp(growth_q, -5.0, 6.0)
    s["gdp_real_growth_qoq_pct"] = growth_q
    s["gdp_real_growth_yoy_pct"] = _clamp(4 * growth_q * 0.75 + s["gdp_real_growth_yoy_pct"] * 0.25, -12, 15)
    s["gdp_growth_4q_pct"] = _clamp(s["gdp_growth_4q_pct"] * 0.70 + s["gdp_real_growth_yoy_pct"] * 0.30, -10, 12)
    s["real_gdp_index"] *= 1 + growth_q / 100

    potential_q = s["potential_growth_annual_pct"] / 4
    s["output_gap_pct"] = _clamp(s["output_gap_pct"] + 0.55 * (growth_q - potential_q), -8, 8)

    # 3) Inflação: inércia + hiato + câmbio + salários + commodities - efeito monetário defasado.
    min_wage_nominal_growth_q = policy.minimum_wage_growth_pct
    wage_pressure = max(0.0, min_wage_nominal_growth_q - s["ipca_12m_pct"] / 4)
    annual_inflation = (
        0.72 * s["ipca_12m_pct"]
        + 0.28 * 3.0
        + 0.28 * s["output_gap_pct"]
        + 8.0 * max(fx_change, -0.05)
        + 0.06 * policy.commodity_shock_pct
        + 0.05 * wage_pressure
        - 0.10 * max(real_rate_gap, 0)
    )
    s["ipca_12m_pct"] = _clamp(annual_inflation, -1.5, 25.0)
    s["ipca_month_pct"] = s["ipca_12m_pct"] / 12
    q_infl = (1 + s["ipca_12m_pct"] / 100) ** 0.25 - 1
    s["price_level_index"] *= 1 + q_infl
    s["gdp_deflator_index"] *= 1 + q_infl

    # 4) Mercado de trabalho e rendas: regra de Okun simplificada.
    delta_u = -0.28 * (growth_q - potential_q) + 0.015 * max(real_rate_gap, 0)
    s["unemployment_pct"] = _clamp(s["unemployment_pct"] + delta_u, 2.5, 22.0)
    s["labor_force_m"] *= 1 + 0.0010
    s["unemployed_m"] = s["labor_force_m"] * s["unemployment_pct"] / 100
    s["employed_m"] = s["labor_force_m"] - s["unemployed_m"]
    s["minimum_wage_brl"] *= 1 + policy.minimum_wage_growth_pct / 100
    real_income_growth_q = 0.35 * growth_q + 0.20 * policy.productivity_quarterly_pct - 0.12 * max(s["ipca_12m_pct"] - 3, 0)
    s["avg_real_income_brl"] *= 1 + real_income_growth_q / 100
    s["real_wage_index"] *= 1 + real_income_growth_q / 100

    # 5) Shares de demanda e identidade Y = C + I + G + X - M + variação de estoques.
    s["tax_burden_pct_gdp"] = _clamp(s["tax_burden_pct_gdp"] + policy.tax_burden_delta_pp, 20, 45)
    s["government_consumption_share_pct"] = _clamp(
        s["government_consumption_share_pct"] * (1 + policy.government_consumption_growth_pct / 100), 10, 30
    )
    s["investment_share_pct"] = _clamp(
        s["investment_share_pct"]
        + policy.public_investment_delta_pct_gdp
        - 0.08 * real_rate_gap
        + 0.025 * policy.confidence_delta
        + 0.10 * policy.productivity_quarterly_pct,
        8, 30,
    )
    s["gross_savings_share_pct"] = _clamp(
        s["gross_savings_share_pct"] + 0.04 * real_rate_gap + 0.02 * growth_q - 0.03 * policy.transfers_growth_pct,
        8, 30,
    )
    s["consumption_share_pct"] = _clamp(
        s["consumption_share_pct"] + 0.05 * real_income_growth_q + 0.03 * policy.transfers_growth_pct - 0.12 * policy.tax_burden_delta_pp,
        50, 75,
    )
    s["exports_share_pct"] = _clamp(
        s["exports_share_pct"] + 0.10 * (policy.world_growth_pct - 2.8) + 0.025 * policy.commodity_shock_pct + 8 * max(fx_change, -0.03),
        8, 28,
    )
    s["imports_share_pct"] = _clamp(
        s["imports_share_pct"] + 0.08 * growth_q - 5 * fx_change,
        8, 28,
    )

    # Fecha a identidade pelo estoque para evitar inconsistência contábil artificial.
    s["inventory_share_pct"] = 100 - (
        s["consumption_share_pct"] + s["government_consumption_share_pct"] + s["investment_share_pct"]
        + s["exports_share_pct"] - s["imports_share_pct"]
    )
    s["inventory_share_pct"] = _clamp(s["inventory_share_pct"], -6, 8)

    nominal_growth_q = (1 + growth_q / 100) * (1 + q_infl) - 1
    s["gdp_nominal_q_brl_bn"] = prev_gdp * (1 + nominal_growth_q)
    gdp = s["gdp_nominal_q_brl_bn"]
    s["nominal_gdp_index"] *= 1 + nominal_growth_q

    s["consumption_brl_bn"] = gdp * s["consumption_share_pct"] / 100
    s["government_consumption_brl_bn"] = gdp * s["government_consumption_share_pct"] / 100
    s["investment_brl_bn"] = gdp * s["investment_share_pct"] / 100
    s["exports_brl_bn"] = gdp * s["exports_share_pct"] / 100
    s["imports_brl_bn"] = gdp * s["imports_share_pct"] / 100
    s["inventory_change_brl_bn"] = gdp * s["inventory_share_pct"] / 100
    s["net_exports_brl_bn"] = s["exports_brl_bn"] - s["imports_brl_bn"]
    s["aggregate_expenditure_brl_bn"] = (
        s["consumption_brl_bn"] + s["government_consumption_brl_bn"] + s["investment_brl_bn"]
        + s["exports_brl_bn"] - s["imports_brl_bn"] + s["inventory_change_brl_bn"]
    )
    s["aggregate_income_brl_bn"] = s["aggregate_expenditure_brl_bn"]

    # 6) Produto líquido, produto nacional e custo de fatores.
    s["depreciation_brl_bn"] = gdp * s["depreciation_share_pct"] / 100
    s["net_domestic_product_brl_bn"] = gdp - s["depreciation_brl_bn"]
    s["gnp_brl_bn"] = gdp * (1 + s["net_factor_income_abroad_pct_gdp"] / 100)
    net_indirect_tax_q = (s["tax_burden_pct_gdp"] - s["subsidies_pct_gdp"]) / 4
    s["gdp_at_factor_cost_brl_bn"] = gdp * (1 - net_indirect_tax_q / 100)
    s["savings_brl_bn"] = gdp * s["gross_savings_share_pct"] / 100
    s["taxes_brl_bn"] = gdp * s["tax_burden_pct_gdp"] / 100 / 4

    # 7) Fiscal: saldo primário endógeno simplificado e dinâmica da dívida.
    structural_primary = -0.67
    primary = structural_primary + 0.75 * policy.tax_burden_delta_pp - 0.20 * policy.government_consumption_growth_pct - 0.35 * policy.public_investment_delta_pct_gdp - 0.05 * policy.transfers_growth_pct + 0.12 * max(growth_q - potential_q, -3)
    s["primary_balance_pct_gdp"] = _clamp(primary, -12, 8)
    interest_bill = _clamp(0.58 * s["selic_pct_aa"] * s["gross_debt_pct_gdp"] / 100, 2, 16)
    s["nominal_interest_pct_gdp"] = interest_bill
    s["nominal_balance_pct_gdp"] = s["primary_balance_pct_gdp"] - interest_bill

    annual_nominal_growth = ((1 + nominal_growth_q) ** 4 - 1) * 100
    effective_debt_rate = max(0.0, 0.55 * s["selic_pct_aa"])
    debt_change = ((effective_debt_rate - annual_nominal_growth) / 100) * prev_debt / 4 - s["primary_balance_pct_gdp"] / 4
    s["gross_debt_pct_gdp"] = _clamp(prev_debt + debt_change, 20, 160)
    s["net_debt_pct_gdp"] = _clamp(s["net_debt_pct_gdp"] + 0.82 * debt_change - 0.03 * policy.fx_intervention_usd_bn, 10, 150)

    # 8) Setor externo e reservas.
    nx_share = s["exports_share_pct"] - s["imports_share_pct"]
    s["current_account_pct_gdp"] = _clamp(0.78 * s["current_account_pct_gdp"] + 0.22 * nx_share - 0.10 * max(growth_q - potential_q, 0), -10, 8)
    reserve_flow = -policy.fx_intervention_usd_bn + 0.25 * (s["fdi_pct_gdp"] + s["current_account_pct_gdp"])
    s["reserves_usd_bn"] = _clamp(s["reserves_usd_bn"] + reserve_flow, 20, 600)

    # 9) Indicadores sintéticos de bem-estar e governabilidade.
    real_income_delta = (s["avg_real_income_brl"] / max(prev_real_income, 1e-9) - 1) * 100
    debt_penalty = max(s["gross_debt_pct_gdp"] - 80, 0)
    approval_raw = (
        0.45 * growth_q + 0.22 * real_income_delta - 0.20 * (s["unemployment_pct"] - 5)
        - 0.12 * (s["ipca_12m_pct"] - 3) - 0.035 * debt_penalty
    )
    s["approval_pct"] = _clamp(0.82 * s["approval_pct"] + 0.18 * _logistic_score(approval_raw / 3), 5, 95)
    s["quality_of_life_index"] = _clamp(
        s["quality_of_life_index"] * (1 + (0.25 * real_income_delta + 0.15 * growth_q - 0.08 * max(s["ipca_12m_pct"] - 3, 0) - 0.08 * max(s["unemployment_pct"] - 5, 0)) / 100),
        50, 160,
    )
    s["fiscal_space_index"] = _clamp(100 - 0.65 * s["gross_debt_pct_gdp"] + 2.0 * s["primary_balance_pct_gdp"], 0, 100)
    s["external_vulnerability_index"] = _clamp(35 + 3.5 * max(-s["current_account_pct_gdp"], 0) + 0.10 * max(s["risk_premium_index"] - 100, 0) - 0.03 * (s["reserves_usd_bn"] - 300), 0, 100)

    # 10) Setores produtivos: redistribuição leve para visualização.
    s["agriculture_share_va_pct"] = _clamp(s["agriculture_share_va_pct"] + 0.01 * policy.commodity_shock_pct, 4, 15)
    s["industry_share_va_pct"] = _clamp(s["industry_share_va_pct"] + 0.04 * policy.productivity_quarterly_pct + 0.01 * policy.confidence_delta, 15, 32)
    s["services_share_va_pct"] = 100 - s["agriculture_share_va_pct"] - s["industry_share_va_pct"]

    # 11) Estado, alertas e encerramento do mandato.
    s["quarter"] += 1
    s["period"] = _period_label(s["quarter"])
    s["last_policy"] = asdict(policy)
    alerts = []
    if s["ipca_12m_pct"] > 8: alerts.append("Inflação elevada")
    if s["unemployment_pct"] > 10: alerts.append("Desemprego elevado")
    if s["gross_debt_pct_gdp"] > 95: alerts.append("Dívida bruta em zona de risco")
    if s["current_account_pct_gdp"] < -4: alerts.append("Déficit externo elevado")
    if s["reserves_usd_bn"] < 250: alerts.append("Reservas em queda relevante")
    if s["approval_pct"] < 25: alerts.append("Baixa governabilidade")
    if abs(s["inventory_share_pct"]) >= 5.5: alerts.append("Fechamento contábil depende fortemente de estoques")
    s["alerts"] = alerts

    if s["quarter"] >= 16:
        s["status"] = "Mandato concluído"
    elif s["gross_debt_pct_gdp"] >= 135 or s["ipca_12m_pct"] >= 20 or s["unemployment_pct"] >= 18 or s["reserves_usd_bn"] <= 80:
        s["status"] = "Crise macroeconômica"

    s["history"].append(snapshot(s))
    s["history"] = s["history"][-20:]
    return s
