import streamlit as st
from pymongo import MongoClient
from bson import ObjectId
import pandas as pd

# --- Conexão com MongoDB ---
client = MongoClient("mongodb://localhost:27017")
db = client["e_shop"]
collection = db["produtos"]
fornecedores_col = db["fornecedores"]

st.title("📦 Gerenciador de Produtos - E-Shop Brasil")

# --- Criar dados fictícios na coleção fornecedores (uma vez) ---
if fornecedores_col.count_documents({}) == 0:
    fornecedores_col.insert_many([
        {"categoria": "Eletrônicos", "fornecedor": "TechFast", "email": "contato@techfast.com"},
        {"categoria": "Moda", "fornecedor": "FashionWay", "email": "sac@fashionway.com.br"},
        {"categoria": "Beleza", "fornecedor": "GlowStore", "email": "glow@glowstore.com"},
    ])

# --- INSERIR NOVO PRODUTO ---
st.header("➕ Adicionar Produto")
with st.form(key="form_insercao"):
    nome = st.text_input("Nome do Produto")
    categoria = st.text_input("Categoria")
    preco = st.number_input("Preço", min_value=0.0, format="%.2f")
    quantidade = st.number_input("Quantidade em Estoque", min_value=0, step=1)
    submit = st.form_submit_button("Cadastrar")

    if submit:
        if nome and categoria:
            collection.insert_one({
                "nome": nome,
                "categoria": categoria,
                "preco": preco,
                "quantidade": quantidade
            })
            st.success("✅ Produto cadastrado com sucesso.")
            st.rerun()
        else:
            st.error("❌ Preencha todos os campos obrigatórios.")

# --- LISTAR PRODUTOS ---
st.header("📋 Lista de Produtos")
produtos = list(collection.find())
if produtos:
    for p in produtos:
        st.markdown(f"""
        🔹 **{p['nome']}**
        - Categoria: {p['categoria']}
        - Preço: R$ {p['preco']:.2f}
        - Estoque: {p['quantidade']}
        """)
else:
    st.info("Nenhum produto cadastrado.")

# --- EXCLUIR PRODUTO ---
st.header("🗑️ Excluir Produto")
if produtos:
    mapa_id_nome = {str(p["_id"]): p["nome"] for p in produtos}
    id_excluir = st.selectbox("Selecione um produto para excluir", options=list(mapa_id_nome.keys()), format_func=lambda x: mapa_id_nome[x])
    if st.button("Excluir Produto"):
        collection.delete_one({"_id": ObjectId(id_excluir)})
        st.success("✅ Produto excluído.")
        st.rerun()

# --- EDITAR PRODUTO ---
st.header("✏️ Editar Produto")
if produtos:
    id_editar = st.selectbox("Selecione um produto para editar", options=list(mapa_id_nome.keys()), format_func=lambda x: mapa_id_nome[x], key="editar")
    produto = collection.find_one({"_id": ObjectId(id_editar)})

    with st.form(key="form_edicao"):
        novo_nome = st.text_input("Novo Nome", value=produto["nome"])
        nova_categoria = st.text_input("Nova Categoria", value=produto["categoria"])
        novo_preco = st.number_input("Novo Preço", min_value=0.0, format="%.2f", value=produto["preco"])
        nova_quantidade = st.number_input("Nova Quantidade", min_value=0, step=1, value=produto["quantidade"])
        editar = st.form_submit_button("Salvar Alterações")

        if editar:
            collection.update_one(
                {"_id": ObjectId(id_editar)},
                {"$set": {
                    "nome": novo_nome,
                    "categoria": nova_categoria,
                    "preco": novo_preco,
                    "quantidade": nova_quantidade
                }}
            )
            st.success("✅ Produto atualizado com sucesso.")
            st.rerun()

# --- CONSULTAR PRODUTOS POR NOME ---
st.header("🔍 Consultar Produtos por Nome")
termo = st.text_input("Digite o nome ou parte do nome do produto:", key="busca")
if termo:
    resultados = list(collection.find({"nome": {"$regex": termo, "$options": "i"}}))
    if resultados:
        df_result = pd.DataFrame(resultados)
        st.dataframe(df_result[["nome", "categoria", "preco", "quantidade"]])
    else:
        st.warning("Nenhum produto encontrado com esse nome.")

# --- CONCATENAR PRODUTOS E FORNECEDORES ---
st.header("🔗 Produtos + Fornecedores (Concatenação de Coleções)")
produtos_df = pd.DataFrame(produtos)
fornecedores = list(fornecedores_col.find())
fornecedores_df = pd.DataFrame(fornecedores)

if not produtos_df.empty and not fornecedores_df.empty:
    df_merged = pd.merge(produtos_df, fornecedores_df, on="categoria", how="left")
    df_merged = df_merged[["nome", "categoria", "preco", "quantidade", "fornecedor", "email"]]
    st.dataframe(df_merged)
else:
    st.info("Sem dados suficientes para concatenar coleções.")


