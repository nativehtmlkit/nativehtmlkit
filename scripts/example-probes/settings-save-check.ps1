# Checks the Save-Settings / Read-Settings functions of the settings tutorial outside the UI (a
# click cannot be simulated headlessly). Loads only the function definitions from the example.
param([Parameter(Mandatory)][string]$Example, [Parameter(Mandatory)][string]$Folder)
$ErrorActionPreference = 'Stop'
$ast = [System.Management.Automation.Language.Parser]::ParseFile($Example, [ref]$null, [ref]$null)
foreach ($fn in $ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $true)) {
    . ([scriptblock]::Create($fn.Extent.Text))
}
$Path = Join-Path $Folder 'sub/settings.json'
$defaults = [ordered]@{ DisplayName = ''; Email = ''; Theme = 'cobalt'; RefreshSeconds = 60; Notifications = $false }
$themes = @('cobalt', 'graphite', 'daylight')
function New-FakeState($Value) { [pscustomobject]@{ Value = $Value } }
$name = New-FakeState ' Ada '; $email = New-FakeState 'ada@example.org'; $theme = New-FakeState 'daylight'
$interval = New-FakeState '30'; $notify = New-FakeState $true
Save-Settings          # creates the folder and the file
$name.Value = 'Grace'
Save-Settings          # replaces the existing file
$back = Read-Settings
$leftovers = @(Get-ChildItem -LiteralPath (Split-Path $Path) -Force | Where-Object { $_.Name -ne 'settings.json' })
if ($back.DisplayName -ne 'Grace' -or $back.RefreshSeconds -ne 30 -or $back.Theme -ne 'daylight' -or -not $back.Notifications -or $leftovers.Count) {
    throw ("unexpected result: " + ($back | ConvertTo-Json -Compress) + " leftovers=" + $leftovers.Count)
}
'OK'
