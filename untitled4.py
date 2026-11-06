

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Desigualdad Global",
    page_icon="🌎",
    layout="wide"
)

BASE_URL = "https://api.worldbank.org/v2"

COUNTRIES = {
    "Colombia": "COL",
    "Brasil": "BRA",
    "Chile": "CHL",
    "Argentina": "ARG",
    "México": "MEX",
    "Perú": "PER",
    "Estados Unidos": "USA",
    "España": "ESP"
}

INDICATORS = {
    "Índice de Gini": "SI.POV.GINI",
    "Pobreza extrema": "SI.POV.DDAY"
}

# ==========================================
# 2. CONEXIÓN CON BANCO MUNDIAL
# ==========================================

@st.cache_data(ttl=3600)
def get_indicator(
    indicator,
    country="all",
    start_year=2000,
    end_year=2025
):

    url = (
        f"{BASE_URL}/country/{country}/indicator/"
        f"{indicator}"
    )

    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 20000
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    if not isinstance(result, list) or len(result) < 2:
        return pd.DataFrame()

    records = result[1]

    if not records:
        return pd.DataFrame()

    data = []

    for item in records:

        if item["value"] is not None:

            data.append({
                "country": item["country"]["value"],
                "country_code": item["countryiso3code"],
                "year": int(item["date"]),
                "value": float(item["value"])
            })

    return pd.DataFrame(data)


# ==========================================
# 3. ENCABEZADO
# ==========================================

st.title("🌎 DESIGUALDAD GLOBAL")

st.subheader(
    "Explorador de desigualdad económica mundial"
)

st.markdown("""
Consulta y compara indicadores económicos y sociales
de diferentes países utilizando datos oficiales del
Banco Mundial.
""")

st.divider()

# ==========================================
# 4. MENÚ LATERAL
# ==========================================

st.sidebar.title("📊 Navegación")

page = st.sidebar.radio(
    "Selecciona una sección:",
    [
        "Análisis por país",
        "Comparador de países"
    ]
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "Fuente: Banco Mundial | API pública"
)

# ==========================================
# 5. ANÁLISIS POR PAÍS
# ==========================================

if page == "Análisis por país":

    st.header("📍 Consulta de indicadores")

    col1, col2 = st.columns(2)

    with col1:
        country_name = st.selectbox(
            "Selecciona un país",
            list(COUNTRIES.keys())
        )

    with col2:
        indicator_name = st.selectbox(
            "Selecciona un indicador",
            list(INDICATORS.keys())
        )

    start_year, end_year = st.slider(
        "Selecciona el período",
        1990, 2025, (2000, 2025)
    )

    country_code = COUNTRIES[country_name]
    indicator_code = INDICATORS[indicator_name]

    try:

        with st.spinner("Consultando Banco Mundial..."):

            df = get_indicator(
                indicator_code,
                country_code,
                start_year,
                end_year
            )

        if df.empty:

            st.warning(
                "No existen datos disponibles para "
                "este país, indicador y período."
            )

        else:

            df = df.sort_values("year")

            latest = df.iloc[-1]

            # INDICADORES

            st.subheader("Resultados principales")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Último valor registrado",
                f"{latest['value']:.2f}"
            )

            col2.metric(
                "Último año disponible",
                int(latest["year"])
            )

            col3.metric(
                "Observaciones",
                len(df)
            )

            st.divider()

            # GRÁFICA

            st.subheader(
                f"Evolución de {indicator_name} en {country_name}"
            )

            fig = px.line(
                df,
                x="year",
                y="value",
                markers=True,
                labels={
                    "year": "Año",
                    "value": indicator_name
                },
                title=indicator_name
            )

            fig.update_traces(
                line_color="#159B80",
                marker_size=8
            )

            fig.update_layout(
                template="plotly_white",
                hovermode="x unified"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # TABLA

            st.subheader("Datos históricos")

            st.dataframe(
                df.sort_values(
                    "year",
                    ascending=False
                ),
                use_container_width=True,
                hide_index=True
            )

            # DESCARGA

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "📥 Descargar datos CSV",
                data=csv,
                file_name="datos_banco_mundial.csv",
                mime="text/csv"
            )

            st.caption(
                f"Fuente: Banco Mundial | "
                f"Indicador: {indicator_code}"
            )

    except requests.exceptions.RequestException as error:

        st.error(
            f"Error al conectar con el Banco Mundial: {error}"
        )

    except Exception as error:

        st.error(
            f"Se produjo un error: {error}"
        )


