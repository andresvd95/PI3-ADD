# Guion de la presentación (10 minutos)

Proyecto Integrado III · Analítica de Datos · Supervivencia registrada en el Titanic

**Antes de grabar o presentar:** abrir la app con `streamlit run streamlit_app.py`
(o el enlace de Streamlit Cloud) en la página **Inicio**, con el repositorio
abierto en otra pestaña. Si el equipo tiene varios integrantes, repartir los
bloques como se indica entre corchetes.

---

## Bloque 1 · Necesidad, preguntas y datos (0:00 – 2:00) [Integrante 1]

**En pantalla:** página *Inicio*.

> Buenos días. Soy Santiago Andrés Valencia Duque y les presento el Proyecto
> Integrado III de Analítica de Datos: la supervivencia registrada de los
> pasajeros del Titanic.
>
> Partimos de un escenario académico hipotético: un equipo que prepara material
> de estudio sobre seguridad marítima necesita describir cómo se distribuyó la
> supervivencia entre los grupos de pasajeros, para apoyar sus comparaciones en
> datos y señalar qué grupos merecen una revisión posterior.
>
> La pregunta general es: ¿cómo varía la proporción de sobrevivientes según la
> clase, el sexo, el grupo de edad y el puerto de embarque? Para responderla la
> dividimos en cinco preguntas de negocio, una por variable, que ven en esta
> tabla.
>
> Usamos el dataset público BIT/titanic-dataset de Hugging Face, split train:
> 891 pasajeros y 15 variables, con licencia Apache 2.0. En la etapa de
> transformación no eliminamos ninguna fila: las 177 edades vacías quedaron como
> "Edad no registrada" y los 2 puertos vacíos como "No registrado". Tampoco
> borramos las 120 filas con atributos repetidos, porque no hay un identificador
> de pasajero que pruebe que son duplicados.
>
> Una aclaración importante: el análisis es descriptivo. Muestra asociaciones en
> los registros, no causas.

---

## Bloque 2 · Demostración de la aplicación (2:00 – 8:00)

### P1 · Supervivencia total (2:00 – 2:45) [Integrante 2]

**En pantalla:** menú *Preguntas → P1 · Supervivencia total*.

> La aplicación tiene un menú superior, como una página web. Cada pregunta
> empieza con una ficha que dice qué métrica usamos, cómo se calcula, en qué
> unidad está y qué periodo cubre.
>
> En P1 la métrica es la tasa de supervivencia: sobrevivientes entre pasajeros,
> por cien. Sobrevivieron 342 de 891 pasajeros, es decir, el 38,38 %. Más o menos
> seis de cada diez no sobrevivieron. Este 38,38 % es nuestra línea de
> referencia: en las siguientes gráficas aparece como una línea punteada para
> comparar cada grupo.

### P2 · Clase (2:45 – 3:45) [Integrante 2]

**En pantalla:** *P2 · Por clase*. Pasar el cursor por una barra para mostrar el detalle.

> A la izquierda está la tasa por clase y a la derecha cuántas personas había en
> cada clase, en azul quienes sobrevivieron y en naranja quienes no.
>
> La tasa baja por escalones: primera clase 62,96 %, segunda 47,28 % y tercera
> 24,24 %. Solo la primera clase supera la referencia. Y la tercera clase pesa
> mucho: tiene el 55 % de los pasajeros y 372 de los 549 no sobrevivientes.
>
> Esto apoya una decisión concreta: usar la clase como eje del material y marcar
> la tercera clase como el grupo a profundizar. La limitación es que la clase se
> mezcla con otras variables y el dataset no dice dónde estaban los camarotes ni
> quién tuvo acceso a los botes, así que no podemos decir que la clase fuera la
> causa.

### P3 · Sexo (3:45 – 4:55) [Integrante 3]

**En pantalla:** *P3 · Por sexo*; bajar hasta la gráfica por clase y sexo.

> Por sexo está la diferencia más grande de todo el análisis: las mujeres
> tuvieron una tasa de 74,20 % y los hombres de 18,89 %. Son 55,31 puntos
> porcentuales de brecha, aunque los hombres eran casi dos de cada tres
> pasajeros.
>
> Abajo cruzamos sexo y clase. La brecha aparece en las tres clases: en primera
> sobrevivió el 96,81 % de las mujeres y el 36,89 % de los hombres; en tercera,
> el 50 % de las mujeres y solo el 13,54 % de los hombres.
>
> Por eso recomendamos presentar sexo y clase juntos. No afirmamos que el sexo
> haya causado la supervivencia: no tenemos datos del orden de evacuación.

