import pandas as pd
import numpy as np
import random
import re
from datetime import datetime, timedelta

# ==========================================
# RF01 - Criar ou Carregar o Dataset de Vendas
# ==========================================
def gerar_dataset_vendas(n_registros=200, seed=42):
    """Gera um dataset sintético de vendas com dados sujos."""
    random.seed(seed)
    np.random.seed(seed)
    
    produtos = ["Notebook", "Smartphone", "Tablet", "Monitor", "Teclado", "Mouse", "Headset"]
    categorias = {
        "Notebook": "Computadores", "Smartphone": "Celulares",
        "Tablet": "Celulares", "Monitor": "Computadores",
        "Teclado": "Perifericos", "Mouse": "Perifericos",
        "Headset": "Perifericos"
    }
    precos = {
        "Notebook": 3500, "Smartphone": 2200, "Tablet": 1800,
        "Monitor": 1200, "Teclado": 250, "Mouse": 120, "Headset": 350
    }
    regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
    data_inicio = datetime(2025, 1, 1)
    
    dados = []
    for i in range(n_registros):
        produto = random.choice(produtos)
        categoria = categorias[produto]
        quantidade = random.randint(1, 10)
        preco = round(precos[produto] * random.uniform(0.85, 1.15), 2)
        data = data_inicio + timedelta(days=random.randint(0, 364))
        cliente = f"Cliente_{random.randint(1, 50):03d}"
        data_txt = data.strftime("%Y-%m-%d")
        
        # Sujeira proposital
        if random.random() < 0.05:
            quantidade = None
        if random.random() < 0.04:
            preco = None
        if random.random() < 0.06:
            produto = " " + produto + " "
        if random.random() < 0.03:
            data_txt = "DATA INVALIDA"
        if random.random() < 0.10:
            cliente = random.choice([
                cliente.upper().replace("_", "-"),
                cliente + "!!",
                " " + cliente,
                cliente.replace("Cliente_", "cliente#"),
            ])
            
        dados.append({
            "id_venda": i + 1,
            "data_venda": data_txt,
            "cliente": cliente,
            "produto": produto,
            "categoria": categoria,
            "regiao": random.choice(regioes),
            "quantidade": quantidade,
            "preco_unitario": preco,
        })
        
    return pd.DataFrame(dados)


# ==========================================
# RF02 - Inspecionar e Descrever os Dados
# ==========================================
def inspecionar_dados(df):
    """Exibe as informações estruturais do DataFrame."""
    print("\n=== INSPEÇÃO INICIAL DO DATASET ===")
    print(f"Shape: {df.shape}")
    print(f"\nColunas: {list(df.columns)}")
    print(f"\nTipos de dados:\n{df.dtypes}")
    print(f"\nValores nulos por coluna:\n{df.isnull().sum()}")
    print(f"\nPrimeiros registros:\n{df.head()}")
    return df


# ==========================================
# RF03 - Limpar e Tratar os Dados
# ==========================================
def limpar_dados(df):
    """
    Limpa e trata o DataFrame de vendas.
    Retorna: (df_limpo, relatorio)
    """
    df_limpo = df.copy()
    registros_iniciais = len(df_limpo)
    
    # 1. Espaços extras em colunas de texto
    colunas_texto = ["produto", "categoria", "regiao", "cliente"]
    for col in colunas_texto:
        if col in df_limpo.columns:
            df_limpo[col] = df_limpo[col].astype(str).str.strip()
            
    # 2. Tratar datas inválidas
    df_limpo["data_venda"] = pd.to_datetime(df_limpo["data_venda"], errors="coerce")
    removidos_data = df_limpo["data_venda"].isnull().sum()
    df_limpo = df_limpo.dropna(subset=["data_venda"])
    
    # 3. Remover nulos em quantidade e preço
    removidos_qtd = df_limpo["quantidade"].isnull().sum()
    df_limpo = df_limpo.dropna(subset=["quantidade"])
    
    removidos_preco = df_limpo["preco_unitario"].isnull().sum()
    df_limpo = df_limpo.dropna(subset=["preco_unitario"])
    
    # 4. Ajustar tipos numéricos
    df_limpo["quantidade"] = df_limpo["quantidade"].astype(int)
    df_limpo["preco_unitario"] = df_limpo["preco_unitario"].astype(float)
    
    # 5. Padronizar nomes de clientes com regex
    padrao_cliente = re.compile(r"^Cliente_\d{3}$", flags=re.IGNORECASE)
    
    def padronizar_nome(nome):
        # Remove caracteres indesejados
        limpo = re.sub(r"[^A-Za-z0-9_]", "", str(nome).strip())
        # Tenta extrair os números para recriar o padrão Cliente_NNN
        numeros = re.findall(r"\d+", limpo)
        if numeros:
            num_str = numeros[0].zfill(3)
            return f"Cliente_{num_str}"
        return "Cliente_000"

    df_limpo["cliente"] = df_limpo["cliente"].apply(padronizar_nome)
    
    # Relatório de limpeza
    registros_finais = len(df_limpo)
    relatorio = {
        "registros_iniciais": registros_iniciais,
        "removidos_data_invalida": int(removidos_data),
        "removidos_quantidade_nula": int(removidos_qtd),
        "removidos_preco_nulo": int(removidos_preco),
        "total_removidos": registros_iniciais - registros_finais,
        "registros_finais": registros_finais
    }
    
    print("\n=== RELATÓRIO DE LIMPEZA ===")
    for chave, valor in relatorio.items():
        print(f"{chave}: {valor}")
        
    return df_limpo, relatorio


