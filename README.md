# Presidente do Brasil - Simulador Macroeconômico em Flask

Versão focada apenas na simulação "O Presidente da República", reconstruída como um simulador macroeconômico moderno em Python 3 + Flask.

## Escopo

O núcleo contábil segue a estrutura didática de macroeconomia da ENAP:

- Produto, renda e despesa agregada.
- Identidade `Y = C + I + G + X - M + ΔEstoques`.
- Consumo, investimento, poupança, gastos do governo e tributos.
- Economia aberta, exportações, importações e exportações líquidas.
- Produto interno, produto nacional, depreciação, produto bruto e líquido.
- Produto a preços de mercado e aproximação a custo de fatores.

A simulação adiciona inflação, desemprego, Selic, câmbio, dívida pública, resultado fiscal, conta corrente, reservas, produtividade, confiança, renda real, salário mínimo e índices sintéticos de governabilidade.

## Importante sobre o modelo

As identidades contábeis são preservadas. As relações causais usadas para projetar o trimestre seguinte são hipóteses didáticas parametrizadas, não previsões econométricas oficiais. Os coeficientes ficam explícitos em `domain/engine.py` para permitir recalibração futura com regressões, VAR, DSGE ou séries temporais.

## Baseline real

`data/brazil_2026.py` guarda as sementes observadas e o vintage de referência. Como IBGE, BCB e Tesouro publicam indicadores em frequências e datas distintas, o baseline combina os dados mais recentes disponíveis até 07/10/2026, sem fingir que todos são simultâneos.

Principais sementes:

- PIB trimestral 2T26: R$ 3.425,7 bilhões.
- Crescimento do PIB 2T26: 0,5% t/t e 2,0% a/a.
- IPCA 12 meses ago/2026: 4,22%.
- Desemprego jun-jul-ago/2026: 5,3%.
- Rendimento médio real: R$ 3.777.
- População estimada 01/07/2026: 214.211.951.
- Selic desde 17/09/2026: 13,75% a.a.
- Salário mínimo 2026: R$ 1.621.
- DBGG jul/2026: 82,5% do PIB.
- DLSP jul/2026: 69,1% do PIB.
- Conta corrente 12m até ago/2026: -2,47% do PIB.
- Reservas internacionais ago/2026: US$ 372,6 bilhões.

## Execução

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abra `http://localhost:5000`.

## Docker / EasyPanel

```bash
docker build -t presidente-macro .
docker run --rm -p 5000:5000 -e SECRET_KEY='troque' presidente-macro
```

No EasyPanel exponha a porta 5000.

## API

- `GET /api/state`
- `POST /api/advance`
- `POST /api/reset`

Exemplo:

```bash
curl -X POST http://localhost:5000/api/advance \
  -H 'Content-Type: application/json' \
  -d '{"government_consumption_growth_pct":2,"public_investment_delta_pct_gdp":0.3,"selic_pct_aa":13.75}'
```

## Testes

```bash
pytest -q
```

## Fontes

- ENAP: https://repositorio.enap.gov.br/server/api/core/bitstreams/62a51f61-bf5e-42c2-8445-beefee6e8888/content
- IBGE Indicadores: https://www.ibge.gov.br/indicadores
- IBGE Contas Nacionais: https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/9300-contas-nacionais-trimestrais.html
- IBGE PNAD Contínua: https://www.ibge.gov.br/estatisticas/sociais/trabalho/9171-pesquisa-nacional-por-amostra-de-domicilios-continua-mensal.html
- BCB Política Monetária: https://www.bcb.gov.br/publicacoes/rpm/202609
- BCB Estatísticas Fiscais: https://www.bcb.gov.br/estatisticas/estatisticasfiscais
- BCB Setor Externo: https://www.bcb.gov.br/estatisticas/estatisticassetorexterno

## Controles por sliders

As 12 principais decisões e hipóteses macroeconômicas são apresentadas como sliders, sem campo de digitação livre. O valor atual aparece ao lado do nome da variável e os limites mínimo e máximo ficam visíveis abaixo de cada controle. As mesmas faixas são validadas no backend em `domain/engine.py`, reduzindo o risco de envio manual de valores fora do intervalo didático.

Faixas adotadas por trimestre/cenário: consumo do governo -10% a +10%; investimento público -1,0 a +1,0 p.p. do PIB; carga tributária -2,0 a +2,0 p.p.; transferências -10% a +15%; salário mínimo -5% a +15%; Selic 2% a 20% a.a.; intervenção cambial -US$20 bi a +US$20 bi; produtividade -0,5% a +1,0% no trimestre; confiança -10 a +10 pontos; crescimento mundial -2% a +6% a.a.; commodities -20% a +20%; prêmio de risco -15 a +15 pontos.


## Histórico e comparação entre períodos

- Legenda colorida visível para as quatro séries do gráfico: PIB t/t, IPCA 12m, desemprego e dívida/PIB.
- Tabela abaixo do gráfico com todos os períodos armazenados no histórico.
- Para cada indicador, a tabela apresenta o valor do período e a variação percentual relativa ao período imediatamente anterior.
- Variações positivas aparecem em verde, negativas em vermelho e zero em tom neutro.
