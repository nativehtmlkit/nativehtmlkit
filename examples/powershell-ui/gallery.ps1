# NativeHTMLKit PowerShell UI gallery. Run: pwsh -File examples/powershell-ui/gallery.ps1
# Uses only public PowerShell UI and SDK functions; no Core/transport RPC directly.
$ErrorActionPreference = 'Stop'
Import-Module NativeHTMLKit.UI -ErrorAction Stop
$app = Start-NativeHTMLKitScript -Name 'NativeHTMLKit PowerShell UI Gallery'
$ui = New-NHKUi -Title 'PowerShell UI gallery' -Theme cobalt -Density compact -Width 900 -Height 720
$count = New-NHKUiState -Value 0
$name = New-NHKUiState -Value 'Developer'
$visible = New-NHKUiState -Value $true
$enabled = New-NHKUiState -Value $false
$choice = New-NHKUiState -Value 'cobalt'
$history = New-NHKUiState -Value @('Demo loaded')
$computed = New-NHKUiComputed -DependsOn @($count,$name) -Data @{Count=$count;Name=$name} -Compute {
    param($data) "$($data.Name.Value) clicked $($data.Count.Value) times"
}
$null = Add-NHKUiColumn -UI $ui -Content {
    $null = Add-NHKUiHeading -UI $ui -Text 'NativeHTMLKit PowerShell UI' -Level 1
    $null = Add-NHKUiText -UI $ui -Text 'Native UI components, layout and reactive state; no browser or JavaScript.'
    $null = Add-NHKUiRow -UI $ui -Content {
        $null = Add-NHKUiBadge -UI $ui -Text 'PowerShell 7 / Windows PowerShell 5.1'
        $null = Add-NHKUiBadge -UI $ui -Text 'Compact density'
    }
    $null = Add-NHKUiGrid -UI $ui -Content {
        $null = Add-NHKUiCard -UI $ui -Content {
            $null = Add-NHKUiHeading -UI $ui -Text 'State and events'
            $null = Add-NHKUiText -UI $ui -Bind $computed
            $null = Add-NHKUiButton -UI $ui -Text 'Increment' -Data @{Count=$count;History=$history} -OnClick {
                param($eventObject,$data)
                $data.Count.Set([int]$data.Count.Value + 1)
                $data.History.Set(@("Incremented to $($data.Count.Value)") + @($data.History.Value | Select-Object -First 7))
            }
            $null = Add-NHKUiButton -UI $ui -Text 'Reset' -Variant secondary -Data $count -OnClick {
                param($eventObject,$state) $state.Set(0)
            }
        }
        $null = Add-NHKUiCard -UI $ui -Content {
            $null = Add-NHKUiHeading -UI $ui -Text 'Inputs'
            $null = Add-NHKUiInput -UI $ui -Bind $name -Label 'Name'
            $null = Add-NHKUiCheckbox -UI $ui -Bind $enabled -Label 'Enable extra feature'
            $null = Add-NHKUiSelect -UI $ui -Bind $choice -Label 'Example choice' -Options @(
                @{Value='cobalt';Label='Cobalt'},@{Value='olive';Label='Olive'})
        }
        $null = Add-NHKUiCard -UI $ui -Content {
            $null = Add-NHKUiHeading -UI $ui -Text 'Conditional list'
            $null = Add-NHKUiCheckbox -UI $ui -Bind $visible -Label 'Show event history'
            $null = Add-NHKUiWhen -UI $ui -Bind $visible -Content {
                $null = Add-NHKUiTextList -UI $ui -Bind $history
            }
        }
    }
    $null = Add-NHKUiAlert -UI $ui -Text 'The SDK gallery covers native dialogs, bitmaps and extra windows.'
}
try {
    $null = Start-NHKUi -UI $ui -Application $app
    Wait-NativeHTMLKit -Application $app -UntilShutdown
} finally {
    Stop-NHKUi -UI $ui
    $computed.Dispose()
    Close-NativeHTMLKit -Application $app
}
