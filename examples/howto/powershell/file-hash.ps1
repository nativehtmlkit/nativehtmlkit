# File hash: compute a file checksum in the background while the window stays responsive (PowerShell).
#
# Teaches: Start-NativeHTMLKitTask (an isolated runspace: pass plain data with -ArgumentList, never
#          SDK objects), -OnCompleted / -OnFailed callbacks that run on the owning runspace,
#          -TimeoutMilliseconds, Stop-NativeHTMLKitTask for Cancel, and enabling/disabling buttons.
# Run:     pwsh -File file-hash.ps1 [-Path FILE]  (Windows PowerShell 5.1: powershell.exe -File file-hash.ps1)
# Guide:   docs/how-to/background-work.md
param([string]$Path = '')
$ErrorActionPreference = 'Stop'
Import-Module NativeHTMLKit -ErrorAction Stop
$app = Start-NativeHTMLKitScript -Name 'File hash'

$page = @'
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 14px sans-serif; margin: 0; padding: 18px; background: #f4f6fa; color: #1d2433; }
  form { display: grid; grid-template-columns: auto 1fr; gap: 8px 10px; align-items: center; }
  input, select { padding: 6px; }
  .buttons { grid-column: 2; display: flex; gap: 8px; }
  button { padding: 6px 12px; }
  #hash { font: 13px monospace; word-break: break-all; background: white; padding: 8px; border-radius: 6px; min-height: 1.2em; }
</style></head>
<body>
  <h1>File hash</h1>
  <form id="job">
    <label for="path">File</label><input id="path" required placeholder="Full path of a file">
    <label for="algorithm">Algorithm</label>
    <select id="algorithm"><option>SHA256</option><option>SHA384</option><option>SHA512</option><option>MD5</option></select>
    <div class="buttons"><button id="start">Compute</button><button id="cancel" type="button" disabled>Cancel</button></div>
  </form>
  <p id="status" role="status">Ready.</p>
  <div id="hash"></div>
</body></html>
'@

# Runs in its own runspace with only the arguments it is given.
$hashJob = {
    param([string]$File, [string]$Algorithm)
    (Get-FileHash -LiteralPath $File -Algorithm $Algorithm).Hash
}

$job = [pscustomobject]@{ Task = $null; Started = $null }

function Set-Running([bool]$Running) {
    if ($Running) {
        Set-NativeHTMLKitDocumentAttribute -Document $doc -Element start -Name disabled -Value ''
        Set-NativeHTMLKitDocumentAttribute -Document $doc -Element cancel -Name disabled -Remove
    } else {
        Set-NativeHTMLKitDocumentAttribute -Document $doc -Element start -Name disabled -Remove
        Set-NativeHTMLKitDocumentAttribute -Document $doc -Element cancel -Name disabled -Value ''
    }
}

try {
    $window = New-NativeHTMLKitWindow -Application $app -Title 'File hash' -Width 620 -Height 380
    $doc = Open-NativeHTMLKitHtml -Window $window -Html $page
    if ($Path) { Set-NativeHTMLKitDocumentValue -Document $doc -Element path -Value ([IO.Path]::GetFullPath($Path)) }

    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type submit -Element job -Callback {
        param($eventObject)
        if ($null -ne $job.Task) { return }
        $file = (Get-NativeHTMLKitValue -Document $doc -Element path).Trim()
        $algorithm = Get-NativeHTMLKitValue -Document $doc -Element algorithm
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
            Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text 'That file does not exist.'
            return
        }
        Set-Running $true
        Set-NativeHTMLKitDocumentText -Document $doc -Element hash -Text ''
        Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text "Computing $algorithm..."
        $job.Started = [Diagnostics.Stopwatch]::StartNew()
        $job.Task = Start-NativeHTMLKitTask -Application $app -ScriptBlock $hashJob -ArgumentList @($file, $algorithm) `
            -TimeoutMilliseconds 600000 -OnCompleted {
                param($result)
                $job.Task = $null
                Set-Running $false
                Set-NativeHTMLKitDocumentText -Document $doc -Element hash -Text ([string]@($result)[0])
                Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text ("Done in {0:N2} s." -f $job.Started.Elapsed.TotalSeconds)
            } -OnFailed {
                param($failure)
                $job.Task = $null
                Set-Running $false
                $text = if ($failure -is [OperationCanceledException]) { 'Cancelled.' } else { 'Failed: ' + $failure.Message }
                Set-NativeHTMLKitDocumentText -Document $doc -Element status -Text $text
            }
    }
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type click -Element cancel -Callback {
        param($eventObject)
        if ($null -ne $job.Task) { Stop-NativeHTMLKitTask -Task $job.Task }
    }
    Set-NativeHTMLKitReady -Application $app
    Wait-NativeHTMLKit -Application $app -UntilShutdown
} finally {
    Close-NativeHTMLKit -Application $app
}
