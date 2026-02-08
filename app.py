import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# Forzamos la versión de la API antes de cualquier otra cosa
os.environ["GOOGLE_API_VERSION"] = "v1"

# 1. Configuración de Seguridad
GENAI_API_KEY = "AIzaSyBk3xJh1ntrZ1yjFgaGy-W3ZGd3M4EPvcU" 
genai.configure(api_key=GENAI_API_KEY)

# 2. Configuración de Datos del Sheet
SHEET_ID = "1wsvS9D1PkJZUVdeUuZdJFP2uuPwJZi8Us7H6prgaJjg"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.set_page_config(page_title="Analista IA de Ventas", page_icon="📈")
st.title("🤖 Tu Analista Personal de Sheets")

@st.cache_data
def cargar_datos():
    return pd.read_csv(url)

try:
    df = cargar_datos()
    st.success("¡Datos cargados con éxito! ✅")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("¿Qué quieres saber de tus ventas?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Convertimos la tabla a un texto limpio
        contexto_datos = df.to_string(index=False)
        
        # PROMPT REFORZADO
        full_prompt = f"Eres un analista. Datos:\n{contexto_datos}\n Pregunta: {prompt}"

        with st.chat_message("assistant"):
            try:
                # LLAMADA DIRECTA AL MODELO
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(full_prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e_api:
                st.error(f"Error en la IA: {e_api}")

except Exception as e:
    st.error(f"Error de conexión: {e}")
