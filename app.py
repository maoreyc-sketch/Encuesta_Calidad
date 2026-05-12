import streamlit as st
import pandas as pd

# Requisito 1: Estilos MEN
st.markdown("""
    <h1 style='font-family: Arial; font-size: 18pt; font-weight: bold; text-align: center;'>
        Ministerio de Educación Nacional
    </h1>
    <h2 style='font-family: Arial; font-size: 14pt; font-weight: bold; text-align: center;'>
        Encuesta de Calidad en la Información
    </h2>
    <hr>
""", unsafe_allow_html=True)

# Requisito 2: Carga de Base de Datos (Archivo XLSX)
@st.cache_data
def cargar_datos_ee():
    # Cargamos el archivo Excel y la hoja específica
    archivo_ee = "EE 2026.xlsx"
    # Se asume que la hoja se llama ESTABLECIMIENTOS_ABR2026 o es la primera
    df = pd.read_excel(archivo_ee, sheet_name=0, dtype=str)
    df['EMAIL'] = df['EMAIL'].str.strip().str.lower()
    return df

try:
    df_ee = cargar_datos_ee()
    
    # Campo de búsqueda por correo
    email_ingresado = st.text_input("Ingrese el correo electrónico del establecimiento:").strip().lower()

    if email_ingresado:
        resultado = df_ee[df_ee['EMAIL'] == email_ingresado]
        
        if not resultado.empty:
            fila = resultado.iloc[0]
            
            if 'editando' not in st.session_state:
                st.session_state.editando = False
            if 'encuesta_iniciada' not in st.session_state:
                st.session_state.encuesta_iniciada = False

            # Visualización de datos (Bloqueo gris claro)
            col1, col2 = st.columns(2)
            bloqueado = not st.session_state.editando
            
            with col1:
                nombre_act = st.text_input("Nombre", value=fila['NOMBRE_ESTABLECIMIENTO'], disabled=bloqueado)
                dane_act = st.text_input("Código DANE", value=fila['CODIGO_DANE'], disabled=bloqueado)
            with col2:
                rector_act = st.text_input("Rector", value=fila['RECTOR'], disabled=bloqueado)
                dir_act = st.text_input("Dirección", value=fila['DIRECCION'], disabled=bloqueado)

            # Requisito 3: Botón Actualizar y Guardar
            if not st.session_state.editando:
                if st.button("Actualizar"):
                    st.session_state.editando = True
                    st.rerun()
            else:
                if st.button("Guardar Información"):
                    st.session_state.editando = False
                    st.session_state.encuesta_iniciada = True
                    st.success("Información actualizada exitosamente.")
                    st.rerun()

            # --- INICIO DE LA ENCUESTA (Requisito 4) ---
            if st.session_state.encuesta_iniciada:
                st.markdown("### Diligenciamiento de Encuesta")
                
                # Lista de hojas dentro de Encuesta_Calidad.xlsx
                hojas = ["Identificación", "Infraestructura", "Computadores", "Recursos Pedagógicos", "Programas", "docentes"]
                tabs = st.tabs(hojas)
                
                for i, nombre_hoja in enumerate(hojas):
                    with tabs[i]:
                        try:
                            # Leemos la hoja correspondiente del Excel único
                            df_preguntas = pd.read_excel("Encuesta_Calidad.xlsx", sheet_name=nombre_hoja, skiprows=2)
                            
                            for idx, row in df_preguntas.iterrows():
                                preg = str(row.get('Pregunta / campo', ''))
                                tipo = str(row.get('Tipo de respuesta', '')).lower()
                                opts = str(row.get('Opciones o criterio', ''))
                                var = str(row.get('Variable', idx))
                                
                                if preg and preg != 'nan':
                                    st.write(f"**{preg}**")
                                    
                                    if 'lista' in tipo:
                                        opciones = [o.strip() for o in opts.split(';')] if ';' in opts else [opts]
                                        st.selectbox("Seleccione:", opciones, key=f"sel_{var}")
                                    elif 'numérico' in tipo:
                                        # Aplicamos restricción de enteros positivos
                                        st.number_input("Cantidad:", min_value=0, step=1, key=f"num_{var}")
                                    else:
                                        st.text_input("Respuesta:", key=f"txt_{var}")
                                    st.write("---")
                                    
                        except Exception as e:
                            st.error(f"No se pudo cargar la hoja '{nombre_hoja}': {e}")

        else:
            st.error("Correo no encontrado en la base de datos.")

except Exception as e:
    st.error(f"Error técnico: {e}")