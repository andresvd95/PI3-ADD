"""Genera el documento final del proyecto (Word) con las cifras de ``metricas.py``.

Uso:
    python "AE4 Proyecto integrador - Métricas y Visualización/src/generar_documento_final.py" [URL_APP]

El PDF se obtiene con ``exportar_pdf.ps1`` (Microsoft Word), que además
actualiza la tabla de contenido y los índices de tablas y figuras.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
import graficos as g  # noqa: E402
import metricas as m  # noqa: E402

AUTOR = "Santiago Andrés Valencia Duque"
DOCENTE = "Andrés Felipe Callejas"
TITULO = "Supervivencia registrada de los pasajeros del Titanic: análisis descriptivo, métricas y visualización"
REPO = "https://github.com/andresvd95/PI3-ADD"
NOMBRE_ARCHIVO = "Proyecto_Integrado_III_Titanic_Santiago_Andres_Valencia_Duque"


def num(v: float, d: int = 2) -> str:
    texto = f"{v:,.{d}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def pct(v: float) -> str:
    return f"{num(v)} %"


# ------------------------------------------------------------------ ayudantes de Word
def campo(parrafo, instruccion: str, texto: str = ""):
    """Inserta un campo de Word (TOC, SEQ, PAGE) que Word actualiza al exportar."""
    def marca(tipo: str):
        r = OxmlElement("w:r")
        f = OxmlElement("w:fldChar")
        f.set(qn("w:fldCharType"), tipo)
        r.append(f)
        return r

    parrafo._p.append(marca("begin"))
    r = OxmlElement("w:r")
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = f" {instruccion} "
    r.append(it)
    parrafo._p.append(r)
    parrafo._p.append(marca("separate"))
    run = parrafo.add_run(texto)
    parrafo._p.append(marca("end"))
    return run


class Documento:
    def __init__(self) -> None:
        self.doc = Document()
        sec = self.doc.sections[0]
        sec.page_height, sec.page_width = Cm(27.94), Cm(21.59)
        for lado in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
            setattr(sec, lado, Cm(2.54))
        normal = self.doc.styles["Normal"]
        normal.font.name = "Times New Roman"
        normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        normal.font.size = Pt(12)
        normal.paragraph_format.space_after = Pt(6)
        normal.paragraph_format.line_spacing = 1.15
        for nombre, tam in (("Heading 1", 15), ("Heading 2", 13), ("Caption", 10), ("Title", 20)):
            est = self.doc.styles[nombre]
            est.font.name = "Times New Roman"
            rpr = est.element.get_or_add_rPr()
            rpr.get_or_add_rFonts().set(qn("w:eastAsia"), "Times New Roman")
            rpr.get_or_add_rFonts().set(qn("w:ascii"), "Times New Roman")
            rpr.get_or_add_rFonts().set(qn("w:hAnsi"), "Times New Roman")
            est.font.size = Pt(tam)
            est.font.color.rgb = RGBColor(0, 0, 0)
            est.font.bold = nombre != "Caption"
        self.doc.styles["Caption"].font.italic = False
        self.doc.styles["Heading 1"].paragraph_format.space_before = Pt(18)
        self.doc.styles["Heading 2"].paragraph_format.space_before = Pt(12)

    def h(self, texto: str, nivel: int = 1) -> None:
        self.doc.add_heading(texto, level=nivel)

    def p(self, texto: str, alinear=WD_ALIGN_PARAGRAPH.JUSTIFY, negrita_inicial: str | None = None):
        par = self.doc.add_paragraph()
        if negrita_inicial:
            par.add_run(negrita_inicial).bold = True
        par.add_run(texto)
        par.alignment = alinear
        return par

    def lista(self, items: list[str], numerada: bool = False) -> None:
        for item in items:
            par = self.doc.add_paragraph(style="List Number" if numerada else "List Bullet")
            if item.startswith("**") and "**" in item[2:]:
                fin = item.index("**", 2)
                par.add_run(item[2:fin]).bold = True
                par.add_run(item[fin + 2:])
            else:
                par.add_run(item)
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def leyenda(self, tipo: str, texto: str) -> None:
        par = self.doc.add_paragraph(style="Caption")
        par.paragraph_format.keep_with_next = True
        par.paragraph_format.space_before = Pt(6)
        par.add_run(f"{tipo} ").bold = True
        campo(par, f"SEQ {tipo} \\* ARABIC", "1").bold = True
        par.add_run(". ").bold = True
        par.add_run(texto).italic = True

    def nota(self, texto: str) -> None:
        par = self.doc.add_paragraph()
        run = par.add_run(texto)
        run.font.size = Pt(9.5)
        run.italic = True
        par.paragraph_format.space_after = Pt(10)

    def tabla(self, titulo: str, encabezados: list[str], filas: list[list[str]], anchos: list[float] | None = None,
              nota: str = "Fuente: elaboración propia a partir de BIT/titanic-dataset (split train).") -> None:
        self.leyenda("Tabla", titulo)
        t = self.doc.add_table(rows=1, cols=len(encabezados))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for celda, texto in zip(t.rows[0].cells, encabezados):
            celda.text = ""
            run = celda.paragraphs[0].add_run(texto)
            run.bold = True
            run.font.size = Pt(9.5)
            sombra = OxmlElement("w:shd")
            sombra.set(qn("w:val"), "clear")
            sombra.set(qn("w:fill"), "D9E2F3")
            celda._tc.get_or_add_tcPr().append(sombra)
        for fila in filas:
            for celda, texto in zip(t.add_row().cells, fila):
                celda.text = ""
                celda.paragraphs[0].add_run(str(texto)).font.size = Pt(9.5)
                celda.paragraphs[0].paragraph_format.space_after = Pt(0)
        if anchos:
            for fila in t.rows:
                for celda, ancho in zip(fila.cells, anchos):
                    celda.width = Cm(ancho)
        self.nota(nota)

    def figura(self, ruta: Path, titulo: str, ancho_cm: float = 16) -> None:
        self.leyenda("Figura", titulo)
        par = self.doc.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.keep_with_next = True
        par.add_run().add_picture(str(ruta), width=Cm(ancho_cm))
        self.nota("Fuente: elaboración propia con el dataset preparado (891 registros). "
                  "La misma gráfica, interactiva, está en la aplicación de Streamlit.")

    def salto(self) -> None:
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def filas_resultado(tabla, col) -> list[list[str]]:
    return [
        [str(r[col]), str(int(r["pasajeros"])), str(int(r["sobrevivientes"])), str(int(r["no_sobrevivientes"])),
         num(r["tasa_supervivencia_pct"]), num(r["participacion_pasajeros_pct"])]
        for _, r in tabla.iterrows()
    ]


def enc(primera: str) -> list[str]:
    return [primera, "Pasajeros", "Sobrevivientes", "No sobrevivientes", "Tasa de supervivencia (%)", "Participación (%)"]


# ------------------------------------------------------------------ documento
def construir(raiz: Path, url_app: str = "") -> Path:
    carpeta = raiz / m.CARPETA_AE4
    r = m.calcular_todo(raiz)
    if not r["verificacion"]["coincide_con_ae3"].all():
        raise AssertionError("Las métricas no coinciden con los resultados de AE3.")
    fig = g.generar_figuras(r, carpeta / "figuras")
    T = r["tablas"]
    tot = T["pregunta_1_supervivencia_total"].iloc[0]
    N, S = int(tot["pasajeros"]), int(tot["sobrevivientes"])
    NS, TT = int(tot["no_sobrevivientes"]), float(tot["tasa_supervivencia_pct"])
    c = T["pregunta_2_supervivencia_por_clase"].set_index("clase")
    s = T["pregunta_3_supervivencia_por_sexo"].set_index("sexo")
    e = T["pregunta_4_supervivencia_por_grupo_edad"].set_index("grupo_edad")
    pu = T["pregunta_5_supervivencia_por_puerto"].set_index("puerto_embarque")
    cs = r["clase_sexo"].set_index(["clase", "sexo"])["tasa_supervivencia_pct"]
    tf = r["tarifas"].set_index("clase")
    d = r["datos"]
    brecha = s.loc["Mujer", "tasa_supervivencia_pct"] - s.loc["Hombre", "tasa_supervivencia_pct"]
    primera_cherbourg = (d.loc[d["ciudad_embarque"] == "Cherbourg", "clase"] == "Primera").mean() * 100
    app_texto = url_app or "ejecución local con «streamlit run streamlit_app.py» (instrucciones en el README)"

    w = Documento()
    doc = w.doc

    # ---------------- Portada
    for _ in range(3):
        doc.add_paragraph()
    w.p("Institución Universitaria Digital de Antioquia", WD_ALIGN_PARAGRAPH.CENTER).runs[0].bold = True
    w.p("Proyecto Integrado III · Analítica de Datos", WD_ALIGN_PARAGRAPH.CENTER)
    for _ in range(3):
        doc.add_paragraph()
    titulo = doc.add_paragraph(style="Title")
    titulo.add_run(TITULO)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    w.p("Documento final del proyecto integrador (AE1 a AE4)", WD_ALIGN_PARAGRAPH.CENTER).runs[0].italic = True
    for _ in range(4):
        doc.add_paragraph()
    for linea in (AUTOR, f"Docente: {DOCENTE}", "Medellín, noviembre de 2026"):
        w.p(linea, WD_ALIGN_PARAGRAPH.CENTER)
    for _ in range(3):
        doc.add_paragraph()
    w.p(f"Repositorio: {REPO}", WD_ALIGN_PARAGRAPH.CENTER).runs[0].font.size = Pt(10)
    w.p(f"Aplicación de Streamlit: {app_texto}", WD_ALIGN_PARAGRAPH.CENTER).runs[0].font.size = Pt(10)

    # ---------------- Índices (sección nueva con número de página)
    nueva = doc.add_section(WD_SECTION.NEW_PAGE)
    nueva.footer.is_linked_to_previous = False
    pie = nueva.footer.paragraphs[0]
    pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    campo(pie, "PAGE", "1")
    w.p("Tabla de contenido", WD_ALIGN_PARAGRAPH.LEFT).runs[0].bold = True
    campo(doc.add_paragraph(), 'TOC \\o "1-2" \\h \\z \\u', "Actualice los campos para ver la tabla de contenido.")
    w.salto()
    w.p("Índice de tablas", WD_ALIGN_PARAGRAPH.LEFT).runs[0].bold = True
    campo(doc.add_paragraph(), 'TOC \\h \\z \\c "Tabla"', "Actualice los campos para ver el índice de tablas.")
    doc.add_paragraph()
    w.p("Índice de figuras", WD_ALIGN_PARAGRAPH.LEFT).runs[0].bold = True
    campo(doc.add_paragraph(), 'TOC \\h \\z \\c "Figura"', "Actualice los campos para ver el índice de figuras.")
    w.salto()

    # ---------------- 1. Introducción
    w.h("1. Introducción")
    w.p(
        "Este documento integra el trabajo del Proyecto Integrado III, desarrollado en cuatro actividades sobre el dataset "
        "público BIT/titanic-dataset de Hugging Face. En AE1 se cargó el dataset mediante código y se automatizó su "
        "ejecución; en AE2 se planteó la necesidad analítica y se reconoció la estructura de los datos; en AE3 se "
        "transformó y enriqueció el dataset para responder las preguntas de negocio; y en AE4 se construyeron las "
        "métricas, las visualizaciones y una aplicación de Streamlit que presenta los resultados."
    )
    w.p(
        f"El análisis es descriptivo. Con los {N} registros del split train se calcula cuántos pasajeros sobrevivieron y "
        "cómo varió esa proporción según la clase, el sexo, el grupo de edad y el puerto de embarque. Los resultados "
        "permiten caracterizar asociaciones en los registros, pero no demostrar que una característica haya causado la "
        "supervivencia. El código, los datos preparados, los notebooks, la aplicación y este documento se conservan "
        f"en el repositorio {REPO}."
    )

    # ---------------- 2. Necesidad
    w.h("2. Planteamiento de la necesidad")
    w.p(
        "Se propone un escenario académico hipotético. Un equipo que prepara material de estudio sobre seguridad marítima "
        "necesita describir cómo se distribuyó la supervivencia entre los grupos de pasajeros registrados. La información "
        "le permitiría organizar comparaciones sustentadas en datos y señalar qué grupos presentan diferencias que merecen "
        "una revisión posterior. No se afirma que exista un problema comprobado en una organización actual: el dataset "
        "contiene registros históricos y se usa como base para practicar un análisis descriptivo."
    )
    w.p("¿Cómo varía la proporción de pasajeros registrados como sobrevivientes según la clase, el sexo, el grupo de edad y "
        "el puerto de embarque en el dataset BIT/titanic-dataset?", negrita_inicial="Pregunta general. ")
    w.p("Para responderla, en AE3 la pregunta general se dividió en cinco preguntas de negocio, una por variable, de modo "
        "que cada una tenga su propia tabla, métrica y gráfico.")
    w.tabla(
        "Preguntas de negocio y variables utilizadas",
        ["Pregunta", "Formulación", "Variables"],
        [
            ["P1", "¿Cuál fue la supervivencia total registrada?", "sobrevivio"],
            ["P2", "¿Cómo varió la supervivencia según la clase?", "sobrevivio, clase"],
            ["P3", "¿Cómo varió la supervivencia según el sexo?", "sobrevivio, sexo"],
            ["P4", "¿Cómo varió la supervivencia según el grupo de edad?", "sobrevivio, grupo_edad"],
            ["P5", "¿Cómo varió la supervivencia según el puerto de embarque?", "sobrevivio, ciudad_embarque"],
        ],
        [2, 10, 4.5],
    )

    # ---------------- 3. Justificación
    w.h("3. Justificación")
    w.p(
        "El análisis resume un conjunto de registros individuales en comparaciones comprensibles entre grupos. Para el "
        "beneficiario hipotético, estas comparaciones sirven para preparar tablas, gráficos y explicaciones basadas en "
        "evidencia observable, y para reconocer dónde la falta de datos limita una conclusión."
    )
    w.p(
        "El dataset permite abordar la necesidad porque incluye una variable de resultado (survived) y variables de "
        "agrupación (pclass, sex, age y embark_town), además de la tarifa (fare) como variable complementaria. Su tamaño "
        "permite procesarlo con un equipo personal, el split completo se carga directamente desde Hugging Face y su "
        "licencia (Apache 2.0) permite el uso académico."
    )

    # ---------------- 4. Objetivos
    w.h("4. Objetivos")
    w.h("4.1 Objetivo general", 2)
    w.p("Caracterizar la supervivencia registrada en BIT/titanic-dataset mediante métricas y visualizaciones descriptivas "
        "por clase del pasajero, sexo, grupo de edad y puerto de embarque, presentadas en una aplicación de Streamlit.")
    w.h("4.2 Objetivos específicos", 2)
    w.lista([
        "Reconocer la estructura del dataset: dimensiones, columnas, tipos de datos y valores nulos (AE1 y AE2).",
        "Transformar y enriquecer los datos con reglas de calidad documentadas, sin eliminar registros (AE3).",
        "Calcular la cantidad y la proporción de sobrevivientes en total y por grupo, y verificar los totales (AE3 y AE4).",
        "Presentar los resultados con gráficos e interpretaciones en una aplicación de Streamlit vinculada al repositorio, "
        "e informar las limitaciones que afectan su lectura (AE4).",
    ], numerada=True)

    # ---------------- 5. Marco teórico
    w.h("5. Marco teórico")
    w.h("5.1 Analítica descriptiva", 2)
    w.p("La analítica descriptiva organiza datos observados mediante conteos, proporciones, medidas de resumen, tablas y "
        "gráficos para responder qué ocurrió en un conjunto de registros. Se diferencia de la analítica diagnóstica, que "
        "busca explicar por qué ocurrió, y de la predictiva, que estima resultados futuros. En este proyecto el alcance es "
        "descriptivo, por lo que no se atribuyen causas ni se predicen resultados para otras poblaciones.")
    w.h("5.2 Análisis exploratorio de datos", 2)
    w.p("El análisis exploratorio busca comprender la estructura de un conjunto de datos, reconocer variables relevantes y "
        "detectar anomalías o valores faltantes antes de hacer comparaciones específicas (NIST, s. f.). En AE2 se aplicó "
        "para revisar dimensiones, tipos y nulos.")
    w.h("5.3 Calidad, transformación y enriquecimiento de datos", 2)
    w.p("La transformación ajusta tipos, normaliza categorías y trata faltantes y duplicados; el enriquecimiento crea "
        "variables derivadas que facilitan el análisis. Cada decisión debe documentarse, porque imputar o eliminar "
        "registros puede alterar las estadísticas. Un DataFrame de pandas, estructura tabular etiquetada con columnas de "
        "distintos tipos, permite aplicar estas operaciones de forma reproducible (pandas development team, 2026).")
    w.h("5.4 Métricas: tasas, participación y puntos porcentuales", 2)
    w.p("Una tasa expresa la proporción de casos con un resultado dentro de un grupo (sobrevivientes / pasajeros × 100) y "
        "permite comparar grupos de distinto tamaño. La participación expresa el peso de un grupo en el total. La "
        "diferencia entre dos tasas se expresa en puntos porcentuales (p. p.). Comparar tasas sin informar el tamaño del "
        "grupo puede llevar a conclusiones engañosas, porque una tasa calculada sobre pocos casos es inestable.")
    w.h("5.5 Asociación, causalidad y variables de confusión", 2)
    w.p("Que dos variables aparezcan relacionadas no prueba que una cause la otra. Una tercera variable puede explicar la "
        "relación (confusión): por ejemplo, el puerto de embarque puede asociarse con la supervivencia porque cada puerto "
        "tuvo una composición distinta por clase. Por eso las interpretaciones se redactan como asociaciones.")
    w.h("5.6 Ingresos frente a rentabilidad", 2)
    w.p("Un ingreso es el valor recibido por una venta; la rentabilidad compara ese ingreso con los costos o la inversión "
        "necesarios para obtenerlo. Con solo la tarifa del pasaje puede describirse un ingreso registrado, pero no la "
        "rentabilidad, porque el dataset no contiene costos.")
    w.h("5.7 Visualización y aplicaciones de datos", 2)
    w.p("Un gráfico debe elegirse según la tarea: las barras comparan magnitudes entre categorías y las barras apiladas "
        "muestran la composición de un total. Cada gráfico necesita título, ejes con unidades y fuente. Streamlit es una "
        "biblioteca de Python que convierte scripts de análisis en aplicaciones web interactivas y se puede publicar "
        "desde un repositorio de GitHub (Streamlit, s. f.).")

    # ---------------- 6. Metodología
    w.h("6. Metodología")
    w.p("El proyecto siguió un flujo reproducible en cuatro etapas. Cada etapa conserva su notebook, su código y sus "
        "resultados en el repositorio, y GitHub Actions vuelve a ejecutar las pruebas y los notebooks en cada envío.")
    w.tabla(
        "Etapas del proyecto y evidencias",
        ["Etapa", "Procedimiento", "Evidencia en el repositorio"],
        [
            ["AE1 Carga", "Carga del split train con la biblioteca datasets y selección de variables.",
             "AE1/notebooks, AE1/resultados/titanic_transformado.csv"],
            ["AE2 Necesidad", "Planteamiento de la necesidad, ficha del dataset y reconocimiento de su estructura.",
             "AE2/notebooks, AE2/resultados/resumen_dataframe.txt"],
            ["AE3 Transformación", "Tipos, validaciones, faltantes, duplicados, enriquecimiento y tablas por pregunta.",
             "Carpeta AE3: datos/titanic_preparado.csv y resultados/pregunta_*.csv"],
            ["AE4 Visualización", "Métricas, verificación contra AE3, figuras, aplicación de Streamlit y documento final.",
             "Carpeta AE4 y streamlit_app.py"],
        ],
        [3, 7, 6.5],
    )
    w.h("6.1 Ficha del dataset", 2)
    w.tabla(
        "Ficha del dataset",
        ["Campo", "Detalle"],
        [
            ["Identificador", "BIT/titanic-dataset (Beijing Institute of Technology, Hugging Face)"],
            ["Enlace", "https://huggingface.co/datasets/BIT/titanic-dataset"],
            ["Split y tamaño", "train; 891 filas y 15 columnas; se procesa completo, sin muestra"],
            ["Unidad de análisis", "Registro de un pasajero"],
            ["Licencia", "Apache 2.0"],
            ["Fecha de consulta", "23 de octubre de 2026"],
            ["Procedencia y carácter sintético", "No documentados en la ficha; pendientes de verificar"],
        ],
        [5, 11.5],
    )
    w.h("6.2 Herramientas", 2)
    w.p("Python 3.12, pandas para la manipulación de datos, Jupyter para los notebooks, pytest para las pruebas, "
        "matplotlib para las figuras del documento, Plotly y Streamlit para la aplicación interactiva, python-docx para "
        "generar este documento y GitHub Actions para la ejecución automática.")

    # ---------------- 7. Transformación y enriquecimiento
    w.h("7. Transformación y enriquecimiento de datos")
    w.p("La transformación de AE3 partió del CSV de AE1 (891 filas y seis variables: sobrevivio, clase_pasajero, sexo, "
        "edad, tarifa y ciudad_embarque) y conservó una copia sin modificar para comparar el antes y el después.")
    w.lista([
        "**Tipos:** sobrevivio y clase_pasajero pasaron de int64 a int8; edad y tarifa se convirtieron a numéricas sin perder valores.",
        "**Validaciones:** sobrevivio solo 0 o 1, clase_pasajero solo 1, 2 o 3 y sin edades ni tarifas negativas. "
        "Si una regla falla, la ejecución se detiene; ninguna falló.",
        f"**Categorías:** sexo pasó de male y female a Hombre y Mujer en los {N} registros.",
        "**Faltantes:** las 177 edades vacías se conservaron como nulas, porque imputarlas alteraría las estadísticas, y "
        "se clasificaron como «Edad no registrada»; los 2 puertos vacíos pasaron a «No registrado».",
        "**Duplicados:** 120 filas coinciden en las seis variables, pero no se eliminaron porque no hay identificador de "
        "pasajero y dos personas distintas pueden coincidir en todos los atributos.",
        "**Resultado:** no se eliminó ninguna fila (891 antes y después); las columnas pasaron de 6 a 9.",
    ])
    w.tabla(
        "Diccionario de datos del dataset preparado",
        ["Variable", "Significado", "Tipo", "Unidad o valores", "Origen"],
        [
            ["sobrevivio", "Indica si el pasajero sobrevivió", "Entero", "0 = no, 1 = sí", "Original"],
            ["clase_pasajero", "Clase del pasaje, codificada", "Entero", "1, 2 o 3", "Original"],
            ["sexo", "Sexo registrado", "Texto", "Hombre o Mujer", "Original, normalizada"],
            ["edad", "Edad del pasajero", "Decimal", "Años", "Original"],
            ["tarifa", "Valor pagado por el pasaje", "Decimal", "Moneda no indicada", "Original"],
            ["ciudad_embarque", "Puerto de embarque", "Texto", "Cherbourg, Queenstown, Southampton o No registrado", "Original, normalizada"],
            ["estado_supervivencia", "Etiqueta de sobrevivio", "Texto", "Sobrevivió o No sobrevivió", "Incorporada"],
            ["clase", "Etiqueta de clase_pasajero", "Texto", "Primera, Segunda o Tercera", "Incorporada"],
            ["grupo_edad", "Intervalo de edad", "Texto", "0–12, 13–17, 18–29, 30–44, 45–59, 60 o más, Edad no registrada", "Incorporada"],
        ],
        [3.3, 3.8, 1.7, 5, 2.7],
    )

    # ---------------- 8. Métricas y visualizaciones
    w.h("8. Métricas y visualizaciones")
    w.p("Las métricas se calculan en el módulo metricas.py a partir de datos/titanic_preparado.csv. El mismo módulo "
        "alimenta el notebook de AE4, la aplicación de Streamlit y este documento, y comprueba que las cinco tablas "
        "recalculadas coincidan, grupo a grupo, con las exportadas por el notebook de AE3.")
    w.tabla(
        "Definición de las métricas",
        ["Métrica", "Cálculo", "Unidad"],
        [
            ["Pasajeros", "Número de registros del grupo", "Personas"],
            ["Sobrevivientes", "Suma de sobrevivio (1 = sobrevivió)", "Personas"],
            ["No sobrevivientes", "Pasajeros − sobrevivientes", "Personas"],
            ["Tasa de supervivencia", "Sobrevivientes / pasajeros del grupo × 100", "%"],
            ["Participación", f"Pasajeros del grupo / {N} × 100", "%"],
            ["Brecha", "Diferencia entre dos tasas", "Puntos porcentuales (p. p.)"],
            ["Tarifa total (complemento)", "Suma de tarifa por clase; ingreso registrado, no rentabilidad", "Moneda no indicada"],
        ],
        [4, 9, 3.5],
    )
    w.tabla(
        "Pregunta, métrica y gráfico seleccionado",
        ["Pregunta", "Métrica principal", "Gráfico", "Por qué"],
        [
            ["P1", "Tasa total (%)", "Barra horizontal apilada", "Muestra la composición del total en una sola vista"],
            ["P2 a P5", "Tasa por grupo (%) y participación (%)",
             "Barras de tasa con línea de tasa total y barras apiladas de pasajeros",
             "Compara tasas entre grupos y muestra el tamaño de cada grupo"],
            ["Complementos", "Tasa por clase y sexo; participación en tarifa", "Barras agrupadas", "Compara dos categorías a la vez"],
        ],
        [2.3, 4.2, 5, 5],
    )
    w.p(f"Periodo y alcance: todas las cifras corresponden a los {N} registros del split train (pasajeros del viaje de abril "
        "de 1912). Las categorías sin dato se muestran en gris para no confundirlas con grupos reales; el azul "
        "representa a los sobrevivientes y el naranja a los no sobrevivientes en todos los gráficos.")
    w.h("8.1 Aplicación de Streamlit", 2)
    w.p("La aplicación (streamlit_app.py, en la raíz del repositorio) tiene un menú lateral con diez secciones: inicio "
        "(necesidad, preguntas y dataset), una sección por pregunta, el complemento de tarifas, un explorador de "
        "segmentos con filtros, las conclusiones y una sección de verificación que confirma que las cifras coinciden con "
        "el notebook de AE3. Cada sección de pregunta presenta la ficha de la métrica (métrica, cálculo, unidad y "
        "periodo), indicadores clave, los gráficos interactivos, la interpretación (qué muestran los datos, cómo "
        "responden la pregunta, qué decisión podrían apoyar y sus limitaciones) y la tabla descargable en CSV.")
    w.p(app_texto + ".", negrita_inicial="Acceso a la aplicación: ")

    # ---------------- 9. Resultados y discusión
    w.h("9. Resultados y discusión")
    w.h("9.1 P1: supervivencia total", 2)
    w.tabla("Supervivencia total", enc("Grupo"), filas_resultado(T["pregunta_1_supervivencia_total"], "grupo"))
    w.figura(fig["p1"], "Distribución de los pasajeros según estado de supervivencia")
    w.p(f"Sobrevivieron {S} de {N} pasajeros ({pct(TT)}); {NS} ({pct(100 - TT)}) no sobrevivieron. Esta tasa es la "
        "referencia para comparar los grupos de P2 a P5: un grupo claramente por encima o por debajo merece una "
        "explicación en el material. La cifra describe solo este archivo, cuyo origen no está documentado.")

    w.h("9.2 P2: supervivencia por clase", 2)
    w.tabla("Supervivencia por clase", enc("Clase"), filas_resultado(T["pregunta_2_supervivencia_por_clase"], "clase"))
    w.figura(fig["p2"], "Tasa de supervivencia y pasajeros por clase")
    w.p(f"La tasa baja de forma escalonada: Primera {pct(c.loc['Primera', 'tasa_supervivencia_pct'])}, Segunda "
        f"{pct(c.loc['Segunda', 'tasa_supervivencia_pct'])} y Tercera {pct(c.loc['Tercera', 'tasa_supervivencia_pct'])}. Solo la "
        f"primera clase supera la tasa total. La tercera es la más numerosa ({pct(c.loc['Tercera', 'participacion_pasajeros_pct'])} "
        f"de los pasajeros) y reúne {int(c.loc['Tercera', 'no_sobrevivientes'])} de los {NS} no sobrevivientes. "
        "Decisión que apoya: usar la clase como eje del material y señalar la tercera clase como grupo a profundizar con "
        "otras fuentes. Limitación: es una asociación; la clase se relaciona con sexo, edad y tarifa, y el dataset no "
        "informa la ubicación de los camarotes ni el acceso a los botes.")

    w.h("9.3 P3: supervivencia por sexo", 2)
    w.tabla("Supervivencia por sexo", enc("Sexo"), filas_resultado(T["pregunta_3_supervivencia_por_sexo"], "sexo"))
    w.figura(fig["p3"], "Tasa de supervivencia y pasajeros por sexo")
    w.p(f"Las mujeres tuvieron una tasa de {pct(s.loc['Mujer', 'tasa_supervivencia_pct'])} y los hombres de "
        f"{pct(s.loc['Hombre', 'tasa_supervivencia_pct'])}, una brecha de {num(brecha)} p. p., la mayor de las cinco preguntas, "
        f"aunque los hombres eran {pct(s.loc['Hombre', 'participacion_pasajeros_pct'])} de los pasajeros. La lectura conjunta con "
        "la clase (tabla y figura siguientes) muestra que la brecha se mantiene dentro de cada clase.")
    w.tabla(
        "Complemento: supervivencia por clase y sexo",
        ["Clase", "Sexo", "Pasajeros", "Sobrevivientes", "Tasa de supervivencia (%)"],
        [[f_["clase"], f_["sexo"], str(f_["pasajeros"]), str(f_["sobrevivientes"]), num(f_["tasa_supervivencia_pct"])]
         for _, f_ in r["clase_sexo"].iterrows()],
    )
    w.figura(fig["clase_sexo"], "Tasa de supervivencia por clase y sexo", 14)
    w.p(f"Las tasas van de {pct(cs.min())} (hombres de tercera clase) a {pct(cs.max())} (mujeres de primera clase). Decisión que "
        "apoya: presentar sexo y clase juntos en el material. Limitación: la comparación no controla la edad y no "
        "demuestra que el sexo causara la supervivencia; no hay datos sobre el orden de evacuación.")

    w.h("9.4 P4: supervivencia por grupo de edad", 2)
    w.tabla("Supervivencia por grupo de edad", enc("Grupo de edad (años)"),
            filas_resultado(T["pregunta_4_supervivencia_por_grupo_edad"], "grupo_edad"))
    w.figura(fig["p4"], "Tasa de supervivencia y pasajeros por grupo de edad")
    w.p(f"Los menores de 13 años tienen la tasa más alta ({pct(e.loc['0 a 12', 'tasa_supervivencia_pct'])}) y el grupo de 60 o más "
        f"la más baja ({pct(e.loc['60 o más', 'tasa_supervivencia_pct'])}). Entre 18 y 59 años las tasas son parecidas "
        f"({pct(e.loc['18 a 29', 'tasa_supervivencia_pct'])} a {pct(e.loc['30 a 44', 'tasa_supervivencia_pct'])}). Decisión que apoya: "
        "destacar a los menores de 13 años y pedir la fuente original para completar las edades. Limitaciones: faltan "
        f"{int(e.loc['Edad no registrada', 'pasajeros'])} edades ({pct(e.loc['Edad no registrada', 'participacion_pasajeros_pct'])}), "
        f"el grupo de 60 o más solo tiene {int(e.loc['60 o más', 'pasajeros'])} personas y los cortes de edad son un criterio propio.")

    w.h("9.5 P5: supervivencia por puerto de embarque", 2)
    w.tabla("Supervivencia por puerto de embarque", enc("Puerto"),
            filas_resultado(T["pregunta_5_supervivencia_por_puerto"], "puerto_embarque"))
    w.figura(fig["p5"], "Tasa de supervivencia y pasajeros por puerto de embarque")
    w.p(f"Cherbourg tuvo la tasa más alta ({pct(pu.loc['Cherbourg', 'tasa_supervivencia_pct'])}) y Southampton la más baja "
        f"({pct(pu.loc['Southampton', 'tasa_supervivencia_pct'])}), aunque concentró {pct(pu.loc['Southampton', 'participacion_pasajeros_pct'])} "
        f"de los pasajeros. En Cherbourg el {pct(primera_cherbourg)} de los pasajeros era de primera clase, lo que puede explicar "
        "parte de la diferencia (posible confusión). Decisión que apoya: tratar el puerto como dato de contexto y no "
        "como factor explicativo. Limitación: los 2 casos sin puerto sobrevivieron, pero ese 100 % con dos registros no "
        "es un patrón.")

    w.h("9.6 Complemento: tarifas por clase", 2)
    w.tabla(
        "Tarifa registrada por clase (moneda no indicada)",
        ["Clase", "Pasajeros", "Tarifa total", "Tarifa media", "Tarifa mediana", "Tarifas en cero", "Participación en tarifa (%)"],
        [[cl, str(int(f_["pasajeros"])), num(f_["tarifa_total"]), num(f_["tarifa_media"]), num(f_["tarifa_mediana"]),
          str(int(f_["pasajes_tarifa_cero"])), num(f_["participacion_tarifa_pct"])] for cl, f_ in tf.iterrows()],
    )
    w.figura(fig["tarifas"], "Participación de cada clase en pasajeros y en tarifa total registrada", 14)
    w.p(f"La primera clase reúne {pct(tf.loc['Primera', 'participacion_pasajeros_pct'])} de los pasajeros y "
        f"{pct(tf.loc['Primera', 'participacion_tarifa_pct'])} de la tarifa total registrada; la tercera, con "
        f"{pct(tf.loc['Tercera', 'participacion_pasajeros_pct'])} de los pasajeros, aporta {pct(tf.loc['Tercera', 'participacion_tarifa_pct'])}. "
        "Esta suma es un ingreso registrado por pasajes y no una medida de rentabilidad, porque no hay costos; además, "
        f"la moneda no se indica y hay {int(r['tarifas']['pasajes_tarifa_cero'].sum())} tarifas en cero. Una tarifa más alta "
        "tampoco demuestra que haya causado una mayor supervivencia.")

    w.h("9.7 Discusión", 2)
    w.p("Las cinco preguntas muestran que la supervivencia registrada no fue pareja. El sexo y la clase son las variables "
        "con mayores diferencias y su lectura conjunta indica que la brecha por sexo existe en todas las clases. La edad "
        "separa sobre todo a los menores de 13 años, y el puerto muestra diferencias menores que pueden deberse a la "
        "composición por clase. Como cada variable se analizó por separado (salvo clase y sexo), no se puede medir cuánto "
        "aporta cada una cuando las demás se mantienen constantes; para eso se necesitaría un modelo multivariado, como "
        "una regresión logística, fuera del alcance descriptivo del proyecto.")
    w.tabla(
        "Limitaciones del análisis",
        ["Limitación", "Efecto en la interpretación"],
        [
            ["Alcance descriptivo", "Las diferencias son asociaciones; no prueban causas."],
            ["Variables analizadas por separado", "No se mide el efecto conjunto de clase, sexo, edad y puerto."],
            ["177 edades y 2 puertos faltantes", "Reducen la comparación por edad; no se imputaron."],
            ["Grupos pequeños", "60 o más (26) y sin puerto (2) tienen tasas inestables."],
            ["Origen no documentado", "No se sabe si los datos son sintéticos; no deben generalizarse."],
            ["120 filas coincidentes", "No se pueden confirmar como duplicados sin identificador."],
            ["Tarifa sin moneda y con 15 ceros", "Solo describe un ingreso registrado, no rentabilidad."],
        ],
        [5.5, 11],
    )

    # ---------------- 10. Conclusiones
    w.h("10. Conclusiones y recomendaciones")
    w.h("10.1 Conclusiones", 2)
    w.lista([
        f"La supervivencia registrada fue de {pct(TT)} ({S} de {N} pasajeros) y sirve como referencia para comparar grupos.",
        f"El sexo presenta la mayor diferencia: {num(brecha)} p. p. entre mujeres ({pct(s.loc['Mujer', 'tasa_supervivencia_pct'])}) "
        f"y hombres ({pct(s.loc['Hombre', 'tasa_supervivencia_pct'])}), y se mantiene dentro de cada clase.",
        f"La clase muestra un patrón escalonado, de {pct(c.loc['Primera', 'tasa_supervivencia_pct'])} en primera a "
        f"{pct(c.loc['Tercera', 'tasa_supervivencia_pct'])} en tercera.",
        f"Por edad, los menores de 13 años ({pct(e.loc['0 a 12', 'tasa_supervivencia_pct'])}) se separan de la referencia; los "
        "adultos tienen tasas parecidas entre sí.",
        "El puerto muestra diferencias menores, probablemente relacionadas con la composición por clase de cada puerto.",
        "Las cifras de la aplicación de Streamlit, del notebook de AE4 y de este documento coinciden con las tablas del notebook de AE3.",
    ], numerada=True)
    w.h("10.2 Recomendaciones", 2)
    w.lista([
        "Organizar el material de estudio alrededor del sexo y la clase, mostrados juntos y comparados con la tasa total.",
        "Presentar la edad y el puerto como contexto, siempre con el tamaño de cada grupo y la advertencia de datos faltantes.",
        "Completar la documentación del dataset (procedencia, edades faltantes e identificador de pasajero) antes de proponer explicaciones.",
        "Si se requiere medir efectos conjuntos, aplicar un modelo multivariado en una etapa posterior.",
        "No usar la tarifa como medida de rentabilidad; para ello harían falta datos de costos.",
    ])

    # ---------------- 11. Referencias
    w.h("11. Referencias")
    for ref in (
        "Beijing Institute of Technology. (s. f.). BIT/titanic-dataset [Conjunto de datos]. Hugging Face. Recuperado el 23 de "
        "octubre de 2026 de https://huggingface.co/datasets/BIT/titanic-dataset",
        "Hugging Face. (s. f.). Datasets documentation. https://huggingface.co/docs/datasets/",
        "Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. Computing in Science & Engineering, 9(3), 90–95. "
        "https://doi.org/10.1109/MCSE.2007.55",
        "National Institute of Standards and Technology. (s. f.). What is exploratory data analysis? NIST/SEMATECH "
        "e-Handbook of Statistical Methods. https://www.itl.nist.gov/div898/handbook/eda/section1/eda11.htm",
        "pandas development team. (2026). pandas documentation. https://pandas.pydata.org/docs/",
        "Plotly Technologies Inc. (s. f.). Plotly Python graphing library. https://plotly.com/python/",
        "Streamlit. (s. f.). Streamlit documentation. https://docs.streamlit.io/",
        f"Valencia Duque, S. A. (2026). PI3-ADD: Proyecto Integrado III, analítica de datos [Repositorio de código]. GitHub. {REPO}",
    ):
        par = doc.add_paragraph(ref)
        par.paragraph_format.left_indent = Cm(1.27)
        par.paragraph_format.first_line_indent = Cm(-1.27)

    prop = doc.core_properties
    prop.author = prop.last_modified_by = AUTOR
    prop.title = TITULO
    prop.subject = "Documento final del Proyecto Integrado III, Analítica de Datos"
    prop.comments = ""
    prop.created = prop.modified = datetime.now()
    destino = carpeta / "documento" / f"{NOMBRE_ARCHIVO}.docx"
    destino.parent.mkdir(parents=True, exist_ok=True)
    doc.save(destino)
    return destino


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    print(f"Documento generado: {construir(m.localizar_raiz(), url)}")
