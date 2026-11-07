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
        self._numero_de_pagina()

    def _numero_de_pagina(self) -> None:
        parrafo = self.doc.sections[0].footer.paragraphs[0]
        parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = parrafo.add_run()
        for tipo, texto in (("begin", None), (None, "PAGE"), ("end", None)):
            if tipo:
                nodo = OxmlElement("w:fldChar")
                nodo.set(qn("w:fldCharType"), tipo)
            else:
                nodo = OxmlElement("w:instrText")
                nodo.set(qn("xml:space"), "preserve")
                nodo.text = texto
            run._r.append(nodo)

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

    # Portada sencilla
    for _ in range(5):
        w.parrafo("", centrado=True)
    t = w.doc.add_paragraph(TITULO)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t.runs[0].bold = True
    t.runs[0].font.size = Pt(20)
    w.parrafo("Avance de la actividad AE3", centrado=True)
    w.parrafo("", centrado=True)
    w.parrafo(AUTOR, centrado=True)
    w.parrafo("Proyecto Integrado III - Analítica de Datos", centrado=True)
    w.parrafo("Docente: Andrés Felipe Callejas", centrado=True)
    w.parrafo("Institución Universitaria Digital de Antioquia", centrado=True)
    w.parrafo("Medellín, noviembre de 2026", centrado=True)
    w.salto()

    # Índices
    w.titulo("Contenido")
    for linea in (
        "1. Introducción",
        "2. Necesidad, preguntas y alcance",
        "3. Metodología",
        "    3.1 Datos de entrada y copia sin modificar",
        "    3.2 Transformaciones y reglas de calidad",
        "    3.3 Enriquecimiento de la información",
        "    3.4 Procedimiento para responder cada pregunta",
        "    3.5 Archivos generados y reproducción",
        "4. Diccionario de datos actualizado",
        "5. Resultados y discusión",
        "6. Conclusiones del avance",
        "7. Referencias",
    ):
        p = w.doc.add_paragraph(linea)
        p.paragraph_format.space_after = Pt(2)
    w.titulo("Índice de tablas")
    indice_tablas = w.doc.add_paragraph()  # se completa al final, cuando ya se conocen las tablas
    w.salto()

    # 1. Introducción
    w.titulo("1. Introducción")
    w.parrafo(
        "Este documento recoge el avance de la tercera actividad del proyecto integrador. "
        "En la actividad anterior (AE2) se definió una necesidad analítica sobre el dataset "
        "BIT/titanic-dataset, que es público y está en Hugging Face. En esta etapa se prepara ese "
        f"dataset por medio de código y se responden descriptivamente las preguntas de negocio. Se trabajaron {n} registros "
        "de pasajeros, sin eliminar ninguno, y se construyeron cinco tablas de resultados que "
        "quedan listas para graficarse en AE4."
    )
    w.parrafo(
        f"En total sobrevivieron {sobrev} de los {n} pasajeros registrados, es decir {num(tasa_total)} %. "
        "Las diferencias entre grupos se interpretan como asociaciones dentro de este dataset, "
        "no como causas."
    )

    # 2. Necesidad
    w.titulo("2. Necesidad, preguntas y alcance")
    w.parrafo(
        "La necesidad se mantiene igual que en AE2. Un equipo académico que prepara material sobre "
        "seguridad marítima necesita describir cómo se distribuyó la supervivencia observada entre "
        "los pasajeros registrados según su clase, su sexo, su edad y su puerto de embarque. Es un "
        "escenario hipotético de estudio y el análisis es solamente descriptivo."
    )
    w.parrafo(
        "En AE2 la pregunta de negocio se había planteado de forma compuesta. Para esta entrega se "
        "dividió en cinco preguntas operativas, porque la rúbrica pide una tabla por pregunta y de "
        "ese modo cada resultado se puede graficar por separado en AE4. Esta división no cambia la "
        "necesidad ni las variables principales, solo organiza mejor la respuesta."
    )
    w.tabla(
        "Preguntas de negocio, variables necesarias y resultado esperado",
        ["N.º", "Pregunta de negocio", "Variables", "Resultado esperado"],
        [
            ["1", "¿Cuál fue la supervivencia total registrada?", "sobrevivio", "Conteos y tasa total"],
            ["2", "¿Cómo varió la supervivencia según la clase?", "sobrevivio, clase_pasajero", "Conteos y tasa por clase"],
            ["3", "¿Cómo varió según el sexo registrado?", "sobrevivio, sexo", "Conteos y tasa por sexo"],
            ["4", "¿Cómo varió según el grupo de edad?", "sobrevivio, edad", "Conteos y tasa por intervalo de edad"],
            ["5", "¿Cómo varió según el puerto de embarque?", "sobrevivio, ciudad_embarque", "Conteos y tasa por puerto"],
        ],
    )
    w.parrafo(
        "Un ajuste de alcance: la variable tarifa se conserva en el dataset preparado y se describe "
        "estadísticamente, pero no se usa para ninguna pregunta principal. En AE2 se había definido "
        "como complementaria y el dataset no indica en qué moneda está expresada, así que comparar "
        "tarifas entre grupos no sería confiable."
    )

    # 3. Metodología
    w.titulo("3. Metodología")
    w.titulo("3.1 Datos de entrada y copia sin modificar", 2)
    w.parrafo(
        "Se usó como entrada el archivo AE1/resultados/titanic_transformado.csv, que se generó en AE1 "
        "a partir del split train del dataset BIT/titanic-dataset. Tiene 891 filas y las seis "
        "variables que se necesitan: sobrevivio, clase_pasajero, sexo, edad, tarifa y ciudad_embarque. "
        "Se prefirió este archivo local porque permite reproducir la actividad sin volver a "
        "descargar el dataset en cada ejecución."
    )
    w.parrafo(
        "Al cargar los datos se guarda una copia sin modificar (df_original). Todas las "
        "transformaciones se hacen sobre otra copia, de modo que siempre se puede comparar el "
        "antes y el después."
    )

    w.titulo("3.2 Transformaciones y reglas de calidad", 2)
    w.parrafo("Las operaciones aplicadas fueron las siguientes:")
    w.lista(
        [
            "Tipos de datos: sobrevivio y clase_pasajero ya eran enteros, pero se convirtieron a int8 "
            "porque solo toman valores pequeños. Edad y tarifa se convirtieron a numéricas de forma "
            "explícita y no hubo valores que se perdieran en la conversión.",
            "Validación de dominios: sobrevivio solo puede ser 0 o 1 y clase_pasajero solo 1, 2 o 3. "
            "Además se comprobó que no hubiera edades ni tarifas negativas. El código se detiene con "
            "un error si alguna regla falla; en esta ejecución ninguna falló.",
            f"Normalización de categorías: la variable sexo venía en inglés (male y female). Los {n} "
            "valores se pasaron a Hombre y Mujer. No se encontraron espacios sobrantes ni "
            "mayúsculas inconsistentes en el puerto.",
            f"Valores faltantes: hay {aud['edades_no_registradas']} edades y {aud['puertos_no_registrados']} "
            "puertos sin registrar. La edad se deja vacía en la columna edad, porque inventar un valor "
            "(por ejemplo la media) cambiaría las estadísticas, y en grupo_edad se clasifica como "
            "Edad no registrada. Los dos puertos faltantes se rotulan como No registrado para "
            "que los pasajeros sigan apareciendo en los totales.",
            f"Duplicados: hay {aud['coincidencias_en_seis_variables']} filas que coinciden en las seis variables. "
            "No se eliminaron porque el dataset no tiene un identificador de pasajero y dos personas "
            "distintas pueden tener los mismos atributos. Eliminarlas habría cambiado el total de "
            "pasajeros sin una razón comprobable.",
            f"Selección de columnas y registros: se conservaron las seis columnas pertinentes y "
            f"los {n} registros, porque todas las variables se usan en alguna pregunta o en el "
            "apartado descriptivo.",
        ]
    )
    w.tabla(
        "Comparación del DataFrame antes y después de la transformación",
        ["Control", "Antes", "Después", "Decisión"],
        [
            ["Filas", str(aud["filas_antes"]), str(aud["filas_despues"]), "No se eliminaron registros"],
            ["Columnas", str(aud["columnas_antes"]), str(aud["columnas_despues"]), "Se añadieron 3 variables"],
            ["Tipo de sobrevivio y clase_pasajero", "int64", "int8", "Se compactó el tipo"],
            ["Edad nula", str(aud["edades_no_registradas"]), str(int(final["edad"].isna().sum())), "Se conserva; la categoría se marca en grupo_edad"],
            ["Puerto nulo", str(aud["puertos_no_registrados"]), str(int(final["ciudad_embarque"].isna().sum())), "Se rotula como No registrado"],
            ["Filas con atributos coincidentes", str(aud["coincidencias_en_seis_variables"]), str(aud["coincidencias_en_seis_variables"]), "No se asumen duplicados"],
            ["Valores de sexo cambiados", "male / female", "Hombre / Mujer", f"{n} registros afectados"],
        ],
    )

    w.titulo("3.3 Enriquecimiento de la información", 2)
    w.parrafo(
        "Se añadieron tres variables calculadas a partir de los datos existentes. No se unió "
        "ninguna otra tabla, por lo que no hay riesgo de que una unión multiplique registros. "
        "Para cada pregunta se calcularon, además, los pasajeros, los sobrevivientes, los no "
        "sobrevivientes, la tasa de supervivencia y la participación de cada grupo sobre el total."
    )
    w.tabla(
        "Variables incorporadas, regla de cálculo y utilidad",
        ["Variable", "Regla", "Utilidad para las preguntas"],
        [
            ["estado_supervivencia", "0 pasa a No sobrevivió y 1 pasa a Sobrevivió", "Hace legibles las tablas y los futuros gráficos"],
            ["clase", "1, 2 y 3 pasan a Primera, Segunda y Tercera", "Etiqueta la pregunta 2 y ordena la presentación"],
            ["grupo_edad", "Intervalos de 0 a 12, 13 a 17, 18 a 29, 30 a 44, 45 a 59 y 60 o más; edad vacía pasa a Edad no registrada", "Permite responder la pregunta 4 sin comparar 88 edades distintas"],
        ],
    )
    w.parrafo(
        "Los intervalos de edad se definieron para separar la niñez, la adolescencia, la edad adulta "
        "temprana, la adultez media y las personas mayores. Son un criterio propio del análisis y "
        "otros cortes podrían dar tasas algo distintas."
    )
    w.parrafo(
        "Las fórmulas de las medidas de cada tabla son: no sobrevivientes = pasajeros - "
        "sobrevivientes; tasa de supervivencia (%) = sobrevivientes / pasajeros x 100; participación (%) = "
        f"pasajeros del grupo / {n} x 100."
    )

    w.titulo("3.4 Procedimiento para responder cada pregunta", 2)
    w.parrafo(
        "Para cada pregunta se agrupó el DataFrame final por la variable correspondiente (clase, "
        "sexo, grupo_edad o ciudad_embarque) y se calcularon los conteos y las tasas. La pregunta "
        "1 se resuelve con el total sin agrupar. Después de construir las tablas el código verifica "
        f"que cada una sume {n} pasajeros y {sobrev} sobrevivientes, y que ninguna tasa quede fuera "
        "del rango de 0 a 100. Si alguna comprobación falla, la ejecución se detiene."
    )

    w.titulo("3.5 Archivos generados y reproducción", 2)
    w.parrafo(
        "El notebook y el script transformar_titanic.py exportan automáticamente, con rutas relativas, "
        "los archivos de la tabla siguiente. Cada ejecución los reemplaza, de manera que su contenido "
        "siempre corresponde a los datos de esa ejecución."
    )
    w.tabla(
        "Archivos generados por el código",
        ["Archivo", "Contenido"],
        [
            ["datos/titanic_preparado.csv", f"Dataset transformado y enriquecido ({n} filas y 9 columnas)"],
            ["resultados/pregunta_1_supervivencia_total.csv", "Respuesta a la pregunta 1"],
            ["resultados/pregunta_2_supervivencia_por_clase.csv", "Respuesta a la pregunta 2"],
            ["resultados/pregunta_3_supervivencia_por_sexo.csv", "Respuesta a la pregunta 3"],
            ["resultados/pregunta_4_supervivencia_por_grupo_edad.csv", "Respuesta a la pregunta 4"],
            ["resultados/pregunta_5_supervivencia_por_puerto.csv", "Respuesta a la pregunta 5"],
            ["resultados/resumen_dataframe_ae3.txt", "Filas, columnas, tipos, nulos y estadísticas descriptivas del DataFrame final"],
        ],
    )

    # 4. Diccionario
    w.titulo("4. Diccionario de datos actualizado")
    w.parrafo(
        "La tabla incluye las variables originales utilizadas y las tres incorporadas en esta etapa."
    )
    w.tabla(
        "Diccionario de datos del dataset preparado",
        ["Variable", "Significado", "Tipo", "Unidad o valores", "Origen"],
        [
            ["sobrevivio", "Indica si el pasajero sobrevivió", "Entero", "0 = no, 1 = sí", "Original"],
            ["clase_pasajero", "Clase del pasaje, codificada", "Entero", "1, 2 o 3", "Original"],
            ["sexo", "Sexo registrado del pasajero", "Texto", "Hombre o Mujer", "Original, normalizada"],
            ["edad", "Edad del pasajero", "Decimal", "Años", "Original"],
            ["tarifa", "Valor pagado por el pasaje", "Decimal", "Moneda no indicada en la fuente", "Original"],
            ["ciudad_embarque", "Puerto de embarque", "Texto", "Cherbourg, Queenstown, Southampton o No registrado", "Original, normalizada"],
            ["estado_supervivencia", "Etiqueta de sobrevivio", "Texto", "Sobrevivió o No sobrevivió", "Incorporada"],
            ["clase", "Etiqueta de clase_pasajero", "Texto", "Primera, Segunda o Tercera", "Incorporada"],
            ["grupo_edad", "Intervalo al que pertenece la edad", "Texto", "Años; incluye Edad no registrada", "Incorporada"],
        ],
    )

    # 5. Resultados
    w.titulo("5. Resultados y discusión")
    w.parrafo(
        "Las tablas siguientes salen directamente de los archivos CSV exportados por el notebook. "
        "En todas, la tasa de supervivencia se calcula dentro de cada grupo y la participación "
        "indica qué parte de los pasajeros representa ese grupo."
    )

    w.titulo("5.1 Pregunta 1: supervivencia total", 2)
    w.tabla("Supervivencia total", [e.format("Grupo") for e in ENCABEZADO_RESULTADO],
            filas_resultado(res["pregunta_1_supervivencia_total"], "grupo"))
    w.parrafo(
        f"Sobrevivieron {sobrev} de {n} pasajeros, con una tasa de {num(tasa_total)} %. Este valor sirve "
        "como referencia para ver si cada grupo estuvo por encima o por debajo del promedio."
    )

    w.titulo("5.2 Pregunta 2: supervivencia por clase", 2)
    w.tabla("Supervivencia por clase", [e.format("Clase") for e in ENCABEZADO_RESULTADO],
            filas_resultado(res["pregunta_2_supervivencia_por_clase"], "clase"))
    w.parrafo(
        f"La primera clase tuvo la tasa más alta ({num(clase.loc['Primera', 'tasa_supervivencia_pct'])} %), seguida de la "
        f"segunda ({num(clase.loc['Segunda', 'tasa_supervivencia_pct'])} %) y la tercera ({num(clase.loc['Tercera', 'tasa_supervivencia_pct'])} %). La tercera clase fue "
        f"además la más numerosa, con {int(clase.loc['Tercera', 'pasajeros'])} pasajeros "
        f"({num(clase.loc['Tercera', 'participacion_pasajeros_pct'])} % del total). Esto muestra que la supervivencia no se "
        "repartió de forma pareja entre las clases, pero no permite afirmar que la clase haya sido la causa."
    )

    w.titulo("5.3 Pregunta 3: supervivencia por sexo", 2)
    w.tabla("Supervivencia por sexo", [e.format("Sexo") for e in ENCABEZADO_RESULTADO],
            filas_resultado(res["pregunta_3_supervivencia_por_sexo"], "sexo"))
    w.parrafo(
        f"La tasa de las mujeres ({num(sexo.loc['Mujer', 'tasa_supervivencia_pct'])} %) fue {num(brecha_sexo)} puntos "
        f"porcentuales mayor que la de los hombres ({num(sexo.loc['Hombre', 'tasa_supervivencia_pct'])} %), aunque ellos fueron "
        f"mayoría ({num(sexo.loc['Hombre', 'participacion_pasajeros_pct'])} % de los pasajeros). Esta comparación no controla "
        "otras variables como la clase o la edad."
    )

    w.titulo("5.4 Pregunta 4: supervivencia por grupo de edad", 2)
    w.tabla("Supervivencia por grupo de edad", [e.format("Grupo de edad (años)") for e in ENCABEZADO_RESULTADO],
            filas_resultado(res["pregunta_4_supervivencia_por_grupo_edad"], "grupo_edad"))
    w.parrafo(
        f"Entre los pasajeros con edad registrada, el grupo de {mejor_edad} años tuvo la tasa más alta "
        f"({num(edad.loc[mejor_edad, 'tasa_supervivencia_pct'])} %) y el de {peor_edad} años la más baja "
        f"({num(edad.loc[peor_edad, 'tasa_supervivencia_pct'])} %). Los {int(edad.loc['Edad no registrada', 'pasajeros'])} pasajeros sin edad "
        f"({num(edad.loc['Edad no registrada', 'participacion_pasajeros_pct'])} % del total) se muestran aparte y limitan esta "
        "comparación, porque no se sabe a qué grupo pertenecen. Además, el grupo de 60 años o más "
        f"solo tiene {int(edad.loc['60 o más', 'pasajeros'])} pasajeros y su tasa es poco estable."
    )

    w.titulo("5.5 Pregunta 5: supervivencia por puerto de embarque", 2)
    w.tabla("Supervivencia por puerto de embarque", [e.format("Puerto de embarque") for e in ENCABEZADO_RESULTADO],
            filas_resultado(res["pregunta_5_supervivencia_por_puerto"], "puerto_embarque"))
    w.parrafo(
        f"{mejor_puerto} tuvo la tasa más alta entre los puertos registrados "
        f"({num(puerto.loc[mejor_puerto, 'tasa_supervivencia_pct'])} %) y {peor_puerto} la más baja "
        f"({num(puerto.loc[peor_puerto, 'tasa_supervivencia_pct'])} %). Southampton fue el puerto de la mayoría de los "
        f"pasajeros ({num(puerto.loc['Southampton', 'participacion_pasajeros_pct'])} %). Los dos pasajeros sin puerto sobrevivieron "
        "ambos, pero con solo dos casos ese 100 % no se puede interpretar como un patrón."
    )

    w.titulo("5.6 Limitaciones de las respuestas", 2)
    w.lista(
        [
            "La ficha de Hugging Face no explica de dónde vienen originalmente los datos ni indica "
            "si son sintéticos, por eso los resultados describen este archivo y no se generalizan.",
            "No hay identificador de pasajero, así que no se puede confirmar si las 120 filas con "
            "atributos coincidentes son personas distintas.",
            "Hay 177 edades y 2 puertos sin registrar.",
            "Cada pregunta se analizó por separado: las diferencias por clase, sexo, edad y puerto "
            "pueden estar mezcladas entre sí y no se midió su efecto conjunto.",
            f"La tarifa tiene {tarifa_cero} valores en cero y no se conoce su moneda, por lo que se "
            "conserva solo como dato descriptivo.",
        ]
    )

    # 6. Conclusiones
    w.titulo("6. Conclusiones del avance")
    w.parrafo(
        "La transformación y el enriquecimiento permitieron responder las cinco preguntas con tablas "
        "claras, reproducibles y que conservan los 891 registros. El análisis muestra que la "
        f"supervivencia no fue pareja: la primera clase ({num(clase.loc['Primera', 'tasa_supervivencia_pct'])} %), las mujeres "
        f"({num(sexo.loc['Mujer', 'tasa_supervivencia_pct'])} %) y el grupo de 0 a 12 años ({num(edad.loc['0 a 12', 'tasa_supervivencia_pct'])} %) estuvieron por "
        f"encima de la tasa total ({num(tasa_total)} %), mientras que la tercera clase y los hombres estuvieron por debajo. "
        f"Por puerto, Southampton concentró más pasajeros y {mejor_puerto} tuvo la tasa más alta."
    )
    w.parrafo(
        "Queda sin resolver el origen del dataset, la identidad única de cada registro, la edad de "
        "177 pasajeros y el efecto conjunto de las variables. En AE4 las tablas exportadas se "
        "podrán representar gráficamente, conservando estas advertencias y evitando afirmaciones "
        "causales."
    )

    # 7. Referencias
    w.titulo("7. Referencias")
    for ref in (
        "Beijing Institute of Technology. (s. f.). BIT/titanic-dataset [Conjunto de datos]. Hugging Face. https://huggingface.co/datasets/BIT/titanic-dataset",
        "Hugging Face. (s. f.). Datasets documentation. https://huggingface.co/docs/datasets/",
        "The pandas development team. (s. f.). pandas documentation. https://pandas.pydata.org/docs/",
    ):
        p = w.doc.add_paragraph(ref)
        p.paragraph_format.left_indent = Pt(36)
        p.paragraph_format.first_line_indent = Pt(-36)

    # Índice de tablas (ya se conocen todas)
    for i, titulo in enumerate(w.tablas, start=1):
        indice_tablas.add_run(f"Tabla {i}. {titulo}\n")

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
