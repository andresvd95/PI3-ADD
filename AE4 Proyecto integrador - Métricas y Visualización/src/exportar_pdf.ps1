# Convierte el documento final de Word a PDF con Microsoft Word y actualiza
# la tabla de contenido y los indices de tablas y figuras.
# Uso (desde la raiz del repositorio):
#   powershell -ExecutionPolicy Bypass -File "<carpeta AE4>/src/exportar_pdf.ps1" "<carpeta AE4>/documento"
$ErrorActionPreference = 'Stop'
$carpeta = if ($args.Count -gt 0) { $args[0] } else { Join-Path (Split-Path -Parent $PSScriptRoot) 'documento' }
$docx = Get-ChildItem -LiteralPath $carpeta -Filter 'Proyecto_Integrado_III_*.docx' | Select-Object -First 1
if ($null -eq $docx) { throw "No se encontro el .docx. Ejecute primero generar_documento_final.py." }
$pdf = [System.IO.Path]::ChangeExtension($docx.FullName, '.pdf')

# Word COM no maneja bien rutas con tildes: se trabaja en una carpeta temporal.
$tmpDocx = "$env:PUBLIC\Documents\pi3_documento_final.docx"
$tmpPdf = "$env:PUBLIC\Documents\pi3_documento_final.pdf"
Copy-Item -LiteralPath $docx.FullName -Destination $tmpDocx -Force

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$word.AutomationSecurity = 3
$documento = $word.Documents.Open($tmpDocx, $false, $true)
$documento.Fields.Update() | Out-Null
foreach ($indice in $documento.TablesOfContents) { $indice.Update() }
$documento.ExportAsFixedFormat($tmpPdf, 17)
$documento.Close($false)
$word.Quit()

Copy-Item -LiteralPath $tmpPdf -Destination $pdf -Force
Remove-Item -LiteralPath $tmpDocx, $tmpPdf -ErrorAction SilentlyContinue
Write-Output "PDF generado: $pdf"
