# Headless probe for one PowerShell example (used by scripts/test-examples.py; not an example itself).
#
# Usage: pwsh -NoProfile -File probe.ps1 EXAMPLE.ps1 [ARGS...]  with NHK_PROBE_SPEC=<spec.json> and
# NATIVEHTMLKIT_TEST_MODE=1 in the environment.
#
# The example runs unchanged (dot-sourced). Two global aliases redirect it through this probe:
# Start-NativeHTMLKitScript gets -ScriptPath of this probe (so the host re-runs the probe as the
# backend), and the first Wait-NativeHTMLKit call runs the scenario from the spec file against the
# live documents with public document commands (replace_control_range types into a control and
# fires a real input event; request_submit fires real invalid/submit events; get_html reads the DOM
# back), pumping events between steps. Then it requests an orderly quit and writes a JSON report.
# Headless mode has no pointer input: click handlers cannot be exercised here.
param([Parameter(Mandatory)][string]$Example, [Parameter(ValueFromRemainingArguments)][object[]]$Rest)
$ErrorActionPreference = 'Stop'
$global:NHKProbeWrapper = $PSCommandPath
$global:NHKProbeDone = $false
$global:NHKProbePumps = 0
$global:NHKProbeSpec = [IO.File]::ReadAllText($env:NHK_PROBE_SPEC) | ConvertFrom-Json

function global:Invoke-NHKProbeStart {
    [CmdletBinding()] param([string]$Name, [string]$AppId, [string]$Version, [string]$Icon, [string]$Instance,
        [int]$StartupTimeoutMilliseconds, [int]$ShutdownTimeoutMilliseconds, [int]$MaxWindows,
        [string[]]$ArgumentList, [string]$Diagnostics)
    $forward = @{}
    foreach ($key in $PSBoundParameters.Keys) { $forward[$key] = $PSBoundParameters[$key] }
    return (NativeHTMLKit\Start-NativeHTMLKitScript -ScriptPath $global:NHKProbeWrapper @forward)
}

function global:Get-NHKProbeDocuments {
    param($Application)
    $windows = @($Application.Windows.Values | Where-Object { -not $_.Closed -and $null -ne $_.Document } |
        Sort-Object { [int](($_.Id -replace '\D', '') + '0') })
    return ,$windows
}

function global:Invoke-NHKProbePump {
    param($Application, [int]$Milliseconds)
    $clock = [Diagnostics.Stopwatch]::StartNew()
    while ($clock.ElapsedMilliseconds -lt $Milliseconds -and -not $Application.ShutdownRequested) {
        $null = NativeHTMLKit\Wait-NativeHTMLKit -Application $Application -TimeoutMilliseconds 50
    }
}

function global:Resolve-NHKProbeTarget {
    param($Document, $Target)
    if ($null -ne $Target.PSObject.Properties['id']) { return [string]$Target.id }
    $found = NativeHTMLKit\Find-NativeHTMLKitElement -Document $Document -Selector $Target.selector
    $index = 0; if ($null -ne $Target.PSObject.Properties['index']) { $index = [int]$Target.index }
    $ids = @($found.ids)
    if ($index -ge $ids.Count) { throw "selector '$($Target.selector)' matched $($ids.Count) element(s) with an id" }
    return [string]$ids[$index]
}

function global:Get-NHKProbeDocument {
    param($Application, $Step)
    $windows = Get-NHKProbeDocuments $Application
    $index = 0; if ($null -ne $Step.PSObject.Properties['window'] -and $Step.window -ne 'any') { $index = [int]$Step.window }
    if ($index -ge $windows.Count) { throw "window $index does not exist ($($windows.Count) open)" }
    return $windows[$index].Document
}

function global:Get-NHKProbeHtml {
    param($Application, $Step)
    if ($null -eq $Step.PSObject.Properties['window'] -or $Step.window -eq 'any') {
        $parts = foreach ($w in (Get-NHKProbeDocuments $Application)) {
            [string](NativeHTMLKit\Invoke-NativeHTMLKitDocumentCommand -Document $w.Document -Operation get_html).html
        }
        return ($parts -join "`n")
    }
    $doc = Get-NHKProbeDocument $Application $Step
    return [string](NativeHTMLKit\Invoke-NativeHTMLKitDocumentCommand -Document $doc -Operation get_html).html
}

