import sqlite3
import streamlit as st

st.set_page_config(page_title="Sistemita de Proyectos", page_icon="📌")


def obtener_conexion():
    conn = sqlite3.connect("proyectos.db", check_same_thread=False)
    return conn


def inicializar_db():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            responsable TEXT NOT NULL,
            estado TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


inicializar_db()

st.title("📌 Mi Sistemita de Proyectos")

# Formulario para agregar proyectos
with st.expander("➕ Agregar nuevo proyecto", expanded=True):
    with st.form("form_nuevo", clear_on_submit=True):
        nombre = st.text_input("Nombre del proyecto")
        responsable = st.text_input("Responsable")
        estado = st.selectbox(
            "Estado inicial", ["🔴 Por hacer", "🟡 En proceso", "🟢 Terminado"]
        )
        submit = st.form_submit_button("Guardar Proyecto")

        if submit:
            if nombre.strip() != "" and responsable.strip() != "":
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO proyectos (nombre, responsable, estado) VALUES (?, ?, ?)",
                    (nombre, responsable, estado),
                )
                conn.commit()
                conn.close()
                st.success("¡Proyecto guardado con éxito!")
                st.rerun()
            else:
                st.warning("Escribe el nombre y el responsable.")

# Lista de proyectos
st.subheader("📋 Lista de Proyectos")
conn = obtener_conexion()
cursor = conn.cursor()
cursor.execute("SELECT id, nombre, responsable, estado FROM proyectos")
proyectos = cursor.fetchall()
conn.close()

if not proyectos:
    st.info("No hay proyectos registrados aún.")
else:
    for p_id, p_nombre, p_responsable, p_estado in proyectos:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            st.write(f"**{p_nombre}**")
        with col2:
            st.write(f"👤 {p_responsable}")
        with col3:
            opciones = ["🔴 Por hacer", "🟡 En proceso", "🟢 Terminado"]
            idx = opciones.index(p_estado) if p_estado in opciones else 0
            nuevo = st.selectbox(
                "Estado",
                opciones,
                index=idx,
                key=f"est_{p_id}",
                label_visibility="collapsed",
            )
            if nuevo != p_estado:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE proyectos SET estado = ? WHERE id = ?",
                    (nuevo, p_id),
                )
                conn.commit()
                conn.close()
                st.rerun()
        with col4:
            if st.button("🗑️", key=f"del_{p_id}"):
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM proyectos WHERE id = ?", (p_id,)
                )
                conn.commit()
                conn.close()
                st.rerun()
