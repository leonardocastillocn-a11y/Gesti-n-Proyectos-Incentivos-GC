import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Portafolio de Incentivos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- BASE DE DATOS ---
def obtener_conexion():
    conn = sqlite3.connect("portafolio_incentivos.db", check_same_thread=False)
    return conn


def inicializar_db():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio TEXT,
            nombre TEXT NOT NULL,
            atencion TEXT,
            area_negocio TEXT,
            tipo_proyecto TEXT,
            subtipo TEXT,
            puestos_impactar TEXT,
            inicio_planificado TEXT,
            fin_planificado TEXT,
            nacional_incentivos TEXT,
            gerente_incentivos TEXT,
            lider_asignado TEXT,
            origen_presupuesto TEXT,
            etapa_actual TEXT,
            estatus_tiempo TEXT,
            avance_real REAL,
            resumen_estatus TEXT,
            carpeta_url TEXT,
            plan_url TEXT,
            ultima_actualizacion TEXT
        )
    """
    )
    conn.commit()
    conn.close()


inicializar_db()

# --- OPCIONES DESDE TU EXCEL (Pestaña Datos) ---
OPCIONES_ATENCION = [
    "Activo",
    "Por atender",
    "Finalizado",
    "Detenido",
    "Cancelado",
]
OPCIONES_AREAS = [
    "Incentivos",
    "Banca Empresarial",
    "Crédito Automotriz",
    "Inmobiliaria",
    "Afore",
    "Banco",
    "CAT Cobranza",
    "CAT P&V",
    "CEDIS",
    "Cobranza Domiciliaria",
    "Retail",
    "Sale Vale",
]
OPCIONES_TIPOS = [
    "Tecnología",
    "Estratégicos",
    "Esquema de incentivos",
    "Procesos",
    "Campañas",
    "Auditorías",
]
OPCIONES_SUBTIPOS = [
    "TE-Software",
    "TE-Tableros",
    "EI-Nuevo incentivo completo",
    "EI-Actualización completa de incentivo",
    "EI-Ajuste menor de incentivo",
    "EI-Ajuste mayor de incentivo",
    "EI-Casos especiales",
    "CA-Campaña",
    "CA-Concurso",
    "PR-Documentación oficial",
    "PR-Nuevo proceso",
    "Otros",
]
OPCIONES_ETAPAS = [
    "0. Por iniciar",
    "1. Planeación",
    "2. Ejecución",
    "3. Cierre",
    "1. Diseño (EI)",
    "2. Prueba piloto (EI)",
    "3. Escalamiento nacional (EI)",
    "4. Cierre (EI)",
    "1. Diseño (CA)",
    "2. Implementación (CA)",
    "3. Evaluación y cierre (CA)",
]
OPCIONES_ESTATUS = [
    "En tiempo",
    "Retrasado",
    "Detenido",
    "Cancelado",
    "Por iniciar",
]
OPCIONES_NACIONAL = [
    "Giovanni Vallejo",
    "Ruben Rivera",
    "Sin Asignar",
]
OPCIONES_GERENTE = [
    "Andres Avila",
    "Eduardo Rodriguez",
    "Heriberto Vega",
    "Janik Orozco",
    "Kurokusi Ochoa",
    "Noel Aquino",
    "Yahir Ramirez",
    "Giovanni Vallejo",
    "Ruben Rivera",
]
OPCIONES_LIDER = [
    "Leonardo Castillo",
    "Alejandra Torres",
    "Andres Avila",
    "Elvis Garcia",
    "Becario",
    "Constantino Flores",
    "Teresita Marquez",
]
OPCIONES_ORIGEN = ["Coppel", "BanCoppel", "Proveedor", "Otro"]

# --- BARRA LATERAL: CONTROL DE ACCESO Y ROLES ---
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60
)
st.sidebar.title("Sistema de Incentivos")

rol_usuario = st.sidebar.selectbox(
    "👤 Selecciona tu perfil:",
    ["Moderador (Administrador)", "Usuario Normal (Líder/Colaborador)"],
)
es_moderador = rol_usuario == "Moderador (Administrador)"

if es_moderador:
    st.sidebar.success("🔑 Modo Moderador Activo: Tienes permisos completos.")
else:
    st.sidebar.info(
        "👥 Modo Usuario Normal: Puedes consultar y actualizar tus avances."
    )

st.sidebar.divider()

# --- CONSULTA DE DATOS ---
conn = obtener_conexion()
df_proyectos = pd.read_sql_query("SELECT * FROM proyectos", conn)
conn.close()

# --- TABLERO PRINCIPAL / MÉTRICAS ---
st.title("📊 Portafolio de Proyectos de Incentivos")

if not df_proyectos.empty:
    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    total_proj = len(df_proyectos)
    en_tiempo = len(
        df_proyectos[df_proyectos["estatus_tiempo"] == "En tiempo"]
    )
    retrasados = len(
        df_proyectos[df_proyectos["estatus_tiempo"] == "Retrasado"]
    )
    detenidos = len(df_proyectos[df_proyectos["estatus_tiempo"] == "Detenido"])
    completados = len(df_proyectos[df_proyectos["atencion"] == "Finalizado"])

    col_m1.metric("Total Proyectos", total_proj)
    col_m2.metric("🟢 En Tiempo", en_tiempo)
    col_m3.metric("🔴 Retrasados", retrasados)
    col_m4.metric("🟡 Detenidos", detenidos)
    col_m5.metric("✅ Finalizados", completados)
    st.divider()

# --- SECCIÓN 1: CREAR NUEVO PROYECTO (Solo Moderador) ---
if es_moderador:
    with st.expander(
        "➕ **Crear Nuevo Proyecto (Exclusivo Moderador)**", expanded=False
    ):
        with st.form("form_crear_proyecto", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                folio = st.text_input("Folio (ej. INC-TE-010)")
                nombre = st.text_input("Nombre del Proyecto *")
                area = st.selectbox("Área del Negocio", OPCIONES_AREAS)
                tipo = st.selectbox("Tipo de Proyecto", OPCIONES_TIPOS)
                subtipo = st.selectbox("Subtipo", OPCIONES_SUBTIPOS)
            with c2:
                atencion = st.selectbox("Atención", OPCIONES_ATENCION)
                etapa = st.selectbox("Etapa Actual", OPCIONES_ETAPAS)
                estatus_t = st.selectbox(
                    "Estatus de Tiempo", OPCIONES_ESTATUS
                )
                avance = st.slider(
                    "% Avance Real",
                    0.0,
                    1.0,
                    0.0,
                    0.05,
                    format="%.2f",
                )
                origen = st.selectbox(
                    "Origen de Presupuesto", OPCIONES_ORIGEN
                )
            with c3:
                nac = st.selectbox(
                    "Nacional de Incentivos", OPCIONES_NACIONAL
                )
                gte = st.selectbox("Gerente de Incentivos", OPCIONES_GERENTE)
                lider = st.selectbox("Líder Asignado", OPCIONES_LIDER)
                f_inicio = st.date_input("Inicio Planificado")
                f_fin = st.date_input("Fin Planificado")

            puestos = st.text_area("Puestos a Impactar (ID - Nombre)")
            resumen = st.text_area("Resumen de Estatus / Bitácora inicial")
            c_url, p_url = st.columns(2)
            carpeta = c_url.text_input("URL Carpeta Drive")
            plan = p_url.text_input("URL Plan de Trabajo (Excel/Sheets)")

            btn_guardar = st.form_submit_button("🚀 Guardar Proyecto")

            if btn_guardar:
                if nombre.strip():
                    conn = obtener_conexion()
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO proyectos (
                            folio, nombre, atencion, area_negocio, tipo_proyecto, subtipo,
                            puestos_impactar, inicio_planificado, fin_planificado,
                            nacional_incentivos, gerente_incentivos, lider_asignado,
                            origen_presupuesto, etapa_actual, estatus_tiempo, avance_real,
                            resumen_estatus, carpeta_url, plan_url, ultima_actualizacion
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            folio,
                            nombre,
                            atencion,
                            area,
                            tipo,
                            subtipo,
                            puestos,
                            str(f_inicio),
                            str(f_fin),
                            nac,
                            gte,
                            lider,
                            origen,
                            etapa,
                            estatus_t,
                            avance,
                            resumen,
                            carpeta,
                            plan,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                    )
                    conn.commit()
                    conn.close()
                    st.success("¡Proyecto registrado correctamente!")
                    st.rerun()
                else:
                    st.error("El nombre del proyecto es obligatorio.")

# --- SECCIÓN 2: FILTROS Y CONSULTA ---
st.subheader("🔍 Portafolio de Proyectos")

col_f1, col_f2, col_f3 = st.columns(3)
filtro_area = col_f1.selectbox(
    "Filtrar por Área", ["Todas"] + OPCIONES_AREAS
)
filtro_estatus = col_f2.selectbox(
    "Filtrar por Estatus Tiempo", ["Todos"] + OPCIONES_ESTATUS
)
filtro_lider = col_f3.selectbox(
    "Filtrar por Líder", ["Todos"] + OPCIONES_LIDER
)

conn = obtener_conexion()
df = pd.read_sql_query("SELECT * FROM proyectos", conn)
conn.close()

if not df.empty:
    if filtro_area != "Todas":
        df = df[df["area_negocio"] == filtro_area]
    if filtro_estatus != "Todos":
        df = df[df["estatus_tiempo"] == filtro_estatus]
    if filtro_lider != "Todos":
        df = df[df["lider_asignado"] == filtro_lider]

    for idx, row in df.iterrows():
        p_id = row["id"]
        # Color semáforo segun estatus
        color = "🟢" if row["estatus_tiempo"] == "En tiempo" else ("🔴" if row["estatus_tiempo"] == "Retrasado" else "🟡")
        
        with st.expander(
            f"{color} [{row['folio'] or 'SIN-FOLIO'}] **{row['nombre']}** — Líder: {row['lider_asignado']} | Avance: {int(row['avance_real']*100)}%"
        ):
            if es_moderador:
                # EDICIÓN COMPLETA (MODERADOR)
                st.caption("📝 *Modo Moderador: Editar cualquier parámetro*")
                with st.form(f"edit_mod_{p_id}"):
                    ec1, ec2, ec3 = st.columns(3)
                    efolio = ec1.text_input("Folio", row["folio"], key=f"f_{p_id}")
                    enombre = ec1.text_input("Nombre", row["nombre"], key=f"n_{p_id}")
                    eatencion = ec1.selectbox("Atención", OPCIONES_ATENCION, index=OPCIONES_ATENCION.index(row["atencion"]) if row["atencion"] in OPCIONES_ATENCION else 0, key=f"at_{p_id}")
                    earea = ec2.selectbox("Área", OPCIONES_AREAS, index=OPCIONES_AREAS.index(row["area_negocio"]) if row["area_negocio"] in OPCIONES_AREAS else 0, key=f"ar_{p_id}")
                    etipa = ec2.selectbox("Etapa", OPCIONES_ETAPAS, index=OPCIONES_ETAPAS.index(row["etapa_actual"]) if row["etapa_actual"] in OPCIONES_ETAPAS else 0, key=f"et_{p_id}")
                    eestatus = ec2.selectbox("Estatus Tiempo", OPCIONES_ESTATUS, index=OPCIONES_ESTATUS.index(row["estatus_tiempo"]) if row["estatus_tiempo"] in OPCIONES_ESTATUS else 0, key=f"es_{p_id}")
                    eavance = ec3.slider("% Avance", 0.0, 1.0, float(row["avance_real"] or 0.0), 0.05, key=f"av_{p_id}")
                    elider = ec3.selectbox("Líder Asignado", OPCIONES_LIDER, index=OPCIONES_LIDER.index(row["lider_asignado"]) if row["lider_asignado"] in OPCIONES_LIDER else 0, key=f"li_{p_id}")
                    
                    eresumen = st.text_area("Resumen / Bitácora", row["resumen_estatus"] or "", key=f"res_{p_id}")
                    
                    c_btn1, c_btn2 = st.columns([1, 5])
                    btn_actualizar = c_btn1.form_submit_button("💾 Actualizar")
                    btn_eliminar = c_btn2.form_submit_button("🗑️ Eliminar Proyecto")

                    if btn_actualizar:
                        conn = obtener_conexion()
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE proyectos SET 
                            folio=?, nombre=?, atencion=?, area_negocio=?, etapa_actual=?,
                            estatus_tiempo=?, avance_real=?, lider_asignado=?, resumen_estatus=?,
                            ultima_actualizacion=? WHERE id=?
                        """, (efolio, enombre, eatencion, earea, etipa, eestatus, eavance, elider, eresumen, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), p_id))
                        conn.commit()
                        conn.close()
                        st.success("Proyecto actualizado.")
                        st.rerun()

                    if btn_eliminar:
                        conn = obtener_conexion()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM proyectos WHERE id=?", (p_id,))
                        conn.commit()
                        conn.close()
                        st.warning("Proyecto eliminado.")
                        st.rerun()
            else:
                # VISTA / EDICIÓN BÁSICA (USUARIO NORMAL)
                st.write(f"**Área:** {row['area_negocio']} | **Tipo:** {row['tipo_proyecto']} ({row['subtipo']})")
                st.write(f"**Etapa Actual:** {row['etapa_actual']} | **Atención:** {row['atencion']}")
                st.write(f"**Gerente:** {row['gerente_incentivos']} | **Nacional:** {row['nacional_incentivos']}")
                if row["puestos_impactar"]:
                    st.info(f"**Puestos a Impactar:**\n{row['puestos_impactar']}")

                st.write("---")
                st.subheader("📝 Actualizar mi avance")
                with st.form(f"edit_user_{p_id}"):
                    u_col1, u_col2 = st.columns(2)
                    u_etapa = u_col1.selectbox("Etapa Actual", OPCIONES_ETAPAS, index=OPCIONES_ETAPAS.index(row["etapa_actual"]) if row["etapa_actual"] in OPCIONES_ETAPAS else 0, key=f"uet_{p_id}")
                    u_estatus = u_col1.selectbox("Estatus Tiempo", OPCIONES_ESTATUS, index=OPCIONES_ESTATUS.index(row["estatus_tiempo"]) if row["estatus_tiempo"] in OPCIONES_ESTATUS else 0, key=f"ues_{p_id}")
                    u_avance = u_col2.slider("% Avance Real", 0.0, 1.0, float(row["avance_real"] or 0.0), 0.05, key=f"uav_{p_id}")
                    u_resumen = st.text_area("Actualizar Resumen de Estatus / Bitácora", row["resumen_estatus"] or "", key=f"ures_{p_id}")

                    btn_user_update = st.form_submit_button("💾 Guardar Avance")
                    if btn_user_update:
                        conn = obtener_conexion()
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE proyectos SET etapa_actual=?, estatus_tiempo=?, avance_real=?, resumen_estatus=?, ultima_actualizacion=? WHERE id=?
                        """, (u_etapa, u_estatus, u_avance, u_resumen, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), p_id))
                        conn.commit()
                        conn.close()
                        st.success("¡Avance guardado con éxito!")
                        st.rerun()

                # Links a carpetas
                if row["carpeta_url"] or row["plan_url"]:
                    st.write("🔗 **Enlaces del proyecto:**")
                    if row["carpeta_url"]:
                        st.markdown(f"- [📁 Carpeta Google Drive]({row['carpeta_url']})")
                    if row["plan_url"]:
                        st.markdown(f"- [📅 Plan de Trabajo]({row['plan_url']})")
else:
    st.info("No hay proyectos registrados en el sistema.")
