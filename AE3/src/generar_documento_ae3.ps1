param([string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem

$source = Join-Path $RepoRoot 'AE2\documento\AE2_Necesidad_analitica_Titanic_Santiago_Andres_Valencia_Duque.docx'
$outDir = Join-Path $RepoRoot 'AE3\documento'
$target = Join-Path $outDir 'AE3_Transformacion_Titanic_Santiago_Andres_Valencia_Duque.docx'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
Copy-Item -LiteralPath $source -Destination $target -Force

function Escape-Xml([string]$Text) { [System.Security.SecurityElement]::Escape($Text) }
function Paragraph([string]$Text, [string]$Style = 'Normal', [bool]$BreakBefore = $false) {
    $escaped = Escape-Xml $Text
    $break = if ($BreakBefore) { '<w:pageBreakBefore/>' } else { '' }
    return "<w:p><w:pPr><w:pStyle w:val=`"$Style`"/>$break</w:pPr><w:r><w:t xml:space=`"preserve`">$escaped</w:t></w:r></w:p>"
}
function Table([string[]]$Headers, [object[][]]$Rows) {
    $xml = '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblBorders><w:top w:val="single" w:sz="4" w:color="D9D9D9"/><w:left w:val="single" w:sz="4" w:color="D9D9D9"/><w:bottom w:val="single" w:sz="4" w:color="D9D9D9"/><w:right w:val="single" w:sz="4" w:color="D9D9D9"/><w:insideH w:val="single" w:sz="4" w:color="D9D9D9"/><w:insideV w:val="single" w:sz="4" w:color="D9D9D9"/></w:tblBorders></w:tblPr>'
    $xml += '<w:tr><w:trPr><w:tblHeader/></w:trPr>'
    foreach ($h in $Headers) { $xml += '<w:tc><w:tcPr><w:shd w:fill="1F4E78"/></w:tcPr><w:p><w:r><w:rPr><w:b/><w:color w:val="FFFFFF"/></w:rPr><w:t>' + (Escape-Xml $h) + '</w:t></w:r></w:p></w:tc>' }
    $xml += '</w:tr>'
    foreach ($row in $Rows) {
        $xml += '<w:tr>'
        foreach ($v in $row) { $xml += '<w:tc><w:tcPr><w:vAlign w:val="center"/></w:tcPr><w:p><w:r><w:t>' + (Escape-Xml ([string]$v)) + '</w:t></w:r></w:p></w:tc>' }
        $xml += '</w:tr>'
    }
    return $xml + '</w:tbl>'
}

$body = @()
$body += Paragraph 'Transformación y enriquecimiento del dataset Titanic' 'Title'
$body += Paragraph 'Avance de la etapa 3' 'Subtitle'
$body += Paragraph ''
$body += Paragraph 'Santiago Andres Valencia Duque'
$body += Paragraph 'Proyecto Integrado III Analítica de Datos'
$body += Paragraph 'Docente Andrés Felipe Callejas'
$body += Paragraph 'Institución Universitaria Digital de Antioquia'
$body += Paragraph 'Medellín 2026'
$body += Paragraph 'Contenido' 'Heading1' $true
$body += Table @('Sección','Contenido') @(
    @('1','Introducción'),@('2','Necesidad preguntas y alcance'),@('3','Metodología'),
    @('4','Diccionario actualizado'),@('5','Resultados y discusión'),
    @('6','Conclusiones del avance'),@('7','Referencias')
)
$body += Paragraph '1 Introducción' 'Heading1' $true
$body += Paragraph 'Este avance transforma y enriquece los registros de BIT/titanic-dataset para responder descriptivamente las preguntas definidas en AE2. El proceso conserva 891 pasajeros, genera variables interpretables y produce tablas reutilizables para la visualización de AE4. La tasa total observada fue 38,38 %, con diferencias por clase, sexo, edad y puerto que se interpretan como asociaciones dentro del dataset.'
$body += Paragraph '2 Necesidad preguntas y alcance' 'Heading1'
$body += Paragraph 'Un equipo académico que prepara material sobre seguridad marítima necesita describir cómo se distribuyó la supervivencia entre grupos de pasajeros. La pregunta compuesta de AE2 se dividió en cinco preguntas operativas para obtener una tabla por resultado, sin cambiar la necesidad ni las variables centrales.'
$body += Table @('Pregunta','Variables','Resultado') @(
    @('Supervivencia total','sobrevivio','Conteos y tasa total'),
    @('Supervivencia por clase','sobrevivio, clase_pasajero','Conteos y tasa por clase'),
    @('Supervivencia por sexo','sobrevivio, sexo','Conteos y tasa por sexo'),
    @('Supervivencia por edad','sobrevivio, edad','Conteos y tasa por grupo de edad'),
    @('Supervivencia por puerto','sobrevivio, ciudad_embarque','Conteos y tasa por puerto')
)
$body += Paragraph 'La tarifa se conserva en el dataset preparado y en las estadísticas descriptivas, pero no se formuló como pregunta principal porque AE2 la definió como complementaria y su unidad monetaria no está documentada. El análisis es descriptivo: no prueba causas ni generaliza a otras poblaciones.'
$body += Paragraph '3 Metodología' 'Heading1'
$body += Paragraph 'El archivo AE1/resultados/titanic_transformado.csv funciona como entrada local reproducible del mismo dataset y split usados en AE2. Se conservó una copia sin modificar. Después se corrigieron tipos, se validaron los dominios de supervivencia y clase, y se comprobó que no hubiera edades ni tarifas negativas.'
$body += Paragraph 'Calidad y tratamiento de faltantes' 'Heading2'
$body += Paragraph 'Las etiquetas de sexo se normalizaron al español. Los 177 valores faltantes de edad permanecieron nulos en edad y se clasificaron como Edad no registrada en la variable derivada. Los dos puertos faltantes se convirtieron en No registrado para mantenerlos en las agrupaciones. No se eliminaron filas ni se imputaron valores numéricos.'
$body += Paragraph 'Se detectaron 120 filas coincidentes en las seis variables disponibles. No se eliminaron porque el archivo no contiene un identificador de pasajero y la coincidencia de atributos no demuestra que dos filas representen a la misma persona. Esta decisión conserva los conteos del dataset original.'
$body += Paragraph 'Enriquecimiento' 'Heading2'
$body += Paragraph 'Se añadieron estado_supervivencia, clase y grupo_edad. Los intervalos de edad son 0 a 12, 13 a 17, 18 a 29, 30 a 44, 45 a 59 y 60 o más, además de Edad no registrada. Para cada pregunta se calcularon pasajeros, sobrevivientes, no sobrevivientes, tasa de supervivencia y participación sobre el total.'
$body += Table @('Control','Antes','Después','Decisión') @(
    @('Filas','891','891','No se eliminaron registros'),
    @('Columnas','6','9','Se añadieron 3 variables'),
    @('Edad nula','177','177 en edad','Categoría derivada explícita'),
    @('Puerto nulo','2','0','Categoría No registrado'),
    @('Coincidencias completas','120','120','No se asumieron duplicados')
)
$body += Paragraph '4 Diccionario actualizado' 'Heading1' $true
$body += Table @('Variable','Significado','Tipo','Unidad o escala') @(
    @('sobrevivio','Indicador de supervivencia','entero','0 o 1'),
    @('clase_pasajero','Clase codificada','entero','1 a 3'),
    @('sexo','Sexo registrado normalizado','texto','Hombre o Mujer'),
    @('edad','Edad registrada','decimal','Años'),
    @('tarifa','Tarifa registrada','decimal','Unidad monetaria no indicada'),
    @('ciudad_embarque','Puerto o ciudad de embarque','texto','Categoría'),
    @('estado_supervivencia','Etiqueta del indicador','texto','Sobrevivió o No sobrevivió'),
    @('clase','Etiqueta de la clase','texto','Primera, Segunda o Tercera'),
    @('grupo_edad','Intervalo derivado de edad','texto','Categoría etaria')
)
$body += Paragraph '5 Resultados y discusión' 'Heading1' $true
$body += Paragraph 'Supervivencia total' 'Heading2'
$body += Table @('Grupo','Pasajeros','Sobrevivientes','No sobrevivientes','Tasa %') @(@('Total','891','342','549','38,38'))
$body += Paragraph 'Sobrevivieron 342 de los 891 pasajeros registrados. Esta tasa sirve como referencia para las comparaciones entre grupos.'
$body += Paragraph 'Supervivencia por clase' 'Heading2'
$body += Table @('Clase','Pasajeros','Sobrevivientes','No sobrevivientes','Tasa %') @(@('Primera','216','136','80','62,96'),@('Segunda','184','87','97','47,28'),@('Tercera','491','119','372','24,24'))
$body += Paragraph 'La primera clase presentó la tasa más alta y la tercera la más baja. La tercera clase reunió el 55,11 % de los pasajeros. La comparación no demuestra que la clase haya causado el resultado.'
$body += Paragraph 'Supervivencia por sexo' 'Heading2'
$body += Table @('Sexo','Pasajeros','Sobrevivientes','No sobrevivientes','Tasa %') @(@('Hombre','577','109','468','18,89'),@('Mujer','314','233','81','74,20'))
$body += Paragraph 'La tasa observada entre las mujeres fue 55,31 puntos porcentuales mayor. Esta comparación no controla simultáneamente clase, edad u otras características.'
$body += Paragraph 'Supervivencia por grupo de edad' 'Heading2'
$body += Table @('Grupo','Pasajeros','Sobrevivientes','No sobrevivientes','Tasa %') @(@('0 a 12','69','40','29','57,97'),@('13 a 17','44','21','23','47,73'),@('18 a 29','271','95','176','35,06'),@('30 a 44','215','91','124','42,33'),@('45 a 59','89','36','53','40,45'),@('60 o más','26','7','19','26,92'),@('Edad no registrada','177','52','125','29,38'))
$body += Paragraph 'El grupo de 0 a 12 años tuvo la tasa más alta entre los intervalos con edad registrada. Los 177 registros sin edad representan 19,87 % del dataset y limitan la comparación etaria.'
$body += Paragraph 'Supervivencia por puerto' 'Heading2'
$body += Table @('Puerto','Pasajeros','Sobrevivientes','No sobrevivientes','Tasa %') @(@('Cherbourg','168','93','75','55,36'),@('Queenstown','77','30','47','38,96'),@('Southampton','644','217','427','33,70'),@('No registrado','2','2','0','100,00'))
$body += Paragraph 'Cherbourg presentó la tasa más alta entre los puertos registrados. Los dos casos sin puerto no constituyen un grupo suficiente para interpretar su tasa de 100 % como patrón.'
$body += Paragraph '6 Conclusiones del avance' 'Heading1'
$body += Paragraph 'El análisis permite conocer el tamaño y la dirección de las diferencias observadas. Primera clase, mujeres y pasajeros de 0 a 12 años registraron tasas superiores a la referencia total, mientras tercera clase y hombres registraron tasas menores. Southampton concentró la mayor cantidad de pasajeros, aunque Cherbourg presentó la mayor tasa entre los puertos documentados.'
$body += Paragraph 'Quedan sin resolver la procedencia original y el método de construcción del dataset, la identidad única de cada registro, la edad de 177 pasajeros y el efecto conjunto de las variables. AE4 podrá representar estas tablas gráficamente, pero deberá conservar las mismas advertencias y evitar afirmaciones causales.'
$body += Paragraph '7 Referencias' 'Heading1'
$body += Paragraph 'Beijing Institute of Technology. (s. f.). BIT/titanic-dataset. Hugging Face. https://huggingface.co/datasets/BIT/titanic-dataset'
$body += Paragraph 'Hugging Face. (s. f.). Datasets documentation. https://huggingface.co/docs/datasets/'
$body += Paragraph 'pandas development team. (2026). pandas documentation. https://pandas.pydata.org/docs/'

$settings = '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>'
$documentXml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + ($body -join '') + $settings + '</w:body></w:document>'

$temp = Join-Path ([IO.Path]::GetTempPath()) ('ae3-docx-' + [guid]::NewGuid())
New-Item -ItemType Directory -Force -Path $temp | Out-Null
[IO.Compression.ZipFile]::ExtractToDirectory($target, $temp)
[IO.File]::WriteAllText((Join-Path $temp 'word\document.xml'), $documentXml, [Text.UTF8Encoding]::new($false))
Remove-Item -LiteralPath $target -Force
$stream = [IO.File]::Open($target, [IO.FileMode]::CreateNew)
$archive = New-Object IO.Compression.ZipArchive($stream, [IO.Compression.ZipArchiveMode]::Create)
foreach ($file in Get-ChildItem -LiteralPath $temp -Recurse -File) {
    $relative = $file.FullName.Substring($temp.Length + 1).Replace('\', '/')
    $entry = $archive.CreateEntry($relative, [IO.Compression.CompressionLevel]::Optimal)
    $entryStream = $entry.Open()
    $sourceStream = [IO.File]::OpenRead($file.FullName)
    $sourceStream.CopyTo($entryStream)
    $sourceStream.Dispose()
    $entryStream.Dispose()
}
$archive.Dispose()
$stream.Dispose()
Remove-Item -LiteralPath $temp -Recurse -Force
Write-Output $target
