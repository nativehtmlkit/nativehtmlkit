# CSV viewer: choose a CSV file with the native open dialog and show it as an HTML table (PowerShell).
#
# Teaches: Show-NativeHTMLKitFileDialog -Kind OpenFiles with -Filters, the result object
#          (cancelled, paths), waiting for a dialog inside a click callback (the SDK keeps pumping
#          host messages meanwhile), Import-Csv, and HtmlEncode for every cell.
# Run:     pwsh -File csv-viewer.ps1 [-Path data.csv]   (Windows PowerShell 5.1: powershell.exe -File csv-viewer.ps1)
# Guide:   docs/how-to/file-dialogs.md
param([string]$Path)
$ErrorActionPreference = 'Stop'
Import-Module NativeHTMLKit -ErrorAction Stop
$app = Start-NativeHTMLKitScript -Name 'CSV viewer'

$page = @'
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 14px sans-serif; margin: 0; padding: 16px; background: #f4f6fa; color: #1d2433; }
  .bar { display: flex; gap: 10px; align-items: center; margin-bottom: 10px; }
  button { padding: 6px 12px; }
  table { border-collapse: collapse; background: white; }
  th, td { border: 1px solid #d5dbe8; padding: 4px 8px; text-align: left; }
  th { background: #e9eef6; }
  #status { color: #5a6578; }
</style></head>
<body>
  <div class="bar"><button id="open">Open CSV...</button><strong id="name">No file</strong></div>
  <div id="table"></div>
  <p id="status" role="status">Choose a .csv file; the first 500 rows are shown.</p>
</body></html>
'@

function ConvertTo-HtmlText([string]$Text) { return [System.Net.WebUtility]::HtmlEncode($Text) }

function Show-Csv([string]$File) {
    try {
        $rows = @(Import-Csv -LiteralPath $File | Select-Object -First 500)
    } catch {
        Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text ('Cannot read the file: ' + $_.Exception.Message)
        return
    }
    $columns = @()
    if ($rows.Count -gt 0) { $columns = @($rows[0].PSObject.Properties.Name) }
    $html = New-Object System.Text.StringBuilder
    [void]$html.Append('<table><thead><tr>')
    foreach ($column in $columns) { [void]$html.Append('<th>' + (ConvertTo-HtmlText $column) + '</th>') }
    [void]$html.Append('</tr></thead><tbody>')
    foreach ($row in $rows) {
        [void]$html.Append('<tr>')
        foreach ($column in $columns) { [void]$html.Append('<td>' + (ConvertTo-HtmlText $row.$column) + '</td>') }
        [void]$html.Append('</tr>')
    }
    [void]$html.Append('</tbody></table>')
    Set-NativeHTMLKitDocumentHtml -Document $doc -Element table -Html $html.ToString()
    Set-NativeHTMLKitDocumentText -Document $doc -Element name -Text ([IO.Path]::GetFileName($File))
    Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text ("{0} rows, {1} columns" -f $rows.Count, $columns.Count)
}

try {
    $window = New-NativeHTMLKitWindow -Application $app -Title 'CSV viewer' -Width 820 -Height 600
    $doc = Open-NativeHTMLKitHtml -Window $window -Html $page
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element open -Callback {
        param($eventObject)
        try {
            $result = Show-NativeHTMLKitFileDialog -Window $window -Kind OpenFiles -Title 'Open a CSV file' `
                -Filters @(@{ name = 'CSV files'; extensions = @('csv') }, @{ name = 'All files'; extensions = @('*') })
        } catch {
            # For example in headless test mode, where native dialogs are unavailable.
            Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text ('The file dialog is not available: ' + $_.Exception.Message)
            return
        }
        if ($result.cancelled -or @($result.paths).Count -eq 0) {
            Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text 'Cancelled'
        } else {
            Show-Csv @($result.paths)[0]
        }
    }
    if ($Path) { Show-Csv ([IO.Path]::GetFullPath($Path)) }
    Set-NativeHTMLKitReady -Application $app
    Wait-NativeHTMLKit -Application $app -UntilShutdown
} finally {
    Close-NativeHTMLKit -Application $app
}
