import os
import urllib.parse
from datetime import date, datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
from supabase import Client, create_client

from config import APP_NAME, LOGIN_USER, LOGIN_PASSWORD

# =========================
# (Opcional) Google Sheets
# =========================


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="💜")

# =========================================================
# SUPABASE
# =========================================================
@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

sb = get_supabase()
try:
    import gspread
    from google.oauth2.service_account import Credentials
    HAS_SHEETS = False
except Exception:
    HAS_SHEETS = False

# =========================================================
# PALETA
# =========================================================
C_BG = "#0B0B10"
C_TEXT = "rgba(255,255,255,0.92)"
C_MUTED = "rgba(255,255,255,0.70)"
C_SURFACE = "rgba(255,255,255,0.055)"
C_SURFACE_2 = "rgba(255,255,255,0.035)"
C_PURPLE_1 = "#4A00E0"
C_PURPLE_2 = "#8E2DE2"
C_GOLD = "#D4AF37"
C_GOLD_SOFT = "rgba(212,175,55,0.22)"
C_WHITE = "#FFFFFF"

MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

STATUS_AGENDA = ["agendado", "confirmado", "concluido", "cancelado", "faltou"]

# =========================================================
# UI
# =========================================================
def apply_ui():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');

    .stApp {{
        background:
          radial-gradient(circle at 20% 0%, rgba(142,45,226,0.30), rgba(11,11,16,0.92) 40%),
          radial-gradient(circle at 80% 30%, rgba(212,175,55,0.12), rgba(11,11,16,0.0) 45%),
          {C_BG};
        color: {C_TEXT};
        font-family: 'Inter', sans-serif;
    }}

    .app-header {{
        background: linear-gradient(135deg, rgba(74,0,224,0.60), rgba(142,45,226,0.35));
        border: 1px solid {C_GOLD_SOFT};
        padding: 18px 22px;
        border-radius: 20px;
        margin-bottom: 16px;
        box-shadow: 0 16px 40px rgba(0,0,0,0.45);
        position: relative;
        overflow: hidden;
    }}
    .app-header:before {{
        content: "";
        position: absolute;
        inset: -60%;
        background: radial-gradient(circle, rgba(212,175,55,0.12), rgba(255,255,255,0.0) 60%);
        transform: rotate(10deg);
        pointer-events: none;
    }}
    .app-title {{
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 0.4px;
        color: {C_WHITE};
        margin: 0;
        line-height: 1.15;
        text-shadow: 0 10px 24px rgba(0,0,0,0.45);
    }}
    .app-sub {{
        font-size: 13px;
        color: {C_MUTED};
        margin-top: 6px;
    }}
    .gold-dot {{
        display: inline-block;
        width: 9px;
        height: 9px;
        background: {C_GOLD};
        border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 0 18px rgba(212,175,55,0.40);
    }}

    div[data-testid="stForm"], div[data-testid="stExpander"], div[data-testid="stMetric"] {{
        background: {C_SURFACE} !important;
        border: 1px solid {C_GOLD_SOFT} !important;
        border-radius: 20px !important;
        padding: 18px !important;
        color: {C_TEXT} !important;
        backdrop-filter: blur(10px);
    }}

    div[data-testid="stDataFrame"] {{
        background: {C_SURFACE_2} !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 18px !important;
        padding: 10px !important;
        backdrop-filter: blur(10px);
    }}

    div[data-testid="stMetric"] * {{
        color: {C_TEXT} !important;
        opacity: 1 !important;
        filter: none !important;
    }}
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] small {{
        color: {C_MUTED} !important;
    }}

    input, textarea, div[data-baseweb="select"] {{
        background-color: rgba(255,255,255,0.92) !important;
        color: #101018 !important;
        border-radius: 14px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }}

    .stButton>button {{
        background: linear-gradient(90deg, {C_GOLD}, #B8860B) !important;
        color: #0B0B10 !important;
        border: 1px solid rgba(212,175,55,0.45) !important;
        border-radius: 14px;
        height: 48px;
        font-weight: 800;
        transition: 0.18s ease;
        text-transform: none;
        box-shadow:
          0 10px 26px rgba(212,175,55,0.16),
          0 0 0 rgba(142,45,226,0.0);
    }}
    .stButton>button:hover {{
        transform: translateY(-1px);
        box-shadow:
          0 14px 34px rgba(212,175,55,0.22),
          0 0 24px rgba(142,45,226,0.20);
    }}

    section[data-testid="stSidebar"] {{
        background: #0B0B10 !important;
        border-right: 1px solid rgba(212,175,55,0.30) !important;
        position: relative !important;
    }}
    section[data-testid="stSidebar"] > div {{
        background: #0B0B10 !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {C_TEXT} !important;
    }}

    #sidebar-resizer {{
        position: absolute;
        top: 0;
        right: 0;
        width: 10px;
        height: 100%;
        cursor: col-resize;
        background: rgba(212,175,55,0.10);
        border-left: 1px solid rgba(212,175,55,0.35);
        z-index: 9999;
    }}
    #sidebar-resizer:hover {{
        background: rgba(212,175,55,0.20);
    }}

    .login-wrap {{
        display: flex;
        justify-content: center;
        align-items: center;
        padding-top: 40px;
    }}
    .login-card {{
        width: 480px;
        max-width: 92vw;
        background: {C_SURFACE};
        border: 1px solid {C_GOLD_SOFT};
        border-radius: 22px;
        padding: 22px 22px 16px 22px;
        box-shadow: 0 22px 60px rgba(0,0,0,0.55);
        backdrop-filter: blur(12px);
    }}
    .login-title {{
        font-family: 'Playfair Display', serif;
        font-size: 26px;
        font-weight: 700;
        color: {C_WHITE};
        margin: 0 0 6px 0;
    }}
    .login-sub {{
        color: {C_MUTED};
        font-size: 13px;
        margin-bottom: 14px;
    }}
    </style>
    """, unsafe_allow_html=True)

def header():
    st.markdown(
        f"""
        <div class="app-header">
            <div class="app-title"><span class="gold-dot"></span>{APP_NAME}</div>
            <div class="app-sub">Agenda • Atendimento • Financeiro • Relatórios • CRM</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def sidebar_resizer():
    components.html(
        """
        <script>
          (function () {
            const sidebar = parent.document.querySelector("section[data-testid='stSidebar']");
            if (!sidebar) return;
            if (parent.document.getElementById("sidebar-resizer")) return;

            const resizer = parent.document.createElement("div");
            resizer.id = "sidebar-resizer";
            sidebar.appendChild(resizer);

            let isResizing = false;

            resizer.addEventListener("mousedown", (e) => {
              e.preventDefault();
              isResizing = true;
              parent.document.body.style.cursor = "col-resize";
            });

            parent.document.addEventListener("mousemove", (e) => {
              if (!isResizing) return;

              let newWidth = e.clientX;
              const minW = 240;
              const maxW = 520;
              newWidth = Math.max(minW, Math.min(maxW, newWidth));

              sidebar.style.width = newWidth + "px";
              sidebar.style.minWidth = newWidth + "px";
              sidebar.style.maxWidth = newWidth + "px";
              sidebar.style.flex = "0 0 " + newWidth + "px";
            });

            parent.document.addEventListener("mouseup", () => {
              if (!isResizing) return;
              isResizing = false;
              parent.document.body.style.cursor = "";
            });
          })();
        </script>
        """,
        height=0,
    )

