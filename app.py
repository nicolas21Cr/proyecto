import streamlit as st
import google.generativeai as genai
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Analista IA de Ventas", page_icon="📈")
st.title("🤖 Tu Analista Personal de Sheets")

# 1. Configuración de Seguridad (Input en la barra lateral para no quemar la clave)
api_key = st.sidebar.text_input("Ingresa tu Gemini API Key", type="password")

# 2. Configuración de Datos del Sheet
# Asegúrate de que este Sheet tenga acceso "Cualquiera con el link"
SHEET_ID = "1wsvS9D1PkJZUVdeUuZdJFP2uuPwJZi8Us7H6prgaJjg"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data
def cargar_datos():
    try:
        # on_bad_lines='skip' ayuda a evitar errores si el CSV tiene formato irregular
        return pd.read_csv(url, on_bad_lines='skip')
    except Exception as e:
        return None

# Solo ejecutamos si hay API Key
if not api_key:
    st.warning("⚠️ Por favor ingresa tu API Key en la barra lateral para continuar.")
    st.stop()

# Configurar GenAI
genai.configure(api_key=api_key)

# Carga de datos
df = cargar_datos()

if df is not None:
    st.success("¡Datos cargados con éxito! ✅")
    
    # Vista previa de los datos (opcional, para verificar que se leen bien)
    with st.expander("Ver datos cargados"):
        st.dataframe(df.head())

    # Inicializar historial de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensajes anteriores
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Input del usuario
    if prompt := st.chat_input("¿Qué quieres saber de tus ventas?"):
        # Mostrar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Convertir datos a texto (limitado a las primeras 50 filas para no saturar si es enorme)
        # Si tu tabla es pequeña, puedes quitar el .head(50)
        contexto_datos = df.head(50).to_string(index=False)
        
        full_prompt = (
            f"Actúa como un analista de datos experto. "
            f"Aquí tienes los datos de ventas en formato CSV:\n\n{contexto_datos}\n\n"
            f"Pregunta del usuario: {prompt}\n"
            f"Responde de forma concisa y basada solo en estos datos."
        )

        with st.chat_message("assistant"):
            try:
                # Usar Gemini 1.5 Flash
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(full_prompt)
                
                # Mostrar respuesta
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            except Exception as e_api:
                st.error(f"Error en la IA: {e_api}")

else:
    st.error("Error al cargar los datos. Verifica que el Google Sheet sea PÚBLICO (Cualquiera con el enlace).")
