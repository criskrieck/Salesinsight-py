# Relatório Executivo de Análise de Vendas — SalesInsight

## 1. Visão Geral do Projeto
O objetivo do projeto **SalesInsight** é processar, tratar e analisar o histórico de vendas de eletrônicos e periféricos para extrair métricas de desempenho e apoiar a tomada de decisões estratégicas de negócios.

---

## 2. Metodologia de Limpeza e Tratamento de Dados
Durante a etapa de saneamento, foram identificadas inconsistências de formatação, valores nulos e erros de digitação nos registros originais.

* **Remoção de Nulos:** Registros com quantidade ou preço inconsistentes/ausentes foram descartados para manter a integridade dos cálculos.
* **Tratamento de Datas:** Strings inválidas no campo de data foram convertidas via `pd.to_datetime` com `errors='coerce'` e tratadas.
* **Padronização de Clientes:** Utilização de Expressões Regulares (Regex) para identificar padrões como `cliente#001` ou `CLIENTE-001!!` e padronizá-los no formato estrito `Cliente_XXX`.

---

## 3. Principais Insights e Indicadores de Desempenho

### 📊 Desempenho por Categoria e Produto
* As categorias de **Computadores** e **Celulares** lideram o volume de faturamento total, impulsionadas pelo valor ticket unitário elevado de Notebooks e Smartphones.
* Periféricos apresentam alto volume de transações, sendo ideais para estratégias de venda casada (*cross-selling*).

### 🌍 Distribuição Regional
* A região **Sudeste** se mantém como a principal geradora de receita, enquanto regiões como **Norte** e **Centro-Oeste** apresentam oportunidades para expansão e campanhas direcionadas.

### 👑 Segmentação de Clientes
* **Clientes Ouro (> R$ 15.000):** Representam a fatia mais valiosa da carteira, demandando estratégias de fidelização e atendimento exclusivo[cite: 1].
* **Clientes Prata (R$ 5.000 - R$ 15.000) e Bronze (< R$ 5.000):** Têm potencial de migração de faixa através de cupons de incentivo para compras recorrentes[cite: 1].

---

## 4. Recomendações Estratégicas
1. **Estoque e Logística:** Garantir estoque prioritário para os produtos Top 5 e otimizar prazos de entrega para a região Sudeste[cite: 1].
2. **Campanhas Comerciais:** Promover pacotes de Periféricos com descontos na compra conjunta de Computadores[cite: 1].
3. **Programa de Fidelidade:** Lançar incentivos direcionados para clientes nas faixas Prata e Bronze a fim de elevar o ticket médio geral[cite: 1].