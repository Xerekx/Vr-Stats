
import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import os
from google.auth.transport.requests import Request

# Configuración de credenciales
# scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
# creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
# client = gspread.authorize(creds)

#Obtén las credenciales de Google Drive desde el secreto
credentials_info = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

creds = Credentials.from_service_account_info(
    credentials_info,  # Obtén las credenciales desde el secreto
    scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
)

# Autenticación con Google Sheets
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

# Función para cargar los datos de cada jugador (B:N)
def load_player_data(sheet_name):
    sheet = client.open_by_key(SHEET_ID).worksheet(sheet_name)
    data = sheet.get_all_values()
    
    headers = data[1][1:14]  # Columnas B hasta N (14 columnas)
    rows = [row[1:14] for row in data[2:]]  # Filas de datos desde la fila 3 en adelante
    
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
        
        st.subheader("🔹 Datos de T2:U16")
        st.table(range_1)

        st.subheader("🔹 Datos de W2:X18")
        st.table(range_2)

    except Exception as e:
        st.error(f"Error al cargar los datos extra: {e}")


# Función para cargar los tramos P2:S2, P11:T22, P23:T34 de cada jugador
def load_player_extra_data(sheet_name):
    sheet = client.open_by_key(SHEET_ID).worksheet(sheet_name)
    
    # Leer tramos P2:S2, P11:T22, P23:T34
    range_1 = sheet.get("P2:S2")
    range_2 = sheet.get("P11:T22")
    range_3 = sheet.get("P23:T34")
    
    return range_1, range_2, range_3

# 🔥 Pestañas individuales para cada jugador
for i, player in enumerate(players, start=2):
    with tab_selection[i]:
        try:
            # Cargar los datos principales del jugador
            df_player = load_player_data(player)
            st.subheader(f"📌 Datos de {player}")
            st.dataframe(df_player, use_container_width=True)

            # Cargar y mostrar los tramos extra sin encabezados
            range_1, range_2, range_3 = load_player_extra_data(player)

            st.subheader("🔹 KDA")
            st.table(range_1)  # Mostrar sin encabezados

            st.subheader("🔹 Campeones más usados 1-4")
            st.table(range_2)  # Mostrar sin encabezados

            st.subheader("🔹 Campeones más usados 5-8")
            st.table(range_3)  # Mostrar sin encabezados

        except Exception as e:
            st.error(f"Error al cargar los datos de {player}: {e}")
