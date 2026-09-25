import io
from datetime import datetime, timedelta
import tempfile
from fpdf import FPDF
import pandas as pd
import plotly.express as px
import sqlalchemy
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Portafolio de Incentivos Coppel",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- AVATARES CORPORATIVOS ---
URL_ROBOT = "https://cdn-icons-png.flaticon.com/512/8943/8943377.png" 
URL_USER = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

# --- CSS CORPORATIVO (ENTERPRISE UI) ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif !important; background-color: #F4F6F9 !important; color: #0F172A !important; }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; }
    h1, h2, h3, h4, h5, h6 { color: #0F172A !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
    label { color: #475569 !important; font-weight: 600 !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.05em; }
    
    /* INPUTS MINIMALISTAS */
    .stTextInput > div > div, .stSelectbox > div > div, .stTextArea > div > div { border-radius: 6px !important; border: 1px solid #CBD5E1 !important; background-color: #F8FAFC !important; transition: all 0.15s ease; }
    .stTextInput > div > div:focus-within, .stSelectbox > div > div:focus-within { border-color: #05297A !important; box-shadow: 0 0 0 2px rgba(5, 41, 122, 0.15) !important; background-color: #FFFFFF !important; }
    
    /* BOTONES CORPORATIVOS */
    div[data-testid="stFormSubmitButton"] button, .stButton > button[kind="primary"] { background: linear-gradient(135deg, #05297A 0%, #1C42E8 100%) !important; color: #FFFFFF !important; border: none !important; border-radius: 6px !important; font-weight: 600 !important; padding: 0.5rem 1rem !important; box-shadow: 0 4px 6px -1px rgba(28, 66, 232, 0.2) !important; transition: all 0.2s ease !important; }
    div[data-testid="stFormSubmitButton"] button:hover, .stButton > button[kind="primary"]:hover { transform: translateY(-1px); box-shadow: 0 8px 12px -2px rgba(28, 66, 232, 0.3) !important; }
    
    button[data-testid="baseButton-secondary"], .stButton > button[kind="secondary"] { background-color: #FFFFFF !important; border: 1px solid #CBD5E1 !important; color: #334155 !important; border-radius: 6px !important; font-weight: 600 !important; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.04) !important; }
    button[data-testid="baseButton-secondary"]:hover, .stButton > button[kind="secondary"]:hover { border-color: #05297A !important; color: #05297A !important; background-color: #F8FAFC !important; }
    .stButton > button[kind="primary"] p { color: #FFFFFF !important; } .stButton > button[kind="secondary"] p { color: inherit !important; }
    
    /* TARJETAS DIRECTIVAS */
    div[data-testid="metric-container"] { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-top: 4px solid #05297A !important; padding: 18px 20px !important; border-radius: 8px !important; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02) !important; }
    div[data-testid="metric-container"] label { color: #64748B !important; font-size: 0.78rem !important; font-weight: 700 !important; }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] div { color: #0F172A !important; font-size: 2rem !important; font-weight: 800 !important; letter-spacing: -0.03em; }
    
    /* PESTAÑAS (TABS) */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 2px solid #E2E8F0; }
    .stTabs [aria-selected="true"] { border-bottom: 3px solid #05297A !important; font-weight: 700 !important; color: #05297A !important; background-color: transparent !important; }
    .stTabs [aria-selected="false"] { color: #64748B !important; font-weight: 500 !important; }
    
    /* PANELES DESPLEGABLES */
    .streamlit-expanderHeader { background-color: #FFFFFF !important; color: #0F172A !important; font-weight: 600 !important; border-radius: 8px !important; border: 1px solid #E2E8F0 !important; padding: 0.9rem !important; }
    .streamlit-expanderContent { border: 1px solid #E2E8F0 !important; border-top: none !important; background-color: #FFFFFF !important; padding: 20px !important; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; }
    .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.70rem; font-weight: 700; display: inline-block; text-transform: uppercase; letter-spacing: 0.05em; }
    .status-green { background-color: #DCFCE7; color: #166534 !important; border: 1px solid #BBF7D0;}
    .status-yellow { background-color: #FEF9C3; color: #854D0E !important; border: 1px solid #FEF08A;}
    .status-gray { background-color: #F1F5F9; color: #475569 !important; border: 1px solid #E2E8F0;}
    
    .kanban-card { background: #FFFFFF; padding: 14px; border-radius: 8px; border: 1px solid #E2E8F0; border-left: 4px solid #05297A; box-shadow: 0 1px 3px rgba(0,0,0,0.02); margin-bottom: 12px; }
    .kanban-title { font-weight: 700; color: #0F172A; font-size: 0.9rem; margin-bottom: 6px; }
    .kanban-meta { font-size: 0.78rem; color: #64748B; margin-bottom: 3px;}
    .timeline-item { border-left: 2px solid #CBD5E1; padding-left: 12px; margin-bottom: 12px; position: relative; }
    .timeline-item::before { content: ''; position: absolute; left: -5px; top: 0; width: 8px; height: 8px; border-radius: 50%; background: #05297A; }
    .timeline-date { font-size: 0.72rem; color: #64748B; font-weight: 600; }
    .timeline-text { font-size: 0.83rem; color: #1E293B; }
    
    /* LOGIN PANEL */
    .login-box { background-color: #FFFFFF; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; }
    
    /* BOTÓN FLOTANTE "PROJECT IA" */
    div[data-testid="stPopover"] { position: fixed !important; bottom: 25px !important; right: 25px !important; z-index: 999999 !important; }
    div[data-testid="stPopover"] > button { background: linear-gradient(135deg, #05297A 0%, #1C42E8 100%) !important; color: #FFFFFF !important; border-radius: 30px !important; padding: 10px 20px !important; box-shadow: 0 8px 20px rgba(5, 41, 122, 0.35) !important; border: 2px solid #FFFFFF !important; font-size: 0.95rem !important; font-weight: 700 !important; }
    div[data-testid="stPopover"] > button p { color: #FFFFFF !important; font-weight: 700 !important; }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# --- CONSTANTES ---
OPCIONES_AREAS = ["Incentivos", "Afore", "Banca Empresarial", "Banco", "CAT Cobranza", "CAT P&V", "CEDIS", "Cobranza Domiciliaria", "Credito Automotriz", "Inmobiliaria", "Retail", "Sale Vale"]
OPCIONES_TIPOS = ["Esquema de Incentivos", "Tecnología", "Estratégicos", "Procesos", "Campañas", "Auditorías"]
OPCIONES_SUBTIPOS = ["EI-Nuevo incentivo completo", "EI-Actualización completa de incentivo", "EI-Ajuste menor de incentivo", "EI-Ajuste mayor de incentivo", "EI-Casos especiales", "CA-Campaña", "CA-Concurso", "PR-Documentación oficial", "PR-Nuevo proceso", "TE-Software", "TE-Tableros", "Otros"]
OPCIONES_ETAPAS = ["1. Diseño (EI)", "2. Prueba piloto (EI)", "3. Escalamiento nacional (EI)", "4. Cierre (EI)", "1. Diseño (CA)", "2. Implementación (CA)", "3. Evaluación y cierre (CA)", "4. Cierre (CA)", "1. Planeación", "2. Ejecución", "3. Cierre"]
OPCIONES_ESTATUS = ["Por iniciar", "En tiempo", "Retrasado", "Detenido", "Cancelado"]
OPCIONES_GERENTES = ["Andres Avila", "Eduardo Rodriguez", "Heriberto Vega", "Janik Orozco", "Kurokusi Ochoa", "Noel Aquino", "Yahir Ramirez", "Giovanni Vallejo", "Ruben Rivera"]

# --- BASE DE DATOS Y CACHÉ ---
@st.cache_resource
def obtener_engine():
  db_url = st.secrets["postgres"]["url"] if "postgres" in st.secrets else "sqlite:///db_coppel_v5.db"
  return sqlalchemy.create_engine(db_url, pool_size=10, max_overflow=20, pool_pre_ping=True)

def inicializar_db():
  engine = obtener_engine()
  with engine.begin() as conn:
    conn.execute(sqlalchemy.text("""CREATE TABLE IF NOT EXISTS proyectos (id SERIAL PRIMARY KEY, folio TEXT, nombre TEXT NOT NULL, area_negocio TEXT, tipo_proyecto TEXT, subtipo TEXT, gerente TEXT, lider_asignado TEXT, etapa_actual TEXT, estatus_tiempo TEXT, avance_real REAL, resumen_estatus TEXT, carpeta_url TEXT, plan_url TEXT, ultima_actualizacion TEXT)"""))
    conn.execute(sqlalchemy.text("""CREATE TABLE IF NOT EXISTS usuarios (correo TEXT PRIMARY KEY, password TEXT NOT NULL, rol TEXT NOT NULL, nombre TEXT)"""))
    conn.execute(sqlalchemy.text("""CREATE TABLE IF NOT EXISTS tareas (id SERIAL PRIMARY KEY, proyecto_id INTEGER, nombre_tarea TEXT NOT NULL, responsable TEXT, fecha_inicio TEXT, duracion_dias INTEGER, fecha_fin TEXT, porcentaje_avance REAL, predecesoras TEXT)"""))
    conn.execute(sqlalchemy.text("""CREATE TABLE IF NOT EXISTS bitacora (id SERIAL PRIMARY KEY, proyecto_id INTEGER, usuario_nombre TEXT, fecha_hora TEXT, comentario TEXT)"""))
    res = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM usuarios")).fetchone()
    if res[0] == 0:
      conn.execute(sqlalchemy.text("INSERT INTO usuarios VALUES ('leonardo.castillo@coppel.com', 'Coppel2026', 'Moderador', 'Leonardo Castillo')"))

inicializar_db()

@st.cache_data(ttl=3)
def cargar_datos_completos():
  engine = obtener_engine()
  df_p = pd.read_sql("SELECT * FROM proyectos ORDER BY id DESC", engine)
  df_b = pd.read_sql("SELECT * FROM bitacora ORDER BY id DESC", engine)
  df_t = pd.read_sql("SELECT * FROM tareas ORDER BY id ASC", engine)
  # AHORA SE EXTRAE EL PASSWORD PARA MOSTRARLO EN EL PANEL DE ADMINISTRADOR
  df_u = pd.read_sql("SELECT nombre, correo, password, rol FROM usuarios ORDER BY nombre ASC", engine)
  return df_p, df_b, df_t, df_u

def limpiar_cache_y_recargar():
  cargar_datos_completos.clear()

def obtener_lista_usuarios(df_u):
  return df_u["nombre"].tolist() if not df_u.empty else ["Leonardo Castillo"]

def calcular_fechas_tarea_df(df_tareas_proyecto):
  if df_tareas_proyecto.empty: return df_tareas_proyecto
  df_t = df_tareas_proyecto.copy()
  df_t["fecha_inicio"] = pd.to_datetime(df_t["fecha_inicio"])
  df_t["fecha_fin"] = pd.to_datetime(df_t["fecha_fin"])
  fechas_fin = {}
  for idx, row in df_t.iterrows():
    t_id = row["id"]
    preds = str(row["predecesoras"]).strip() if row["predecesoras"] else ""
    if preds:
      pred_ids = [int(p.strip()) for p in preds.split(",") if p.strip().isdigit() and int(p.strip()) in fechas_fin]
      if pred_ids:
        max_pred_fin = max([fechas_fin[pid] for pid in pred_ids])
        df_t.at[idx, "fecha_inicio"] = max_pred_fin + timedelta(days=1)
    inicio = df_t.at[idx, "fecha_inicio"]
    duracion = int(row["duracion_dias"] or 1)
    fin = inicio + timedelta(days=duracion - 1)
    df_t.at[idx, "fecha_fin"] = fin
    fechas_fin[t_id] = fin
    df_t.at[idx, "avance_txt"] = f"{int(row['porcentaje_avance'])}%"
  return df_t

# --- LOGIN Y RECUPERACIÓN DE CONTRASEÑA ---
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False; st.session_state.correo_actual = None; st.session_state.nombre_actual = None; st.session_state.rol = None

if not st.session_state.autenticado:
  col_izq, col_centro, col_der = st.columns([1, 1.4, 1])
  with col_centro:
    st.write(""); st.write(""); st.write("")
    st.markdown("<h1 style='text-align: center; color:#05297A !important; font-size: 2.2rem; letter-spacing: -1px;'>Plataforma Ejecutiva de Incentivos</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 30px; font-size: 1rem;'>Acceso Corporativo Coppel</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    with st.form("login_form"):
      st.markdown("<h3 style='color:#0F172A !important; font-size: 1.1rem; margin-bottom: 20px; border-bottom: 1px solid #E2E8F0; padding-bottom: 10px;'>Credenciales de Acceso</h3>", unsafe_allow_html=True)
      correo_input = st.text_input("Correo Institucional", placeholder="tu.nombre@coppel.com")
      password_input = st.text_input("Contraseña", type="password")
      st.write("")
      if st.form_submit_button("Iniciar Sesión", type="primary", use_container_width=True):
        if correo_input.strip() == "": st.warning("El correo institucional es requerido.")
        else:
          engine = obtener_engine()
          with engine.connect() as conn:
            res = conn.execute(sqlalchemy.text("SELECT password, rol, nombre FROM usuarios WHERE LOWER(correo)=:c"), {"c": correo_input.strip().lower()}).fetchone()
            if res and res[0] == password_input:
              st.session_state.autenticado = True; st.session_state.correo_actual = correo_input.strip().lower(); st.session_state.rol = res[1]; st.session_state.nombre_actual = res[2]; st.rerun()
            else: st.error("Credenciales incorrectas o usuario no registrado.")
    
    # OPCIÓN: OLVIDÉ MI CONTRASEÑA
    if st.button("¿Olvidaste tu contraseña?", type="secondary", use_container_width=True):
        st.info("🔒 **Protocolo de Seguridad:** Para visualizar o restablecer tu contraseña, por favor contacta al Administrador de la plataforma (Leonardo Castillo) vía correo o Teams corporativo.")
    st.markdown("</div>", unsafe_allow_html=True)
  st.stop()

# --- CARGA DE DATOS EN MEMORIA ---
df, df_bitacora, df_tareas_all, df_users_raw = cargar_datos_completos()
es_moderador = st.session_state.rol == "Moderador"
lista_lideres_registrados = obtener_lista_usuarios(df_users_raw)

# --- ALERTAS INTELIGENTES ---
if not df.empty:
  proyectos_retrasados = df[df["estatus_tiempo"].isin(["Retrasado", "Detenido"])]
  if not proyectos_retrasados.empty and "alerta_mostrada" not in st.session_state:
    st.toast(f"Reporte: {len(proyectos_retrasados)} iniciativas en estatus crítico.", icon="🚨")
    st.session_state.alerta_mostrada = True

# --- SIDEBAR ---
with st.sidebar:
  st.markdown(f"<div style='background-color:#F8FAFC; padding: 18px; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 15px;'><h3 style='margin:0 0 4px 0; font-size:1.05rem; color:#0F172A;'>👤 {st.session_state.nombre_actual}</h3><p style='margin:0 0 8px 0; color:#64748B; font-size:0.78rem;'>{st.session_state.correo_actual}</p><span class='status-badge {'status-green' if es_moderador else 'status-gray'}'>{st.session_state.rol}</span></div>", unsafe_allow_html=True)
  with st.expander("⚙️ Mi Cuenta", expanded=False):
    with st.form("form_cambio_pass"):
      nueva_pass = st.text_input("Nueva Contraseña", type="password"); confirmar_pass = st.text_input("Confirmar Contraseña", type="password")
      if st.form_submit_button("Actualizar", use_container_width=True):
        if nueva_pass == confirmar_pass and nueva_pass:
          engine = obtener_engine()
          with engine.begin() as conn: conn.execute(sqlalchemy.text("UPDATE usuarios SET password=:p WHERE correo=:c"), {"p": nueva_pass, "c": st.session_state.correo_actual})
          limpiar_cache_y_recargar(); st.success("Guardado exitosamente.")
        else: st.error("Las contraseñas no coinciden.")
  st.write("")
  st.markdown("<h4 style='color:#0F172A; font-size: 0.85rem;'>📥 Exportación Institucional</h4>", unsafe_allow_html=True)
  if not df.empty:
    def generar_pdf(dataframe):
      pdf = FPDF(orientation="L", unit="mm", format="A4"); pdf.set_auto_page_break(auto=True, margin=15); pdf.add_page(); pdf.set_font("Arial", "B", 16); pdf.set_text_color(5, 41, 122)
      pdf.cell(0, 8, "Reporte Directivo del Portafolio", ln=True, align="L"); pdf.set_font("Arial", "", 9); pdf.set_text_color(100, 100, 100)
      pdf.cell(0, 6, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="L"); pdf.ln(4)
      pdf.set_font("Arial", "B", 8); pdf.set_fill_color(241, 245, 249); pdf.set_text_color(8, 23, 84)
      pdf.cell(22, 8, "Folio", 1, 0, "C", True); pdf.cell(60, 8, "Nombre de Iniciativa", 1, 0, "L", True); pdf.cell(30, 8, "Área", 1, 0, "L", True); pdf.cell(35, 8, "Responsable", 1, 0, "L", True); pdf.cell(25, 8, "Estatus", 1, 0, "C", True); pdf.cell(18, 8, "Avance", 1, 0, "C", True); pdf.cell(42, 8, "Ult. Act.", 1, 0, "C", True); pdf.cell(45, 8, "Fase Actual", 1, 1, "L", True)
      pdf.set_font("Arial", "", 8); pdf.set_text_color(40, 40, 40)
      for _, row in dataframe.iterrows():
        pdf.cell(22, 7, str(row["folio"])[:12], 1, 0, "C"); pdf.cell(60, 7, str(row["nombre"])[:35], 1, 0, "L"); pdf.cell(30, 7, str(row["area_negocio"])[:18], 1, 0, "L"); pdf.cell(35, 7, str(row["lider_asignado"])[:22], 1, 0, "L"); pdf.cell(25, 7, str(row["estatus_tiempo"])[:15], 1, 0, "C"); pdf.cell(18, 7, f"{int((row['avance_real'] or 0)*100)}%", 1, 0, "C"); pdf.set_font("Arial", "B", 8); pdf.cell(42, 7, str(row["ultima_actualizacion"])[:19], 1, 0, "C"); pdf.set_font("Arial", "", 8); pdf.cell(45, 7, str(row["etapa_actual"])[:25], 1, 1, "L")
      with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp: pdf.output(tmp.name); return tmp.name

    with open(generar_pdf(df), "rb") as file: st.download_button("Descargar Reporte (PDF)", data=file, file_name=f"Reporte_{datetime.now().strftime('%Y%m%d')}.pdf", use_container_width=True, type="secondary")
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer: df.to_excel(writer, index=False, sheet_name="Proyectos")
    st.download_button("Descargar Base de Datos (Excel)", data=excel_buffer.getvalue(), file_name=f"Base_Datos_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, type="secondary")

  st.write("")
  if st.button("Cerrar Sesión Segura", use_container_width=True): st.session_state.autenticado = False; st.rerun()

# --- HEADER Y MÉTRICAS PERMANENTES ---
st.markdown("<h2 style='margin-bottom: 20px; color:#0F172A;'>📊 Panorama Ejecutivo del Portafolio</h2>", unsafe_allow_html=True)
if not df.empty and not proyectos_retrasados.empty:
  st.markdown(f"<div style='background-color:#FEF2F2; border-left: 4px solid #EF4444; padding: 12px; border-radius: 8px; margin-bottom: 15px;'><p style='color:#991B1B; margin:0; font-weight:600;'>⚠️ Atención Crítica: Se detectaron {len(proyectos_retrasados)} iniciativas en estatus de Retraso o Detenidas.</p></div>", unsafe_allow_html=True)

total_p = len(df); en_t = len(df[df["estatus_tiempo"] == "En tiempo"]) if total_p > 0 else 0; ret = len(proyectos_retrasados) if total_p > 0 else 0; prom = df["avance_real"].mean() * 100 if total_p > 0 else 0.0
m1, m2, m3, m4 = st.columns(4)
m1.metric("INICIATIVAS ACTIVAS", total_p); m2.metric("EJECUCIÓN EN TIEMPO", en_t); m3.metric("EN RIESGO / RETRASOS", ret); m4.metric("AVANCE GLOBAL", f"{prom:.1f}%")
st.write("")

# --- PESTAÑAS (TABS CORPORATIVAS) ---
if es_moderador: tabs = st.tabs(["📈 Dashboard Directivo", "🚀 Control Operativo", "📋 Tablero Kanban", "➕ Alta de Iniciativa", "👥 Control de Accesos"])
else: tabs = st.tabs(["📈 Dashboard Directivo", "🚀 Control Operativo", "📋 Tablero Kanban", "➕ Alta de Iniciativa"])

# PESTAÑA 1: DASHBOARD
with tabs[0]:
  st.write("")
  if df.empty: st.info("Datos insuficientes para renderizar gráficos ejecutivos.")
  else:
    d_col1, d_col2 = st.columns(2)
    with d_col1:
      fig1 = px.pie(df, names="area_negocio", title="Distribución por Área de Negocio", hole=0.4, color_discrete_sequence=px.colors.qualitative.Prism)
      fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"); st.plotly_chart(fig1, use_container_width=True)
    with d_col2:
      df_status_count = df["estatus_tiempo"].value_counts().reset_index(); df_status_count.columns = ["Estatus", "Cantidad"]
      fig2 = px.bar(df_status_count, x="Estatus", y="Cantidad", title="Salud General del Portafolio", color="Estatus", color_discrete_map={"En tiempo": "#166534", "Retrasado": "#475569", "Detenido": "#854D0E", "Por iniciar": "#94A3B8"})
      fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"); st.plotly_chart(fig2, use_container_width=True)

# PESTAÑA 2: CONTROL OPERATIVO CON 6 FILTROS ESTRATÉGICOS
with tabs[1]:
  if df.empty: st.info("El portafolio corporativo está vacío.")
  else:
    # FILTROS RÁPIDOS
    f_pills1, f_pills2, f_pills3, f_pills4 = st.columns([1.2, 1.2, 1.2, 2.4])
    modo_filtro = f_pills1.radio("Visualización Rápida", ["Todo el Portafolio", "🚨 Ver Críticos", "🟢 En Tiempo", "⭐ Mis Proyectos"], horizontal=True)

    # 6 FILTROS AVANZADOS EN 2 FILAS
    st.markdown("<h5 style='color:#334155; margin-top:10px; margin-bottom:10px; font-size:0.9rem;'>Filtros Avanzados</h5>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3 = st.columns(3)
    txt_busqueda = f_col1.text_input("Búsqueda por Folio o Nombre")
    filtro_area = f_col2.selectbox("Área de Negocio", ["Todas las Áreas"] + OPCIONES_AREAS)
    filtro_lider = f_col3.selectbox("Responsable Operativo", ["Todos los Responsables"] + lista_lideres_registrados)

    f_col4, f_col5, f_col6 = st.columns(3)
    filtro_estatus = f_col4.selectbox("Estatus Operativo", ["Todos los Estatus"] + OPCIONES_ESTATUS)
    filtro_gerente = f_col5.selectbox("Gerente / Sponsor", ["Todos los Gerentes"] + OPCIONES_GERENTES)
    filtro_etapa = f_col6.selectbox("Fase de Avance", ["Todas las Fases"] + OPCIONES_ETAPAS)

    df_filtrado = df.copy()

    # Aplicar Filtro Rápido
    if modo_filtro == "🚨 Ver Críticos": df_filtrado = df_filtrado[df_filtrado["estatus_tiempo"].isin(["Retrasado", "Detenido"])]
    elif modo_filtro == "🟢 En Tiempo": df_filtrado = df_filtrado[df_filtrado["estatus_tiempo"] == "En tiempo"]
    elif modo_filtro == "⭐ Mis Proyectos": df_filtrado = df_filtrado[df_filtrado["lider_asignado"] == st.session_state.nombre_actual]

    # Aplicar Filtros Avanzados
    if txt_busqueda.strip(): df_filtrado = df_filtrado[df_filtrado["nombre"].str.lower().str.contains(txt_busqueda.lower(), na=False) | df_filtrado["folio"].str.lower().str.contains(txt_busqueda.lower(), na=False)]
    if filtro_area != "Todas las Áreas": df_filtrado = df_filtrado[df_filtrado["area_negocio"] == filtro_area]
    if filtro_lider != "Todos los Responsables": df_filtrado = df_filtrado[df_filtrado["lider_asignado"] == filtro_lider]
    if filtro_estatus != "Todos los Estatus": df_filtrado = df_filtrado[df_filtrado["estatus_tiempo"] == filtro_estatus]
    if filtro_gerente != "Todos los Gerentes": df_filtrado = df_filtrado[df_filtrado["gerente"] == filtro_gerente]
    if filtro_etapa != "Todas las Fases": df_filtrado = df_filtrado[df_filtrado["etapa_actual"] == filtro_etapa]

    st.markdown(f"<p style='color: #64748B; font-size: 0.85rem; margin-top: 15px;'>📌 Listando <b>{len(df_filtrado)}</b> de <b>{len(df)}</b> iniciativas bajo los criterios seleccionados.</p>", unsafe_allow_html=True)

    for _, row in df_filtrado.iterrows():
      p_id = row["id"]
      badge_status = "status-green" if row["estatus_tiempo"] == "En tiempo" else ("status-yellow" if row["estatus_tiempo"] == "Detenido" else "status-gray")

      with st.expander(f"{row['folio'] or 'S/F'} | {row['nombre']} — Avance Global Validado: {int((row['avance_real'] or 0)*100)}%"):
        st.progress(float(row["avance_real"] or 0.0))

        with st.form(f"update_{p_id}"):
          c1, c2, c3 = st.columns(3)
          c1.markdown(f"<p style='margin:0; font-size:0.88rem;'><span style='color:#64748B;'>Líder Asignado:</span> <b style='color:#0F172A;'>{row['lider_asignado']}</b></p>", unsafe_allow_html=True)
          c2.markdown(f"<p style='margin:0; font-size:0.88rem;'><span style='color:#64748B;'>Estatus Actual:</span> <span class='status-badge {badge_status}'>{row['estatus_tiempo']}</span></p>", unsafe_allow_html=True)
          c3.markdown(f"<p style='margin:0; font-size:0.88rem; text-align:right;'><span style='color:#64748B;'>Últ. Actualización:</span> <b style='color:#05297A;'>{row['ultima_actualizacion'] or 'N/A'}</b></p>", unsafe_allow_html=True)
          st.divider()

          c_form1, c_form2, c_form3 = st.columns(3)
          u_etapa = c_form1.selectbox("Fase de Despliegue", OPCIONES_ETAPAS, index=(OPCIONES_ETAPAS.index(row["etapa_actual"]) if row["etapa_actual"] in OPCIONES_ETAPAS else 0))
          u_estatus = c_form2.selectbox("Estado de Ejecución", OPCIONES_ESTATUS, index=(OPCIONES_ESTATUS.index(row["estatus_tiempo"]) if row["estatus_tiempo"] in OPCIONES_ESTATUS else 0))
          u_avance = c_form3.slider("Progreso Validado (%)", 0.0, 1.0, float(row["avance_real"] or 0.0), 0.05)
          
          st.markdown("<p style='font-size:0.80rem; font-weight:700; color:#334155; margin-bottom:4px;'>NUEVA ENTRADA DE BITÁCORA</p>", unsafe_allow_html=True)
          u_comentario = st.text_input("Reporte de estatus", placeholder="Describa el estatus ejecutivo de la semana...")
          
          l1, l2 = st.columns(2)
          u_carpeta = l1.text_input("Directorio Drive (URL)", row["carpeta_url"] or "")
          u_plan = l2.text_input("Documentación Anexa (URL)", row["plan_url"] or "")
          
          st.write("")
          btn1, btn2, btn3 = st.columns([3, 3, 6])
          if btn1.form_submit_button("Guardar Cambios", type="primary"):
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            engine = obtener_engine()
            with engine.begin() as conn:
              conn.execute(sqlalchemy.text("""UPDATE proyectos SET etapa_actual=:e, estatus_tiempo=:s, avance_real=:a, carpeta_url=:c, plan_url=:p, ultima_actualizacion=:u WHERE id=:id"""), {"e": u_etapa, "s": u_estatus, "a": u_avance, "c": u_carpeta, "p": u_plan, "u": ahora, "id": p_id})
              if u_comentario.strip(): conn.execute(sqlalchemy.text("""INSERT INTO bitacora (proyecto_id, usuario_nombre, fecha_hora, comentario) VALUES (:p_id, :usr, :fh, :com)"""), {"p_id": p_id, "usr": st.session_state.nombre_actual, "fh": ahora, "com": u_comentario.strip()})
            limpiar_cache_y_recargar(); st.rerun()

          if es_moderador and btn2.form_submit_button("Eliminar Iniciativa", type="secondary"):
            engine = obtener_engine()
            with engine.begin() as conn: conn.execute(sqlalchemy.text("DELETE FROM proyectos WHERE id=:id"), {"id": p_id})
            limpiar_cache_y_recargar(); st.rerun()

        # Historial
        historial_proyecto = df_bitacora[df_bitacora["proyecto_id"] == p_id]
        if not historial_proyecto.empty:
          st.markdown("<h5 style='margin-top: 12px; color:#0F172A; font-size:1rem;'>📜 Historial de Ejecución</h5>", unsafe_allow_html=True)
          for _, h_row in historial_proyecto.iterrows():
            st.markdown(f"<div class='timeline-item'><div class='timeline-date'>{h_row['fecha_hora']} | Registrado por: {h_row['usuario_nombre']}</div><div class='timeline-text'>{h_row['comentario']}</div></div>", unsafe_allow_html=True)

        # GANTT CHART
        st.markdown("<h4 style='color:#0F172A; margin-top: 25px; padding-top: 15px; border-top: 1px dashed #CBD5E1; font-size:1.05rem;'>📅 Cronograma de Ejecución y Tareas</h4>", unsafe_allow_html=True)
        df_tareas_proj = df_tareas_all[df_tareas_all["proyecto_id"] == p_id]
        df_tareas_calc = calcular_fechas_tarea_df(df_tareas_proj)

        if not df_tareas_calc.empty:
          fig = px.timeline(
              df_tareas_calc, x_start="fecha_inicio", x_end="fecha_fin", y="nombre_tarea",
              color="porcentaje_avance", text="avance_txt",
              color_continuous_scale=[[0, "#E2E8F0"], [0.5, "#3B82F6"], [1, "#05297A"]],
              range_color=[0, 100], hover_data={"responsable": True, "porcentaje_avance": False, "avance_txt": False}
          )
          fig.update_yaxes(autorange="reversed")
          fig.update_traces(textposition='inside', insidetextanchor='middle', marker_line_color='rgba(0,0,0,0.1)', marker_line_width=1, opacity=0.95, textfont=dict(color='white', size=11, weight='bold'))
          fig.update_layout(height=160 + (len(df_tareas_calc) * 35), margin=dict(l=0, r=0, t=10, b=0), font=dict(family="Inter"), xaxis=dict(showgrid=True, gridcolor="#F1F5F9"), yaxis=dict(showgrid=False, title=""), coloraxis_colorbar=dict(title="% Avance"))
          st.plotly_chart(fig, use_container_width=True)

          st.markdown("<p style='font-size:0.85rem; font-weight:700; color:#05297A;'>✏️ Actualizar Progreso de Tarea</p>", unsafe_allow_html=True)
          with st.form(f"upd_t_{p_id}", clear_on_submit=True):
            col_sel, col_val, col_btn = st.columns([2, 1, 1])
            opciones_tareas = df_tareas_calc.apply(lambda x: f"{x['id']} - {x['nombre_tarea']}", axis=1).tolist()
            t_sel = col_sel.selectbox("Seleccione Tarea", opciones_tareas)
            t_val = col_val.number_input("Nuevo % de Avance", min_value=0, max_value=100, step=10)
            st.write("")
            if col_btn.form_submit_button("Actualizar", type="secondary"):
              if t_sel:
                t_id_real = int(t_sel.split(" - ")[0])
                engine = obtener_engine()
                with engine.begin() as conn: conn.execute(sqlalchemy.text("UPDATE tareas SET porcentaje_avance=:a WHERE id=:id"), {"a": t_val, "id": t_id_real})
                limpiar_cache_y_recargar(); st.rerun()
        else: st.info("El plan de trabajo no tiene tareas configuradas.")

        with st.expander("➕ Configurar Nueva Tarea Operativa"):
          with st.form(f"ft_{p_id}", clear_on_submit=True):
            t_nom = st.text_input("Descripción de la Tarea *")
            c_t1, c_t2, c_t3, c_t4 = st.columns(4)
            t_res = c_t1.selectbox("Responsable", lista_lideres_registrados)
            t_ini = c_t2.date_input("Fecha de Inicio")
            t_dur = c_t3.number_input("Duración (Días)", 1, value=5)
            t_pre = c_t4.text_input("IDs Predecesoras (Ej. 1, 2)")
            if st.form_submit_button("Guardar en Cronograma"):
              if t_nom.strip():
                engine = obtener_engine()
                with engine.begin() as conn: conn.execute(sqlalchemy.text("""INSERT INTO tareas (proyecto_id, nombre_tarea, responsable, fecha_inicio, duracion_dias, fecha_fin, porcentaje_avance, predecesoras) VALUES (:pid, :n, :r, :fi, :d, :ff, 0.0, :p)"""), {"pid": p_id, "n": t_nom, "r": t_res, "fi": str(t_ini), "d": t_dur, "ff": str(pd.to_datetime(t_ini) + timedelta(days=t_dur - 1)), "p": t_pre})
                limpiar_cache_y_recargar(); st.rerun()

# PESTAÑA 3: VISTA KANBAN
with tabs[2]:
  st.write("")
  if df.empty: st.info("Datos insuficientes para el tablero Kanban.")
  else:
    k_cols = st.columns(len(OPCIONES_ESTATUS))
    for i, status in enumerate(OPCIONES_ESTATUS):
      with k_cols[i]:
        st.markdown(f"<div style='background-color:#F8FAFC; padding:8px; border-radius:6px; border:1px solid #E2E8F0; text-align:center; font-weight:700; color:#0F172A; font-size:0.85rem; margin-bottom:12px;'>{status.upper()}</div>", unsafe_allow_html=True)
        df_k = df[df["estatus_tiempo"] == status]
        for _, k_row in df_k.iterrows():
          st.markdown(f"<div class='kanban-card'><div class='kanban-title'>{k_row['nombre']}</div><div class='kanban-meta'>👤 {k_row['lider_asignado']}</div><div class='kanban-meta'>📈 {int((k_row['avance_real'] or 0)*100)}% Avance</div><div class='kanban-meta' style='margin-top:6px;'><i>Folio: {k_row['folio'] or 'S/F'}</i></div></div>", unsafe_allow_html=True)

# PESTAÑA 4: NUEVO PROYECTO
with tabs[3]:
  st.write("")
  if es_moderador:
    with st.form("f_nuevo", clear_on_submit=True):
      st.markdown("<h3 style='font-size:1.2rem; color:#0F172A; margin-bottom:15px;'>Registro de Nueva Iniciativa</h3>", unsafe_allow_html=True)
      c1, c2, c3 = st.columns(3); folio = c1.text_input("Folio Asignado"); nombre = c2.text_input("Denominación del Proyecto *"); lider = c3.selectbox("Responsable Operativo *", lista_lideres_registrados)
      c4, c5, c6 = st.columns(3); area = c4.selectbox("Área Solicitante", OPCIONES_AREAS); tipo = c5.selectbox("Categoría Principal", OPCIONES_TIPOS); subtipo = c6.selectbox("Subcategoría Específica", OPCIONES_SUBTIPOS)
      c7, c8, c9 = st.columns(3); gerente = c7.selectbox("Gerente Sponsor", OPCIONES_GERENTES); etapa = c8.selectbox("Fase Inicial", OPCIONES_ETAPAS); estatus_inicial = c9.selectbox("Estado", OPCIONES_ESTATUS, index=0)
      if st.form_submit_button("Crear Registro Institucional", type="primary"):
        if nombre.strip():
          engine = obtener_engine()
          with engine.begin() as conn: conn.execute(sqlalchemy.text("""INSERT INTO proyectos (folio, nombre, area_negocio, tipo_proyecto, subtipo, gerente, lider_asignado, etapa_actual, estatus_tiempo, avance_real) VALUES (:f, :n, :a, :t, :s, :g, :l, :e, :st, 0)"""), {"f": folio, "n": nombre, "a": area, "t": tipo, "s": subtipo, "g": gerente, "l": lider, "e": etapa, "st": estatus_inicial})
          limpiar_cache_y_recargar(); st.success("Registro completado con éxito."); st.rerun()
        else: st.error("El nombre del proyecto es obligatorio.")

# PESTAÑA 5: USUARIOS (Solo Moderador) - AHORA MUESTRA CONTRASEÑAS
if es_moderador:
  with tabs[4]:
    st.write("")
    df_users = df_users_raw.copy()
    # Mapeo de columnas para mostrar de forma ejecutiva la base de usuarios (Incluyendo Contraseña)
    df_users.columns = ["Colaborador", "Correo Corporativo", "Contraseña Asignada", "Nivel de Acceso"]

    col_table, col_forms = st.columns([1.5, 1])
    with col_table:
      st.markdown("<h4>Directorio de Acceso</h4>", unsafe_allow_html=True)
      st.dataframe(df_users, use_container_width=True, hide_index=True)

    with col_forms:
      with st.form("f_alta"):
        st.markdown("<h4>Generar Credencial</h4>", unsafe_allow_html=True)
        n_nom = st.text_input("Nombre del Colaborador")
        n_cor = st.text_input("Correo Institucional")
        n_pas = st.text_input("Clave Temporal") # Quitamos type password para el admin vea que escribe
        n_rol = st.selectbox("Perfil de Seguridad", ["Usuario", "Moderador"])
        if st.form_submit_button("Registrar en Sistema", type="primary"):
          if n_cor and n_pas and n_nom:
            try:
              engine = obtener_engine()
              with engine.begin() as conn: conn.execute(sqlalchemy.text("INSERT INTO usuarios VALUES (:c, :p, :r, :n)"), {"c": n_cor.strip().lower(), "p": n_pas, "r": n_rol, "n": n_nom})
              limpiar_cache_y_recargar(); st.rerun()
            except: st.error("El correo institucional ya cuenta con registro.")

      with st.form("f_baja"):
        lista_correos = df_users["Correo Corporativo"].tolist()
        if st.session_state.correo_actual in lista_correos: lista_correos.remove(st.session_state.correo_actual)
        correo_borrar = st.selectbox("Revocar Acceso a:", ["Seleccionar..."] + lista_correos)
        if st.form_submit_button("Eliminar Registro", type="secondary"):
          if correo_borrar != "Seleccionar...":
            engine = obtener_engine()
            with engine.begin() as conn: conn.execute(sqlalchemy.text("DELETE FROM usuarios WHERE correo=:c"), {"c": correo_borrar})
            limpiar_cache_y_recargar(); st.rerun()


# ==============================================================================
# --- MOTOR NLP REESTRUCTURADO (MULTIENTIDAD CON FILTRADO DE SALUDOS) ---
# ==============================================================================
def consultar_ia_ultra_rapido(prompt, dataframe, usuario_nombre="Colaborador"):
  p_lower = prompt.lower().strip()
  p_analizar = p_lower
  saludos_lista = ["hola", "buenos dias", "buenas tardes", "buenas noches", "que tal", "que onda", "ey", "saludos", "buenas", "por favor", "quisiera saber", "quiero saber", "me dices", "dime", "podrias decirme"]
  for s in saludos_lista:
    if p_analizar.startswith(s): p_analizar = p_analizar[len(s) :].strip()

  if len(p_analizar) <= 2:
    tot = len(dataframe) if not dataframe.empty else 0
    ret = len(dataframe[dataframe["estatus_tiempo"].isin(["Retrasado", "Detenido"])]) if not dataframe.empty else 0
    resp = f"¡Hola, **{usuario_nombre}**! 👋 Soy tu Asistente **Project IA**.\n\nActualmente el portafolio corporativo cuenta con **{tot} iniciativas**. "
    if ret > 0: resp += f"⚠️ Se detectan **{ret} proyectos que requieren atención** por retrasos en el plan. ¿Qué datos deseas analizar?"
    else: resp += " Las métricas globales están en orden. ¿Qué información requieres extraer de la base de datos?"
    return resp

  if dataframe.empty: return "La base de datos del portafolio no tiene registros activos."

  if any(k in p_analizar for k in ["gerente", "patrocinador", "sponsor", "gerentes"]):
    if "gerente" in dataframe.columns and not dataframe["gerente"].isna().all():
      counts_g = dataframe["gerente"].value_counts()
      if not counts_g.empty:
        top_g = counts_g.index[0]; top_val = counts_g.iloc[0]; pct = (top_val / len(dataframe)) * 100
        res = f"El Gerente con **mayor asignación de proyectos** es **{top_g}**, con **{top_val} iniciativa(s)** ({pct:.0f}% del portafolio).\n\n📌 **Desglose Ejecutivo por Gerente:**\n"
        for g_name, val in counts_g.items(): res += f"* **{g_name}**: {val} registro(s)\n"
        return res
    return "La consulta no devolvió resultados para la entidad Gerente."

  if any(k in p_analizar for k in ["lider", "líder", "responsable", "colaborador", "encargado", "lideres", "líderes"]) and any(k in p_analizar for k in ["mas", "más", "mayor", "quien", "quién", "carga", "numero"]):
    counts_l = dataframe["lider_asignado"].value_counts(); top_l = counts_l.index[0]; top_val = counts_l.iloc[0]; pct = (top_val / len(dataframe)) * 100
    res = f"El Líder Operativo con **mayor carga de proyectos** es **{top_l}**, con **{top_val} iniciativa(s)** ({pct:.0f}% del total).\n\n📌 **Carga Operativa por Responsable:**\n"
    for l_name, val in counts_l.items(): res += f"* **{l_name}**: {val} proyecto(s)\n"
    return res

  if any(k in p_analizar for k in ["area", "área", "departamento", "areas"]):
    counts_a = dataframe["area_negocio"].value_counts(); top_a = counts_a.index[0]; top_val = counts_a.iloc[0]; pct = (top_val / len(dataframe)) * 100
    res = f"El Área de Negocio que concentra la **mayor cantidad de iniciativas** es **{top_a}**, con **{top_val} registro(s)** ({pct:.0f}% del portafolio).\n\n📌 **Distribución Departamental:**\n"
    for a_name, val in counts_a.items(): res += f"* **{a_name}**: {val} registro(s)\n"
    return res

  if any(k in p_analizar for k in ["retras", "riesgo", "deteni", "critico", "problema", "urgente", "alerta"]):
    p_ret = dataframe[dataframe["estatus_tiempo"].isin(["Retrasado", "Detenido"])]
    if p_ret.empty: return "Las métricas indican que no existen proyectos en riesgo ni retraso documentado."
    res = f"🚨 **Atención:** Se identificaron **{len(p_ret)} iniciativa(s)** en estado crítico u observación:\n\n"
    for _, r in p_ret.iterrows(): res += f"* **{r['folio'] or 'S/F'} — {r['nombre']}**\n  * 🏢 **Área:** {r['area_negocio']} | 👤 **Líder:** {r['lider_asignado']}\n  * ⚠️ **Estatus:** `{r['estatus_tiempo']}` | 📈 **Progreso:** {int((r['avance_real'] or 0)*100)}%\n\n"
    return res

  areas_found = [a for a in OPCIONES_AREAS if a.lower() in p_analizar]
  if areas_found:
    area = areas_found[0]; p_area = dataframe[dataframe["area_negocio"] == area]
    if p_area.empty: return f"Consulta vacía. Sin iniciativas para el área: **{area}**."
    res = f"📂 **Registros operativos para el área {area} ({len(p_area)}):**\n\n"
    for _, r in p_area.iterrows(): res += f"* **{r['nombre']}** (`{r['folio'] or 'S/F'}`)\n  * 👤 **Responsable:** {r['lider_asignado']} | 📌 **Estatus:** `{r['estatus_tiempo']}` | 📈 **Progreso:** {int((r['avance_real'] or 0)*100)}%\n\n"
    return res

  lideres = obtener_lista_usuarios(df_users_raw) + OPCIONES_GERENTES
  personas_found = [p for p in set(lideres) if p.lower() in p_analizar and len(p) > 3]
  if personas_found:
    persona = personas_found[0]; p_persona = dataframe[(dataframe["lider_asignado"] == persona) | (dataframe["gerente"] == persona)]
    if p_persona.empty: return f"La búsqueda no devolvió asignaciones para el colaborador: **{persona}**."
    res = f"👤 **Reporte de asignaciones para {persona} ({len(p_persona)}):**\n\n"
    for _, r in p_persona.iterrows(): res += f"* **{r['nombre']}** (`{r['folio'] or 'S/F'}`)\n  * 🏢 **Área:** {r['area_negocio']} | 📌 **Estatus:** `{r['estatus_tiempo']}` | 📈 **Progreso:** {int((r['avance_real'] or 0)*100)}%\n\n"
    return res

  tot = len(dataframe)
  return f"Búsqueda ejecutada, **{usuario_nombre}**. La base de datos central cuenta con **{tot} registros**. Para mayor exactitud, por favor formula la consulta refiriendo a Áreas, Gerentes, Líderes o Análisis de Retrasos."

# --- BOTÓN FLOTANTE "PROJECT IA" CON AVATARES 3D ---
with st.popover("🤖 Project IA", help="Asistente Ejecutivo de Análisis de Portafolio"):
  st.markdown("<h3 style='color:#05297A; margin-bottom: 0px;'>🤖 Project IA</h3>", unsafe_allow_html=True)
  st.caption("Motor de Inteligencia de Datos Corporativos (Off-grid).")
  st.divider()

  if "chat_history_fast" not in st.session_state:
    st.session_state.chat_history_fast = [{"role": "assistant", "content": f"Saludos **{st.session_state.nombre_actual}**. Soy **Project IA**, tu analista de datos asignado. ¿Qué métrica analizaremos hoy?"}]

  chat_box = st.container(height=350)
  with chat_box:
    for msg in st.session_state.chat_history_fast:
      avatar_img = URL_ROBOT if msg["role"] == "assistant" else URL_USER
      with st.chat_message(msg["role"], avatar=avatar_img):
        st.markdown(msg["content"])

  if prompt_fast := st.chat_input("Ingrese su instrucción analítica...", key="ia_fast_input"):
    st.session_state.chat_history_fast.append({"role": "user", "content": prompt_fast})
    ans = consultar_ia_ultra_rapido(prompt_fast, df, st.session_state.nombre_actual)
    st.session_state.chat_history_fast.append({"role": "assistant", "content": ans})
    st.rerun()
