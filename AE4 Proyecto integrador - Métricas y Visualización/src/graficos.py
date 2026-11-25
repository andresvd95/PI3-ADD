"""Figuras estáticas (PNG) para el notebook y el documento PDF de AE4.

Reproducen los gráficos de la aplicación de Streamlit con matplotlib, a partir
de las mismas tablas de ``metricas.py``.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

AZUL = "#2a78d6"
NARANJA = "#eb6834"
GRIS = "#9a9893"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
FUENTE = "Fuente: BIT/titanic-dataset (split train, 891 registros), dataset preparado en AE3."

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#c3c2b7",
        "axes.titleweight": "bold",
        "axes.titlesize": 12,
        "axes.labelcolor": TINTA_2,
        "xtick.color": TINTA_2,
        "ytick.color": TINTA_2,
    }
)


def _coma(v: float) -> str:
    return f"{v:.2f}".replace(".", ",")


def _rejilla(ax) -> None:
    ax.yaxis.grid(True, color="#e6e5e0", lw=0.8)
    ax.set_axisbelow(True)


def _cerrar(fig, ruta: Path) -> Path:
    fig.text(0.01, 0.01, FUENTE, fontsize=7.5, color=TINTA_2)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(ruta, dpi=200)
    plt.close(fig)
    return ruta


def barras_tasa(ax, tabla: pd.DataFrame, col: str, tasa_total: float, sin_dato: str | None = None) -> None:
    colores = [GRIS if g == sin_dato else AZUL for g in tabla[col]]
    barras = ax.bar(tabla[col], tabla["tasa_supervivencia_pct"], color=colores, width=0.6)
    for b, v, n in zip(barras, tabla["tasa_supervivencia_pct"], tabla["pasajeros"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{_coma(v)} %\n(n = {n})", ha="center", va="bottom",
                fontsize=8.5, color=TINTA, bbox=dict(facecolor="white", edgecolor="none", pad=0.6), zorder=3)
    ax.axhline(tasa_total, color=TINTA_2, ls="--", lw=1, label=f"Tasa total {_coma(tasa_total)} %")
    ax.legend(frameon=False, loc="upper center", fontsize=8.5)
    ax.set_ylim(0, 125)
    ax.set_ylabel("Tasa de supervivencia (%)")
    _rejilla(ax)


def barras_conteo(ax, tabla: pd.DataFrame, col: str) -> None:
    ax.bar(tabla[col], tabla["sobrevivientes"], color=AZUL, width=0.6, label="Sobrevivió", edgecolor="white", lw=1.5)
    ax.bar(tabla[col], tabla["no_sobrevivientes"], bottom=tabla["sobrevivientes"], color=NARANJA, width=0.6,
           label="No sobrevivió", edgecolor="white", lw=1.5)
    for x, n, p in zip(tabla[col], tabla["pasajeros"], tabla["participacion_pasajeros_pct"]):
        ax.text(x, n + tabla["pasajeros"].max() * 0.02, f"{n}\n({_coma(p)} %)", ha="center", fontsize=8, color=TINTA)
    ax.set_ylim(0, tabla["pasajeros"].max() * 1.25)
    ax.set_ylabel("Pasajeros (personas)")
    ax.legend(frameon=False, loc="upper left", ncols=2, fontsize=8.5)
    _rejilla(ax)


ESPECIFICACIONES = [
    ("p2", "pregunta_2_supervivencia_por_clase", "clase", "Clase del pasaje", None, "P2. Supervivencia por clase"),
    ("p3", "pregunta_3_supervivencia_por_sexo", "sexo", "Sexo registrado", None, "P3. Supervivencia por sexo"),
    ("p4", "pregunta_4_supervivencia_por_grupo_edad", "grupo_edad", "Grupo de edad (años)", "Edad no registrada",
     "P4. Supervivencia por grupo de edad"),
    ("p5", "pregunta_5_supervivencia_por_puerto", "puerto_embarque", "Puerto de embarque", "No registrado",
     "P5. Supervivencia por puerto de embarque"),
]


def generar_figuras(resultado: dict[str, object], carpeta: Path) -> dict[str, Path]:
    """Crea una figura por pregunta y las dos figuras complementarias."""
    carpeta.mkdir(parents=True, exist_ok=True)
    t = resultado["tablas"]
    total = t["pregunta_1_supervivencia_total"].iloc[0]
    tasa_total = float(total["tasa_supervivencia_pct"])
    rutas: dict[str, Path] = {}

    # P1: barra apilada única
    fig, ax = plt.subplots(figsize=(8, 2.4))
    s, ns = int(total["sobrevivientes"]), int(total["no_sobrevivientes"])
    ax.barh([0], [s], color=AZUL, edgecolor="white", lw=2)
    ax.barh([0], [ns], left=[s], color=NARANJA, edgecolor="white", lw=2)
    ax.text(s / 2, 0, f"Sobrevivió: {s} ({_coma(tasa_total)} %)", ha="center", va="center", color="white", fontweight="bold")
    ax.text(s + ns / 2, 0, f"No sobrevivió: {ns} ({_coma(100 - tasa_total)} %)", ha="center", va="center",
            color="white", fontweight="bold")
    ax.set_yticks([])
    ax.set_xlim(0, s + ns)
    ax.set_xlabel("Pasajeros (personas)")
    ax.set_title(f"P1. Distribución de los {s + ns} pasajeros según estado de supervivencia", loc="left")
    rutas["p1"] = _cerrar(fig, carpeta / "fig_p1_supervivencia_total.png")

    # P2 a P5: tasa (%) y conteos apilados
    for clave, nombre, col, eje, sin_dato, titulo in ESPECIFICACIONES:
        fig, (a, b) = plt.subplots(1, 2, figsize=(11 if clave == "p4" else 10, 4.4))
        barras_tasa(a, t[nombre], col, tasa_total, sin_dato)
        a.set_title("Tasa de supervivencia (%)", loc="left", fontsize=10.5)
        a.set_xlabel(eje)
        barras_conteo(b, t[nombre], col)
        b.set_title("Pasajeros por estado de supervivencia", loc="left", fontsize=10.5)
        b.set_xlabel(eje)
        if clave == "p4":
            for eje_ax in (a, b):
                eje_ax.tick_params(axis="x", labelrotation=25, labelsize=8.5)
        fig.suptitle(titulo, x=0.01, ha="left", fontweight="bold", fontsize=12.5)
        rutas[clave] = _cerrar(fig, carpeta / f"fig_{clave}_{col}.png")

    clases = ["Primera", "Segunda", "Tercera"]
    x = list(range(len(clases)))

    # Complemento: clase x sexo
    cs = resultado["clase_sexo"]
    fig, ax = plt.subplots(figsize=(8, 4))
    for desp, sexo, color in ((-0.2, "Mujer", AZUL), (0.2, "Hombre", NARANJA)):
        d = cs[cs["sexo"] == sexo].set_index("clase").loc[clases]
        barras = ax.bar([i + desp for i in x], d["tasa_supervivencia_pct"], width=0.38, color=color, label=sexo,
                        edgecolor="white", lw=1.5)
        for b_, v, n in zip(barras, d["tasa_supervivencia_pct"], d["pasajeros"]):
            ax.text(b_.get_x() + b_.get_width() / 2, v + 1.5, f"{_coma(v)} %\n(n = {n})", ha="center", fontsize=8,
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.6), zorder=3)
    ax.axhline(tasa_total, color=TINTA_2, ls="--", lw=1, label=f"Tasa total {_coma(tasa_total)} %")
    ax.set_xticks(x, clases)
    ax.set_ylim(0, 118)
    ax.set_ylabel("Tasa de supervivencia (%)")
    ax.set_xlabel("Clase del pasaje")
    ax.legend(frameon=False, ncols=3, loc="upper right", fontsize=9)
    _rejilla(ax)
    ax.set_title("Complemento. Tasa de supervivencia por clase y sexo (%)", loc="left")
    rutas["clase_sexo"] = _cerrar(fig, carpeta / "fig_complemento_clase_sexo.png")

    # Complemento: tarifas
    tf = resultado["tarifas"]
    fig, ax = plt.subplots(figsize=(8, 4))
    for desp, serie, color, etiqueta in (
        (-0.2, "participacion_pasajeros_pct", GRIS, "Participación en pasajeros (%)"),
        (0.2, "participacion_tarifa_pct", AZUL, "Participación en tarifa total registrada (%)"),
    ):
        barras = ax.bar([i + desp for i in x], tf[serie], width=0.38, color=color, label=etiqueta, edgecolor="white", lw=1.5)
        for b_, v in zip(barras, tf[serie]):
            ax.text(b_.get_x() + b_.get_width() / 2, v + 1, f"{_coma(v)} %", ha="center", fontsize=8.5)
    ax.set_xticks(x, tf["clase"])
    ax.set_ylim(0, 85)
    ax.set_ylabel("Participación (%)")
    ax.set_xlabel("Clase del pasaje")
    ax.legend(frameon=False, loc="upper right", fontsize=8.5)
    _rejilla(ax)
    ax.set_title("Complemento. Participación por clase en pasajeros y en tarifa registrada", loc="left")
    rutas["tarifas"] = _cerrar(fig, carpeta / "fig_complemento_tarifas.png")
    return rutas
