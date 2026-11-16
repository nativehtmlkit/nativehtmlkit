# Sign-up form: native HTML validation plus a custom rule, then read the submitted values (PowerShell).
#
# Teaches: required/type/minlength constraints checked by the host, the set_custom_validity document
#          command (via Invoke-NativeHTMLKitDocumentCommand) for a rule HTML cannot express, the
#          "invalid" and "submit" events, Get-NativeHTMLKitFormData and Reset-NativeHTMLKitForm.
# Run:     pwsh -File signup-form.ps1        (Windows PowerShell 5.1: powershell.exe -File signup-form.ps1)
# Guide:   docs/how-to/forms.md
$ErrorActionPreference = 'Stop'
Import-Module NativeHTMLKit -ErrorAction Stop
$app = Start-NativeHTMLKitScript -Name 'Sign up'

$page = @'
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><style>
  body { font: 15px sans-serif; margin: 0; background: #f6f7fb; color: #1d2433; }
  main { max-width: 440px; margin: 0 auto; padding: 24px; }
  label { display: block; margin: 12px 0 4px; font-weight: 600; }
  input, select { width: 100%; box-sizing: border-box; padding: 8px; border: 1px solid #9aa6bf; border-radius: 6px; }
  input:invalid { border-color: #c0392b; }
  button { margin-top: 16px; padding: 9px 16px; border: 0; border-radius: 6px; background: #2f6fd0; color: white; }
  #problem { color: #b03224; min-height: 1.2em; }
  #result { margin-top: 16px; padding: 12px; background: #e8f3ea; border-radius: 6px; }
  #result:empty { display: none; }
</style></head>
<body><main>
  <h1>Create an account</h1>
  <form id="signup">
    <label for="email">E-mail</label>
    <input id="email" name="email" type="email" required>
    <label for="password">Password (at least 8 characters)</label>
    <input id="password" name="password" type="password" required minlength="8">
    <label for="confirm">Repeat password</label>
    <input id="confirm" name="confirm" type="password" required>
    <label for="plan">Plan</label>
    <select id="plan" name="plan"><option value="free">Free</option><option value="team">Team</option></select>
    <button id="create">Create account</button>
  </form>
  <p id="problem" role="alert"></p>
  <div id="result" role="status"></div>
</main></body></html>
'@

try {
    $window = New-NativeHTMLKitWindow -Application $app -Title 'Sign up' -Width 520 -Height 600
    $doc = Open-NativeHTMLKitHtml -Window $window -Html $page

    $checkPasswords = {
        param($eventObject)
        $same = (Get-NativeHTMLKitValue -Document $doc -Element password) -ceq (Get-NativeHTMLKitValue -Document $doc -Element confirm)
        $message = if ($same) { '' } else { 'The passwords do not match.' }
        $null = Invoke-NativeHTMLKitDocumentCommand -Document $doc -Operation set_custom_validity -Parameters @{ element = 'confirm'; message = $message }
    }
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type input -Element password -Callback $checkPasswords
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type input -Element confirm -Callback $checkPasswords

    # "invalid" is sent once per failing control when a submit is attempted; it does not bubble.
    # The host focuses the first failing control, so only that one is reported.
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type invalid -Callback {
        param($eventObject)
        if ((Get-NativeHTMLKitFocusedElement -Document $doc).element -ne $eventObject.element) { return }
        $validity = Invoke-NativeHTMLKitDocumentCommand -Document $doc -Operation get_validity -Parameters @{ element = $eventObject.element }
        Set-NativeHTMLKitDocumentText -Document $doc -Element problem -Text ("{0}: {1}" -f $eventObject.element, $validity.message)
    }

    # "submit" only arrives after every constraint, including the custom one, passed.
    $null = Register-NativeHTMLKitDocumentEvent -Document $doc -Type submit -Element signup -Callback {
        param($eventObject)
        $values = @{}
        foreach ($entry in @((Get-NativeHTMLKitFormData -Document $doc -Form signup).entries)) { $values[$entry.name] = $entry.value }
        Set-NativeHTMLKitDocumentText -Document $doc -Element problem -Text ''
        Set-NativeHTMLKitDocumentText -Document $doc -Element result -Text ("Welcome, {0}! Plan: {1}." -f $values.email, $values.plan)
        $null = Reset-NativeHTMLKitForm -Document $doc -Form signup
    }

    Set-NativeHTMLKitFocus -Document $doc -Element email
    Set-NativeHTMLKitReady -Application $app
    Wait-NativeHTMLKit -Application $app -UntilShutdown
} finally {
    Close-NativeHTMLKit -Application $app
}
