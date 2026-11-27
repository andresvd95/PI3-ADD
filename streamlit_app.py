"""Aplicación de Streamlit del Proyecto Integrado III (AE4).

Presenta la necesidad, las preguntas de negocio, las métricas, los gráficos y
las conclusiones del análisis descriptivo del dataset BIT/titanic-dataset.
Todas las cifras se calculan en ``metricas.py`` a partir del dataset preparado
en AE3 y se comparan con las tablas que exportó su notebook.

Ejecución local:  streamlit run streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "AE4 Proyecto integrador - Métricas y Visualización" / "src"))
import metricas as m  # noqa: E402

# Paleta validada (slots 1 y 2 del tema categórico) + gris para "no registrado".
AZUL = "#2a78d6"  # Sobrevivió / tasa de supervivencia
NARANJA = "#eb6834"  # No sobrevivió
GRIS = "#9a9893"  # Categorías sin dato
REFERENCIA = "#52514e"  # Línea de la tasa total
REPO = "https://github.com/andresvd95/PI3-ADD"

st.set_page_config(page_title="Supervivencia en el Titanic | PI III", page_icon="🚢", layout="wide")


@st.cache_data
def cargar() -> dict[str, object]:
    return m.calcular_todo(RAIZ)


R = cargar()
T = R["tablas"]
TOTAL = T["pregunta_1_supervivencia_total"].iloc[0]
N = int(TOTAL["pasajeros"])
SOBREV = int(TOTAL["sobrevivientes"])
NO_SOBREV = int(TOTAL["no_sobrevivientes"])
TASA_TOTAL = float(TOTAL["tasa_supervivencia_pct"])


# ---------------------------------------------------------------- utilidades
def num(valor: float, dec: int = 2) -> str:
    """Número con coma decimal y punto de miles (formato en español)."""
    texto = f"{valor:,.{dec}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def pct(valor: float) -> str:
    return f"{num(valor)} %"


def _base(fig: go.Figure, titulo: str, eje_y: str, eje_x: str, alto: int = 420) -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=16)),
        height=alto,
        margin=dict(l=10, r=10, t=80, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title=None, traceorder="normal"),
        bargap=0.35,
        hoverlabel=dict(font_size=13),
    )
    fig.update_yaxes(title=eje_y, gridcolor="rgba(128,128,128,0.18)", zeroline=False)
    fig.update_xaxes(title=eje_x, showgrid=False)
    return fig


def grafico_tasa(tabla: pd.DataFrame, col: str, titulo: str, eje_x: str, sin_dato: str | None = None) -> go.Figure:
    """Barras de tasa de supervivencia (%) con la tasa total como referencia."""
    colores = [GRIS if g == sin_dato else AZUL for g in tabla[col]]
    fig = go.Figure(
        go.Bar(
            x=tabla[col],
            y=tabla["tasa_supervivencia_pct"],
            marker=dict(color=colores, cornerradius=4),
            text=[pct(v) for v in tabla["tasa_supervivencia_pct"]],
            textposition="outside",
            customdata=tabla[["sobrevivientes", "pasajeros"]],
            hovertemplate="<b>%{x}</b><br>Tasa: %{y:.2f} %<br>%{customdata[0]} de %{customdata[1]} pasajeros<extra></extra>",
            showlegend=False,
        )
    )
    fig.add_hline(
        y=TASA_TOTAL,
        line=dict(color=REFERENCIA, dash="dash", width=1.5),
        annotation_text=f"Tasa total {pct(TASA_TOTAL)}",
        annotation_position="top right",
    )
    fig.update_yaxes(range=[0, 110], ticksuffix=" %")
    return _base(fig, titulo, "Tasa de supervivencia (%)", eje_x)


def grafico_conteos(tabla: pd.DataFrame, col: str, titulo: str, eje_x: str) -> go.Figure:
    """Barras apiladas de pasajeros: sobrevivientes y no sobrevivientes."""
    fig = go.Figure()
    for serie, color, nombre in (
        ("sobrevivientes", AZUL, "Sobrevivió"),
        ("no_sobrevivientes", NARANJA, "No sobrevivió"),
    ):
        fig.add_bar(
            x=tabla[col],
            y=tabla[serie],
            name=nombre,
            marker=dict(color=color, line=dict(color="white", width=2)),
            hovertemplate=f"<b>%{{x}}</b><br>{nombre}: %{{y}} pasajeros<extra></extra>",
        )
    fig.update_layout(barmode="stack")
    for _, fila in tabla.iterrows():
        fig.add_annotation(
            x=fila[col],
            y=fila["pasajeros"],
            text=f"{int(fila['pasajeros'])} ({pct(fila['participacion_pasajeros_pct'])})",
            showarrow=False,
            yshift=12,
            font=dict(size=12),
        )
    fig.update_yaxes(range=[0, tabla["pasajeros"].max() * 1.15])
    return _base(fig, titulo, "Pasajeros (personas)", eje_x)


def ficha_metrica(metrica: str, calculo: str, unidad: str,
                  periodo: str = "891 registros del split train; viaje de abril de 1912") -> None:
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([1.2, 2, 1, 1.4])
        c1.markdown(f"**Métrica**  \n{metrica}")
        c2.markdown(f"**Cálculo**  \n{calculo}")
        c3.markdown(f"**Unidad**  \n{unidad}")
        c4.markdown(f"**Periodo / alcance**  \n{periodo}")


def interpretacion(muestra: str, responde: str, decision: str, limitaciones: str) -> None:
    st.markdown("#### Interpretación")
    a, b = st.columns(2)
    with a:
        st.markdown(f"**Qué muestran los datos.** {muestra}")
        st.markdown(f"**Cómo responde la pregunta.** {responde}")
    with b:
        st.markdown(f"**Decisión que podría apoyar.** {decision}")
        st.warning(f"**Limitaciones.** {limitaciones}", icon="⚠️")


def tabla_detalle(tabla: pd.DataFrame, nombre: str) -> None:
    with st.expander("Ver tabla de resultados y descargar CSV"):
        st.dataframe(
            tabla,
            hide_index=True,
            use_container_width=True,
            column_config={
                "tasa_supervivencia_pct": st.column_config.NumberColumn("Tasa de supervivencia (%)", format="%.2f"),
                "participacion_pasajeros_pct": st.column_config.NumberColumn("Participación (%)", format="%.2f"),
                "no_sobrevivientes": "No sobrevivientes",
            },
        )
        st.download_button(
            "Descargar CSV", tabla.to_csv(index=False).encode("utf-8-sig"), f"{nombre}.csv", "text/csv", key=nombre
        )
        st.caption(f"Fuente: `{m.CARPETA_AE3}/resultados/{nombre}.csv`, recalculada desde `datos/titanic_preparado.csv`.")


# ---------------------------------------------------------------- secciones
def inicio() -> None:
    st.title("🚢 Supervivencia registrada de los pasajeros del Titanic")
    st.caption("Proyecto Integrado III · Analítica de Datos · AE4: métricas, visualización y resultados")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Pasajeros analizados", f"{N}")
    k2.metric("Sobrevivientes", f"{SOBREV}")
    k3.metric("Tasa de supervivencia total", pct(TASA_TOTAL))
    k4.metric("Filas eliminadas en la preparación", "0")

    st.subheader("Necesidad analítica")
    st.markdown(
        "En un **escenario académico hipotético**, un equipo que prepara material de estudio sobre "
        "seguridad marítima necesita describir **cómo se distribuyó la supervivencia registrada** entre "
        "los grupos de pasajeros según clase, sexo, edad y puerto de embarque, para sustentar sus "
        "comparaciones en datos y señalar qué grupos merecen una revisión posterior."
    )
    st.info(
        "**Pregunta general:** ¿cómo varía la proporción de pasajeros registrados como sobrevivientes "
        "según la clase, el sexo, el grupo de edad y el puerto de embarque?",
        icon="❓",
    )

    st.subheader("Preguntas de negocio")
    st.markdown(
        "| # | Pregunta | Variables | Métrica principal |\n|---|---|---|---|\n"
        "| P1 | ¿Cuál fue la supervivencia total registrada? | `sobrevivio` | Tasa de supervivencia (%) |\n"
        "| P2 | ¿Cómo varió según la clase? | `sobrevivio`, `clase` | Tasa por clase (%) |\n"
        "| P3 | ¿Cómo varió según el sexo? | `sobrevivio`, `sexo` | Tasa por sexo (%) y brecha (p. p.) |\n"
        "| P4 | ¿Cómo varió según el grupo de edad? | `sobrevivio`, `grupo_edad` | Tasa por grupo de edad (%) |\n"
        "| P5 | ¿Cómo varió según el puerto de embarque? | `sobrevivio`, `ciudad_embarque` | Tasa por puerto (%) |"
    )

    st.subheader("Dataset")
    a, b = st.columns([1.3, 1])
    with a:
        st.markdown(
            "- **Fuente:** [`BIT/titanic-dataset`](https://huggingface.co/datasets/BIT/titanic-dataset) "
            "(Hugging Face), split `train`, licencia Apache 2.0.\n"
            "- **Original:** 891 registros y 15 variables; cada fila es un pasajero.\n"
            "- **Preparado (AE3):** 891 registros y 9 variables (6 originales + `estado_supervivencia`, `clase`, `grupo_edad`).\n"
            "- **Calidad:** 177 edades vacías (19,87 %) quedan como *Edad no registrada*; 2 puertos vacíos como "
            "*No registrado*; 120 filas con atributos coincidentes no se eliminan porque no hay identificador de pasajero.\n"
            "- **Alcance:** análisis **descriptivo**; muestra asociaciones en los registros, **no causas**."
        )
    with b:
        st.markdown("**Muestra del dataset preparado**")
        st.dataframe(R["datos"].head(8), hide_index=True, use_container_width=True, height=300)
    st.caption("Recorre las preguntas desde el menú superior.")


def p1() -> None:
    st.header("P1. ¿Cuál fue la supervivencia total registrada?")
    ficha_metrica(
        "Tasa de supervivencia total",
        "sobrevivientes / pasajeros × 100 (sobrevivientes = suma de `sobrevivio`)",
        "Porcentaje (%) y personas",
    )
    k1, k2, k3 = st.columns(3)
    k1.metric("Pasajeros", N)
    k2.metric("Sobrevivientes", SOBREV)
    k3.metric("No sobrevivientes", NO_SOBREV)

    fig = go.Figure()
    for valor, color, nombre, tasa in (
        (SOBREV, AZUL, "Sobrevivió", TASA_TOTAL),
        (NO_SOBREV, NARANJA, "No sobrevivió", 100 - TASA_TOTAL),
    ):
        fig.add_bar(
            y=["Pasajeros"], x=[valor], orientation="h", name=nombre,
            marker=dict(color=color, line=dict(color="white", width=2)),
            text=[f"{nombre}: {valor} ({pct(tasa)})"], textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=14), hovertemplate=f"{nombre}: {valor} pasajeros ({pct(tasa)})<extra></extra>",
        )
    fig.update_layout(barmode="stack")
    fig.update_yaxes(showticklabels=False)
    st.plotly_chart(
        _base(fig, f"Distribución de los {N} pasajeros según estado de supervivencia", "", "Pasajeros (personas)", alto=240),
        use_container_width=True,
    )

    interpretacion(
        f"De {N} pasajeros registrados sobrevivieron {SOBREV}, es decir, {pct(TASA_TOTAL)}; "
        f"{NO_SOBREV} ({pct(100 - TASA_TOTAL)}) no sobrevivieron. Aproximadamente 6 de cada 10 pasajeros no sobrevivieron.",
        f"Responde directamente P1 y fija la **línea de referencia** ({pct(TASA_TOTAL)}) con la que se comparan los grupos de P2 a P5.",
        "Usar la tasa total como punto de comparación en el material: un grupo con una tasa claramente "
        "mayor o menor que la referencia es candidato a una explicación o revisión posterior.",
        "Describe solo los 891 registros del split; la ficha no documenta el origen de los datos ni si son "
        "sintéticos, por lo que la cifra no debe generalizarse a todas las personas a bordo.",
    )
    tabla_detalle(T["pregunta_1_supervivencia_total"], "pregunta_1_supervivencia_total")


def p2() -> None:
    t = T["pregunta_2_supervivencia_por_clase"]
    c = t.set_index("clase")
    st.header("P2. ¿Cómo varió la supervivencia según la clase?")
    ficha_metrica(
        "Tasa de supervivencia por clase y participación",
        "Tasa = sobrevivientes de la clase / pasajeros de la clase × 100. Participación = pasajeros de la clase / 891 × 100",
        "Porcentaje (%) y personas",
    )
    k = st.columns(3)
    for col, clase in zip(k, m.ORDEN["clase"]):
        dif = c.loc[clase, "tasa_supervivencia_pct"] - TASA_TOTAL
        col.metric(f"{clase} clase", pct(c.loc[clase, "tasa_supervivencia_pct"]), f"{num(dif)} p. p. vs. total")
    a, b = st.columns(2)
    a.plotly_chart(grafico_tasa(t, "clase", "Tasa de supervivencia por clase (%)", "Clase del pasaje"), use_container_width=True)
    b.plotly_chart(grafico_conteos(t, "clase", "Pasajeros por clase y estado de supervivencia", "Clase del pasaje"), use_container_width=True)

    razon = c.loc["Primera", "tasa_supervivencia_pct"] / c.loc["Tercera", "tasa_supervivencia_pct"]
    interpretacion(
        f"La tasa baja de forma escalonada: Primera {pct(c.loc['Primera', 'tasa_supervivencia_pct'])}, "
        f"Segunda {pct(c.loc['Segunda', 'tasa_supervivencia_pct'])} y Tercera {pct(c.loc['Tercera', 'tasa_supervivencia_pct'])}. "
        f"La tasa de la primera clase es {num(razon)} veces la de la tercera. La tercera clase concentra "
        f"{pct(c.loc['Tercera', 'participacion_pasajeros_pct'])} de los pasajeros y {int(c.loc['Tercera', 'no_sobrevivientes'])} "
        f"de los {NO_SOBREV} no sobrevivientes.",
        "Sí hubo diferencias por clase: solo la primera clase supera la tasa total; la tercera queda "
        f"{num(TASA_TOTAL - c.loc['Tercera', 'tasa_supervivencia_pct'])} p. p. por debajo.",
        "Priorizar la clase como eje de comparación en el material y destacar la tercera clase como el "
        "grupo con más personas no sobrevivientes, que merece revisión con otras fuentes (ubicación de cabinas, acceso a botes).",
        "Asociación, no causa: la clase se cruza con sexo, edad y tarifa, y aquí se analiza por separado. "
        "El dataset no informa la ubicación de los camarotes ni el acceso a botes salvavidas.",
    )
    tabla_detalle(t, "pregunta_2_supervivencia_por_clase")


def p3() -> None:
    t = T["pregunta_3_supervivencia_por_sexo"]
    s = t.set_index("sexo")
    brecha = s.loc["Mujer", "tasa_supervivencia_pct"] - s.loc["Hombre", "tasa_supervivencia_pct"]
    st.header("P3. ¿Cómo varió la supervivencia según el sexo?")
    ficha_metrica(
        "Tasa de supervivencia por sexo y brecha",
        "Tasa = sobrevivientes del sexo / pasajeros del sexo × 100. Brecha = tasa mujeres − tasa hombres",
        "Porcentaje (%) y puntos porcentuales (p. p.)",
    )
    k1, k2, k3 = st.columns(3)
    k1.metric("Mujeres", pct(s.loc["Mujer", "tasa_supervivencia_pct"]), f"{int(s.loc['Mujer', 'pasajeros'])} pasajeras", delta_color="off")
    k2.metric("Hombres", pct(s.loc["Hombre", "tasa_supervivencia_pct"]), f"{int(s.loc['Hombre', 'pasajeros'])} pasajeros", delta_color="off")
    k3.metric("Brecha", f"{num(brecha)} p. p.")
    a, b = st.columns(2)
    a.plotly_chart(grafico_tasa(t, "sexo", "Tasa de supervivencia por sexo (%)", "Sexo registrado"), use_container_width=True)
    b.plotly_chart(grafico_conteos(t, "sexo", "Pasajeros por sexo y estado de supervivencia", "Sexo registrado"), use_container_width=True)

    cs = R["clase_sexo"]
    st.markdown("##### Lectura complementaria: sexo dentro de cada clase")
    fig = go.Figure()
    for sexo, color in (("Mujer", AZUL), ("Hombre", NARANJA)):
        d = cs[cs["sexo"] == sexo]
        fig.add_bar(
            x=d["clase"], y=d["tasa_supervivencia_pct"], name=sexo, marker=dict(color=color, cornerradius=4),
            text=[pct(v) for v in d["tasa_supervivencia_pct"]], textposition="outside",
            customdata=d[["sobrevivientes", "pasajeros"]],
            hovertemplate=f"<b>{sexo}, %{{x}}</b><br>Tasa: %{{y:.2f}} %<br>%{{customdata[0]}} de %{{customdata[1]}}<extra></extra>",
        )
    fig.update_layout(barmode="group", bargroupgap=0.08)
    fig.update_yaxes(range=[0, 110], ticksuffix=" %")
    st.plotly_chart(
        _base(fig, "Tasa de supervivencia por clase y sexo (%)", "Tasa de supervivencia (%)", "Clase del pasaje", alto=380),
        use_container_width=True,
    )
    ci = cs.set_index(["clase", "sexo"])["tasa_supervivencia_pct"]

    interpretacion(
        f"Las mujeres tuvieron una tasa de {pct(s.loc['Mujer', 'tasa_supervivencia_pct'])} frente a "
        f"{pct(s.loc['Hombre', 'tasa_supervivencia_pct'])} de los hombres: una brecha de {num(brecha)} p. p., aunque "
        f"ellos eran {pct(s.loc['Hombre', 'participacion_pasajeros_pct'])} de los pasajeros. La brecha aparece en las "
        f"tres clases (Primera {pct(ci['Primera', 'Mujer'])} vs. {pct(ci['Primera', 'Hombre'])}; "
        f"Tercera {pct(ci['Tercera', 'Mujer'])} vs. {pct(ci['Tercera', 'Hombre'])}).",
        "El sexo es la variable con la diferencia más grande entre grupos de las cinco preguntas.",
        "Presentar el sexo junto con la clase en el material, porque la combinación separa grupos con tasas "
        f"de {pct(ci.min())} a {pct(ci.max())}; un análisis posterior podría modelar ambas variables a la vez.",
        "Es una comparación descriptiva: no controla edad ni otras variables y no demuestra que el sexo "
        "causara la supervivencia (por ejemplo, no hay datos sobre el orden de evacuación).",
    )
    tabla_detalle(t, "pregunta_3_supervivencia_por_sexo")


def p4() -> None:
    t = T["pregunta_4_supervivencia_por_grupo_edad"]
    e = t.set_index("grupo_edad")
    con_edad = e.drop(index="Edad no registrada")
    mejor, peor = con_edad["tasa_supervivencia_pct"].idxmax(), con_edad["tasa_supervivencia_pct"].idxmin()
    st.header("P4. ¿Cómo varió la supervivencia según el grupo de edad?")
    ficha_metrica(
        "Tasa de supervivencia por grupo de edad",
        "Tasa = sobrevivientes del grupo / pasajeros del grupo × 100. Grupos: 0–12, 13–17, 18–29, 30–44, 45–59, 60+ años y Edad no registrada",
        "Porcentaje (%); edad en años",
    )
    k1, k2, k3 = st.columns(3)
    k1.metric(f"Mayor tasa ({mejor} años)", pct(e.loc[mejor, "tasa_supervivencia_pct"]))
    k2.metric(f"Menor tasa ({peor} años)", pct(e.loc[peor, "tasa_supervivencia_pct"]))
    k3.metric(
        "Pasajeros sin edad",
        f"{int(e.loc['Edad no registrada', 'pasajeros'])} ({pct(e.loc['Edad no registrada', 'participacion_pasajeros_pct'])})",
    )
    a, b = st.columns(2)
    a.plotly_chart(
        grafico_tasa(t, "grupo_edad", "Tasa de supervivencia por grupo de edad (%)", "Grupo de edad (años)", "Edad no registrada"),
        use_container_width=True,
    )
    b.plotly_chart(grafico_conteos(t, "grupo_edad", "Pasajeros por grupo de edad y estado", "Grupo de edad (años)"), use_container_width=True)
    st.caption("La barra gris corresponde a los pasajeros sin edad registrada; no es un grupo de edad real.")

    interpretacion(
        f"Los niños de {mejor} años tienen la tasa más alta ({pct(e.loc[mejor, 'tasa_supervivencia_pct'])}); también supera la "
        f"referencia el grupo de 13 a 17 ({pct(e.loc['13 a 17', 'tasa_supervivencia_pct'])}). "
        f"El grupo más numeroso, 18 a 29 años ({int(e.loc['18 a 29', 'pasajeros'])} pasajeros), queda en "
        f"{pct(e.loc['18 a 29', 'tasa_supervivencia_pct'])}, y el de {peor} años registra la menor tasa ({pct(e.loc[peor, 'tasa_supervivencia_pct'])}).",
        "La supervivencia sí cambia con la edad, sobre todo entre los menores de 13 años y el resto; entre 18 y 59 años "
        "las tasas son parecidas (35 % a 42 %).",
        "Destacar en el material a los menores de 13 años como el grupo de edad con mayor supervivencia y "
        "solicitar la fuente original para completar las edades antes de sacar conclusiones por edad.",
        f"Faltan {int(e.loc['Edad no registrada', 'pasajeros'])} edades (19,87 %) y no se imputaron; el grupo de 60 o más tiene "
        f"solo {int(e.loc['60 o más', 'pasajeros'])} personas, por lo que su tasa es poco estable. Los cortes de edad son un criterio propio.",
    )
    tabla_detalle(t, "pregunta_4_supervivencia_por_grupo_edad")


def p5() -> None:
    t = T["pregunta_5_supervivencia_por_puerto"]
    p = t.set_index("puerto_embarque")
    st.header("P5. ¿Cómo varió la supervivencia según el puerto de embarque?")
    ficha_metrica(
        "Tasa de supervivencia por puerto de embarque",
        "Tasa = sobrevivientes del puerto / pasajeros del puerto × 100. Participación = pasajeros del puerto / 891 × 100",
        "Porcentaje (%) y personas",
    )
    k = st.columns(3)
    for col, puerto in zip(k, ["Cherbourg", "Queenstown", "Southampton"]):
        col.metric(puerto, pct(p.loc[puerto, "tasa_supervivencia_pct"]), f"{int(p.loc[puerto, 'pasajeros'])} pasajeros", delta_color="off")
    a, b = st.columns(2)
    a.plotly_chart(
        grafico_tasa(t, "puerto_embarque", "Tasa de supervivencia por puerto (%)", "Puerto de embarque", "No registrado"),
        use_container_width=True,
    )
    b.plotly_chart(grafico_conteos(t, "puerto_embarque", "Pasajeros por puerto y estado de supervivencia", "Puerto de embarque"), use_container_width=True)

    d = R["datos"]
    mezcla = (pd.crosstab(d["ciudad_embarque"], d["clase"], normalize="index") * 100).round(2)
    mezcla = mezcla.reindex(["Cherbourg", "Queenstown", "Southampton"])[m.ORDEN["clase"]]
    st.markdown("##### Contexto: composición por clase de cada puerto (% de pasajeros del puerto)")
    st.dataframe(mezcla.style.format("{:.2f} %"), use_container_width=True)

    interpretacion(
        f"Cherbourg tiene la tasa más alta ({pct(p.loc['Cherbourg', 'tasa_supervivencia_pct'])}) y Southampton la más baja "
        f"({pct(p.loc['Southampton', 'tasa_supervivencia_pct'])}), aunque Southampton concentra "
        f"{pct(p.loc['Southampton', 'participacion_pasajeros_pct'])} de los pasajeros. "
        f"En Cherbourg embarcó una mayor proporción de primera clase ({pct(mezcla.loc['Cherbourg', 'Primera'])}).",
        "Hay diferencias por puerto, pero son menores que las de sexo o clase y pueden reflejar la composición de "
        "pasajeros de cada puerto.",
        "No usar el puerto como factor explicativo en el material sin presentar antes la clase; sirve como dato de "
        "contexto sobre el perfil de los pasajeros embarcados en cada ciudad.",
        "El puerto es un dato de embarque, no de lo ocurrido a bordo. Los 2 registros sin puerto sobrevivieron, pero "
        "ese 100 % con dos casos no es un patrón. Queenstown solo tiene 77 pasajeros.",
    )
    tabla_detalle(t, "pregunta_5_supervivencia_por_puerto")


def tarifas() -> None:
    t = R["tarifas"]
    f = t.set_index("clase")
    st.header("Complemento: tarifas por clase (ingreso registrado ≠ rentabilidad)")
    ficha_metrica(
        "Tarifa total, media y mediana por clase",
        "Tarifa total = suma de `tarifa` de la clase. Participación = tarifa total de la clase / tarifa total × 100",
        "Unidad monetaria no indicada en la fuente",
    )
    k = st.columns(3)
    for col, clase in zip(k, m.ORDEN["clase"]):
        col.metric(
            f"{clase}: tarifa mediana",
            num(f.loc[clase, "tarifa_mediana"]),
            f"{pct(f.loc[clase, 'participacion_tarifa_pct'])} de la tarifa total",
            delta_color="off",
        )

    fig = go.Figure()
    for serie, color, nombre in (
        ("participacion_pasajeros_pct", GRIS, "Participación en pasajeros (%)"),
        ("participacion_tarifa_pct", AZUL, "Participación en tarifa total registrada (%)"),
    ):
        fig.add_bar(
            x=t["clase"], y=t[serie], name=nombre, marker=dict(color=color, cornerradius=4),
            text=[pct(v) for v in t[serie]], textposition="outside",
            hovertemplate=f"<b>%{{x}}</b><br>{nombre}: %{{y:.2f}} %<extra></extra>",
        )
    fig.update_layout(barmode="group", bargroupgap=0.08)
    fig.update_yaxes(range=[0, 75], ticksuffix=" %")
    st.plotly_chart(
        _base(fig, "Participación de cada clase en pasajeros y en tarifa total registrada (%)", "Participación (%)", "Clase del pasaje"),
        use_container_width=True,
    )

    interpretacion(
        f"La primera clase reúne {pct(f.loc['Primera', 'participacion_pasajeros_pct'])} de los pasajeros, pero "
        f"{pct(f.loc['Primera', 'participacion_tarifa_pct'])} de la tarifa total registrada; la tercera, con "
        f"{pct(f.loc['Tercera', 'participacion_pasajeros_pct'])} de los pasajeros, aporta {pct(f.loc['Tercera', 'participacion_tarifa_pct'])}.",
        "No es una de las cinco preguntas: da contexto a P2, porque la clase también separa niveles de tarifa muy distintos.",
        "Ayuda a explicar en el material qué representaba cada clase en términos de valor pagado.",
        "La suma de tarifas es un **ingreso registrado por pasajes**, no **rentabilidad**: no hay costos de operación. "
        f"Tampoco se conoce la moneda ni el año del valor, y hay {int(t['pasajes_tarifa_cero'].sum())} tarifas en cero sin explicación. "
        "Una tarifa más alta no demuestra que haya causado una mayor supervivencia.",
    )
    with st.expander("Ver tabla de tarifas"):
        st.dataframe(t, hide_index=True, use_container_width=True)


def explorador() -> None:
    st.header("Explorador: tasa de supervivencia por segmento")
    st.caption("Filtra el dataset preparado y observa cómo cambia la tasa. Útil para responder preguntas durante la presentación.")
    d = R["datos"]
    c1, c2, c3, c4 = st.columns(4)
    clases = c1.multiselect("Clase", m.ORDEN["clase"], default=m.ORDEN["clase"])
    sexos = c2.multiselect("Sexo", m.ORDEN["sexo"], default=m.ORDEN["sexo"])
    edades = c3.multiselect("Grupo de edad", m.ORDEN["grupo_edad"], default=m.ORDEN["grupo_edad"])
    puertos = c4.multiselect("Puerto", m.ORDEN["puerto_embarque"], default=m.ORDEN["puerto_embarque"])
    f = d[
        d["clase"].isin(clases)
        & d["sexo"].isin(sexos)
        & d["grupo_edad"].isin(edades)
        & d["ciudad_embarque"].isin(puertos)
    ]
    if f.empty:
        st.info("No hay pasajeros con esa combinación de filtros.")
        return
    tasa = f["sobrevivio"].mean() * 100
    k1, k2, k3 = st.columns(3)
    k1.metric("Pasajeros del segmento", len(f), f"{pct(len(f) / N * 100)} del total", delta_color="off")
    k2.metric("Sobrevivientes", int(f["sobrevivio"].sum()))
    k3.metric("Tasa del segmento", pct(tasa), f"{num(tasa - TASA_TOTAL)} p. p. vs. total")
    if len(f) < 30:
        st.warning("El segmento tiene menos de 30 pasajeros: la tasa es poco estable.", icon="⚠️")
    st.dataframe(f, hide_index=True, use_container_width=True, height=320)


def conclusiones() -> None:
    c = T["pregunta_2_supervivencia_por_clase"].set_index("clase")["tasa_supervivencia_pct"]
    s = T["pregunta_3_supervivencia_por_sexo"].set_index("sexo")["tasa_supervivencia_pct"]
    e = T["pregunta_4_supervivencia_por_grupo_edad"].set_index("grupo_edad")["tasa_supervivencia_pct"].drop("Edad no registrada")
    p = T["pregunta_5_supervivencia_por_puerto"].set_index("puerto_embarque")["tasa_supervivencia_pct"].drop("No registrado")
    st.header("Conclusiones, recomendaciones y limitaciones")

    resumen = pd.DataFrame(
        {
            "Pregunta": ["P2 Clase", "P3 Sexo", "P4 Edad (con dato)", "P5 Puerto (con dato)"],
            "Mayor tasa": [f"{c.idxmax()} ({pct(c.max())})", f"{s.idxmax()} ({pct(s.max())})",
                           f"{e.idxmax()} ({pct(e.max())})", f"{p.idxmax()} ({pct(p.max())})"],
            "Menor tasa": [f"{c.idxmin()} ({pct(c.min())})", f"{s.idxmin()} ({pct(s.min())})",
                           f"{e.idxmin()} ({pct(e.min())})", f"{p.idxmin()} ({pct(p.min())})"],
            "Diferencia (p. p.)": [num(c.max() - c.min()), num(s.max() - s.min()), num(e.max() - e.min()), num(p.max() - p.min())],
        }
    )
    st.markdown(f"**Referencia (P1):** tasa total {pct(TASA_TOTAL)} ({SOBREV} de {N}).")
    st.dataframe(resumen, hide_index=True, use_container_width=True)

    st.subheader("Conclusiones")
    st.markdown(
        f"1. La supervivencia registrada fue de **{pct(TASA_TOTAL)}** ({SOBREV} de {N}) y **no se repartió de forma pareja** entre grupos.\n"
        f"2. El **sexo** muestra la mayor diferencia ({num(s.max() - s.min())} p. p.), seguido de la **clase** ({num(c.max() - c.min())} p. p.); "
        "la brecha por sexo se mantiene dentro de cada clase.\n"
        f"3. Por **edad**, los menores de 13 años ({pct(e['0 a 12'])}) se separan con claridad de la referencia; los adultos de 18 a 59 años tienen tasas parecidas.\n"
        "4. El **puerto** muestra diferencias más pequeñas, que pueden reflejar la composición por clase de cada puerto.\n"
        f"5. Las cinco tablas conservan los {N} pasajeros y los {SOBREV} sobrevivientes, y coinciden con las del notebook de AE3."
    )
    st.subheader("Recomendaciones")
    st.markdown(
        "- Estructurar el material de estudio alrededor de **sexo y clase**, mostrados juntos, y usar la tasa total como referencia.\n"
        "- Presentar edad y puerto como contexto, siempre con el tamaño de cada grupo y la advertencia de datos faltantes.\n"
        "- Antes de afirmar explicaciones, **completar la documentación** del dataset (procedencia, edades faltantes, identificador de pasajero) "
        "y, si se requiere medir efectos conjuntos, aplicar un modelo multivariado (por ejemplo, regresión logística).\n"
        "- No usar la tarifa como medida de rentabilidad: solo representa el valor registrado del pasaje."
    )
    st.subheader("Limitaciones")
    st.markdown(
        "- **Descriptivo, no causal:** las diferencias son asociaciones en los registros; no prueban que una característica causara la supervivencia.\n"
        "- **Variables analizadas por separado** (salvo la lectura clase × sexo): no se mide su efecto conjunto.\n"
        "- **Datos faltantes:** 177 edades (19,87 %) y 2 puertos; grupos pequeños (60 o más: 26; sin puerto: 2) dan tasas inestables.\n"
        "- **Origen no documentado:** la ficha de Hugging Face no indica procedencia ni si los datos son sintéticos; "
        "120 filas coincidentes no se pueden confirmar como duplicados.\n"
        "- **Tarifa:** moneda no indicada y 15 valores en cero; es ingreso registrado, no rentabilidad."
    )


def verificacion() -> None:
    st.header("Verificación de datos y reproducibilidad")
    v = R["verificacion"]
    if v["coincide_con_ae3"].all():
        st.success("Las 5 tablas recalculadas desde el dataset preparado coinciden con los CSV del notebook de AE3.", icon="✅")
    else:
        st.error("Alguna tabla no coincide con los resultados de AE3. Revisa la ejecución de los notebooks.", icon="❌")
    st.dataframe(v, hide_index=True, use_container_width=True)
    st.markdown(
        f"- **Datos que carga la app:** `{m.CARPETA_AE3}/datos/titanic_preparado.csv` y `{m.CARPETA_AE3}/resultados/pregunta_*.csv`.\n"
        f"- **Cálculo:** `{m.CARPETA_AE4}/src/metricas.py` (el mismo módulo que usan el notebook de AE4 y el documento PDF).\n"
        f"- **Repositorio:** [{REPO}]({REPO})"
    )


# ---------------------------------------------------------------- navegación tipo app web
st.markdown(
    """
    <style>
      [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
      [data-testid="stToolbarActions"], [data-testid="stAppDeployButton"], [data-testid="stMainMenu"],
      [data-testid="stDecoration"], footer { display: none !important; }
      [data-testid="stToolbar"] { left: 1rem; right: 1rem; }
      header[data-testid="stHeader"] {
        background: linear-gradient(90deg, #0d366b 0%, #1c5cab 60%, #2a78d6 100%);
        box-shadow: 0 2px 12px rgba(13, 54, 107, .25);
      }
      header[data-testid="stHeader"] a, header[data-testid="stHeader"] span,
      header[data-testid="stHeader"] p, header[data-testid="stHeader"] svg { color: #ffffff !important; fill: #ffffff; }
      header[data-testid="stHeader"] a[aria-current="page"] {
        background: rgba(255, 255, 255, .18) !important; border-radius: 8px;
      }
      .block-container { padding-top: 4.5rem; max-width: 1280px; }
      .marca { display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap;
               padding:.55rem 0 .8rem; margin-bottom:.6rem; border-bottom:1px solid rgba(128,128,128,.25); }
      .marca b { font-size:1.05rem; } .marca span { opacity:.75; font-size:.85rem; }
      .marca a { text-decoration:none; font-size:.85rem; font-weight:600; color:#2a78d6; }
    </style>
    """,
    unsafe_allow_html=True,
)

paginas = {
    "": [st.Page(inicio, title="Inicio", icon=":material/home:", default=True)],
    "Preguntas": [
        st.Page(p1, title="P1 · Supervivencia total", icon=":material/groups:", url_path="p1-total"),
        st.Page(p2, title="P2 · Por clase", icon=":material/airline_seat_recline_extra:", url_path="p2-clase"),
        st.Page(p3, title="P3 · Por sexo", icon=":material/wc:", url_path="p3-sexo"),
        st.Page(p4, title="P4 · Por grupo de edad", icon=":material/cake:", url_path="p4-edad"),
        st.Page(p5, title="P5 · Por puerto", icon=":material/anchor:", url_path="p5-puerto"),
    ],
    "Análisis": [
        st.Page(tarifas, title="Tarifas por clase", icon=":material/payments:", url_path="tarifas"),
        st.Page(explorador, title="Explorador de segmentos", icon=":material/filter_alt:", url_path="explorador"),
    ],
    "Cierre": [
        st.Page(conclusiones, title="Conclusiones", icon=":material/flag:", url_path="conclusiones"),
        st.Page(verificacion, title="Verificación de datos", icon=":material/verified:", url_path="verificacion"),
    ],
}
pagina = st.navigation(paginas, position="top")
st.markdown(
    f"""<div class="marca"><div><b>🚢 Titanic · Supervivencia registrada</b><br>
    <span>Proyecto Integrado III · Analítica de Datos · Santiago Andrés Valencia Duque · IU Digital 2026</span></div>
    <a href="{REPO}" target="_blank">Repositorio en GitHub ↗</a></div>""",
    unsafe_allow_html=True,
)
pagina.run()
