"""Baseline macroeconômico do Brasil para a simulação.

Os valores abaixo têm vintages diferentes porque indicadores oficiais são publicados
em frequências diferentes. Eles são sementes observadas, não uma fotografia síncrona.
A simulação inicia no 3º trimestre de 2026 e usa os valores mais recentes disponíveis
até 07/10/2026, com metadados de fonte/data preservados.
"""

BASELINE = {
    # Demografia e mercado de trabalho
    "population_m": 214.211951,                 # IBGE, estimativa 01/07/2026
    "labor_force_m": 109.5,                     # aproximação de escala, variável calibrável
    "unemployment_pct": 5.3,                    # PNAD, tri móvel encerrado ago/2026
    "avg_real_income_brl": 3777.0,              # PNAD, jun-jul-ago/2026
    "minimum_wage_brl": 1621.0,                 # Decreto 12.797/2025, vigência 2026

    # Atividade e preços
    "gdp_nominal_q_brl_bn": 3425.7,             # PIB corrente, 2T26
    "gdp_real_growth_qoq_pct": 0.5,             # 2T26 vs 1T26, dessazonalizado
    "gdp_real_growth_yoy_pct": 2.0,             # 2T26 vs 2T25
    "gdp_growth_4q_pct": 1.9,                   # acumulado 4 trimestres
    "ipca_12m_pct": 4.22,                       # ago/2026
    "ipca_month_pct": -0.32,                    # ago/2026
    "ipca15_month_pct": 0.70,                   # set/2026
    "gdp_deflator_index": 100.0,

    # Política monetária e câmbio
    "selic_pct_aa": 13.75,                      # Copom, desde 17/09/2026
    "fx_brl_usd": 4.9695,                       # BCB/PTAX exibida para 06/10/2026
    "neutral_real_rate_pct": 5.0,               # hipótese de calibração, não dado observado
    "risk_premium_index": 100.0,                # índice sintético de simulação

    # Fiscal
    "gross_debt_pct_gdp": 82.5,                 # DBGG, jul/2026
    "net_debt_pct_gdp": 69.1,                   # DLSP, jul/2026
    "primary_balance_pct_gdp": -0.67,           # setor público, 12m até jul/2026
    "nominal_balance_pct_gdp": -9.34,           # setor público, 12m até jul/2026
    "nominal_interest_pct_gdp": 8.67,           # juros nominais, 12m até jul/2026
    "tax_burden_pct_gdp": 32.0,                 # parâmetro inicial calibrável; não é leitura mensal
    "subsidies_pct_gdp": 0.6,                   # hipótese de calibração

    # Setor externo
    "current_account_pct_gdp": -2.47,           # 12m até ago/2026
    "reserves_usd_bn": 372.6,                   # ago/2026
    "fdi_pct_gdp": 3.50,                        # IDP 12m jul/2026
    "trade_balance_month_usd_bn": 6.6,          # ago/2026
    "exports_month_usd_bn": 33.3,               # ago/2026
    "imports_month_usd_bn": 26.7,               # ago/2026

    # Contas nacionais, estrutura da despesa. Percentuais derivados dos valores
    # correntes do 1T26 publicados pelo IBGE e usados como shares de partida.
    "consumption_share_pct": 63.20,
    "government_consumption_share_pct": 18.42,
    "investment_share_pct": 16.46,
    "exports_share_pct": 15.99,
    "imports_share_pct": 16.33,
    "inventory_share_pct": 2.26,
    "gross_savings_share_pct": 15.5,             # 1T26
    "depreciation_share_pct": 12.0,              # hipótese didática
    "net_factor_income_abroad_pct_gdp": -1.3,    # hipótese de calibração para PNB/RNB

    # Estrutura produtiva, shares aproximados no VA para exibição/calibração.
    "agriculture_share_va_pct": 8.3,
    "industry_share_va_pct": 22.7,
    "services_share_va_pct": 69.0,
    "productivity_index": 100.0,
    "confidence_index": 100.0,
}

SOURCES = [
    {
        "name": "ENAP - Macroeconomia, Módulo 1: Produto e Renda Nacional",
        "url": "https://repositorio.enap.gov.br/server/api/core/bitstreams/62a51f61-bf5e-42c2-8445-beefee6e8888/content",
        "note": "Base conceitual para Y, C, I, S, G, T, X, M, produto interno/nacional, depreciação e demanda agregada."
    },
    {
        "name": "IBGE - Painel de Indicadores",
        "url": "https://www.ibge.gov.br/indicadores",
        "note": "IPCA, PIB, população e indicadores conjunturais."
    },
    {
        "name": "IBGE - Contas Nacionais Trimestrais",
        "url": "https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/9300-contas-nacionais-trimestrais.html",
        "note": "PIB e componentes da demanda agregada."
    },
    {
        "name": "IBGE - PNAD Contínua",
        "url": "https://www.ibge.gov.br/estatisticas/sociais/trabalho/9171-pesquisa-nacional-por-amostra-de-domicilios-continua-mensal.html",
        "note": "Desemprego e rendimento real."
    },
    {
        "name": "Banco Central do Brasil - Política Monetária",
        "url": "https://www.bcb.gov.br/publicacoes/rpm/202609",
        "note": "Selic e contexto de política monetária."
    },
    {
        "name": "Banco Central do Brasil - Estatísticas fiscais",
        "url": "https://www.bcb.gov.br/estatisticas/estatisticasfiscais",
        "note": "DBGG, DLSP, resultado primário, nominal e juros."
    },
    {
        "name": "Banco Central do Brasil - Setor externo",
        "url": "https://www.bcb.gov.br/estatisticas/estatisticassetorexterno",
        "note": "Conta corrente, reservas, exportações/importações e IDP."
    },
]
