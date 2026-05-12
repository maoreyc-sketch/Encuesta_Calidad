import streamlit as st
import pandas as pd

# Requisito 1: Estilos
st.markdown("""
    <h1 style='font-family: Arial; font-size: 18pt; font-weight: bold; text-align: center;'>
        Ministerio de Educación Nacional
    </h1>
    <h2 style='font-family: Arial; font-size: 14pt; font-weight: bold; text-align: center;'>
        Encuesta de Calidad en la Información
    </h2>
""", unsafe_allow_html=True)

# Requisito 2: Carga de Base de Datos con el nombre real de tu archivo
@st.cache_data
def cargar_datos():
    # Usamos el nombre exacto que aparece en tu repositorio
    archivo_base = "EE 2026.xlsx"
    df = pd.read_csv(archivo_base, dtype=str)
    df['EMAIL'] = df['EMAIL'].str.strip().str.lower()
    return df

try:
    df_ee = cargar_datos()
    
    # Campo de búsqueda
    email_ingresado = st.text_input("Ingrese el correo electrónico del establecimiento:").strip().lower()

    if email_ingresado:
        resultado = df_ee[df_ee['EMAIL'] == email_ingresado]
        
        if not resultado.empty:
            st.success("Establecimiento localizado.")
            fila = resultado.iloc[0]
            
            # Estado de edición
            if 'editando' not in st.session_state:
                st.session_state.editando = False

            # Campos bloqueados (gris claro) inicialmente
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Nombre", value=fila['NOMBRE_ESTABLECIMIENTO'], disabled=not st.session_state.editando)
                st.text_input("Código DANE", value=fila['CODIGO_DANE'], disabled=not st.session_state.editando)
            with col2:
                st.text_input("Rector", value=fila['RECTOR'], disabled=not st.session_state.editando)
                st.text_input("Dirección", value=fila['DIRECCION'], disabled=not st.session_state.editando)

            # Requisito 3: Botón Actualizar
            if not st.session_state.editando:
                if st.button("Actualizar"):
                    st.session_state.editando = True
                    st.rerun()
            else:
                if st.button("Guardar Información"):
                    st.session_state.editando = False
                    st.success("Información actualizada en la base.")
                    # Aquí activaremos el paso a la encuesta
                    st.session_state.mostrar_encuesta = True
                    st.rerun()
        else:
            st.error("El correo no se encuentra en la base EE 2026.")

except Exception as e:
    st.error(f"Error al cargar la base de datos: {e}")
    st.info("Asegúrate de que el archivo 'EE 2026.xlsx' esté en la misma carpeta que este script.")