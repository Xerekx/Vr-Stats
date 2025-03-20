import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# Obtener las credenciales directamente desde los secretos de Streamlit Cloud
creds_dict = st.secrets["google_creds"]

# Crear las credenciales utilizando la información del secreto
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

# Autorizar con Google Sheets
client = gspread.authorize(creds)

# ID del archivo de Google Sheets
SHEET_ID = "12vLjygoaI46vyrqw3EhqFrBN6c5lFHUdhibutxgapu4"

# Nombres de las pestañas en Google Sheets
players = ["Danz", "Lord", "Zedorzo", "King", "Albert"]

# Función para cargar la tabla principal (B:R) de la pestaña "Estadísticas generales"
def load_main_data():
    sheet = client.open_by_key(SHEET_ID).worksheet("Estadísticas generales")
    data = sheet.get_all_values()
    
    headers = data[1][1:18]  # Columnas B hasta R
    rows = [row[1:18] for row in data[2:]]
    
    return pd.DataFrame(rows, columns=headers)

# Función para cargar los datos extra de la pestaña "Estadísticas generales"
def load_extra_data():
    sheet = client.open_by_key(SHEET_ID).worksheet("Estadísticas generales")
    
    range_1 = sheet.get("T2:U16")
    range_2 = sheet.get("W2:X18")

    return range_1, range_2

# Función para cargar los datos de cada jugador (B:O)
def load_player_data(sheet_name):
    sheet = client.open_by_key(SHEET_ID).worksheet(sheet_name)
    data = sheet.get_all_values()
    
    headers = data[1][1:15]  # Columnas B hasta O (15 columnas)
    rows = [row[1:15] for row in data[2:]]  # Filas de datos desde la fila 3 en adelante
    
    return pd.DataFrame(rows, columns=headers)

# Interfaz en Streamlit con pestañas
st.title("📊 Visualizador de Datos en Google Sheets")

# Crear las pestañas principales
tabs = ["📈 Tabla Principal", "📊 Datos Extras"] + players
tab_selection = st.tabs(tabs)

# 📈 Pestaña de la tabla principal
with tab_selection[0]:
    try:
        df_main = load_main_data()
        st.dataframe(df_main, use_container_width=True)
    except Exception as e:
        st.error(f"Error al cargar los datos principales: {e}")

# 📊 Pestaña de datos extra
with tab_selection[1]:
    try:
        range_1, range_2 = load_extra_data()
        
        st.subheader("🔹 Winrate según side")
        st.table(range_1)

        st.subheader("🔹 Winrate según objetivos")
        st.table(range_2)

    except Exception as e:
        st.error(f"Error al cargar los datos extra: {e}")

# Función para cargar los tramos P2:S2, P11:T22, P23:T34 de cada jugador
def load_player_extra_data(sheet_name):
    sheet = client.open_by_key(SHEET_ID).worksheet(sheet_name)
    
    # Leer tramos Q2:T2, Q11:U22, Q23:U34, Q36:U39
    range_1 = sheet.get("Q2:T2")
    range_2 = sheet.get("Q11:U22")
    range_3 = sheet.get("Q23:U34")
    range_4 = sheet.get("Q36:U39")
    
    return range_1, range_2, range_3, range_4

# 🔥 Pestañas individuales para cada jugador
for i, player in enumerate(players, start=2):
    with tab_selection[i]:
        try:
            # Cargar los datos principales del jugador
            df_player = load_player_data(player)
            st.subheader(f"📌 Datos de {player}")
            st.dataframe(df_player, use_container_width=True)

            # Cargar y mostrar los tramos extra sin encabezados
            range_1, range_2, range_3, range_4 = load_player_extra_data(player)

            st.subheader("🔹 KDA")
            st.table(range_1)  # Mostrar sin encabezados

            st.subheader("🔹 Campeones más usados 1-4")
            st.table(range_2)  # Mostrar sin encabezados

            st.subheader("🔹 Campeones más usados 5-8")
            st.table(range_3)  # Mostrar sin encabezados

            st.subheader("🔹 Campeones enemigos 1-8")
            st.table(range_4)  # Mostrar sin encabezados

        except Exception as e:
            st.error(f"Error al cargar los datos de {player}: {e}")

