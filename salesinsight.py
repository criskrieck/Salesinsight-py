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