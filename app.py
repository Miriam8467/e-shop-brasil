import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Conexão com MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['eshop']
colecao = db['pedidos']

st.title("📦 E-Shop Brasil – Gestão de Dados")

# Inserção de dados
with st.form("formulario"):
    nome = st.text_input("Nome do cliente")
    produto = st.text_input("Produto")
    valor = st.number_input("Valor", min_value=0.0)
    submit = st.form_submit_button("Salvar")

    if submit:
        colecao.insert_one({"nome": nome, "produto": produto, "valor": valor})
        st.success("Pedido inserido com sucesso!")

# Exibição de dados
dados = list(colecao.find())
df = pd.DataFrame(dados)
if not df.empty:
    df.drop(columns=["_id"], inplace=True)
    st.dataframe(df)

# Deleção simples
if st.button("🗑️ Apagar todos os dados"):
    colecao.delete_many({})
    st.warning("Todos os dados foram apagados.")
