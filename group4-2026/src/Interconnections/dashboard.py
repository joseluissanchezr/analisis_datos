import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

# --- Configuración de Página ---
st.set_page_config(page_title="Dashboard Interconexiones", layout="wide", page_icon="⚡")

# --- Estilos CSS Personalizados ---
st.markdown("""
<style>
    .reportview-container {
        background-color: #0E1117;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #F0F2F6;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# --- Rutas y Carga de Datos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "data", "processed"))
RESULTADOS_DIR = os.path.join(PROCESSED_DIR, "resultados")

@st.cache_data
def load_data():
    data = {}
    files = {
        "convergencia_detalle": os.path.join(RESULTADOS_DIR, "convergencia_detalle.csv"),
        "convergencia_mensual": os.path.join(RESULTADOS_DIR, "convergencia_mensual.csv"),
        "correlacion_mensual": os.path.join(RESULTADOS_DIR, "correlacion_mensual.csv"),
        "importexport_ES_FR": os.path.join(RESULTADOS_DIR, "importexport_mensualESFR.csv"),
        "importexport_FR_DE": os.path.join(RESULTADOS_DIR, "importexport_mensualFRDE.csv"),
        "congestiones_mensual": os.path.join(RESULTADOS_DIR, "congestiones_mensual.csv"),
        "datos_limpios": os.path.join(PROCESSED_DIR, "datos_limpios.csv")
    }
    for key, path in files.items():
        if os.path.exists(path):
            df = pd.read_csv(path, index_col=0, parse_dates=True)
            # Eliminar la zona horaria para facilitar el filtrado con fechas locales
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            data[key] = df
        else:
            data[key] = pd.DataFrame() # Fallback si no existe el archivo
    return data

data = load_data()

# --- Barra Lateral (Sidebar) ---
st.sidebar.title("Filtros ⚙️")

country_pair = st.sidebar.radio(
    "Selecciona Interconexión:",
    ("ES-FR", "FR-DE")
)

# Filtro de Fechas (Máximo 3 meses)
min_date = None
max_date = None
if not data["convergencia_detalle"].empty:
    min_date = data["convergencia_detalle"].index.min().date()
    max_date = data["convergencia_detalle"].index.max().date()
else:
    min_date = pd.to_datetime("2024-01-01").date()
    max_date = pd.to_datetime("2024-12-31").date()

date_range = st.sidebar.date_input(
    "Rango de Fechas (Máx 3 meses):",
    value=(min_date, min_date + timedelta(days=90)),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) != 2:
    st.warning("Por favor, selecciona una fecha de inicio y una fecha de fin.")
    st.stop()

start_date, end_date = date_range

if (end_date - start_date).days > 92:
    st.sidebar.error("El rango temporal no puede superar los 3 meses (92 días).")
    st.stop()

# --- Funciones Auxiliares para Filtrado ---
def filter_hourly_df(df):
    if df.empty: return df
    mask = (df.index.date >= start_date) & (df.index.date <= end_date)
    return df.loc[mask]

def filter_monthly_df(df):
    if df.empty: return df
    # Filtrar considerando el mes, ya que los datos mensuales pueden estar indexados a final de mes
    start_period = pd.Timestamp(start_date).to_period("M")
    end_period = pd.Timestamp(end_date).to_period("M")
    mask = (df.index.to_period("M") >= start_period) & (df.index.to_period("M") <= end_period)
    return df.loc[mask]

# Aplicar filtros
conv_det = filter_hourly_df(data["convergencia_detalle"])
conv_men = filter_monthly_df(data["convergencia_mensual"])
corr_men = filter_monthly_df(data["correlacion_mensual"])
impexp_key = "importexport_ES_FR" if country_pair == "ES-FR" else "importexport_FR_DE"
impexp_men = filter_monthly_df(data[impexp_key])
cong_men = filter_monthly_df(data["congestiones_mensual"])
dl = filter_hourly_df(data["datos_limpios"])

# --- Dashboard Principal ---
st.title(f"Dashboard Interconexiones: {country_pair} 🌍")
st.markdown(f"**Datos filtrados desde** `{start_date}` **hasta** `{end_date}`")

st.markdown("---")

# 1. Tabla de Import/Export (en la parte superior)
st.subheader("Datos de Importación/Exportación Mensual")
if country_pair == "ES-FR":
    st.text(r"Los datos de importación/exportación se basan en el flujo neto desde ES a FR.")
else:    st.text(r"Los datos de importación/exportación se basan en el flujo neto desde FR a DE.")
impexp_display = impexp_men.copy()
if not impexp_display.empty:
    # Formatear el índice para mostrar solo el mes/año
    impexp_display.index = impexp_display.index.strftime("%Y-%m")
    # Añadir unidades [MWh] a todos los nombres de las columnas
    impexp_display.columns = [f"{str(col)} [MWh]" for col in impexp_display.columns]
    # Asegurarnos de no mostrar columnas extras si no hacen falta, o formatear números
    st.dataframe(impexp_display.style.format("{:.2f}"), use_container_width=True)
else:
    st.info("Sin datos de importación/exportación para las fechas seleccionadas.")


# 2. Congestiones
st.markdown("---")
st.subheader("Horas de Congestión Mensuales")
st.text(r"Una congestión ocurre cuando el flujo real supera el 90% de la capacidad máxima de la línea (NTC).")
cong_col = f"horas_congestion_{country_pair.replace('-', '_')}"
if not cong_men.empty and cong_col in cong_men.columns:
    fig_cong = px.line(
        cong_men,
        y=cong_col,
        title=f"Total de Horas de Congestión ({country_pair})",
        labels={"index": "Mes", cong_col: "Nº de Horas Congestionadas"},
        template="plotly_dark",
        color_discrete_sequence=["#FFEA00"],
        markers=True
    )
    fig_cong.update_xaxes(tickformat="%Y-%m")
    st.plotly_chart(fig_cong, use_container_width=True)
else:
    st.info("Sin datos de congestión mensual.")


col1, col2 = st.columns(2)

# 5. Intercambios Mensuales (Import / Export)
with col1:
    st.subheader("Intercambios Mensuales")
    if country_pair == "ES-FR":
        st.text(r"Datos de importación/exportación desde el punto de vista Español.")
    else:
        st.text(r"Datos de importación/exportación desde el punto de vista Frances.")
    if not impexp_men.empty:
        fig_impexp = go.Figure()
        fig_impexp.add_trace(go.Scatter(
            x=impexp_men.index.strftime("%Y-%m"), y=impexp_men['total_exportado'],
            mode='lines+markers', name='Exportado',
            line=dict(color='#00E676')
        ))
        fig_impexp.add_trace(go.Scatter(
            x=impexp_men.index.strftime("%Y-%m"), y=impexp_men['total_importado'],
            mode='lines+markers', name='Importado',
            line=dict(color='#FF1744')
        ))
        fig_impexp.update_layout(
            title="Importaciones y Exportaciones Totales",
            template="plotly_dark",
            xaxis_title="Mes",
            yaxis_title="Volumen (MWh)"
        )
        fig_impexp.update_xaxes(tickformat="%Y-%m")
        st.plotly_chart(fig_impexp, use_container_width=True)
    else:
        st.info("Sin datos de intercambios mensuales.")


import streamlit as st


# 6. Intercambios Diarios
with col2:
    st.subheader("Intercambios Diarios")
    if country_pair == "ES-FR":
        st.text(r"Datos de importación/exportación desde el punto de vista Español.")
    else:
        st.text(r"Datos de importación/exportación desde el punto de vista Frances.")
    if not dl.empty:
        neto_col = f"neto_{country_pair.replace('-', '_')}_MWh"
        
        # Resample por día (sumar exportaciones e importaciones por separado)
        daily_export = dl[neto_col].apply(lambda x: x if x > 0 else 0).resample('D').sum()
        daily_import = dl[neto_col].apply(lambda x: x if x < 0 else 0).resample('D').sum()
        
        fig_daily = go.Figure()
        fig_daily.add_trace(go.Bar(
            x=daily_export.index, y=daily_export,
            name='Exportado', marker_color='#00E676'
        ))
        fig_daily.add_trace(go.Bar(
            x=daily_import.index, y=daily_import,
            name='Importado', marker_color='#FF1744'
        ))
        fig_daily.update_layout(
            title="Import/Export Diario",
            template="plotly_dark",
            barmode="relative",
            xaxis_title="Día",
            yaxis_title="Volumen (MWh)"
        )
        fig_daily.update_xaxes(tickformat="%Y-%m")
        st.plotly_chart(fig_daily, use_container_width=True)
    else:
        st.info("Sin datos limpios para intercambios diarios.")


st.markdown("---")

col3, col4 = st.columns(2)

# 3. Convergencia de precios (Hora a Hora)
with col3:
    st.subheader("Convergencia de Precios (Mensual)")
    st.text("Medimos esto con el SPREAD: diferencia de precio entre dos países.\n\tSpread ES-FR = precio_ES - precio_FR\n\tSi el spread es cercano a 0 → precios convergentes\n\tSi el spread es grande → mercados poco integrados o \n\tcongestionados.\n.")
    spread_men_col = f"spread_medio_{country_pair.replace('-', '_')}"
    if not conv_men.empty and spread_men_col in conv_men.columns:
        fig_spread_men = px.line(
            conv_men,
            y=spread_men_col,
            title=f"Spread Medio Mensual ({country_pair})",
            labels={"index": "Mes", spread_men_col: "Spread Promedio (EUR/MWh)"},
            template="plotly_dark",
            color_discrete_sequence=["#D500F9"],
            markers=True
        )
        # Asegurar que el eje x muestre formato de mes
        fig_spread_men.update_xaxes(tickformat="%Y-%m")
        st.plotly_chart(fig_spread_men, use_container_width=True)
    else:
        st.info("Sin datos de spread mensual.")

# 4. Correlación Mensual
with col4:
    st.subheader("Correlación Mensual de Precios")
    st.text("La correlación mide si los precios de dos países se muevena la vez en la misma dirección.\n\tCorrelación = 1.0  → se mueven exactamente igual\n\tCorrelación = 0.0  → no hay relación entre ellos\n\tCorrelación = -1.0 → se mueven en direcciones opuestas\nUna correlación alta indica mercados bien integrados.\n")
    corr_col = f"correlacion_{country_pair.replace('-', '_')}"
    if not corr_men.empty and corr_col in corr_men.columns:
        fig_corr = px.line(
            corr_men,
            y=corr_col,
            title=f"Correlación Mensual ({country_pair})",
            labels={"index": "Mes", corr_col: "Correlación (Pearson)"},
            template="plotly_dark",
            color_discrete_sequence=["#FF3D00"],
            markers=True
        )
        fig_corr.update_yaxes(range=[-1, 1])
        fig_corr.update_xaxes(tickformat="%Y-%m")
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Sin datos para correlación mensual.")


