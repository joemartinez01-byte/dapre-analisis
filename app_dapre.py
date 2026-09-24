import os
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Configuración de la página
st.set_page_config(
    page_title="Dashboard Contratación DAPRE",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 2. Carga optimizada de datos con conversión explícita de tipos
@st.cache_data
def cargar_datos():
  ruta = r"D:\DAPRE_Analisis\datos\CONTRATOS_DAPRE_2022_2026_LIMPIO.xlsx"
  df = pd.read_excel(ruta)

  df["anio_reporte"] = df["anio_reporte"].fillna(0).astype(int)

  # Convertir columnas de texto a string puro para prevenir errores en PyArrow/Streamlit
  cols_texto = [
      "numero_contrato",
      "modalidad_seleccion",
      "contratista",
      "objeto",
      "rubro",
  ]
  for col in cols_texto:
    if col in df.columns:
      df[col] = df[col].astype(str).str.strip()

  return df


df = cargar_datos()

# 3. Encabezado principal
st.title("📊 Dashboard de Contratación - DAPRE (2022 - 2026)")
st.caption(
    "Visualización interactiva y análisis de valor de los contratos públicos."
)
st.markdown("---")

# 4. Filtros interactivos en la barra lateral
st.sidebar.header("⚙️ Filtros de Control")

anios_unicos = sorted(df["anio_reporte"].unique())
anios_sel = st.sidebar.multiselect(
    "Filtrar por Año:", options=anios_unicos, default=anios_unicos
)

modalidades_unicas = sorted(df["modalidad_seleccion"].unique())
modalidades_sel = st.sidebar.multiselect(
    "Modalidad de Selección:",
    options=modalidades_unicas,
    default=modalidades_unicas,
)

rubros_unicos = sorted(df["rubro"].unique())
rubros_sel = st.sidebar.multiselect(
    "Rubro Presupuestal:", options=rubros_unicos, default=rubros_unicos
)

# Filtrar DataFrame
df_filtrado = df[
    (df["anio_reporte"].isin(anios_sel))
    & (df["modalidad_seleccion"].isin(modalidades_sel))
    & (df["rubro"].isin(rubros_sel))
]

# 5. Tarjetas de KPIs
total_monto = df_filtrado["valor_inicial_num"].sum()
total_contratos = len(df_filtrado)
promedio_contrato = (
    df_filtrado["valor_inicial_num"].mean() if total_contratos > 0 else 0
)

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("💰 Presupuesto Total Contratado", f"${total_monto:,.0f} COP")
kpi2.metric("📄 Total de Contratos", f"{total_contratos:,}")
kpi3.metric("🎯 Valor Promedio por Contrato", f"${promedio_contrato:,.0f} COP")

st.markdown("---")

# 6. Gráficos interactivos
col_g1, col_g2 = st.columns(2)

with col_g1:
  st.subheader("Evolución Anual del Gasto")
  g_anual = (
      df_filtrado.groupby("anio_reporte")["valor_inicial_num"]
      .sum()
      .reset_index()
  )
  fig_anual = px.bar(
      g_anual,
      x="anio_reporte",
      y="valor_inicial_num",
      labels={
          "anio_reporte": "Año",
          "valor_inicial_num": "Monto Total (COP)",
      },
      text_auto=".3s",
      color_discrete_sequence=["#004b87"],
  )
  fig_anual.update_layout(xaxis_type="category")
  st.plotly_chart(fig_anual, use_container_width=True)

with col_g2:
  st.subheader("Participación por Modalidad")
  g_mod = (
      df_filtrado.groupby("modalidad_seleccion")["valor_inicial_num"]
      .sum()
      .reset_index()
  )
  fig_mod = px.pie(
      g_mod,
      values="valor_inicial_num",
      names="modalidad_seleccion",
      hole=0.4,
      color_discrete_sequence=px.colors.qualitative.Bold,
  )
  st.plotly_chart(fig_mod, use_container_width=True)

col_g3, col_g4 = st.columns(2)

with col_g3:
  st.subheader("Top 10 Contratistas por Monto")
  top_10 = (
      df_filtrado.groupby("contratista")["valor_inicial_num"]
      .sum()
      .reset_index()
      .sort_values(by="valor_inicial_num", ascending=True)
      .tail(10)
  )
  fig_top = px.bar(
      top_10,
      x="valor_inicial_num",
      y="contratista",
      orientation="h",
      labels={
          "valor_inicial_num": "Monto Acumulado (COP)",
          "contratista": "Contratista",
      },
      color_discrete_sequence=["#2b5c8f"],
      text_auto=".3s",
  )
  st.plotly_chart(fig_top, use_container_width=True)

with col_g4:
  st.subheader("Distribución Presupuestal por Rubro")
  g_rubro = (
      df_filtrado.groupby("rubro")["valor_inicial_num"].sum().reset_index()
  )
  fig_rubro = px.bar(
      g_rubro,
      x="rubro",
      y="valor_inicial_num",
      color="rubro",
      labels={"rubro": "Rubro", "valor_inicial_num": "Monto Total (COP)"},
      text_auto=".3s",
  )
  st.plotly_chart(fig_rubro, use_container_width=True)

# 7. Tabla Exploradora
st.markdown("---")
st.subheader("📋 Explorador Detallado de Contratos")

busqueda = st.text_input(
    "🔎 Buscar por Contratista, Objeto o Número de Contrato:"
)

df_tabla = df_filtrado.copy()
if busqueda:
  filtro_txt = (
      df_tabla["contratista"].str.contains(busqueda, case=False, na=False)
      | df_tabla["objeto"].str.contains(busqueda, case=False, na=False)
      | df_tabla["numero_contrato"].str.contains(busqueda, case=False, na=False)
  )
  df_tabla = df_tabla[filtro_txt]

st.dataframe(
    df_tabla[
        [
            "anio_reporte",
            "numero_contrato",
            "modalidad_seleccion",
            "contratista",
            "objeto",
            "valor_inicial_num",
            "rubro",
        ]
    ],
    column_config={
        "anio_reporte": "Año",
        "numero_contrato": "N° Contrato",
        "modalidad_seleccion": "Modalidad",
        "contratista": "Contratista",
        "objeto": "Objeto Contractual",
        "valor_inicial_num": st.column_config.NumberColumn(
            "Valor (COP)", format="$ %,d"
        ),
        "rubro": "Rubro",
    },
    use_container_width=True,
    height=350,
)