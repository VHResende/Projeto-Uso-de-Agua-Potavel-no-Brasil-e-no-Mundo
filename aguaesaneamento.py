import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

# Configuração do Streamlit
st.set_page_config(page_title="Análise do Uso de Água Potável", layout="wide")
st.title("Análise do Uso de Água Potável no Mundo")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Carregue o arquivo CSV", type=["csv"])

if uploaded_file is not None:
    # Carregar os dados
    df = pd.read_csv(uploaded_file)
    
    # Renomear colunas para português
    df.columns = ["País", "Ano", "Uso_Água_Potável"]
    
    # Converter a coluna "Ano" para inteiro
    df["Ano"] = df["Ano"].astype(int)

    # Substituir "Brazil" por "Brasil" para manter o idioma consistente
    df["País"] = df["País"].replace("Brazil", "Brasil")

    # Listar os países presentes no dataset
    paises = df["País"].unique()

    # Criar filtro interativo para seleção de países
    paises_selecionados = st.multiselect(
        "Selecione os países para visualizar:",
        paises,
        default=["Brasil"],  
    )

    if paises_selecionados:
        df_filtrado = df[df["País"].isin(paises_selecionados)]
        fig = px.line(df_filtrado, x="Ano", y="Uso_Água_Potável", color="País",
                      title="Evolução do Uso de Água Potável por País",
                      labels={"Uso_Água_Potável": "% da População com Acesso"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Selecione pelo menos um país para visualizar o gráfico.")
    
    # Exibir tabelas lado a lado
    st.subheader("Dados Históricos dos Países Selecionados")
    colunas = st.columns(len(paises_selecionados))  

    for i, pais in enumerate(paises_selecionados):
        df_pais = df[df["País"] == pais]
        with colunas[i]:
            st.write(f"**{pais}**")
            st.write(df_pais)

    # Seleção do ano da projeção
    ano_maximo = df["Ano"].max()
    ano_projecao = st.slider("Escolha o ano para projeção:", min_value=ano_maximo+1, max_value=2100, value=2050, step=1)

    # Projeção de tendência com regressão linear
    st.subheader("Projeção da Evolução do Uso de Água Potável")
    projecoes = {}

    for pais in paises_selecionados:
        df_pais = df[df["País"] == pais]
        
        if df_pais.shape[0] > 1:  
            X = df_pais["Ano"].values.reshape(-1, 1)
            y = df_pais["Uso_Água_Potável"].values.reshape(-1, 1)

            modelo = LinearRegression()
            modelo.fit(X, y)

            anos_previstos = np.arange(df_pais["Ano"].min(), ano_projecao + 1).reshape(-1, 1)
            previsoes = modelo.predict(anos_previstos)

            df_projecao = pd.DataFrame({"Ano": anos_previstos.flatten(), "Uso_Água_Potável": previsoes.flatten()})
            df_projecao["País"] = pais
            projecoes[pais] = df_projecao  # Armazena para exibição posterior

            fig_proj = px.line(df_projecao, x="Ano", y="Uso_Água_Potável", title=f"Projeção para {pais}",
                               labels={"Uso_Água_Potável": "% da População com Acesso"})
            fig_proj.add_scatter(x=df_pais["Ano"], y=df_pais["Uso_Água_Potável"], mode="markers", name="Dados Reais")
            st.plotly_chart(fig_proj, use_container_width=True)

    # Tabelas de projeção lado a lado
    st.subheader("Tabelas de Projeção dos Países Selecionados")
    colunas_proj = st.columns(len(paises_selecionados))  

    for i, pais in enumerate(paises_selecionados):
        with colunas_proj[i]:
            st.write(f"**{pais} - Projeção**")
            st.write(projecoes[pais])

    # Comparação de propensão à água potável no ano escolhido
    st.subheader(f"Comparação das Projeções:")
    df_ano_projecao = pd.DataFrame({
        "País": paises_selecionados,
        f"Projeção_{ano_projecao}": [projecoes[pais].query(f"Ano == {ano_projecao}")["Uso_Água_Potável"].values[0] for pais in paises_selecionados]
    })

    fig_comp = px.bar(df_ano_projecao, x="País", y=f"Projeção_{ano_projecao}", 
                      title=f"Comparação do Percentual de População com Acesso à Água Potável em {ano_projecao}",
                      labels={f"Projeção_{ano_projecao}": "% da População com Acesso"},
                      color="País")

    st.plotly_chart(fig_comp, use_container_width=True)

# Assinatura no final
st.markdown("---")
st.markdown("📊 **by Victor Resende**")
