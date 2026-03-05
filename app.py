import streamlit as st
from core.engine import ArticleEngine

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Validador Lemos v1.1", layout="centered", page_icon="🧬")

st.markdown("""
<style>
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #ff4b4b, #ffa500, #21c354); }
    a { text-decoration: none; color: #007acc; font-weight: bold; }
    .stButton>button { width: 100%; }
    .journal-card {
        border-radius: 8px;
        padding: 16px;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO BACKEND ---
@st.cache_resource
def get_engine():
    return ArticleEngine()

engine = get_engine()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Acesso")
    api_key = st.text_input("API Key Google", type="password")
    st.markdown("👉 [Gerar chave no Google AI Studio](https://aistudio.google.com/app/apikey)")
    st.markdown("---")
    st.caption("v1.1 - Lemos Lambda Core")

# --- ÁREA PRINCIPAL ---
st.title("🧬 Validador de Artigos")
st.caption("Análise Técnica de Farmacologia & Biologia Molecular")

uploaded_file = st.file_uploader("Arraste o PDF do Manuscrito", type="pdf")

# Limpa memória se o usuário trocar o PDF
if uploaded_file and 'last_file' in st.session_state and st.session_state['last_file'] != uploaded_file.name:
    st.session_state.clear()
    st.session_state['last_file'] = uploaded_file.name

if uploaded_file and api_key:

    # --- CAMPO DE REVISTA (OPCIONAL) ---
    st.markdown("#### 🎯 Avaliação por Revista (opcional)")
    journal_name = st.text_input(
        "Nome da revista-alvo",
        placeholder="Ex: Journal of Urology, Nature Neuroscience, PLOS ONE...",
        help="Deixe em branco para pular esta análise. O sistema avalia compatibilidade temática, rigor e escopo."
    )

    # Botão de análise
    if st.button("Validar Metodologia", type="primary"):
        engine.configure(api_key)
        with st.spinner("Lendo PDF, analisando estatística e verificando vieses..."):
            st.session_state['analysis_data'] = engine.analyze(uploaded_file, journal_name=journal_name)
            st.session_state['last_file'] = uploaded_file.name

    # Exibição dos resultados
    if 'analysis_data' in st.session_state:
        data = st.session_state['analysis_data']

        if "error" in data:
            st.error(f"Erro no Processamento: {data['error']}")
            with st.expander("Ver Detalhes do Erro (Debug)", expanded=True):
                st.code(data.get('details', 'Sem detalhes disponíveis'))
        else:
            scores = data['scores']

            # --- SCORE PONDERADO ---
            peso_total = 3 + 3 + 2 + 2
            final_score = (
                scores['rigor_estatistico'] * 3 +
                scores['metodologia'] * 3 +
                scores['plausibilidade_biologica'] * 2 +
                scores['clareza_novidade'] * 2
            ) / peso_total * 10
            final_score = round(final_score, 1)

            # Dashboard de métricas
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Estatística (x3)", scores['rigor_estatistico'])
            col2.metric("Metodologia (x3)", scores['metodologia'])
            col3.metric("Biologia (x2)", scores['plausibilidade_biologica'])
            col4.metric("Novidade (x2)", scores['clareza_novidade'])

            st.write("---")

            # Barra de progresso
            st.subheader(f"Score Técnico: {final_score}%")
            st.progress(int(final_score) / 100)

            if final_score >= 80:
                st.success(f"VEREDITO: {data['veredito']}")
            elif final_score >= 50:
                st.warning(f"VEREDITO: {data['veredito']}")
            else:
                st.error(f"VEREDITO: {data['veredito']}")

            # Abas principais
            tab1, tab2 = st.tabs(["📝 Curadoria Técnica", "🧮 Entenda o Cálculo"])
            with tab1:
                st.info(data['justificativa'])
                st.write(data['curadoria'])
            with tab2:
                st.latex(r'''Score = \frac{(Estatística \times 3) + (Metodologia \times 3) + (Biologia \times 2) + (Novidade \times 2)}{10} \times 10''')

            # --- BLOCO DE COMPATIBILIDADE COM REVISTA ---
            if "journal_analysis" in data:
                ja = data["journal_analysis"]
                compat_score = ja.get("compatibility_score", 0)
                verdict = ja.get("compatibility_verdict", "")
                justif = ja.get("compatibility_justificativa", "")
                journal = ja.get("journal_name", "")

                st.markdown("---")
                st.subheader(f"📰 Compatibilidade com a Revista")

                col_j1, col_j2 = st.columns([2, 1])
                with col_j1:
                    st.markdown(f"**Revista:** {journal}")
                    st.markdown(f"**Veredito:** `{verdict}`")
                    st.caption(justif)
                with col_j2:
                    st.metric("Score de Fit", f"{compat_score}/10")
                    st.progress(compat_score / 10)

                # Cor do alerta baseada no score
                if compat_score >= 8:
                    st.success("✅ Excelente escolha de revista para este manuscrito.")
                elif compat_score >= 6:
                    st.info("🔵 Boa compatibilidade. Pequenos ajustes de enquadramento podem ajudar.")
                elif compat_score >= 4:
                    st.warning("⚠️ Compatibilidade marginal. Considere revistas alternativas.")
                else:
                    st.error("❌ Baixa compatibilidade. Este artigo provavelmente será desk-rejected.")

            # --- ZONA DE CONFLITO ---
            st.markdown("---")
            st.subheader("⚔️ Zona de Conflito")
            st.caption("Simulação de Peer Review: Desafie seus argumentos.")

            if st.button("😡 Invocar Revisor #2 (Modo Crítico)"):
                with st.spinner("O revisor está procurando falhas no seu N amostral..."):
                    engine.configure(api_key)
                    texto = data.get("full_text_hidden", "")
                    if texto:
                        st.session_state['reviewer_attacks'] = engine.generate_hardcore_review(texto)
                        if 'defense_strategy' in st.session_state:
                            del st.session_state['defense_strategy']
                    else:
                        st.warning("Texto não encontrado.")

            if 'reviewer_attacks' in st.session_state:
                st.markdown("### 🔥 Críticas do Revisor:")
                st.error(st.session_state['reviewer_attacks'])
                st.markdown("---")
                st.markdown("### 🛡️ Preparar Resposta")
                st.caption("⚠️ **Desafio:** Tente responder mentalmente às críticas acima primeiro. Use o botão abaixo apenas se estiver bloqueado ou quiser validar sua argumentação.")

                if st.button("💡 Consultar 'Advogado de Defesa' (Sugestão de IA)"):
                    with st.spinner("Analisando estratégias para salvar o paper..."):
                        engine.configure(api_key)
                        texto = data.get("full_text_hidden", "")
                        ataques = st.session_state['reviewer_attacks']
                        st.session_state['defense_strategy'] = engine.generate_defense_strategy(texto, ataques)

            if 'defense_strategy' in st.session_state:
                st.info(st.session_state['defense_strategy'])

elif not api_key:
    st.warning("Insira a API Key na barra lateral para liberar o sistema.")
