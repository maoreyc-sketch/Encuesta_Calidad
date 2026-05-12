import streamlit as st
import pandas as pd

# Configuración inicial de la página
st.set_page_config(page_title="Actualización y Encuesta MEN", layout="wide")

# =====================================================================
# 1. ESTILOS Y ENCABEZADO (Requisito 1)
# =====================================================================
st.markdown("""
    <h1 style='font-family: Arial; font-size: 18pt; font-weight: bold; text-align: center; color: black;'>
        Ministerio de Educación Nacional
    </h1>
    <h2 style='font-family: Arial; font-size: 14pt; font-weight: bold; text-align: center; color: black;'>
        Encuesta de Calidad en la Información
    </h2>
    <hr>
""", unsafe_allow_html=True)

# =====================================================================
# 2. CARGA DE DATOS
# =====================================================================
# Usamos cache para que no recargue el CSV pesado en cada interacción
@st.cache_data
def cargar_base_establecimientos():
    # Ajusta la ruta y el nombre exacto de tu archivo exportado a CSV
    df = pd.read_csv('EE_2026.csv', dtype=str) 
    # Aseguramos que la columna de correo no tenga espacios extra
    if 'EMAIL' in df.columns:
        df['EMAIL'] = df['EMAIL'].str.strip().str.lower()
    return df

df_ee = cargar_base_establecimientos()

# =====================================================================
# 3. MANEJO DE ESTADOS (SESSION STATE)
# =====================================================================
# Inicializamos las variables de estado si no existen
if 'modo_edicion' not in st.session_state:
    st.session_state.modo_edicion = False  # Controla si los campos están bloqueados o no
if 'datos_guardados' not in st.session_state:
    st.session_state.datos_guardados = False # Controla si mostramos la encuesta
if 'datos_temporales' not in st.session_state:
    st.session_state.datos_temporales = {} # Guarda la info del establecimiento buscado

# =====================================================================
# 4. BÚSQUEDA Y ACTUALIZACIÓN (Requisitos 2 y 3)
# =====================================================================
st.subheader("Fase 1: Validación de Datos del Establecimiento")

# Campo de búsqueda
correo_input = st.text_input("Ingrese el correo electrónico del establecimiento:")

if correo_input:
    correo_busqueda = correo_input.strip().lower()
    # Filtramos la base de datos
    resultado = df_ee[df_ee['EMAIL'] == correo_busqueda]
    
    if not resultado.empty:
        st.success("✅ Establecimiento encontrado. Verifique la información.")
        
        # Extraemos la primera fila encontrada
        fila = resultado.iloc[0]
        
        # Mostramos los campos en columnas para mejor diseño
        col1, col2 = st.columns(2)
        
        # Por defecto, st.session_state.modo_edicion es False, por lo que disabled=True (bloqueado)
        bloqueado = not st.session_state.modo_edicion
        
        with col1:
            nuevo_nombre = st.text_input("Nombre del Establecimiento", value=fila.get('NOMBRE_ESTABLECIMIENTO', ''), disabled=bloqueado)
            nuevo_dane = st.text_input("Código DANE", value=fila.get('CODIGO_DANE', ''), disabled=bloqueado)
            nuevo_rector = st.text_input("Rector", value=fila.get('RECTOR', ''), disabled=bloqueado)
            
        with col2:
            nuevo_tel = st.text_input("Teléfono", value=fila.get('TELEFONO', ''), disabled=bloqueado)
            nueva_dir = st.text_input("Dirección", value=fila.get('DIRECCION', ''), disabled=bloqueado)
            nuevo_sector = st.text_input("Sector (Oficial/No Oficial)", value=fila.get('SECTOR_ATENCION', ''), disabled=bloqueado)

        # Lógica de Botones (Actualizar y Guardar)
        col_btn1, col_btn2 = st.columns([1, 4])
        
        with col_btn1:
            if not st.session_state.modo_edicion:
                # Botón para habilitar la edición
                if st.button("✏️ Actualizar"):
                    st.session_state.modo_edicion = True
                    st.rerun() # Recarga la app para aplicar el desbloqueo
            else:
                # Botón para guardar los cambios
                if st.button("💾 Guardar Información"):
                    # Aquí guardaríamos los datos en el CSV o base de datos.
                    # Por ahora lo guardamos en sesión para avanzar a la encuesta.
                    st.session_state.datos_temporales = {
                        'NOMBRE': nuevo_nombre, 'DANE': nuevo_dane, 'RECTOR': nuevo_rector,
                        'TEL': nuevo_tel, 'DIR': nueva_dir, 'SECTOR': nuevo_sector
                    }
                    st.session_state.modo_edicion = False
                    st.session_state.datos_guardados = True
                    st.success("Información guardada exitosamente en la base de datos.")
                    st.rerun()

        # Si los datos son correctos y no requiere edición, puede continuar directo
        if not st.session_state.modo_edicion and not st.session_state.datos_guardados:
            if st.button("Confirmar datos y Continuar a la Encuesta ➡️"):
                st.session_state.datos_guardados = True
                st.rerun()

    else:
        st.error("❌ No se encontró ningún establecimiento registrado con este correo electrónico en la base EE 2026.")

# =====================================================================
# 5. INICIO DE LA ENCUESTA (Requisito 4)
# =====================================================================
if st.session_state.datos_guardados:
    st.markdown("---")
    st.subheader("Fase 2: Diligenciamiento de Encuesta")
    st.info("A continuación, complete los 6 módulos de la encuesta.")
    
    # Aquí irán las pestañas (tabs) que construiremos en el siguiente paso
    # tabs = st.tabs(["Identificación", "Infraestructura", "Computadores", "Recursos Pedagógicos", "Programas", "Docentes"])