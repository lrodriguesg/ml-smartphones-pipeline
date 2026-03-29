import streamlit as st
import pandas as pd
import psycopg2
import os
import plotly.express as px
from dotenv import load_dotenv

# Carrega as senhas do arquivo .env
load_dotenv()

st.set_page_config(page_title="Dashboard ML - Smartphones", layout="wide")
st.title("Inteligência de Preços - Smartphones ML")
st.markdown("Análise competitiva baseada em dados coletados da API do Mercado Livre.")

# ----------------------------------------------------
# 1. Conexão e Carga de Dados
# ----------------------------------------------------
@st.cache_data
def load_data(query):
    conn = psycopg2.connect(
        host="localhost",
        port=os.environ.get("POSTGRES_PORT", "5432"),
        dbname=os.environ.get("POSTGRES_DB", "ecommerce_dw"),
        user=os.environ.get("POSTGRES_USER", "admin"),
        password=os.environ.get("POSTGRES_PASSWORD", "teste123")
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df

try:
    df_fct = load_data("SELECT * FROM marts.fct_products;")
    df_dim = load_data("SELECT * FROM marts.dim_sellers;")
except Exception as e:
    st.error(f"Erro de conexão com o banco: {e}")
    st.stop()

# Criando abas para organizar as 10 perguntas
tab1, tab2, tab3 = st.tabs(["💰 Preços e Distribuição (Q1, Q5, Q9)", "📦 Frete e Condição (Q2, Q6, Q8)", "🤝 Vendedores e Descontos (Q3, Q4, Q7, Q10)"])

# ==========================================
# ABA 1: PREÇOS E DISTRIBUIÇÃO
# ==========================================
with tab1:
    # Q1: Preço médio, mínimo e máximo
    st.subheader("Q1. Métricas Gerais de Preço")
    col1, col2, col3 = st.columns(3)
    col1.metric("Preço Médio", f"R$ {df_fct['current_price'].mean():,.2f}")
    col2.metric("Preço Mínimo", f"R$ {df_fct['current_price'].min():,.2f}")
    col3.metric("Preço Máximo", f"R$ {df_fct['current_price'].max():,.2f}")

    st.divider()

    col_a, col_b = st.columns(2)
    # Q9: Histograma em faixas de R$ 500
    with col_a:
        st.subheader("Q9. Concentração de Preços (Faixas de R$ 500)")
        fig9 = px.histogram(df_fct, x="current_price", 
                            title="Distribuição de Produtos por Preço",
                            labels={'current_price': 'Preço (R$)'})
        fig9.update_traces(xbins=dict(start=0, end=df_fct['current_price'].max(), size=500))
        st.plotly_chart(fig9, use_container_width=True)

    # Q5: Evolução do preço médio
    with col_b:
        st.subheader("Q5. Evolução do Preço Médio")
        df_trend = df_fct.groupby(df_fct['collected_at'].dt.date)['current_price'].mean().reset_index()
        fig5 = px.line(df_trend, x="collected_at", y="current_price", markers=True,
                       title="Preço Médio por Dia de Coleta",
                       labels={'current_price': 'Preço Médio (R$)', 'collected_at': 'Data'})
        st.plotly_chart(fig5, use_container_width=True)


# ==========================================
# ABA 2: FRETE E CONDIÇÃO
# ==========================================
with tab2:
    col_c, col_d = st.columns(2)
    
    # Q2: Proporção de Frete Grátis e Variação por Condição
    with col_c:
        st.subheader("Q2. Frete Grátis vs Condição")
        df_fct['Tem Frete Grátis?'] = df_fct['free_shipping'].replace({True: 'Sim', False: 'Não'})
        fig2 = px.histogram(df_fct, x="condition", color="Tem Frete Grátis?", barmode="group",
                            title="Proporção de Frete Grátis (Novo vs Usado)",
                            labels={'condition': 'Condição'})
        st.plotly_chart(fig2, use_container_width=True)

    # Q6: Distribuição por Condição e Ticket Médio
    with col_d:
        st.subheader("Q6. Ticket Médio por Condição")
        df_cond = df_fct.groupby('condition').agg(
            Quantidade=('product_id', 'count'),
            Ticket_Medio=('current_price', 'mean')
        ).reset_index()
        fig6 = px.bar(df_cond, x="condition", y="Ticket_Medio", text_auto='.2f',
                      title="Ticket Médio: Novo vs Usado",
                      labels={'condition': 'Condição', 'Ticket_Medio': 'Ticket Médio (R$)'})
        st.plotly_chart(fig6, use_container_width=True)

    st.divider()

    # Q8: Frete Grátis vs Preço Médio
    st.subheader("Q8. Impacto do Frete Grátis no Preço")
    df_frete = df_fct.groupby('Tem Frete Grátis?')['current_price'].mean().reset_index()
    fig8 = px.bar(df_frete, x="Tem Frete Grátis?", y="current_price", text_auto='.2f', color="Tem Frete Grátis?",
                  title="Preço Médio dos Produtos: Com Frete vs Sem Frete")
    st.plotly_chart(fig8, use_container_width=True)


# ==========================================
# ABA 3: VENDEDORES E DESCONTOS
# ==========================================
with tab3:
    col_e, col_f = st.columns(2)

    # Q3: Top 10 Vendedores por volume
    with col_e:
        st.subheader("Q3. Top 10 Vendedores em Volume")
        top10 = df_dim.nlargest(10, 'lifetime_sold_quantity')
        top10['seller_id'] = top10['seller_id'].astype(str)
        fig3 = px.bar(top10, x="seller_id", y="lifetime_sold_quantity",
                      title="Vendedores com Maior Volume de Vendas",
                      labels={'seller_id': 'Vendedor ID', 'lifetime_sold_quantity': 'Unidades Vendidas'})
        st.plotly_chart(fig3, use_container_width=True)

    # Q4: Correlação Desconto vs Quantidade Vendida
    with col_f:
        st.subheader("Q4. Desconto vs Volume Vendido")
        fig4 = px.scatter(df_fct[df_fct['sold_quantity'] > 0], 
                          x="discount_percentage", y="sold_quantity", 
                          title="Relação: % de Desconto vs Vendas",
                          labels={'discount_percentage': 'Desconto (%)', 'sold_quantity': 'Vendas'},
                          color="discount_category")
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()
    col_g, col_h = st.columns(2)

    # Q10: Equilíbrio Preço Competitivo vs Volume (Vendedores)
    with col_g:
        st.subheader("Q10. Preço vs Volume (Por Vendedor)")
        # Cruzando dimensão de vendedores com a média de preço da Fato
        df_seller_price = df_fct.groupby('seller_id')['current_price'].mean().reset_index()
        df_q10 = pd.merge(df_dim, df_seller_price, on='seller_id')
        df_q10['seller_id'] = df_q10['seller_id'].astype(str)
        fig10 = px.scatter(df_q10, x="current_price", y="lifetime_sold_quantity", hover_name="seller_id",
                           title="Análise de Competitividade dos Vendedores",
                           labels={'current_price': 'Preço Médio Praticado (R$)', 'lifetime_sold_quantity': 'Volume Total Vendido'})
        st.plotly_chart(fig10, use_container_width=True)

    # Q7: Produtos com maior variação de preço
    with col_h:
        st.subheader("Q7. Maior Variação de Preço (Desconto)")
        st.markdown("*Nota técnica: Como a arquitetura utiliza idempotência (SCD Tipo 1) para otimizar armazenamento, a variação exibida é baseada no preço original (cortado) vs preço atual.*")
        df_fct['variacao_absoluta'] = df_fct['original_price'] - df_fct['current_price']
        top_variacao = df_fct[df_fct['variacao_absoluta'] > 0].nlargest(5, 'variacao_absoluta')
        st.dataframe(top_variacao[['product_id', 'title', 'original_price', 'current_price', 'variacao_absoluta']], hide_index=True)