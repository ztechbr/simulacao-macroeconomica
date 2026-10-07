from domain.engine import Policy, advance, new_state


def test_identity_is_closed():
    s = new_state()
    s = advance(s, Policy())
    lhs = s["gdp_nominal_q_brl_bn"]
    rhs = (s["consumption_brl_bn"] + s["investment_brl_bn"] + s["government_consumption_brl_bn"]
           + s["exports_brl_bn"] - s["imports_brl_bn"] + s["inventory_change_brl_bn"])
    assert abs(lhs-rhs) < 1e-6


def test_expansionary_fiscal_policy_raises_short_run_growth():
    base = advance(new_state(), Policy())
    stim = advance(new_state(), Policy(government_consumption_growth_pct=5, public_investment_delta_pct_gdp=0.5))
    assert stim["gdp_real_growth_qoq_pct"] > base["gdp_real_growth_qoq_pct"]


def test_high_selic_restrains_growth():
    low = advance(new_state(), Policy(selic_pct_aa=8))
    high = advance(new_state(), Policy(selic_pct_aa=20))
    assert high["gdp_real_growth_qoq_pct"] < low["gdp_real_growth_qoq_pct"]


def test_four_year_mandate():
    s = new_state()
    for _ in range(16):
        s = advance(s, Policy())
        if s["status"] != "Em andamento":
            break
    assert s["status"] in {"Mandato concluído", "Crise macroeconômica"}


def test_policy_ranges_accept_ui_boundaries():
    from domain.engine import POLICY_RANGES, validate_policy

    for field, (lo, hi) in POLICY_RANGES.items():
        p = Policy()
        setattr(p, field, lo)
        validate_policy(p)
        setattr(p, field, hi)
        validate_policy(p)


def test_policy_ranges_reject_values_outside_ui_limits():
    import pytest
    from domain.engine import POLICY_RANGES, validate_policy

    p = Policy()
    lo, hi = POLICY_RANGES["government_consumption_growth_pct"]
    p.government_consumption_growth_pct = hi + 0.01
    with pytest.raises(ValueError):
        validate_policy(p)