# =========================================================
# HELPERS
# =========================================================
def month_range(year: int, month: int):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end

def date_iso(d: date) -> str:
    return d.isoformat()

def br_money(v) -> str:
    try:
        x = float(v)
    except Exception:
        x = 0.0
    s = f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"

def normalize_phone(phone: str) -> str:
    if not phone:
        return ""
    return "".join(filter(str.isdigit, phone))

def next_maintenance_date(service_row: dict, base_date: date) -> str | None:
    dias = service_row.get("retorno_dias")
    if dias is None:
        return None
    try:
        return (base_date + timedelta(days=int(dias))).isoformat()
    except Exception:
        return None

# =========================================================
# SUPABASE DATA
# =========================================================
def get_profissionais_df() -> pd.DataFrame:
    res = sb.table("profissionais").select("*").eq("ativo", True).order("nome").execute()
    df = pd.DataFrame(res.data)
    if df.empty:
        return pd.DataFrame([{"id": None, "nome": "Eunides"}, {"id": None, "nome": "Evelyn"}])
    return df

def get_servicos_df() -> pd.DataFrame:
    res = sb.table("servicos").select("*").order("nome").execute()
    df = pd.DataFrame(res.data)
    return df

def get_clientes_df() -> pd.DataFrame:
    res = sb.table("clientes").select("*").order("nome").execute()
    return pd.DataFrame(res.data)

def find_or_create_cliente(nome: str, whatsapp: str = "", observacao: str = ""):
    tel = normalize_phone(whatsapp)
    if tel:
        existing = sb.table("clientes").select("*").eq("whatsapp", tel).limit(1).execute()
        if existing.data:
            return existing.data[0]

    existing_by_name = sb.table("clientes").select("*").ilike("nome", nome).limit(1).execute()
    if existing_by_name.data:
        return existing_by_name.data[0]

    payload = {
        "nome": nome,
        "whatsapp": tel if tel else None,
        "observacao": observacao if observacao else None,
    }
    created = sb.table("clientes").insert(payload).execute()
    return created.data[0] if created.data else None

def get_service_row_by_name(servico_nome: str):
    res = sb.table("servicos").select("*").eq("nome", servico_nome).limit(1).execute()
    return res.data[0] if res.data else None

def calc_comissao(profissional: str, servico_nome: str, valor_venda: float) -> float:
    if profissional.strip().lower() != "evelyn":
        return 0.0
    srv = get_service_row_by_name(servico_nome)
    pct = float(srv.get("comissao_evelyn") or 0) if srv else 0.0
    return float(valor_venda) * pct

