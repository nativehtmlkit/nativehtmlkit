# Hello, NativeHTMLKit.UI: a reactive counter in PowerShell.
#
# Teaches: New-NHKUi, New-NHKUiState, Add-NHKUiText -Bind, Add-NHKUiButton -Data/-OnClick,
#          Start-NHKUi and Stop-NHKUi.
# Run:     pwsh -File hello-ui.ps1        (Windows PowerShell 5.1: powershell.exe -File hello-ui.ps1)
# Guide:   docs/getting-started/powershell-ui.md
$ErrorActionPreference = 'Stop'
Import-Module NativeHTMLKit.UI -ErrorAction Stop   # also loads the NativeHTMLKit SDK
$app = Start-NativeHTMLKitScript -Name 'Counter'

$count = New-NHKUiState -Value 0
$label = New-NHKUiComputed -DependsOn @($count) -Data $count -Compute { param($c) "Count: $($c.Value)" }
$ui = New-NHKUi -Title 'Counter' -Theme cobalt -Density regular -Width 420 -Height 300
$null = Add-NHKUiColumn -UI $ui -Content {
    $null = Add-NHKUiHeading -UI $ui -Text 'Counter' -Level 1
    $null = Add-NHKUiText -UI $ui -Bind $label
    $null = Add-NHKUiRow -UI $ui -Content {
        $null = Add-NHKUiButton -UI $ui -Text '+1' -Data $count -OnClick { param($eventObject, $state) $state.Set([int]$state.Value + 1) }
        $null = Add-NHKUiButton -UI $ui -Text 'Reset' -Variant secondary -Data $count -OnClick { param($eventObject, $state) $state.Set(0) }
    }
}

try {
    $null = Start-NHKUi -UI $ui -Application $app   # opens the window and announces ready
    Wait-NativeHTMLKit -Application $app -UntilShutdown
} finally {
    Stop-NHKUi -UI $ui
    $label.Dispose()
    Close-NativeHTMLKit -Application $app
}
