import streamlit as st
from core.engine import ArticleEngine

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Validador Lemos v1.0", layout="centered", page_icon="🧬")

# CSS para barras coloridas e links
st.markdown("""
<style>
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #ff4b4b, #ffa500, #21c354); }
    a { text-decoration: none; color: #007acc; font-weight: bold; }
    .stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO BACKEND ---
@st.cache_resource
def get_engine():
    return ArticleEngine()

engine = get_engine()

# --- SIDEBAR (CONFIGURAÇÃO) ---
with st.sidebar:
    st.header("⚙️ Acesso")
    api_key = st.text_input("API Key Google", type="password")
    
    # LINK PARA GERAR A CHAVE
    st.markdown("👉 [Clique aqui para gerar sua chave (Google AI Studio)](https://aistudio.google.com/app/apikey)")
    
    st.markdown("---")
    st.caption("v1.0 - Lemos Lambda Core")

# --- ÁREA PRINCIPAL ---
st.title("🧬 Validador de Artigos")
st.caption("Análise Técnica de Farmacologia & Biologia Molecular")

uploaded_file = st.file_uploader("Arraste o PDF do Manuscrito", type="pdf")

# Limpa a memória se o usuário trocar o arquivo PDF
if uploaded_file and 'last_file' in st.session_state and st.session_state['last_file'] != uploaded_file.name:
    st.session_state.clear()
    st.session_state['last_file'] = uploaded_file.name

if uploaded_file and api_key:
    # 1. BOTÃO DE ANÁLISE (Salva na memória)
    if st.button("Validar Metodologia", type="primary"):
        engine.configure(api_key)
        with st.spinner("Lendo PDF, analisando estatística e verificando vieses..."):
            st.session_state['analysis_data'] = engine.analyze(uploaded_file)
            st.session_state['last_file'] = uploaded_file.name
        
    # 2. EXIBIÇÃO
    if 'analysis_data' in st.session_state:
        data = st.session_state['analysis_data']
        
        if "error" in data:
            st.error(f"Erro no Processamento: {data['error']}")
            with st.expander("Ver Detalhes do Erro (Debug)", expanded=True):
                st.code(data.get('details', 'Sem detalhes disponíveis'))
        else:
            scores = data['scores']
            
            # --- CÁLCULO ROBUSTO DO SCORE ---
            peso_total = 3 + 3 + 2 + 2
            final_score = (
                scores['rigor_estatistico'] * 3 +
                scores['metodologia'] * 3 +
                scores['plausibilidade_biologica'] * 2 +
                scores['clareza_novidade'] * 2
            ) / peso_total * 10
            final_score = round(final_score, 1)
            
            # Dashboard
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Estatística (x3)", scores['rigor_estatistico'])
            col2.metric("Metodologia (x3)", scores['metodologia'])
            col3.metric("Biologia (x2)", scores['plausibilidade_biologica'])
            col4.metric("Novidade (x2)", scores['clareza_novidade'])
            
            st.write("---")
            
            # Barra de Progresso
            st.subheader(f"Score Técnico: {final_score}%")
            st.progress(int(final_score) / 100)
            
            if final_score >= 80:
                st.success(f"VEREDITO: {data['veredito']}")
            elif final_score >= 50:
                st.warning(f"VEREDITO: {data['veredito']}")
            else:
                st.error(f"VEREDITO: {data['veredito']}")
            
            # Abas
            tab1, tab2 = st.tabs(["📝 Curadoria Técnica", "🧮 Entenda o Cálculo"])
            with tab1:
                st.info(data['justificativa'])
                st.write(data['curadoria'])
            with tab2:
                st.latex(r'''Score = \frac{(Estatística \times 3) + (Metodologia \times 3) + (Biologia \times 2) + (Novidade \times 2)}{10} \times 10''')

            # --- ZONA DE CONFLITO (ATAQUE & DEFESA) ---
            st.markdown("---")
            st.subheader("⚔️ Zona de Conflito")
            st.caption("Simulação de Peer Review: Desafie seus argumentos.")
            
            # Coluna única para o botão de ataque (para centralizar a atenção)
            if st.button("😡 Invocar Revisor #2 (Modo Crítico)"):
                with st.spinner("O revisor está procurando falhas no seu N amostral..."):
                    engine.configure(api_key)
                    texto = data.get("full_text_hidden", "")
                    if texto:
                        # Salva o ataque e LIMPA qualquer defesa anterior (para forçar o pensamento de novo)
                        st.session_state['reviewer_attacks'] = engine.generate_hardcore_review(texto)
                        if 'defense_strategy' in st.session_state:
                            del st.session_state['defense_strategy']
                    else:
                        st.warning("Texto não encontrado.")

            # Mostra o ataque se existir
            if 'reviewer_attacks' in st.session_state:
                st.markdown("### 🔥 Críticas do Revisor:")
                st.error(st.session_state['reviewer_attacks'])
                
                st.markdown("---")
                
                # AQUI ESTÁ A MUDANÇA: Texto que incentiva a reflexão
                st.markdown("### 🛡️ Preparar Resposta")
                st.caption("⚠️ **Desafio:** Tente responder mentalmente às críticas acima primeiro. Use o botão abaixo apenas se estiver bloqueado ou quiser validar sua argumentação.")
                
                # Botão de Defesa (Separado e Opcional)
                if st.button("💡 Consultar 'Advogado de Defesa' (Sugestão de IA)"):
                    with st.spinner("Analisando estratégias para salvar o paper..."):
                        engine.configure(api_key)
                        texto = data.get("full_text_hidden", "")
                        ataques = st.session_state['reviewer_attacks']
                        
                        st.session_state['defense_strategy'] = engine.generate_defense_strategy(texto, ataques)
            
            # Mostra a defesa apenas se o botão foi clicado
            if 'defense_strategy' in st.session_state:
                st.info(st.session_state['defense_strategy'])

elif not api_key:
    st.warning("Insira a API Key na barra lateral para liberar o sistema.")