function global:Wait-NHKProbeCondition {
    param($Application, $Step, [scriptblock]$Check)
    $limit = 5000; if ($null -ne $Step.PSObject.Properties['timeout_ms']) { $limit = [int]$Step.timeout_ms }
    $clock = [Diagnostics.Stopwatch]::StartNew()
    while ($true) {
        if (& $Check) { return $true }
        if ($clock.ElapsedMilliseconds -gt $limit) { return $false }
        Invoke-NHKProbePump $Application 50
    }
}

function global:Invoke-NHKProbeStep {
    param($Application, $Step)
    $has = { param($name) $null -ne $Step.PSObject.Properties[$name] }
    if (& $has 'wait') { Invoke-NHKProbePump $Application ([int]$Step.wait); return 'waited' }
    if (& $has 'type') {
        $doc = Get-NHKProbeDocument $Application $Step
        $element = Resolve-NHKProbeTarget $doc $Step.target
        $current = NativeHTMLKit\Get-NativeHTMLKitValue -Document $doc -Element $element
        $null = NativeHTMLKit\Invoke-NativeHTMLKitDocumentCommand -Document $doc -Operation replace_control_range -Parameters @{
            element = $element; replacement = [string]$Step.type; start = 0; end = $current.Length; selection_mode = 'end' }
        Invoke-NHKProbePump $Application 100
        return "typed into $element"
    }
    if (& $has 'submit') {
        $doc = Get-NHKProbeDocument $Application $Step
        $form = Resolve-NHKProbeTarget $doc $Step.submit
        $p = @{ Document = $doc; Form = $form }
        if (& $has 'submitter') { $p.Submitter = Resolve-NHKProbeTarget $doc $Step.submitter }
        $result = NativeHTMLKit\Submit-NativeHTMLKitForm @p
        $expected = $true; if (& $has 'submitted') { $expected = [bool]$Step.submitted }
        Invoke-NHKProbePump $Application 100
        if ([bool]$result.submitted -ne $expected) { throw "request_submit $form returned submitted=$($result.submitted)" }
        return "submitted $form"
    }
    if (& $has 'command') {
        $doc = Get-NHKProbeDocument $Application $Step
        $fields = @{}
        if (& $has 'fields') { foreach ($p in $Step.fields.PSObject.Properties) { $fields[$p.Name] = $p.Value } }
        if (& $has 'target') { $fields.element = Resolve-NHKProbeTarget $doc $Step.target }
        $null = NativeHTMLKit\Invoke-NativeHTMLKitDocumentCommand -Document $doc -Operation $Step.command -Parameters $fields
        Invoke-NHKProbePump $Application 100
        return "command $($Step.command)"
    }
    if (& $has 'expect') {
        $text = [string]$Step.expect
        if (-not (Wait-NHKProbeCondition $Application $Step { (Get-NHKProbeHtml $Application $Step).Contains($text) })) { throw "expected text not found: $text" }
        return "found $text"
    }
    if (& $has 'expect_not') {
        $text = [string]$Step.expect_not
        if (-not (Wait-NHKProbeCondition $Application $Step { -not (Get-NHKProbeHtml $Application $Step).Contains($text) })) { throw "unexpected text present: $text" }
        return "absent $text"
    }
    if (& $has 'expect_windows') {
        $n = [int]$Step.expect_windows
        if (-not (Wait-NHKProbeCondition $Application $Step { (Get-NHKProbeDocuments $Application).Count -eq $n })) { throw "expected $n window(s)" }
        return "windows $n"
    }
    throw "unknown probe step: $($Step | ConvertTo-Json -Compress)"
}