# Bloco de teste local
if __name__ == "__main__":
    df_bruto = gerar_dataset_vendas()
    df_bruto.to_csv("vendas.csv", index=False)
    inspecionar_dados(df_bruto)
    df_limpo, relatorio = limpar_dados(df_bruto)

# ==========================================
# RF04 - Criar Colunas Derivadas
# ==========================================
def criar_colunas_derivadas(df):
    """Cria colunas calculadas, temporais e faixas condicionais com np.select."""
    df_trans = df.copy()
    
    # Receita total
    df_trans["receita_total"] = df_trans["quantidade"] * df_trans["preco_unitario"]
    
    # Colunas temporais
    df_trans["mes"] = df_trans["data_venda"].dt.month
    
    meses_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    df_trans["mes_nome"] = df_trans["mes"].map(meses_pt)
    df_trans["trimestre"] = "Q" + df_trans["data_venda"].dt.quarter.astype(str)
    df_trans["ano"] = df_trans["data_venda"].dt.year
    
    # Classificação condicional vetorizada com np.select
    condicoes = [
        df_trans["receita_total"] < 500,
        (df_trans["receita_total"] >= 500) & (df_trans["receita_total"] < 5000),
        df_trans["receita_total"] >= 5000
    ]
    faixas = ["Baixo Valor", "Médio Valor", "Alto Valor"]
    df_trans["faixa_receita_item"] = np.select(condicoes, faixas, default="Não Classificado")
    
    return df_trans


# ==========================================
# RF05 - Calcular Métricas Agregadas (groupby)
# ==========================================
def calcular_metricas(df):
    """Calcula métricas agregadas agrupando por mês, produto, categoria e região."""
    metricas = {}
    
    # Por mês
    metricas["por_mes"] = df.groupby(["mes", "mes_nome"]).agg(
        receita_total=("receita_total", "sum"),
        quantidade=("quantidade", "sum"),
        n_vendas=("id_venda", "count")
    ).reset_index().sort_values("mes")
    
    # Top 5 Produtos
    metricas["top_produtos"] = df.groupby("produto").agg(
        receita_total=("receita_total", "sum")
    ).reset_index().sort_values("receita_total", ascending=False).head(5)
    
    # Por Categoria
    metricas["por_categoria"] = df.groupby("categoria").agg(
        receita_total=("receita_total", "sum")
    ).reset_index().sort_values("receita_total", ascending=False)
    
    # Por Região
    metricas["por_regiao"] = df.groupby("regiao").agg(
        receita_total=("receita_total", "sum"),
        ticket_medio=("receita_total", "mean")
    ).reset_index().sort_values("receita_total", ascending=False)
    
    return metricas


# ==========================================
# RF06 - Segmentar Clientes
# ==========================================
def segmentar_clientes(df):
    """Agrupa por cliente, calcula gasto acumulado e segmenta usando lambda."""
    df_clientes = df.groupby("cliente").agg(
        total_gasto=("receita_total", "sum")
    ).reset_index()
    
    # Classificação por faixa acumulada
    classificar = lambda gasto: "Ouro" if gasto > 15000 else ("Prata" if gasto >= 5000 else "Bronze")
    df_clientes["segmento"] = df_clientes["total_gasto"].apply(classificar)
    
    return df_clientes.sort_values("total_gasto", ascending=False)


# ==========================================
# RF07 - Operações Numéricas com NumPy
# ==========================================
def calcular_estatisticas_numpy(df):
    """Aplica operações vetorizadas, broadcasting e agregações via NumPy."""
    receitas = df["receita_total"].to_numpy()
    
    media = np.mean(receitas)
    mediana = np.median(receitas)
    desvio_padrao = np.std(receitas)
    soma_total = np.sum(receitas)
    
    # Escalona os valores (0 a 1) via broadcasting
    min_val = np.min(receitas)
    max_val = np.max(receitas)
    receitas_escalonadas = (receitas - min_val) / (max_val - min_val)
    
    acima_da_media = receitas[receitas > media]
    
    return {
        "media": float(media),
        "mediana": float(mediana),
        "desvio_padrao": float(desvio_padrao),
        "soma_total": float(soma_total),
        "vendas_acima_media_qtd": int(len(acima_da_media)),
        "min_escalonado": float(np.min(receitas_escalonadas)),
        "max_escalonado": float(np.max(receitas_escalonadas))
    }