# =========================================================
# SUPABASE HELPERS
# =========================================================
def inserir_agendamento(cliente_id, data, hora, cliente, telefone, servico, profissional, observacao=""):
    return sb.table("agenda").insert({
        "cliente_id": cliente_id,
        "data": data,
        "hora": hora,
        "cliente": cliente,
        "telefone": normalize_phone(telefone),
        "servico": servico,
        "profissional": profissional,
        "status": "agendado",
        "observacao": observacao if observacao else None,
        "lembrete_enviado": False,
        "confirmacao_enviada": False,
    }).execute()

def listar_agenda(inicio, fim):
    return sb.table("agenda") \
        .select("*") \
        .gte("data", inicio) \
        .lt("data", fim) \
        .order("data") \
        .order("hora") \
        .execute()

def listar_agenda_hoje(hoje):
    return sb.table("agenda") \
        .select("*") \
        .eq("data", hoje) \
        .order("hora") \
        .execute()

def atualizar_status_agendamento(agendamento_id, status):
    return sb.table("agenda").update({"status": status}).eq("id", agendamento_id).execute()

def marcar_confirmacao(agendamento_id):
    return sb.table("agenda").update({"confirmacao_enviada": True}).eq("id", agendamento_id).execute()

def marcar_lembrete(agendamento_id):
    return sb.table("agenda").update({"lembrete_enviado": True}).eq("id", agendamento_id).execute()

def excluir_agenda(ids):
    return sb.table("agenda").delete().in_("id", ids).execute()

def inserir_venda(cliente_id, data, cliente, valor, servico, profissional, comissao, forma_pagamento="", observacao=""):
    return sb.table("vendas").insert({
        "cliente_id": cliente_id,
        "data": data,
        "cliente": cliente,
        "valor": valor,
        "servico": servico,
        "profissional": profissional,
        "comissao": comissao,
        "forma_pagamento": forma_pagamento if forma_pagamento else None,
        "observacao": observacao if observacao else None,
    }).execute()

def listar_vendas(inicio, fim):
    return sb.table("vendas") \
        .select("*") \
        .gte("data", inicio) \
        .lt("data", fim) \
        .order("data", desc=True) \
        .order("id", desc=True) \
        .execute()

def excluir_vendas(ids):
    return sb.table("vendas").delete().in_("id", ids).execute()

def inserir_gasto(data, descricao, valor, categoria="", observacao=""):
    return sb.table("gastos").insert({
        "data": data,
        "descricao": descricao,
        "valor": valor,
        "categoria": categoria if categoria else None,
        "observacao": observacao if observacao else None,
    }).execute()

def listar_gastos(inicio, fim):
    return sb.table("gastos") \
        .select("*") \
        .gte("data", inicio) \
        .lt("data", fim) \
        .order("data", desc=True) \
        .order("id", desc=True) \
        .execute()

def listar_tudo_agenda():
    return sb.table("agenda").select("*").order("data").order("hora").execute()

def listar_tudo_vendas():
    return sb.table("vendas").select("*").order("data", desc=True).order("id", desc=True).execute()

def listar_tudo_gastos():
    return sb.table("gastos").select("*").order("data", desc=True).order("id", desc=True).execute()

def registrar_mensagem(cliente_id, cliente, whatsapp, tipo, mensagem, status="enviada", data_referencia=None):
    return sb.table("mensagens").insert({
        "cliente_id": cliente_id,
        "cliente": cliente,
        "whatsapp": normalize_phone(whatsapp),
        "tipo": tipo,
        "mensagem": mensagem,
        "status": status,
        "data_referencia": data_referencia,
    }).execute()

def listar_mensagens():
    return sb.table("mensagens").select("*").order("id", desc=True).execute()

# =========================================================
# WHATSAPP
# =========================================================
def build_whatsapp_link(nome, tel, servico, hora="", tipo="confirmacao"):
    if not tel:
        return None
    msgs = {
        "confirmacao": f"Olá {nome}! ✨ Confirmamos seu horário para {servico} às {hora}.",
        "lembrete": f"Oi {nome}! 💜 Lembrete do seu horário hoje às {hora} ({servico}).",
        "agradecimento": f"Obrigada pela preferência, {nome}! ✨ Foi um prazer atender você ({servico}).",
        "retorno": f"Olá {nome}! 💜 Já está no tempo ideal de manutenção do seu procedimento de {servico}. Quer agendar seu retorno?"
    }
    msg = msgs.get(tipo, "")
    tel_limpo = normalize_phone(tel)
    if not tel_limpo:
        return None
    return f"https://wa.me/55{tel_limpo}?text={urllib.parse.quote(msg)}"

def open_whatsapp(link):
    if not link:
        return
    components.html(f"<script>window.open('{link}', '_blank');</script>", height=0)