function global:Invoke-NHKProbeScenario {
    param($Application)
    $report = [ordered]@{ ok = $true; steps = @(); error = $null; callback_failures = 0 }
    try {
        $settle = 800; if ($null -ne $global:NHKProbeSpec.PSObject.Properties['settle_ms']) { $settle = [int]$global:NHKProbeSpec.settle_ms }
        Invoke-NHKProbePump $Application $settle
        if ($null -ne $global:NHKProbeSpec.PSObject.Properties['steps']) {
            foreach ($step in @($global:NHKProbeSpec.steps)) {
                $detail = Invoke-NHKProbeStep $Application $step
                $report.steps += [ordered]@{ step = $step; ok = $true; detail = [string]$detail }
            }
        }
    } catch {
        $report.ok = $false
        $report.error = ($_ | Out-String)
    }
    $report.callback_failures = [int]$Application.CallbackFailures
    if ($report.callback_failures -gt 0) { $report.ok = $false }
    [IO.File]::WriteAllText($env:NHK_PROBE_SPEC + '.report.json', (ConvertTo-Json -InputObject $report -Depth 8))
    try { $null = NativeHTMLKit\Request-NativeHTMLKitQuit -Application $Application } catch { $null = $_ }
}

function global:Invoke-NHKProbeWait {
    [CmdletBinding(DefaultParameterSetName = 'Pump')]
    param([Parameter(Mandatory)]$Application,
          [Parameter(ParameterSetName = 'Pump')][int]$TimeoutMilliseconds = 100,
          [Parameter(ParameterSetName = 'Pump')][switch]$Once,
          [Parameter(ParameterSetName = 'Run')][switch]$UntilShutdown)
    # Apps with their own loop call Wait-NativeHTMLKit -TimeoutMilliseconds repeatedly; the spec's
    # start_after_pumps lets such a loop run a while before the scenario starts.
    $global:NHKProbePumps++
    $after = 1; if ($null -ne $global:NHKProbeSpec.PSObject.Properties['start_after_pumps']) { $after = [int]$global:NHKProbeSpec.start_after_pumps }
    if (-not $global:NHKProbeDone -and ($UntilShutdown -or $global:NHKProbePumps -ge $after)) {
        $global:NHKProbeDone = $true
        if (-not $Application.Ready) { NativeHTMLKit\Set-NativeHTMLKitReady -Application $Application }
        Invoke-NHKProbeScenario $Application
    }
    $forward = @{}
    foreach ($key in $PSBoundParameters.Keys) { $forward[$key] = $PSBoundParameters[$key] }
    return (NativeHTMLKit\Wait-NativeHTMLKit @forward)
}

Set-Alias -Name Start-NativeHTMLKitScript -Value Invoke-NHKProbeStart -Scope Global
Set-Alias -Name Wait-NativeHTMLKit -Value Invoke-NHKProbeWait -Scope Global
$global:NHKProbeExample = [IO.Path]::GetFullPath($Example)
# The example's own param() block (if any) receives the remaining arguments, as with pwsh -File.
$named = @{}; $positional = @()
for ($i = 0; $i -lt $Rest.Count; $i++) {
    $item = [string]$Rest[$i]
    if ($item -match '^-([A-Za-z][A-Za-z0-9]*)$') {
        if ($i + 1 -lt $Rest.Count -and ([string]$Rest[$i + 1]) -notmatch '^-[A-Za-z]') { $named[$Matches[1]] = $Rest[$i + 1]; $i++ }
        else { $named[$Matches[1]] = $true }
    } else { $positional += $Rest[$i] }
}
# Give the example its own $PSScriptRoot / $PSCommandPath, inserted after its param() block if any.
$source = [IO.File]::ReadAllText($global:NHKProbeExample)
$parsed = [System.Management.Automation.Language.Parser]::ParseInput($source, [ref]$null, [ref]$null)
$at = 0; if ($null -ne $parsed.ParamBlock) { $at = $parsed.ParamBlock.Extent.EndOffset }
$prologue = "`n`$PSScriptRoot = '" + ([IO.Path]::GetDirectoryName($global:NHKProbeExample) -replace "'", "''") +
    "'; `$PSCommandPath = '" + ($global:NHKProbeExample -replace "'", "''") + "'`n"
$source = $source.Substring(0, $at) + $prologue + $source.Substring($at)
. ([scriptblock]::Create($source)) @named @positional
