# Lesson 5 — Functions and Parameters

## Basic function

```powershell
function Get-VmSummary {
    param(
        [string]$ResourceGroupName
    )

    $vms = Get-AzVM -ResourceGroupName $ResourceGroupName
    foreach ($vm in $vms) {
        Write-Output "$($vm.Name): $($vm.ProvisioningState)"
    }
}
```

Call it like a built-in cmdlet:

```powershell
Get-VmSummary -ResourceGroupName "rg-compute"
```

Functions get named the same Verb-Noun way as real cmdlets — it's a convention, not a hard requirement, but sticking to it means your own functions read consistently with everything else in the language, and `Get-Verb` will tell you which verb actually fits what the function does.

## The param() block

`param()` at the top of a function (or a whole script — see Lesson 7) declares what it accepts, same idea as arguments in a Python `def`.

```powershell
function New-VmTag {
    param(
        [string]$Key,
        [string]$Value = "untagged",   # default value if not supplied
        [Parameter(Mandatory = $true)]
        [string]$ResourceId              # must be supplied or the function refuses to run
    )
    # ...
}
```

- Giving a parameter a default value makes it optional.
- `[Parameter(Mandatory = $true)]` makes PowerShell prompt for the value (or error out in a non-interactive script) if it's missing, instead of quietly running with a blank value — worth using on anything a script genuinely can't function without.
- `[string]` before the parameter name is a type constraint — PowerShell will reject a call that passes the wrong type, catching a mistake at the call site instead of somewhere deeper in the function.

## Return values

PowerShell doesn't require an explicit `return` the way Python does — anything not captured or suppressed gets written to the output pipeline automatically. `return` still works and is useful for exiting early:

```powershell
function Test-IsRunning {
    param([string]$VmName, [string]$ResourceGroupName)

    $vm = Get-AzVM -Name $VmName -ResourceGroupName $ResourceGroupName -Status
    if ($vm.PowerState -eq "VM running") {
        return $true
    }
    return $false
}
```

## Calling with named vs. positional parameters

```powershell
Get-VmSummary -ResourceGroupName "rg-compute"   # named — explicit, readable, order doesn't matter
Get-VmSummary "rg-compute"                       # positional — works if only one param, gets messy fast with more
```

Default to named parameters once a function takes more than one argument. It's the difference between a script that's self-documenting six months from now and one you have to re-derive from the function definition every time.

## Advanced functions — [CmdletBinding()]

Adding `[CmdletBinding()]` above `param()` turns a plain function into something that behaves like a real cmdlet — it gains support for common parameters like `-Verbose` and `-WhatIf` (the same `-WhatIf` pattern behind `az deployment group what-if`, if that's a familiar concept from the Bicep side).

```powershell
function Remove-OldSnapshot {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [Parameter(Mandatory = $true)]
        [string]$SnapshotName
    )

    if ($PSCmdlet.ShouldProcess($SnapshotName, "Remove snapshot")) {
        Remove-AzSnapshot -SnapshotName $SnapshotName -Force
    }
}
```

`SupportsShouldProcess` plus `ShouldProcess` is what gives a function real `-WhatIf` and `-Confirm` support — genuinely worth having on anything that deletes or modifies a resource, not just queries one.

## What's next

Lesson 6 covers connecting to Azure itself — authentication, context, and the Az and Microsoft Graph modules that everything from here on builds against.
