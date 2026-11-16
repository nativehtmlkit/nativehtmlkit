# PowerShell UI — state and layout

The optional `NativeHTMLKit.UI` module provides state, computed values, layout and controls using only public NativeHTMLKit SDK cmdlets. UI 0.1.1 is an early (pre-1.0) release: `Install-Module NativeHTMLKit.UI -Scope CurrentUser` (installs the `NativeHTMLKit` SDK as a dependency).

```powershell
Import-Module NativeHTMLKit.UI -ErrorAction Stop
$app = Start-NativeHTMLKitScript -Name 'Counter'
$ui = New-NHKUi -Title 'Counter' -Theme cobalt -Density compact
$count = New-NHKUiState -Value 0
$null = Add-NHKUiColumn -UI $ui -Content {
  $null = Add-NHKUiText -UI $ui -Bind $count
  $null = Add-NHKUiButton -UI $ui -Text 'Add 1' -Data $count -OnClick {
    param($eventObject,$state) $state.Set([int]$state.Value+1)
  }
}
try {
  $null = Start-NHKUi -UI $ui -Application $app
  Wait-NativeHTMLKit -Application $app -UntilShutdown
} finally {
  Stop-NHKUi -UI $ui
  Close-NativeHTMLKit -Application $app
}
```

Use the complete [PowerShell UI demo](https://github.com/nativehtmlkit/nativehtmlkit/blob/main/examples/powershell-ui/gallery.ps1) for all simple components, and use [PowerShell SDK reference](https://github.com/nativehtmlkit/nativehtmlkit-powershell/blob/main/docs/API.md) for file dialogs and advanced native actions.