# =========================================================
# GOOGLE SHEETS
# =========================================================
def export_mes_para_sheets(df_agenda, df_vendas, df_gastos, sheet_title: str):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.create(sheet_title)

    def upsert_worksheet(name, df):
        try:
            ws = sh.worksheet(name)
            sh.del_worksheet(ws)
        except Exception:
            pass

        ws = sh.add_worksheet(title=name, rows=1000, cols=30)

        if df is None or df.empty:
            ws.update([["(sem dados)"]])
            return

        df2 = df.copy().fillna("")
        values = [df2.columns.tolist()] + df2.values.tolist()
        ws.update(values)

    upsert_worksheet("Agenda", df_agenda)
    upsert_worksheet("Vendas", df_vendas)
    upsert_worksheet("Gastos", df_gastos)

    return sh.url

# =========================================================
# CSV
# =========================================================
def df_to_csv_download(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")

# =========================================================
# APP
# =========================================================
apply_ui()
sidebar_resizer()

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown(
        "<style>section[data-testid='stSidebar']{display:none !important;}</style>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='login-wrap'><div class='login-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='login-title'>{APP_NAME}</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-sub'>Acesso restrito ao sistema interno.</div>", unsafe_allow_html=True)

    u = st.text_input("Usuário", placeholder="Digite seu usuário")
    s = st.text_input("Senha", type="password", placeholder="Digite sua senha")

    colA, colB = st.columns([1, 1])
    with colA:
        entrar = st.button("Entrar")
    with colB:
        st.caption("")

    if entrar:
        if u.strip().lower() == LOGIN_USER and s.strip() == LOGIN_PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

header()

if os.path.exists("assets/logo.png"):
    st.image("assets/logo.png", width=260)

today = date.today()
default_year = today.year
default_month = today.month

profissionais_df = get_profissionais_df()
servicos_df = get_servicos_df()
clientes_df = get_clientes_df()

PROFISSIONAIS = profissionais_df["nome"].dropna().tolist() if not profissionais_df.empty else ["Eunides", "Evelyn"]
SERVICOS = servicos_df["nome"].dropna().tolist() if not servicos_df.empty else [
    "Escova", "Progressiva", "Luzes", "Tintura", "Sobrancelha", "Buço",
    "Camuflagem", "Tonalização", "Penteado", "Corte (unissex)", "Outros"
]

st.sidebar.markdown("### 📅 Filtro")
year = st.sidebar.selectbox("Ano", list(range(default_year - 2, default_year + 1)), index=2)
month_name = st.sidebar.selectbox("Mês", MESES_PT, index=default_month - 1)
month = MESES_PT.index(month_name) + 1

start_m, end_m = month_range(year, month)
st.sidebar.caption(f"Período: {start_m.strftime('%d/%m/%Y')} → {(end_m - timedelta(days=1)).strftime('%d/%m/%Y')}")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Clientes",
        "Agenda",
        "Mensagens",
        "Checkout",
        "gastos",
        "Vendas",
        "Relatórios",
        "Backup",
    ]
)

# =========================================================
# DASHBOARD
# =========================================================
if menu == "Dashboard":
    st.subheader("Visão geral")

    df_v = pd.DataFrame(listar_vendas(date_iso(start_m), date_iso(end_m)).data)
    df_g = pd.DataFrame(listar_gastos(date_iso(start_m), date_iso(end_m)).data)
    df_a = pd.DataFrame(listar_agenda(date_iso(start_m), date_iso(end_m)).data)

    if not df_v.empty:
        df_v["valor"] = pd.to_numeric(df_v["valor"], errors="coerce").fillna(0.0)
        df_v["comissao"] = pd.to_numeric(df_v["comissao"], errors="coerce").fillna(0.0)
    if not df_g.empty:
        df_g["valor"] = pd.to_numeric(df_g["valor"], errors="coerce").fillna(0.0)

    faturamento = float(df_v["valor"].sum()) if not df_v.empty else 0.0
    comissao_total = float(df_v["comissao"].sum()) if not df_v.empty else 0.0
    gastos_total = float(df_g["valor"].sum()) if not df_g.empty else 0.0
    lucro = faturamento - comissao_total - gastos_total
    atendimentos = len(df_v) if not df_v.empty else 0
    ticket = faturamento / atendimentos if atendimentos else 0.0

    df_evelyn = df_v[df_v["profissional"].str.lower() == "evelyn"] if not df_v.empty else pd.DataFrame()
    vendas_evelyn = float(df_evelyn["valor"].sum()) if not df_evelyn.empty else 0.0
    comissao_evelyn = float(df_evelyn["comissao"].sum()) if not df_evelyn.empty else 0.0

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Faturamento", br_money(faturamento))
    m2.metric("Atendimentos", atendimentos)
    m3.metric("Ticket médio", br_money(ticket))
    m4.metric("Comissão Evelyn", br_money(comissao_evelyn))
    m5.metric("Lucro", br_money(lucro))

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Próximos agenda")
        if df_a.empty:
            st.info("Sem agenda no período.")
        else:
            st.dataframe(df_a.sort_values(["data", "hora"]).head(10), width="stretch")

    with c2:
        st.subheader("Vendas por profissional")
        if df_v.empty:
            st.info("Sem vendas no período.")
        else:
            resumo = df_v.groupby("profissional", as_index=False)["valor"].sum()
            fig = px.bar(resumo, x="profissional", y="valor", title="Faturamento por profissional")
            st.plotly_chart(fig, width="stretch")