# Bloco de execução principal atualizado
if __name__ == "__main__":
    df_bruto = gerar_dataset_vendas()
    df_limpo, relatorio = limpar_dados(df_bruto)
    df_trans = criar_colunas_derivadas(df_limpo)
    
    metricas = calcular_metricas(df_trans)
    clientes = segmentar_clientes(df_trans)
    estatisticas_np = calcular_estatisticas_numpy(df_trans)
    
    print("\n=== TOP 5 PRODUTOS ===")
    print(metricas["top_produtos"])
    print("\n=== TOP 5 CLIENTES ===")
    print(clientes.head(5))
    print("\n=== ESTATÍSTICAS NUMPY ===")
    print(estatisticas_np)

if __name__ == "__main__":
    df_bruto = gerar_dataset_vendas()
    df_limpo, relatorio = limpar_dados(df_bruto)
    df_trans = criar_colunas_derivadas(df_limpo)

    import matplotlib.pyplot as plt
import seaborn as sns

# Configuração de estilo geral para os gráficos
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# ==========================================
# RF08 - Tendência Temporal de Vendas
# ==========================================
def plot_tendencia_temporal(df):
    """Gera gráfico de linha com a evolução mensal das vendas."""
    df_mes = df.groupby(["mes", "mes_nome"])["receita_total"].sum().reset_index().sort_values("mes")
    
    plt.figure(figsize=(10, 5))
    ax = sns.lineplot(data=df_mes, x="mes_nome", y="receita_total", marker="o", linewidth=2.5, color="#1f77b4")
    
    plt.title("Evolução Mensal da Receita Total (2025)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Mês", fontsize=11)
    plt.ylabel("Receita (R$)", fontsize=11)
    plt.xticks(rotation=45)
    
    # Anotações dos valores nos pontos
    for _, row in df_mes.iterrows():
        ax.annotate(f"R$ {row['receita_total']:,.0f}",
                    (row["mes_nome"], row["receita_total"]),
                    textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8)
        
    plt.tight_layout()
    plt.savefig("grafico_tendencia_temporal.png", dpi=300)
    plt.close()


# ==========================================
# RF09 - Comparação por Categoria e Região
# ==========================================
def plot_comparacao_categoria_regiao(df):
    """Gera gráficos de barras comparativos por categoria e região."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Vendas por Categoria
    df_cat = df.groupby("categoria")["receita_total"].sum().reset_index().sort_values("receita_total", ascending=False)
    sns.barplot(data=df_cat, x="categoria", y="receita_total", ax=axes[0], palette="Blues_r")
    axes[0].set_title("Receita por Categoria de Produto", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Categoria")
    axes[0].set_ylabel("Receita Total (R$)")
    
    # Vendas por Região
    df_reg = df.groupby("regiao")["receita_total"].sum().reset_index().sort_values("receita_total", ascending=False)
    sns.barplot(data=df_reg, x="regiao", y="receita_total", ax=axes[1], palette="Greens_r")
    axes[1].set_title("Receita por Região geográfica", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Região")
    axes[1].set_ylabel("Receita Total (R$)")
    
    plt.tight_layout()
    plt.savefig("grafico_categoria_regiao.png", dpi=300)
    plt.close()


# ==========================================
# RF10 - Análise de Distribuição e Dispersão
# ==========================================
def plot_distribuicao_dispersao(df):
    """Gera boxplot de preços por categoria e histograma da receita por venda."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Boxplot de Preços por Categoria
    sns.boxplot(data=df, x="categoria", y="preco_unitario", ax=axes[0], palette="Set2")
    axes[0].set_title("Distribuição de Preços Unitários por Categoria", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Categoria")
    axes[0].set_ylabel("Preço Unitário (R$)")
    
    # Histograma da Receita Total por Venda
    sns.histplot(df["receita_total"], kde=True, ax=axes[1], color="#2ca02c", bins=20)
    axes[1].set_title("Distribuição da Receita por Transação", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Receita da Venda (R$)")
    axes[1].set_ylabel("Frequência")
    
    plt.tight_layout()
    plt.savefig("grafico_distribuicao_dispersao.png", dpi=300)
    plt.close()


# ==========================================
# RF11 - Matriz de Correlação (Heatmap)
# ==========================================
def plot_matriz_correlacao(df):
    """Gera mapa de calor com a correlação entre variáveis numéricas."""
    colunas_num = ["quantidade", "preco_unitario", "receita_total"]
    matriz_corr = df[colunas_num].corr()
    
    plt.figure(figsize=(7, 5))
    sns.heatmap(matriz_corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, vmin=-1, vmax=1)
    
    plt.title("Matriz de Correlação das Variáveis Numéricas", fontsize=12, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig("grafico_matriz_correlacao.png", dpi=300)
    plt.close()

    if __name__ == "__main__":
        df_bruto = gerar_dataset_vendas()
        df_limpo, relatorio = limpar_dados(df_bruto)
        df_trans = criar_colunas_derivadas(df_limpo)

        plot_tendencia_temporal(df_trans)
        plot_comparacao_categoria_regiao(df_trans)

       