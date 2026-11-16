# Tutorial: a settings editor (PowerShell UI)

You will build **Settings**, a small editor for a JSON settings file with `NativeHTMLKit.UI`: bound inputs, live validation, an "Unsaved changes" badge, Save and Revert buttons, and a theme the app itself uses on the next start.

<!-- screenshot: tutorial-powershell-ui-settings -->

**Time:** about 25 minutes. **You need:** `NativeHTMLKit.UI` installed and the counter from [PowerShell UI in five minutes](../getting-started/powershell-ui.md) working. Final code: [`examples/tutorials/powershell-ui-settings/settings.ps1`](https://github.com/nativehtmlkit/nativehtmlkit/blob/main/examples/tutorials/powershell-ui-settings/settings.ps1).

## Step 1: a form bound to state

<!-- include: examples/tutorials/powershell-ui-settings/step1-form.ps1 -->
```powershell title="examples/tutorials/powershell-ui-settings/step1-form.ps1"
# Settings editor tutorial, step 1: a form whose controls are bound to UI state.
#
# Teaches: New-NHKUi, New-NHKUiState, two-way Add-NHKUiInput / Add-NHKUiSelect / Add-NHKUiCheckbox,
#          New-NHKUiComputed with explicit -DependsOn, Add-NHKUiText -Bind, Start-NHKUi / Stop-NHKUi.
# Run:     pwsh -File step1-form.ps1        (Windows PowerShell 5.1: powershell.exe -File step1-form.ps1)
# Guide:   docs/tutorials/powershell-ui-settings.md (step 1 of 2)
$ErrorActionPreference = 'Stop'
Import-Module NativeHTMLKit.UI -ErrorAction Stop
$app = Start-NativeHTMLKitScript -Name 'Settings'

$name = New-NHKUiState -Value 'Ada'
$email = New-NHKUiState -Value 'ada@example.org'
$theme = New-NHKUiState -Value 'cobalt'
$notify = New-NHKUiState -Value $true
$summary = New-NHKUiComputed -DependsOn @($name, $email, $theme, $notify) -Data @{ Name = $name; Email = $email; Theme = $theme; Notify = $notify } -Compute {
    param($s)
    $mail = if ($s.Notify.Value) { 'with e-mail notifications' } else { 'without notifications' }
    "$($s.Name.Value) <$($s.Email.Value)>, $($s.Theme.Value) theme, $mail"
}

$ui = New-NHKUi -Title 'Settings' -Theme cobalt -Density regular -Width 560 -Height 520
$null = Add-NHKUiColumn -UI $ui -Content {
    $null = Add-NHKUiHeading -UI $ui -Text 'Settings' -Level 1
    $null = Add-NHKUiCard -UI $ui -Content {
        $null = Add-NHKUiInput -UI $ui -Bind $name -Label 'Display name'
        $null = Add-NHKUiInput -UI $ui -Bind $email -Label 'E-mail' -Type email
        $null = Add-NHKUiSelect -UI $ui -Bind $theme -Label 'Theme' -Options @(
            @{ Value = 'cobalt'; Label = 'Cobalt' }, @{ Value = 'graphite'; Label = 'Graphite' }, @{ Value = 'daylight'; Label = 'Daylight' })
        $null = Add-NHKUiCheckbox -UI $ui -Bind $notify -Label 'Send me e-mail notifications'
    }
    $null = Add-NHKUiText -UI $ui -Bind $summary -Muted
}

try {
    $null = Start-NHKUi -UI $ui -Application $app
    Wait-NativeHTMLKit -Application $app -UntilShutdown
} finally {
    Stop-NHKUi -UI $ui
    $summary.Dispose()
    Close-NativeHTMLKit -Application $app
}
```
<!-- /include -->

Run `pwsh -File step1-form.ps1` and edit the fields: the summary below follows every change.

- Each `New-NHKUiState` holds one setting. `Add-NHKUiInput -Bind $name` is two-way; `-Type email` gives an e-mail field.
- `Add-NHKUiSelect -Options` takes hashtables with `Value` and `Label`. `Add-NHKUiCheckbox` binds a Boolean.
- `New-NHKUiComputed -DependsOn @(...)` lists its dependencies **explicitly** (PowerShell has no automatic dependency tracking), and receives `-Data` as its parameter.
- The summary contains `<` and `>` around the e-mail address; `Add-NHKUiText` always encodes text, so this is safe.

## Step 2: validate, save and revert

<!-- include: examples/tutorials/powershell-ui-settings/settings.ps1 -->
```powershell title="examples/tutorials/powershell-ui-settings/settings.ps1"
# Settings editor: edit, validate and save a JSON settings file with NativeHTMLKit.UI (tutorial final code).
#
# Teaches: loading initial state from a file, computed validation and "unsaved changes" states,
#          buttons with -Data, saving JSON atomically, Revert, an Add-NHKUiAlert status line, and
#          starting the UI in the theme the user saved.
# Run:     pwsh -File settings.ps1 [-Path settings.json]
#          (Windows PowerShell 5.1: powershell.exe -File settings.ps1; default file:
#          nativehtmlkit-settings.json in your application-data folder)
# Guide:   docs/tutorials/powershell-ui-settings.md (step 2 of 2)
param([string]$Path)
$ErrorActionPreference = 'Stop'
Import-Module NativeHTMLKit.UI -ErrorAction Stop
$app = Start-NativeHTMLKitScript -Name 'Settings'

if (-not $Path) { $Path = Join-Path ([Environment]::GetFolderPath('ApplicationData')) 'nativehtmlkit-settings.json' }
$Path = [IO.Path]::GetFullPath($Path)
$defaults = [ordered]@{ DisplayName = ''; Email = ''; Theme = 'cobalt'; RefreshSeconds = 60; Notifications = $false }
$themes = @('cobalt', 'graphite', 'daylight')

function Read-Settings {
    $result = [ordered]@{}
    foreach ($key in $defaults.Keys) { $result[$key] = $defaults[$key] }
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        $data = [IO.File]::ReadAllText($Path) | ConvertFrom-Json
        foreach ($key in $defaults.Keys) {
            if ($null -ne $data.PSObject.Properties[$key]) { $result[$key] = $data.$key }
        }
    }
    if ($themes -notcontains $result.Theme) { $result.Theme = 'cobalt' }
    return $result
}

function Get-Snapshot {
    # The values as they would be saved; also used to detect unsaved changes.
    return [ordered]@{ DisplayName = $name.Value.Trim(); Email = $email.Value.Trim(); Theme = $theme.Value
        RefreshSeconds = $interval.Value.Trim(); Notifications = [bool]$notify.Value }
}

function Save-Settings {
    $snapshot = Get-Snapshot
    $snapshot.RefreshSeconds = [int]$snapshot.RefreshSeconds
    $json = ConvertTo-Json -InputObject $snapshot
    $folder = [IO.Path]::GetDirectoryName($Path)
    if (-not (Test-Path -LiteralPath $folder)) { $null = New-Item -ItemType Directory -Path $folder }
    $temporary = Join-Path $folder ('.settings-' + [guid]::NewGuid().ToString('N') + '.tmp')
    [IO.File]::WriteAllText($temporary, $json, (New-Object Text.UTF8Encoding($false)))
    if (Test-Path -LiteralPath $Path) { [IO.File]::Replace($temporary, $Path, [NullString]::Value) } else { [IO.File]::Move($temporary, $Path) }
}

$loaded = Read-Settings
$name = New-NHKUiState -Value ([string]$loaded.DisplayName)
$email = New-NHKUiState -Value ([string]$loaded.Email)
$theme = New-NHKUiState -Value ([string]$loaded.Theme)
$interval = New-NHKUiState -Value ([string]$loaded.RefreshSeconds)
$notify = New-NHKUiState -Value ([bool]$loaded.Notifications)
$saved = New-NHKUiState -Value (ConvertTo-Json -InputObject (Get-Snapshot) -Compress)
$status = New-NHKUiState -Value "Editing $Path"
$all = @($name, $email, $theme, $interval, $notify, $saved)

$problem = New-NHKUiComputed -DependsOn $all -Compute {
    $s = Get-Snapshot
    $seconds = 0
    if ($s.DisplayName -eq '') { 'Enter a display name.' }
    elseif ($s.Email -notmatch '^[^@\s]+@[^@\s]+\.[^@\s]+$') { 'The e-mail address looks invalid.' }
    elseif (-not [int]::TryParse($s.RefreshSeconds, [ref]$seconds) -or $seconds -lt 5 -or $seconds -gt 3600) { 'Refresh interval must be a whole number from 5 to 3600.' }
    else { '' }
}
$changes = New-NHKUiComputed -DependsOn $all -Compute {
    if ((ConvertTo-Json -InputObject (Get-Snapshot) -Compress) -eq $saved.Value) { 'All changes saved' } else { 'Unsaved changes' }
}
$hasProblem = New-NHKUiComputed -DependsOn @($problem) -Compute { $problem.Value -ne '' }

$ui = New-NHKUi -Title 'Settings' -Theme $loaded.Theme -Density regular -Width 600 -Height 640
$null = Add-NHKUiColumn -UI $ui -Content {
    $null = Add-NHKUiRow -UI $ui -Content {
        $null = Add-NHKUiHeading -UI $ui -Text 'Settings' -Level 1
        $null = Add-NHKUiBadge -UI $ui -Bind $changes
    }
    $null = Add-NHKUiCard -UI $ui -Content {
        $null = Add-NHKUiInput -UI $ui -Bind $name -Label 'Display name'
        $null = Add-NHKUiInput -UI $ui -Bind $email -Label 'E-mail' -Type email
        $null = Add-NHKUiInput -UI $ui -Bind $interval -Label 'Refresh interval (seconds)' -Type number
        $null = Add-NHKUiSelect -UI $ui -Bind $theme -Label 'Theme (applies on next start)' -Options @(
            @{ Value = 'cobalt'; Label = 'Cobalt' }, @{ Value = 'graphite'; Label = 'Graphite' }, @{ Value = 'daylight'; Label = 'Daylight' })
        $null = Add-NHKUiCheckbox -UI $ui -Bind $notify -Label 'Send me e-mail notifications'
    }
    $null = Add-NHKUiWhen -UI $ui -Bind $hasProblem -Content {
        $null = Add-NHKUiText -UI $ui -Bind $problem
    }
    $null = Add-NHKUiRow -UI $ui -Content {
        $null = Add-NHKUiButton -UI $ui -Text 'Save' -OnClick {
            param($eventObject, $data)
            if ($problem.Value -ne '') { $status.Set('Fix the problem above before saving.'); return }
            try {
                Save-Settings
                $saved.Set((ConvertTo-Json -InputObject (Get-Snapshot) -Compress))
                $status.Set("Saved $(Get-Date -Format 'HH:mm:ss')")
            } catch {
                $status.Set('Could not save: ' + $_.Exception.Message)
            }
        }
        $null = Add-NHKUiButton -UI $ui -Text 'Revert' -Variant secondary -OnClick {
            param($eventObject, $data)
            $fresh = Read-Settings
            $name.Set([string]$fresh.DisplayName); $email.Set([string]$fresh.Email); $theme.Set([string]$fresh.Theme)
            $interval.Set([string]$fresh.RefreshSeconds); $notify.Set([bool]$fresh.Notifications)
            $status.Set('Reverted to the saved file')
        }
    }
    $null = Add-NHKUiAlert -UI $ui -Bind $status
}

try {
    $null = Start-NHKUi -UI $ui -Application $app
    Wait-NativeHTMLKit -Application $app -UntilShutdown
} finally {
    Stop-NHKUi -UI $ui
    foreach ($c in @($problem, $changes, $hasProblem)) { $c.Dispose() }
    Close-NativeHTMLKit -Application $app
}
```
<!-- /include -->

- `param([string]$Path)`: `pwsh -File settings.ps1 -Path ./my-settings.json`. Without it, the file is `nativehtmlkit-settings.json` in your application-data folder (`[Environment]::GetFolderPath('ApplicationData')`: `%APPDATA%` on Windows, `~/.config` on Linux).
- `Read-Settings` starts from defaults and copies known keys from the file, so a partial or older file still works.
- `Get-Snapshot` returns the values as they would be saved. Two computed values use it: `$problem` (a validation message or `''`) and `$changes`, which compares the snapshot with `$saved`, the JSON of the last saved state.
- `$hasProblem` is computed from `$problem` and drives `Add-NHKUiWhen`, which shows the message only when there is one.
- **Save** refuses to write while there is a problem, writes a temporary file and replaces the real one (`[IO.File]::Replace`, with `[NullString]::Value` for "no backup", since a plain `$null` would be passed as an empty string), then updates `$saved`, so the badge returns to "All changes saved".
- **Revert** reads the file again and sets every state; the bound inputs update themselves.
- `New-NHKUi -Theme $loaded.Theme`: the theme is chosen when the UI is built, so a changed theme applies on the next start.
- Button callbacks are script blocks defined in the script. They can call `Save-Settings` and read `$problem`, `$status` and the other states directly.

## What you learned

- Bind inputs, selects and checkboxes to states; derive values with explicit `-DependsOn`.
- Show validation messages with computed states and `Add-NHKUiWhen`.
- Save and reload a JSON file safely, and track unsaved changes.

## Where next

- [Theme the UI library](../how-to/theming-ui.md).
- [Native file dialogs](../how-to/file-dialogs.md): add "Save as..." with `Show-NativeHTMLKitFileDialog -Kind SaveFile`.
- [UI API reference](https://github.com/nativehtmlkit/nativehtmlkit_ui/blob/main/docs/API.md).