### P4 · Edad (4:55 – 5:55) [Integrante 3]

**En pantalla:** *P4 · Por grupo de edad*. Señalar la barra gris.

> Por edad, los niños de 0 a 12 años tienen la tasa más alta, 57,97 %, y el grupo
> de 60 años o más la más baja, 26,92 %. Entre 18 y 59 años las tasas son
> parecidas, entre 35 y 42 %.
>
> La barra gris son las 177 personas sin edad registrada, casi el 20 % del
> total. La mostramos aparte para no confundirla con un grupo de edad real. Esa
> falta de datos, y que el grupo de 60 o más solo tenga 26 personas, son las
> limitaciones de esta pregunta.

### P5 · Puerto (5:55 – 6:45) [Integrante 4]

**En pantalla:** *P5 · Por puerto*; señalar la tabla de composición por clase.

> Por puerto de embarque, Cherbourg tuvo la tasa más alta, 55,36 %, y
> Southampton la más baja, 33,70 %, aunque de Southampton salió el 72 % de los
> pasajeros.
>
> Pero ojo: en esta tabla se ve que en Cherbourg embarcó una proporción mucho
> mayor de primera clase. Entonces la diferencia puede deberse a quién subió en
> cada puerto y no al puerto en sí. Por eso lo tratamos como dato de contexto.
> Los dos casos sin puerto sobrevivieron, pero con dos registros ese 100 % no es
> un patrón.

### Tarifas, explorador y verificación (6:45 – 8:00) [Integrante 4]

**En pantalla:** *Análisis → Tarifas por clase*, luego *Explorador de segmentos*
(dejar solo Tercera y Hombre) y por último *Cierre → Verificación de datos*.

> Como complemento revisamos la tarifa. La primera clase era el 24 % de los
> pasajeros, pero reunía el 63 % de la tarifa total registrada. Aquí hay que
> distinguir ingreso de rentabilidad: la suma de tarifas es un ingreso
> registrado. No podemos hablar de rentabilidad porque no hay costos, y además
> no sabemos la moneda.
>
> En el explorador se puede filtrar cualquier combinación. Por ejemplo, hombres
> de tercera clase: 347 personas con una tasa de 13,54 %, unos 25 puntos por
> debajo de la referencia.
>
> Por último, la página de verificación confirma que las cinco tablas que
> calcula la aplicación coinciden con las del notebook. La app lee el dataset
> preparado del repositorio de GitHub y usa el mismo código que el notebook y el
> documento PDF.

---

## Bloque 3 · Conclusiones, recomendaciones y limitaciones (8:00 – 10:00) [Integrante 1]

**En pantalla:** *Cierre → Conclusiones*.

> Para cerrar, las conclusiones.
>
> Primero: la supervivencia fue de 38,38 % y no se repartió de forma pareja.
> Segundo: el sexo es la variable con mayor diferencia, 55 puntos, y se mantiene
> dentro de cada clase. Tercero: la clase muestra un patrón escalonado, de 63 % en
> primera a 24 % en tercera. Cuarto: por edad, solo los menores de 13 años se
> separan con claridad. Y quinto: el puerto muestra diferencias pequeñas que
> probablemente reflejan la composición por clase.
>
> Recomendamos organizar el material de estudio alrededor del sexo y la clase,
> mostrados juntos; presentar edad y puerto solo como contexto, siempre con el
> tamaño del grupo; completar la documentación del dataset antes de proponer
> explicaciones; y no usar la tarifa como medida de rentabilidad.
>
> Las limitaciones: es un análisis descriptivo, no causal; analizamos casi todas
> las variables por separado; faltan 177 edades; algunos grupos son muy pequeños;
> y la ficha del dataset no dice de dónde vienen los datos ni si son sintéticos.
> Para medir el efecto conjunto de las variables, el siguiente paso sería un
> modelo multivariado, como una regresión logística.
>
> Todo el trabajo, con los notebooks, el código de la aplicación, las pruebas y
> el documento final en PDF, está en el repositorio de GitHub PI3-ADD. Muchas
> gracias.

---

**Tiempo aproximado:** unas 1.250 palabras habladas, cerca de 9 minutos y medio
a ritmo normal, más los cambios de pantalla.
