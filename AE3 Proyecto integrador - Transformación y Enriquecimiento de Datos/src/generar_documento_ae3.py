"""Genera el documento Word de AE3 con las cifras leídas de los archivos exportados."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from transformar_titanic import CARPETA_AE3, cargar_datos, localizar_raiz, transformar

AUTOR = "Santiago Andres Valencia Duque"
TITULO = "Transformación y enriquecimiento del dataset Titanic"


def num(valor: float, decimales: int = 2) -> str:
    """Formatea con coma decimal, como se escribe en español."""
    return f"{valor:.{decimales}f}".replace(".", ",")


class Informe:
    """Pequeño ayudante para armar el documento con numeración de tablas."""

    def __init__(self) -> None:
        self.doc = Document()
        self.tablas: list[str] = []
        estilo = self.doc.styles["Normal"]
        estilo.font.name = "Times New Roman"
        estilo.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        estilo.font.size = Pt(12)
        estilo.paragraph_format.space_after = Pt(8)
        estilo.paragraph_format.line_spacing = 1.15
        for nombre, tam in (("Heading 1", 15), ("Heading 2", 13)):
            h = self.doc.styles[nombre]
            h.font.name = "Times New Roman"
            h.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
            h.font.size = Pt(tam)
            h.font.bold = True
            h.font.color.rgb = None

    def titulo(self, texto: str, nivel: int = 1) -> None:
        self.doc.add_heading(texto, level=nivel)

    def parrafo(self, texto: str, centrado: bool = False) -> None:
        p = self.doc.add_paragraph(texto)
        if centrado:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def lista(self, items: list[str]) -> None:
        for item in items:
            self.doc.add_paragraph(item, style="List Bullet")

    def salto(self) -> None:
        self.doc.add_page_break()

    def tabla(self, titulo: str, encabezados: list[str], filas: list[list[str]]) -> None:
        self.tablas.append(titulo)
        leyenda = self.doc.add_paragraph()
        leyenda.paragraph_format.keep_with_next = True
        negrita = leyenda.add_run(f"Tabla {len(self.tablas)}. ")
        negrita.bold = True
        leyenda.add_run(titulo).italic = True
        t = self.doc.add_table(rows=1, cols=len(encabezados))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for celda, texto in zip(t.rows[0].cells, encabezados):
            celda.text = ""
            run = celda.paragraphs[0].add_run(texto)
            run.bold = True
            run.font.size = Pt(10)
            sombra = OxmlElement("w:shd")
            sombra.set(qn("w:val"), "clear")
            sombra.set(qn("w:fill"), "E7E6E6")
            celda._tc.get_or_add_tcPr().append(sombra)
        for fila in filas:
            celdas = t.add_row().cells
            for celda, texto in zip(celdas, fila):
                celda.text = ""
                celda.paragraphs[0].add_run(str(texto)).font.size = Pt(10)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)


def filas_resultado(tabla: pd.DataFrame, primera: str) -> list[list[str]]:
    """Convierte una tabla de resultados en filas de texto para el Word."""
    filas = []
    for _, r in tabla.iterrows():
        filas.append(
            [
                str(r[primera]),
                f"{int(r['pasajeros'])}",
                f"{int(r['sobrevivientes'])}",
                f"{int(r['no_sobrevivientes'])}",
                num(r["tasa_supervivencia_pct"]),
                num(r["participacion_pasajeros_pct"]),
            ]
        )
    return filas


ENCABEZADO_RESULTADO = [
    "{}",
    "Pasajeros",
    "Sobrevivientes",
    "No sobrevivientes",
    "Tasa de supervivencia (%)",
    "Participación (%)",
]


def construir(raiz: Path) -> Path:
    carpeta = raiz / CARPETA_AE3
    original = cargar_datos(raiz / "AE1" / "resultados" / "titanic_transformado.csv")
    final, aud = transformar(original)
    datos = pd.read_csv(carpeta / "datos" / "titanic_preparado.csv", encoding="utf-8-sig")
    res = {
        ruta.stem: pd.read_csv(ruta, encoding="utf-8-sig")
        for ruta in sorted((carpeta / "resultados").glob("pregunta_*.csv"))
    }
    if len(datos) != len(final) or int(datos["sobrevivio"].sum()) != int(final["sobrevivio"].sum()):
        raise AssertionError("El CSV preparado no coincide con la transformación actual.")

    total = res["pregunta_1_supervivencia_total"].iloc[0]
    clase = res["pregunta_2_supervivencia_por_clase"].set_index("clase")
    sexo = res["pregunta_3_supervivencia_por_sexo"].set_index("sexo")
    edad = res["pregunta_4_supervivencia_por_grupo_edad"].set_index("grupo_edad")
    puerto = res["pregunta_5_supervivencia_por_puerto"].set_index("puerto_embarque")
    n = int(total["pasajeros"])
    sobrev = int(total["sobrevivientes"])
    tasa_total = float(total["tasa_supervivencia_pct"])
    tarifa_cero = int((original["tarifa"] == 0).sum())
    brecha_sexo = sexo.loc["Mujer", "tasa_supervivencia_pct"] - sexo.loc["Hombre", "tasa_supervivencia_pct"]
    con_edad = edad.drop(index="Edad no registrada")
    mejor_edad = con_edad["tasa_supervivencia_pct"].idxmax()
    peor_edad = con_edad["tasa_supervivencia_pct"].idxmin()
    puertos_reg = puerto.drop(index="No registrado")
    mejor_puerto = puertos_reg["tasa_supervivencia_pct"].idxmax()
    peor_puerto = puertos_reg["tasa_supervivencia_pct"].idxmin()

    w = Informe()

    t = w.doc.add_paragraph(TITULO)
    t.runs[0].bold = True
    t.runs[0].font.size = Pt(16)
    w.parrafo(f"{AUTOR} - Proyecto Integrado III, Analítica de Datos - Avance AE3")

    # 1. Metodología
    w.titulo("1. Metodología")
    w.parrafo(
        "Se mantiene la necesidad de AE2: describir cómo se distribuyó la supervivencia observada "
        "entre los pasajeros registrados del dataset BIT/titanic-dataset (split train) según clase, "
        "sexo, edad y puerto de embarque. La pregunta compuesta de AE2 se dividió en cinco preguntas "
        "para obtener una tabla por pregunta y poder graficarlas por separado en AE4; esto no cambia "
        "la necesidad ni las variables. Se usó como entrada el CSV de AE1 "
        "(AE1/resultados/titanic_transformado.csv), con 891 filas y seis variables, y se guardó una "
        "copia sin modificar (df_original) para comparar el antes y el después. Las preguntas y las "
        "variables usadas son:"
    )
    w.lista(
        [
            "P1. ¿Cuál fue la supervivencia total? Variable: sobrevivio.",
            "P2. ¿Cómo varió según la clase? Variables: sobrevivio, clase_pasajero.",
            "P3. ¿Cómo varió según el sexo? Variables: sobrevivio, sexo.",
            "P4. ¿Cómo varió según el grupo de edad? Variables: sobrevivio, edad.",
            "P5. ¿Cómo varió según el puerto de embarque? Variables: sobrevivio, ciudad_embarque.",
        ]
    )
    w.parrafo(
        "La tarifa se conserva y se describe, pero no se usa en ninguna pregunta: en AE2 era una "
        "variable complementaria y la fuente no indica su moneda."
    )

    w.titulo("Transformaciones y reglas de calidad", 2)
    w.lista(
        [
            "Tipos: sobrevivio y clase_pasajero ya eran enteros y se pasaron de int64 a int8; edad y "
            "tarifa se convirtieron a numéricas sin perder valores.",
            "Validaciones: sobrevivio solo puede ser 0 o 1, clase_pasajero solo 1, 2 o 3 y no puede "
            "haber edades ni tarifas negativas. Ninguna regla falló.",
            f"Categorías: sexo pasó de male y female a Hombre y Mujer en los {n} registros.",
            f"Faltantes: {aud['edades_no_registradas']} edades y {aud['puertos_no_registrados']} puertos. "
            "La edad se dejó vacía, porque imputarla (por ejemplo con la media) alteraría las "
            "estadísticas, y se clasificó como Edad no registrada en grupo_edad. Los dos puertos "
            "pasaron a la categoría No registrado para que sigan en los totales.",
            f"Duplicados: hay {aud['coincidencias_en_seis_variables']} filas con las seis variables "
            "iguales. No se eliminaron porque el dataset no tiene identificador de pasajero y dos "
            "personas distintas pueden coincidir en todos los atributos.",
            f"Resultado: no se eliminó ninguna fila ({aud['filas_antes']} antes y {aud['filas_despues']} "
            f"después) y las columnas pasaron de {aud['columnas_antes']} a {aud['columnas_despues']}.",
        ]
    )

    w.titulo("Enriquecimiento", 2)
    w.parrafo(
        "Se crearon tres variables con los datos existentes; no se unió ninguna otra tabla, así que no "
        "hay riesgo de multiplicar registros."
    )
    w.lista(
        [
            "estado_supervivencia: 0 = No sobrevivió y 1 = Sobrevivió. Hace legibles las tablas.",
            "clase: 1 = Primera, 2 = Segunda y 3 = Tercera. Etiqueta la pregunta 2.",
            "grupo_edad: intervalos de 0 a 12, 13 a 17, 18 a 29, 30 a 44, 45 a 59 y 60 o más, más "
            "Edad no registrada. Permite responder la pregunta 4. Los cortes son un criterio propio.",
        ]
    )

    w.titulo("Procedimiento para responder cada pregunta", 2)
    w.parrafo(
        "Se agrupó el DataFrame final por clase, sexo, grupo_edad y ciudad_embarque (la pregunta 1 usa "
        "el total) y se calcularon: no sobrevivientes = pasajeros - sobrevivientes; tasa de supervivencia "
        f"(%) = sobrevivientes / pasajeros x 100; participación (%) = pasajeros del grupo / {n} x 100. "
        f"El código comprueba que cada tabla sume {n} pasajeros y {sobrev} sobrevivientes y que ninguna "
        "tasa salga del rango de 0 a 100. El notebook exporta automáticamente el dataset preparado, las "
        "cinco tablas en CSV y el resumen descriptivo en TXT, con rutas relativas."
    )

    # 2. Diccionario
    w.titulo("2. Diccionario de datos actualizado")
    w.tabla(
        "Variables utilizadas e incorporadas",
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
            ["grupo_edad", "Intervalo de edad", "Texto", "Años; incluye Edad no registrada", "Incorporada"],
        ],
    )

    # 3. Resultados
    w.titulo("3. Resultados y discusión")

    w.titulo("Pregunta 1: supervivencia total", 2)
    w.tabla("Supervivencia total", [e.format("Grupo") for e in ENCABEZADO_RESULTADO],
            filas_resultado(res["pregunta_1_supervivencia_total"], "grupo"))
    w.parrafo(
        f"Sobrevivieron {sobrev} de {n} pasajeros ({num(tasa_total)} %). Este valor es la referencia "
        "para comparar los demás grupos."
    )

    w.titulo("Pregunta 2: supervivencia por clase", 2)
    w.tabla("Supervivencia por clase", [e.format("Clase") for e in ENCABEZADO_RESULTADO],
            filas_resultado(res["pregunta_2_supervivencia_por_clase"], "clase"))
    w.parrafo(
        f"La primera clase tuvo la tasa más alta ({num(clase.loc['Primera', 'tasa_supervivencia_pct'])} %), seguida de la "
        f"segunda ({num(clase.loc['Segunda', 'tasa_supervivencia_pct'])} %) y la tercera ({num(clase.loc['Tercera', 'tasa_supervivencia_pct'])} %), que además fue la "
        f"más numerosa ({int(clase.loc['Tercera', 'pasajeros'])} pasajeros, {num(clase.loc['Tercera', 'participacion_pasajeros_pct'])} % del total). "
        "La supervivencia no se repartió de forma pareja, pero esto no prueba que la clase fuera la causa."
    )

    w.titulo("Pregunta 3: supervivencia por sexo", 2)
    w.tabla("Supervivencia por sexo", [e.format("Sexo") for e in ENCABEZADO_RESULTADO],
            filas_resultado(res["pregunta_3_supervivencia_por_sexo"], "sexo"))
    w.parrafo(
        f"La tasa de las mujeres ({num(sexo.loc['Mujer', 'tasa_supervivencia_pct'])} %) fue {num(brecha_sexo)} puntos "
        f"porcentuales mayor que la de los hombres ({num(sexo.loc['Hombre', 'tasa_supervivencia_pct'])} %), aunque ellos eran "
        f"el {num(sexo.loc['Hombre', 'participacion_pasajeros_pct'])} % de los pasajeros. La comparación no controla clase ni edad."
    )

    w.titulo("Pregunta 4: supervivencia por grupo de edad", 2)
    w.tabla("Supervivencia por grupo de edad", [e.format("Grupo de edad (años)") for e in ENCABEZADO_RESULTADO],
            filas_resultado(res["pregunta_4_supervivencia_por_grupo_edad"], "grupo_edad"))
    w.parrafo(
        f"Entre quienes tienen edad registrada, el grupo de {mejor_edad} años tuvo la tasa más alta "
        f"({num(edad.loc[mejor_edad, 'tasa_supervivencia_pct'])} %) y el de {peor_edad} años la más baja "
        f"({num(edad.loc[peor_edad, 'tasa_supervivencia_pct'])} %). Los {int(edad.loc['Edad no registrada', 'pasajeros'])} pasajeros sin edad "
        f"({num(edad.loc['Edad no registrada', 'participacion_pasajeros_pct'])} %) limitan la comparación, y el grupo de 60 o más "
        f"solo tiene {int(edad.loc['60 o más', 'pasajeros'])} pasajeros, por lo que su tasa es poco estable."
    )

    w.titulo("Pregunta 5: supervivencia por puerto de embarque", 2)
    w.tabla("Supervivencia por puerto de embarque", [e.format("Puerto de embarque") for e in ENCABEZADO_RESULTADO],
            filas_resultado(res["pregunta_5_supervivencia_por_puerto"], "puerto_embarque"))
    w.parrafo(
        f"{mejor_puerto} tuvo la tasa más alta entre los puertos registrados "
        f"({num(puerto.loc[mejor_puerto, 'tasa_supervivencia_pct'])} %) y {peor_puerto} la más baja "
        f"({num(puerto.loc[peor_puerto, 'tasa_supervivencia_pct'])} %), con la mayoría de los pasajeros "
        f"({num(puerto.loc['Southampton', 'participacion_pasajeros_pct'])} %). Los dos casos sin puerto sobrevivieron, "
        "pero con solo dos registros ese 100 % no es un patrón."
    )

    w.titulo("Limitaciones", 2)
    w.parrafo(
        "El análisis es descriptivo y solo vale para este archivo: la ficha de Hugging Face no explica "
        "el origen de los datos ni si son sintéticos. Cada pregunta se analizó por separado, así que no "
        "se midió el efecto conjunto de clase, sexo, edad y puerto. Faltan 177 edades y 2 puertos, no hay "
        "identificador de pasajero para confirmar los 120 registros coincidentes y la tarifa tiene "
        f"{tarifa_cero} valores en cero sin moneda conocida."
    )

    # 4. Conclusiones
    w.titulo("4. Conclusiones del avance")
    w.parrafo(
        "Las cinco tablas responden las preguntas conservando los 891 registros. La supervivencia no fue "
        f"pareja: la primera clase ({num(clase.loc['Primera', 'tasa_supervivencia_pct'])} %), las mujeres "
        f"({num(sexo.loc['Mujer', 'tasa_supervivencia_pct'])} %) y el grupo de 0 a 12 años ({num(edad.loc['0 a 12', 'tasa_supervivencia_pct'])} %) "
        f"superaron la tasa total ({num(tasa_total)} %), mientras que la tercera clase y los hombres quedaron por "
        f"debajo, y {mejor_puerto} tuvo la mayor tasa por puerto. Quedan sin resolver el origen del dataset, "
        "la identidad de cada registro, las edades faltantes y el efecto conjunto de las variables. "
        "Las tablas exportadas quedan listas para graficarse en AE4."
    )

    # 5. Referencias
    w.titulo("5. Referencias")
    for ref in (
        "Beijing Institute of Technology. (s. f.). BIT/titanic-dataset [Conjunto de datos]. Hugging Face. https://huggingface.co/datasets/BIT/titanic-dataset",
        "Hugging Face. (s. f.). Datasets documentation. https://huggingface.co/docs/datasets/",
        "The pandas development team. (s. f.). pandas documentation. https://pandas.pydata.org/docs/",
    ):
        p = w.doc.add_paragraph(ref)
        p.paragraph_format.left_indent = Pt(36)
        p.paragraph_format.first_line_indent = Pt(-36)

    propiedades = w.doc.core_properties
    propiedades.author = AUTOR
    propiedades.last_modified_by = AUTOR
    propiedades.title = TITULO
    propiedades.subject = "Avance AE3 de Proyecto Integrado III Analítica de Datos"
    propiedades.comments = ""
    propiedades.created = propiedades.modified = datetime.now()
    destino = carpeta / "documento" / "AE3_Titanic.docx"
    destino.parent.mkdir(parents=True, exist_ok=True)
    w.doc.save(destino)
    return destino


if __name__ == "__main__":
    ruta = construir(localizar_raiz())
    print(f"Documento generado: {ruta}")