# =========================================================
# CLIENTES
# =========================================================
elif menu == "Clientes":
    st.subheader("Cadastro de clientes")

    with st.form("cliente_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome")
        whatsapp = c2.text_input("WhatsApp")

        c3, c4 = st.columns(2)
        aniversario = c3.date_input("Aniversário", value=None)
        observacao = c4.text_input("Observação")

        if st.form_submit_button("Salvar cliente"):
            if not nome.strip():
                st.error("Informe o nome.")
                st.stop()

            payload = {
                "nome": nome.strip(),
                "whatsapp": normalize_phone(whatsapp) if whatsapp.strip() else None,
                "aniversario": aniversario.isoformat() if aniversario else None,
                "observacao": observacao.strip() if observacao else None,
            }
            sb.table("clientes").insert(payload).execute()
            st.success("Cliente salvo com sucesso.")
            st.rerun()

    st.markdown("---")
    st.subheader("Clientes cadastrados")

    clientes_df = get_clientes_df()
    if clientes_df.empty:
        st.info("Nenhum cliente cadastrado.")
    else:
        busca = st.text_input("Buscar cliente")
        df_show = clientes_df.copy()
        if busca.strip():
            df_show = df_show[df_show["nome"].str.contains(busca.strip(), case=False, na=False)]
        st.dataframe(df_show, width="stretch")

