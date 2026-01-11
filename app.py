
import streamlit as st
from services.wordpress_service import get_wordpress_posts
from services.gemini_service import gerar_texto_gemini
from services.prompt_builder import montar_prompt_melivo

st.set_page_config(page_title="Gerador de Artigos IA - Melivo", layout="wide")

st.markdown("""
# 🧠 Gerador de Artigos com IA – Melivo  
Crie artigos sobre ferramentas de Inteligência Artificial seguindo o padrão editorial do seu site.
""")
st.divider()

with st.container():
    st.subheader("🔗 Conectar ao seu WordPress")
    col1, col2 = st.columns([3,1])
    with col1:
        site_url = st.text_input("URL do seu site WordPress", placeholder="https://melivo.com.br")
    with col2:
        qtd = st.number_input("Quantos artigos buscar?", min_value=1, max_value=50, value=10)
    buscar = st.button("📥 Buscar artigos publicados")

posts = []
if buscar:
    if not site_url:
        st.error("Informe a URL do seu site.")
    else:
        with st.spinner("Buscando artigos no WordPress..."):
            posts, error = get_wordpress_posts(site_url, qtd)
        if error:
            st.error(f"Erro ao buscar artigos: {error}")
        else:
            st.success(f"{len(posts)} artigos encontrados!")
            st.subheader("📚 Artigos já publicados")
            for i, post in enumerate(posts, start=1):
                st.markdown(f"""
**{i}. {post['title']}**  
Slug: `{post['slug']}`  
Data: {post['date']}
---
""")

st.divider()
st.header("✍️ Criar novo artigo com IA")

tema = st.text_input("Tema do artigo")
tipo = st.selectbox("Tipo de conteúdo", ["Guia", "Review", "Comparativo", "Artigo explicativo"])
tom = st.selectbox("Tom", ["Educativo", "Profissional", "Casual", "Persuasivo"])
publico = st.text_input("Público-alvo (opcional)")
tamanho = st.selectbox("Tamanho", ["Curto", "Médio", "Longo"])

gerar = st.button("✨ Gerar artigo com IA")

if gerar:
    if not tema:
        st.error("Informe o tema.")
    else:
        with st.spinner("Gerando artigo com Gemini..."):
            prompt = montar_prompt_melivo(tema, tipo, tom, publico, tamanho, posts)
            api_key = st.secrets["GEMINI_API_KEY"]
            resposta = gerar_texto_gemini(prompt, api_key)

        st.success("Artigo gerado!")
        st.subheader("📄 Resultado bruto do Gemini")
        st.text_area("Resposta:", resposta, height=500)

st.divider()
st.caption("Projeto: Gerador de Artigos IA para Melivo • Fase 1")
