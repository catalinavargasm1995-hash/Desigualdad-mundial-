


# ==========================================
# 1. INSTALAR E IMPORTAR LIBRERÍAS
# ==========================================



import requests
import pandas as pd
import plotly.express as px

BASE_URL = "https://api.worldbank.org/v2"


# ==========================================
# 2. FUNCIÓN PARA CONSULTAR EL BANCO MUNDIAL
# ==========================================

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
# 3. CONSULTAR ÍNDICE GINI DE COLOMBIA
# ==========================================

df_gini = get_indicator(
    indicator="SI.POV.GINI",
    country="COL",
    start_year=2000,
    end_year=2025
)

print("ÍNDICE GINI DE COLOMBIA")

display(df_gini.head(10))

print("Total de observaciones:", len(df_gini))


# ==========================================
# 4. CONSULTAR POBREZA EXTREMA
# ==========================================

df_pobreza = get_indicator(
    indicator="SI.POV.DDAY",
    country="COL",
    start_year=2000,
    end_year=2025
)

print("POBREZA EXTREMA EN COLOMBIA")

display(df_pobreza.head(10))


# ==========================================
# 5. COMPARAR DOS PAÍSES
# ==========================================

df_colombia = get_indicator(
    "SI.POV.GINI",
    "COL",
    2000,
    2025
)

df_brasil = get_indicator(
    "SI.POV.GINI",
    "BRA",
    2000,
    2025
)

# Organizar columnas

df_colombia = df_colombia[
    ["year", "value"]
].rename(
    columns={"value": "Colombia"}
)

df_brasil = df_brasil[
    ["year", "value"]
].rename(
    columns={"value": "Brasil"}
)

# Unir por año

comparacion = pd.merge(
    df_colombia,
    df_brasil,
    on="year",
    how="inner"
)

comparacion = comparacion.sort_values("year")

print("COMPARACIÓN COLOMBIA VS BRASIL")

display(comparacion)


# ==========================================
# 6. CALCULAR DIFERENCIA ENTRE PAÍSES
# ==========================================

if not comparacion.empty:

    comparacion["diferencia"] = (
        comparacion["Colombia"] -
        comparacion["Brasil"]
    )

    display(comparacion)

    ultimo = comparacion.iloc[-1]

    print("Último año común:", int(ultimo["year"]))

    print(
        "Diferencia del índice Gini:",
        round(ultimo["diferencia"], 2),
        "puntos"
    )


# ==========================================
# 7. GRÁFICA COMPARATIVA
# ==========================================

if not comparacion.empty:

    datos_grafica = comparacion.melt(
        id_vars="year",
        value_vars=["Colombia", "Brasil"],
        var_name="País",
        value_name="Índice Gini"
    )

    fig = px.line(
        datos_grafica,
        x="year",
        y="Índice Gini",
        color="País",
        markers=True,
        title="Desigualdad económica: Colombia vs Brasil",
        labels={
            "year": "Año",
            "Índice Gini": "Índice Gini (0-100)"
        }
    )

    fig.show()


# ==========================================
# 8. COMPARAR VARIOS PAÍSES
# ==========================================

paises = {
    "Colombia": "COL",
    "Brasil": "BRA",
    "Chile": "CHL",
    "Argentina": "ARG",
    "México": "MEX",
    "Perú": "PER"
}

resultados = []

for nombre, codigo in paises.items():

    df = get_indicator(
        "SI.POV.GINI",
        codigo,
        2000,
        2025
    )

    if not df.empty:

        ultimo = df.sort_values(
            "year"
        ).iloc[-1]

        resultados.append({
            "País": nombre,
            "Código": codigo,
            "Índice Gini": ultimo["value"],
            "Año": ultimo["year"]
        })

ranking = pd.DataFrame(resultados)

ranking = ranking.sort_values(
    "Índice Gini",
    ascending=False
)

print("COMPARACIÓN INTERNACIONAL")

display(ranking)


# ==========================================
# 9. GRÁFICA DE COMPARACIÓN INTERNACIONAL
# ==========================================

if not ranking.empty:

    fig = px.bar(
        ranking,
        x="País",
        y="Índice Gini",
        color="Índice Gini",
        text="Índice Gini",
        title="Índice Gini por país",
        hover_data=["Año"]
    )

    fig.update_layout(
        yaxis_title="Índice Gini (0-100)",
        xaxis_title="País"
    )

    fig.show()


# ==========================================
# 10. EXPORTAR RESULTADOS
# ==========================================

comparacion.to_csv(
    "comparacion_colombia_brasil.csv",
    index=False
)

ranking.to_csv(
    "ranking_desigualdad.csv",
    index=False
)

print("Archivos CSV generados correctamente.")