# =========================================================
# AGENDA
# =========================================================
elif menu == "Agenda":
    st.subheader("Novo agendamento")

    serv_base = st.selectbox("Procedimento", SERVICOS, key="serv_base_ag")
    outro_serv = ""
    if serv_base == "Outros":
        outro_serv = st.text_input("Especifique o serviço", placeholder="Ex: Hidratação Especial", key="outro_serv_ag")

    with st.form("agendamento_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        cli = c1.text_input("Cliente")
        tel = c2.text_input("WhatsApp")

        prof = st.selectbox("Profissional", PROFISSIONAIS)

        c3, c4 = st.columns(2)
        dt = c3.date_input("Data", date.today())
        hr = c4.time_input("Horário")

        observacao = st.text_area("Observação")

        if st.form_submit_button("Confirmar e enviar WhatsApp"):
            if not cli.strip():
                st.error("Informe o nome do cliente.")
                st.stop()
            if not tel.strip():
                st.error("Informe o WhatsApp.")
                st.stop()

            serv_final = outro_serv.strip() if serv_base == "Outros" and outro_serv.strip() else serv_base
            cliente = find_or_create_cliente(cli.strip(), tel.strip())

            inserir_agendamento(
                cliente["id"] if cliente else None,
                dt.isoformat(),
                hr.strftime("%H:%M"),
                cli.strip(),
                tel.strip(),
                serv_final,
                prof,
                observacao.strip()
            )

            link = build_whatsapp_link(cli.strip(), tel.strip(), serv_final, hr.strftime("%H:%M"), "confirmacao")
            open_whatsapp(link)
            if cliente:
                registrar_mensagem(cliente["id"], cli.strip(), tel.strip(), "confirmacao", "Confirmação de agendamento", "enviada", dt.isoformat())
            st.success("Agendamento registrado com sucesso.")
            if link:
                st.link_button("Abrir WhatsApp (se não abriu automaticamente)", link)
            st.rerun()

    df_ag = pd.DataFrame(listar_agenda(date_iso(start_m), date_iso(end_m)).data)

    st.subheader("agenda do mês")
    if df_ag.empty:
        st.info("Nenhum agendamento neste mês.")
    else:
        st.dataframe(df_ag, width="stretch")

        with st.expander("Atualizar status"):
            id_status = st.selectbox("ID do agendamento", df_ag["id"].tolist())
            novo_status = st.selectbox("Novo status", STATUS_AGENDA)
            if st.button("Salvar status"):
                atualizar_status_agendamento(id_status, novo_status)
                st.success("Status atualizado.")
                st.rerun()

        with st.expander("🧹 Excluir agenda"):
            ids_del = st.multiselect("Selecione os IDs para excluir", options=df_ag["id"].tolist())
            confirm = st.checkbox("Confirmar exclusão", key="conf_del_ag")
            if st.button("Excluir selecionados", disabled=(not confirm or len(ids_del) == 0)):
                excluir_agenda([int(x) for x in ids_del])
                st.success(f"Excluídos: {len(ids_del)} agendamento(s).")
                st.rerun()

# =========================================================
# MENSAGENS
# =========================================================
elif menu == "Mensagens":
    st.subheader("Central de mensagens")

    tab1, tab2, tab3 = st.tabs(["Lembretes de hoje", "Retornos sugeridos", "Histórico"])

    with tab1:
        hoje = date.today().isoformat()
        df_hoje = pd.DataFrame(listar_agenda_hoje(hoje).data)

        if df_hoje.empty:
            st.info("Nenhum agendamento para hoje.")
        else:
            for _, r in df_hoje.iterrows():
                st.markdown(f"**{r['hora']} — {r['cliente']} — {r['servico']} — {r['profissional']}**")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Enviar lembrete", key=f"lem_{r['id']}"):
                        link = build_whatsapp_link(r["cliente"], r["telefone"], r["servico"], r["hora"], "lembrete")
                        open_whatsapp(link)
                        marcar_lembrete(r["id"])
                        registrar_mensagem(r.get("cliente_id"), r["cliente"], r["telefone"], "lembrete_hoje", "Lembrete de agendamento", "enviada", r["data"])
                        st.success("Lembrete disparado.")
                        st.rerun()
                with c2:
                    if st.button("Enviar confirmação", key=f"conf_{r['id']}"):
                        link = build_whatsapp_link(r["cliente"], r["telefone"], r["servico"], r["hora"], "confirmacao")
                        open_whatsapp(link)
                        marcar_confirmacao(r["id"])
                        registrar_mensagem(r.get("cliente_id"), r["cliente"], r["telefone"], "confirmacao", "Confirmação de agendamento", "enviada", r["data"])
                        st.success("Confirmação disparada.")
                        st.rerun()

    with tab2:
        df_v = pd.DataFrame(listar_tudo_vendas().data)
        if df_v.empty:
            st.info("Sem vendas registradas.")
        else:
            sugestoes = []
            hoje_dt = date.today()

            for _, v in df_v.iterrows():
                serv_row = get_service_row_by_name(v["servico"])
                if not serv_row:
                    continue
                retorno = serv_row.get("retorno_dias")
                if retorno is None:
                    continue
                try:
                    dt_venda = datetime.strptime(v["data"], "%Y-%m-%d").date()
                    dt_retorno = dt_venda + timedelta(days=int(retorno))
                    if dt_retorno <= hoje_dt:
                        sugestoes.append({
                            "cliente": v["cliente"],
                            "servico": v["servico"],
                            "data_venda": v["data"],
                            "data_retorno": dt_retorno.isoformat(),
                            "cliente_id": v.get("cliente_id"),
                        })
                except Exception:
                    pass

            df_sug = pd.DataFrame(sugestoes).drop_duplicates(subset=["cliente", "servico", "data_retorno"]) if sugestoes else pd.DataFrame()

            if df_sug.empty:
                st.info("Nenhum retorno sugerido no momento.")
            else:
                clientes_df = get_clientes_df()
                st.dataframe(df_sug, width="stretch")

                for i, row in df_sug.iterrows():
                    tel = ""
                    if row.get("cliente_id") and not clientes_df.empty:
                        hit = clientes_df[clientes_df["id"] == row["cliente_id"]]
                        if not hit.empty:
                            tel = hit.iloc[0].get("whatsapp") or ""

                    if st.button(f"Mandar retorno para {row['cliente']} ({row['servico']})", key=f"ret_{i}"):
                        link = build_whatsapp_link(row["cliente"], tel, row["servico"], "", "retorno")
                        open_whatsapp(link)
                        registrar_mensagem(row.get("cliente_id"), row["cliente"], tel, "retorno_procedimento", f"Retorno sugerido para {row['servico']}", "enviada", row["data_retorno"])
                        st.success("Mensagem de retorno aberta.")
                        st.rerun()

    with tab3:
        df_m = pd.DataFrame(listar_mensagens().data)
        if df_m.empty:
            st.info("Nenhuma mensagem registrada.")
        else:
            st.dataframe(df_m, width="stretch")

# =========================================================
# CHECKOUT
# =========================================================
elif menu == "Checkout":
    st.subheader("Finalizar atendimento")

    v_serv_base = st.selectbox("Procedimento", SERVICOS, key="serv_base_checkout")
    v_outro_serv = ""
    if v_serv_base == "Outros":
        v_outro_serv = st.text_input("Qual o serviço realizado?", placeholder="Ex: Lavagem + Massagem", key="outro_serv_checkout")

    with st.form("checkout_form", clear_on_submit=True):
        v_cli = st.text_input("Cliente")
        v_tel = st.text_input("WhatsApp (opcional)")
        v_prof = st.selectbox("Profissional", PROFISSIONAIS)
        v_valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        forma_pg = st.selectbox("Forma de pagamento", ["Pix", "Cartão", "Dinheiro", "Transferência", "Outro"])
        obs = st.text_area("Observação")

        if st.form_submit_button("Concluir"):
            if not v_cli.strip():
                st.error("Informe o nome do cliente.")
                st.stop()
            if v_valor <= 0:
                st.error("Informe um valor maior que zero.")
                st.stop()

            v_serv_final = v_outro_serv.strip() if v_serv_base == "Outros" and v_outro_serv.strip() else v_serv_base
            cliente = find_or_create_cliente(v_cli.strip(), v_tel.strip())
            comissao = calc_comissao(v_prof, v_serv_final, float(v_valor))

            inserir_venda(
                cliente["id"] if cliente else None,
                date.today().isoformat(),
                v_cli.strip(),
                float(v_valor),
                v_serv_final,
                v_prof,
                float(comissao),
                forma_pg,
                obs.strip()
            )

            # Atualiza última visita e próxima manutenção no cliente
            service_row = get_service_row_by_name(v_serv_final)
            if cliente:
                payload_update = {"ultima_visita": date.today().isoformat()}
                prox = next_maintenance_date(service_row, date.today()) if service_row else None
                if prox:
                    payload_update["proxima_manutencao"] = prox
                sb.table("clientes").update(payload_update).eq("id", cliente["id"]).execute()

            link = build_whatsapp_link(v_cli.strip(), v_tel.strip(), v_serv_final, "", "agradecimento")
            open_whatsapp(link)
            if cliente:
                registrar_mensagem(cliente["id"], v_cli.strip(), v_tel.strip(), "agradecimento", "Mensagem pós-atendimento", "enviada", date.today().isoformat())

            if v_prof == "Evelyn":
                st.success(f"Venda registrada. Comissão Evelyn: {br_money(comissao)}")
            else:
                st.success("Venda registrada.")

            if link:
                st.link_button("Abrir WhatsApp (se não abriu automaticamente)", link)
            st.rerun()

    df_vm = pd.DataFrame(listar_vendas(date_iso(start_m), date_iso(end_m)).data)

    st.subheader("Vendas do mês")
    if df_vm.empty:
        st.info("Nenhuma venda neste mês.")
    else:
        st.dataframe(df_vm, width="stretch")

# =========================================================
# gastos
# =========================================================
elif menu == "gastos":
    st.subheader("Registrar despesa")

    with st.form("gastos_form", clear_on_submit=True):
        desc = st.text_input("Descrição")
        val = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        categoria = st.selectbox("Categoria", ["Produto", "Aluguel", "Internet", "Energia", "Manutenção", "Outros"])
        obs = st.text_area("Observação")

        if st.form_submit_button("Registrar"):
            if not desc.strip():
                st.error("Informe a descrição.")
                st.stop()
            if val <= 0:
                st.error("Informe um valor maior que zero.")
                st.stop()

            inserir_gasto(date.today().isoformat(), desc.strip(), float(val), categoria, obs.strip())
            st.success("Despesa registrada.")
            st.rerun()

    df_gm = pd.DataFrame(listar_gastos(date_iso(start_m), date_iso(end_m)).data)

    st.subheader("gastos do mês")
    if df_gm.empty:
        st.info("Nenhuma despesa neste mês.")
    else:
        st.dataframe(df_gm, width="stretch")

# =========================================================
# VENDAS
# =========================================================
elif menu == "Vendas":
    st.subheader("Vendas do mês")

    df_v = pd.DataFrame(listar_vendas(date_iso(start_m), date_iso(end_m)).data)

    if df_v.empty:
        st.info("Nenhuma venda nesse mês.")
        st.stop()

    c1, c2, c3 = st.columns([1.2, 1.2, 2.2])
    with c1:
        f_prof = st.selectbox("Profissional", ["Todos"] + PROFISSIONAIS)
    with c2:
        f_serv = st.selectbox("Serviço", ["Todos"] + SERVICOS)
    with c3:
        f_cli = st.text_input("Buscar cliente", placeholder="Ex: Maria")

    df_f = df_v.copy()
    if f_prof != "Todos":
        df_f = df_f[df_f["profissional"] == f_prof]
    if f_serv != "Todos":
        df_f = df_f[df_f["servico"] == f_serv]
    if f_cli.strip():
        df_f = df_f[df_f["cliente"].str.contains(f_cli.strip(), case=False, na=False)]

    st.dataframe(df_f, width="stretch")

    st.markdown("### 🧹 Excluir vendas")
    df_last = df_f.sort_values(["data", "id"], ascending=[False, False]).head(50).copy()

    def label_row(r):
        return f"ID {r['id']} • {r['data']} • {r['cliente']} • {r['servico']} • {r['profissional']} • {br_money(r['valor'])}"

    options = df_last["id"].tolist()
    labels = {int(r["id"]): label_row(r) for _, r in df_last.iterrows()}

    selected = st.multiselect(
        "Selecione as vendas para excluir",
        options=options,
        format_func=lambda x: labels.get(int(x), f"ID {x}")
    )

    confirm = st.checkbox("Confirmo que quero excluir permanentemente essas vendas.", key="conf_del_vendas_multi")
    if st.button("Excluir vendas selecionadas", disabled=(not confirm or len(selected) == 0)):
        excluir_vendas([int(x) for x in selected])
        st.success(f"Excluídas: {len(selected)} venda(s).")
        st.rerun()

# =========================================================
# RELATÓRIOS
# =========================================================
elif menu == "Relatórios":
    st.subheader("Resumo do mês")

    df_v = pd.DataFrame(listar_vendas(date_iso(start_m), date_iso(end_m)).data)
    df_g = pd.DataFrame(listar_gastos(date_iso(start_m), date_iso(end_m)).data)
    df_a = pd.DataFrame(listar_agenda(date_iso(start_m), date_iso(end_m)).data)

    if not df_v.empty:
        df_v["valor"] = pd.to_numeric(df_v["valor"], errors="coerce").fillna(0.0)
        df_v["comissao"] = pd.to_numeric(df_v["comissao"], errors="coerce").fillna(0.0)
    if not df_g.empty:
        df_g["valor"] = pd.to_numeric(df_g["valor"], errors="coerce").fillna(0.0)

    total_vendas = float(df_v["valor"].sum()) if not df_v.empty else 0.0
    total_comissao = float(df_v["comissao"].sum()) if not df_v.empty else 0.0
    total_gastos = float(df_g["valor"].sum()) if not df_g.empty else 0.0
    lucro = total_vendas - total_comissao - total_gastos

    if not df_v.empty:
        df_eve = df_v[df_v["profissional"].str.lower() == "evelyn"]
        comissao_evelyn = float(df_eve["comissao"].sum()) if not df_eve.empty else 0.0
        vendas_evelyn = float(df_eve["valor"].sum()) if not df_eve.empty else 0.0
    else:
        comissao_evelyn = 0.0
        vendas_evelyn = 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento total", br_money(total_vendas))
    c2.metric("Vendas Evelyn", br_money(vendas_evelyn))
    c3.metric("Comissão Evelyn", br_money(comissao_evelyn))
    c4.metric("Lucro do salão", br_money(lucro))

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Faturamento por profissional")
        if df_v.empty:
            st.info("Sem vendas registradas neste mês.")
        else:
            resumo = (
                df_v.groupby("profissional", as_index=False)
                    .agg(vendas=("valor", "sum"), comissao=("comissao", "sum"))
            )
            st.dataframe(resumo, width="stretch")
            fig = px.bar(resumo, x="profissional", y="vendas", title="Faturamento por profissional")
            st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Serviços mais vendidos")
        if df_v.empty:
            st.info("Sem vendas registradas.")
        else:
            resumo_serv = df_v.groupby("servico", as_index=False)["valor"].sum().sort_values("valor", ascending=False)
            fig2 = px.bar(resumo_serv, x="servico", y="valor", title="Faturamento por serviço")
            st.plotly_chart(fig2, width="stretch")

    st.subheader("Últimas vendas")
    if df_v.empty:
        st.info("Sem vendas registradas.")
    else:
        st.dataframe(
            df_v.sort_values(["data", "id"], ascending=[False, False]).head(25),
            width="stretch"
        )

    st.markdown("---")
    st.subheader("Exportar para Google Sheets")

    if not HAS_SHEETS:
        st.info("Para exportar para Google Sheets, instale: pip install gspread google-auth.")
    else:
        st.caption("Requer st.secrets['gcp_service_account'] configurado.")
        if st.button("📄 Criar planilha no Google Sheets com o mês selecionado"):
            try:
                url = export_mes_para_sheets(
                    df_a, df_v, df_g,
                    sheet_title=f"{APP_NAME} - {month_name}/{year}"
                )
                st.success("Planilha criada no Google Sheets!")
                st.link_button("Abrir planilha", url)
            except Exception as e:
                st.error(f"Falha ao exportar: {e}")

# =========================================================
# BACKUP
# =========================================================
elif menu == "Backup":
    st.subheader("Backup dos dados")
    st.caption("Baixe cópias de segurança da agenda, vendas e gastos.")

    df_ag_backup = pd.DataFrame(listar_tudo_agenda().data)
    df_v_backup = pd.DataFrame(listar_tudo_vendas().data)
    df_g_backup = pd.DataFrame(listar_tudo_gastos().data)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.download_button(
            "⬇️ Baixar Agenda CSV",
            data=df_to_csv_download(df_ag_backup),
            file_name="agenda_backup.csv",
            mime="text/csv"
        )

    with c2:
        st.download_button(
            "⬇️ Baixar Vendas CSV",
            data=df_to_csv_download(df_v_backup),
            file_name="vendas_backup.csv",
            mime="text/csv"
        )

    with c3:
        st.download_button(
            "⬇️ Baixar gastos CSV",
            data=df_to_csv_download(df_g_backup),
            file_name="gastos_backup.csv",
            mime="text/csv"
        )

    st.markdown("---")
    st.subheader("Resumo rápido do backup")

    r1, r2, r3 = st.columns(3)
    r1.metric("Registros da agenda", len(df_ag_backup))
    r2.metric("Registros de vendas", len(df_v_backup))
    r3.metric("Registros de gastos", len(df_g_backup))

    with st.expander("Visualizar dados da agenda"):
        st.dataframe(df_ag_backup, width="stretch")

    with st.expander("Visualizar dados de vendas"):
        st.dataframe(df_v_backup, width="stretch")

    with st.expander("Visualizar dados de gastos"):
        st.dataframe(df_g_backup, width="stretch")