# ==========================================
# 6. COMPARADOR DE PAÍSES
# ==========================================

elif page == "Comparador de países":

    st.header("⚖️ Comparador de países")

    st.write(
        "Compara la evolución de la desigualdad "
        "entre dos países."
    )

    col1, col2 = st.columns(2)

    with col1:

        country1 = st.selectbox(
            "Primer país",
            list(COUNTRIES.keys()),
            index=0
        )

    with col2:

        country2 = st.selectbox(
            "Segundo país",
            list(COUNTRIES.keys()),
            index=1
        )

    start_year, end_year = st.slider(
        "Período de comparación",
        1990, 2025, (2000, 2025),
        key="comparison_years"
    )

    if country1 == country2:

        st.warning(
            "Debes seleccionar dos países diferentes."
        )

    else:

        code1 = COUNTRIES[country1]
        code2 = COUNTRIES[country2]

        try:

            with st.spinner(
                "Comparando datos de ambos países..."
            ):

                df1 = get_indicator(
                    "SI.POV.GINI",
                    code1,
                    start_year,
                    end_year
                )

                df2 = get_indicator(
                    "SI.POV.GINI",
                    code2,
                    start_year,
                    end_year
                )

            if df1.empty or df2.empty:

                st.warning(
                    "No existen suficientes datos para "
                    "comparar ambos países."
                )

            else:

                df1 = df1[["year", "value"]].rename(
                    columns={"value": country1}
                )

                df2 = df2[["year", "value"]].rename(
                    columns={"value": country2}
                )

                comparison = pd.merge(
                    df1,
                    df2,
                    on="year",
                    how="inner"
                ).sort_values("year")

                if comparison.empty:

                    st.warning(
                        "No hay años comunes con datos "
                        "disponibles para ambos países."
                    )

                else:

                    latest = comparison.iloc[-1]

                    st.caption(
                        f"Último año común: {int(latest['year'])}"
                    )

                    difference = abs(
                        latest[country1] -
                        latest[country2]
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        country1,
                        f"{latest[country1]:.2f}"
                    )

                    col2.metric(
                        country2,
                        f"{latest[country2]:.2f}"
                    )

                    col3.metric(
                        "Diferencia",
                        f"{difference:.2f} puntos"
                    )

                    # GRÁFICA COMPARATIVA

                    st.subheader(
                        "Evolución histórica del índice Gini"
                    )

                    chart_data = comparison.melt(
                        id_vars="year",
                        var_name="País",
                        value_name="Índice Gini"
                    )

                    fig = px.line(
                        chart_data,
                        x="year",
                        y="Índice Gini",
                        color="País",
                        markers=True,
                        title="Comparación de desigualdad"
                    )

                    fig.update_layout(
                        template="plotly_white",
                        yaxis_title="Índice Gini (0-100)",
                        xaxis_title="Año"
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

                    # TABLA

                    st.subheader("Comparación de datos")

                    st.dataframe(
                        comparison,
                        use_container_width=True,
                        hide_index=True
                    )

                    # INTERPRETACIÓN

                    st.subheader("Interpretación")

                    if latest[country1] > latest[country2]:

                        st.info(
                            f"En {int(latest['year'])}, "
                            f"{country1} presenta mayor "
                            f"desigualdad que {country2}, "
                            f"con una diferencia de "
                            f"{difference:.2f} puntos Gini."
                        )

                    elif latest[country1] < latest[country2]:

                        st.info(
                            f"En {int(latest['year'])}, "
                            f"{country2} presenta mayor "
                            f"desigualdad que {country1}, "
                            f"con una diferencia de "
                            f"{difference:.2f} puntos Gini."
                        )

                    else:

                        st.info(
                            "Ambos países tienen el mismo "
                            "índice Gini en ese año."
                        )

        except requests.exceptions.RequestException as error:

            st.error(
                f"Error al consultar el Banco Mundial: {error}"
            )

        except Exception as error:

            st.error(
                f"Se produjo un error: {error}"
            )


# ==========================================
# 7. PIE DE PÁGINA
# ==========================================

st.divider()

st.markdown(
    """
    **DESIGUALDAD GLOBAL**

    Proyecto académico de análisis económico.

    Fuente de información:
    [Banco Mundial](https://data.worldbank.org/)

    Los resultados dependen de la disponibilidad
    de observaciones oficiales para cada país y año.
    """
)




