# -*- coding: utf-8 -*-
import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime, timedelta
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="AzureGen.Obras - Davi", page_icon="🏗️", layout="wide")

# --- LÓGICA DE LOGIN (MANTIDA) ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    def password_entered():
        if (st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]):
            st.session_state.password_correct = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.error("Senha incorreta")

    if not st.session_state.password_correct:
        st.markdown("### 🏗️ AzureGen.Obras Login")
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password", on_change=password_entered)
        return False
    return True

# --- INICIALIZAÇÃO DE DADOS (SESSION STATE) ---
if "prospects" not in st.session_state:
    st.session_state.prospects = [] 
if "projects" not in st.session_state:
    st.session_state.projects = []  
if "budget_items" not in st.session_state:
    st.session_state.budget_items = {} 
if "team_members" not in st.session_state:
    st.session_state.team_members = [] 
if "ai_schedules" not in st.session_state:
    st.session_state.ai_schedules = {} 

# --- FUNÇÕES DE IA ---
def generate_smart_schedule(project_name, items):
    """Envia os itens para o Gemini criar um cronograma."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Atue como um Engenheiro Civil Sênior. Vou te passar os itens de um orçamento de obra e você vai gerar um cronograma lógico de execução.
    
    OBRA: {project_name}
    ITENS: {items}
    
    SAÍDA ESPERADA: Apenas um JSON (sem markdown) com uma lista de tarefas.
    Formato: [{{ "fase": "Nome da Fase", "tarefa": "Descrição", "dias": numero_dias, "dependencia": "tarefa anterior ou null" }}]
    """
    
    try:
        with st.spinner('🤖 Gen Obras AI está calculando o cronograma ideal...'):
            response = model.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "")
            return json.loads(text)
    except Exception as e:
        st.error(f"Erro na IA: {e}")
        return []

def analyze_team_productivity(team_data):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Analise esta equipe de obra e sugira melhorias de produtividade ou cortes: {team_data}"
    response = model.generate_content(prompt)
    return response.text

# --- APP PRINCIPAL ---
if check_password():
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

    with st.sidebar:
        st.title("AzureGen.Obras 4.0")
        st.write(f"Bem-vindo, Davi")
        menu = st.radio("Navegação", ["Novo Orçamento", "Obras & Cronogramas", "Gestão de Equipes", "Assistente IA"])
        st.divider()
        st.caption("Sistema Inteligente de Construção")

    if menu == "Novo Orçamento":
        st.header("📝 Criar Prospecção / Orçamento")
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("Nome do Cliente")
            project_name = st.text_input("Nome da Obra/Reforma")
        with col2:
            address = st.text_input("Endereço")
            date = st.date_input("Data", datetime.now())

        st.subheader("Itens do Orçamento")
        st.info("Adicione os itens abaixo (Ex: 50 sacos de cimento, 100m² de piso)")

        df_template = pd.DataFrame(columns=["Descrição", "Qtd", "Unidade", "Preço Unit."])
        edited_df = st.data_editor(df_template, num_rows="dynamic", use_container_width=True)

        if st.button("Salvar Orçamento e Gerar Cronograma IA"):
            prospect_id = f"{client_name}-{datetime.now().strftime('%H%M%S')}"
            new_prospect = {
                "id": prospect_id,
                "client": client_name,
                "project": project_name,
                "address": address,
                "status": "Em Negociação",
                "total": (edited_df["Qtd"].astype(float) * edited_df["Preço Unit."].astype(float)).sum()
            }
            st.session_state.prospects.append(new_prospect)
            st.session_state.budget_items[prospect_id] = edited_df.to_dict('records')
            
            items_str = edited_df.to_json()
            schedule = generate_smart_schedule(project_name, items_str)
            st.session_state.ai_schedules[prospect_id] = schedule
            
            st.success(f"Orçamento salvo! Cronograma gerado com {len(schedule)} etapas.")

    elif menu == "Obras & Cronogramas":
        st.header("🏗️ Gestão de Obras")
        tab1, tab2 = st.tabs(["Em Negociação", "Obras Ativas"])
        
        with tab1:
            if not st.session_state.prospects:
                st.info("Nenhum orçamento cadastrado.")
            for p in st.session_state.prospects:
                if p['status'] == "Em Negociação":
                    with st.expander(f"📄 {p['project']} - {p['client']} (R$ {p['total']:.2f})"):
                        st.write(f"**Endereço:** {p['address']}")
                        if p['id'] in st.session_state.ai_schedules:
                            st.subheader("📅 Sugestão de Cronograma (IA)")
                            schedule_df = pd.DataFrame(st.session_state.ai_schedules[p['id']])
                            st.table(schedule_df)
                        if st.button(f"✅ Aprovar e Iniciar Obra", key=f"btn_{p['id']}"):
                            p['status'] = "Em Andamento"
                            st.session_state.projects.append(p)
                            st.rerun()

        with tab2:
            if not st.session_state.projects:
                st.warning("Nenhuma obra ativa no momento.")
            for proj in st.session_state.projects:
                with st.expander(f"🏗️ {proj['project']} (Em Andamento)", expanded=True):
                    col_a, col_b = st.columns(2)
                    col_a.metric("Status", "Ativo")
                    col_b.metric("Valor Total", f"R$ {proj['total']:.2f}")
                    st.subheader("Acompanhamento")
                    if proj['id'] in st.session_state.ai_schedules:
                        tasks = st.session_state.ai_schedules[proj['id']]
                        for task in tasks:
                            st.checkbox(f"{task.get('tarefa')} ({task.get('dias')} dias)", key=f"{proj['id']}_{task.get('tarefa')}")

    elif menu == "Gestão de Equipes":
        st.header("👷 Gen Equipes AI")
        with st.form("add_worker"):
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("Nome")
            role = c2.selectbox("Função", ["Pedreiro", "Servente", "Pintor", "Mestre", "Eletricista"])
            daily_rate = c3.number_input("Diária (R$)", min_value=0.0)
            if st.form_submit_button("Adicionar Funcionário"):
                st.session_state.team_members.append({"name": name, "role": role, "rate": daily_rate, "active": True})
                st.success("Adicionado!")
        
        if st.session_state.team_members:
            st.subheader("Equipe Ativa")
            df_team = pd.DataFrame(st.session_state.team_members)
            st.dataframe(df_team, use_container_width=True)
            if st.button("🤖 Analisar Custo/Produtividade com IA"):
                analysis = analyze_team_productivity(st.session_state.team_members)
                st.write(analysis)
        else:
            st.info("Cadastre sua equipe acima.")

    elif menu == "Assistente IA":
        st.header("🤖 Consultor da Construtora")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        for msg in st.session_state.chat_history:
            st.chat_message(msg["role"]).write(msg["content"])
        prompt = st.chat_input("Pergunte algo...")
        if prompt:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            contexto = f"Obras atuais: {st.session_state.projects}. Equipe: {st.session_state.team_members}."
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"Contexto: {contexto}. Pergunta do Davi: {prompt}")
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
            st.chat_message("assistant").write(response.text)
