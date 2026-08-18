# Lesson 7 — Script Structure, Error Handling, and Your First Automation Script

Everything from Lessons 1–6 comes together here. By the end of this one you'll have a template you can reuse for every automation script going forward.

## Comment-based help

A block comment at the very top of a script, in a specific format PowerShell recognizes, so `Get-Help ./your-script.ps1` works on your own scripts exactly like it does on built-in cmdlets:

```powershell
<#
.SYNOPSIS
    Reports the power state of every VM in a resource group.
.DESCRIPTION
    Connects to Azure, queries all VMs in the given resource group,
    and prints each VM's name and current power state.
.PARAMETER ResourceGroupName
    The resource group to query.
.EXAMPLE
    ./Get-VmPowerReport.ps1 -ResourceGroupName "rg-compute"
#>
```

## Script-level param()

Same concept as a function's `param()` block, but for the whole script — it becomes the script's command-line interface.

```powershell
param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName
)
```

## Error handling — try/catch/finally

PowerShell has two kinds of errors: **terminating** (stops execution, catchable) and **non-terminating** (prints a warning but keeps going, by default *not* caught by `try/catch`). Most Az cmdlet failures are non-terminating unless you force them to stop:

```powershell
try {
    $vms = Get-AzVM -ResourceGroupName $ResourceGroupName -ErrorAction Stop
}
catch {
    Write-Error "Failed to query resource group '$ResourceGroupName': $_"
    exit 1
}
finally {
    Write-Verbose "Query attempt finished."
}
```

`-ErrorAction Stop` is the important, easy-to-miss detail — without it, a failed Az cmdlet often just writes a red warning to the screen and lets the rest of the script run anyway, which is rarely what you want in something meant to run unattended.

## Write-Output vs. Write-Host vs. Write-Verbose vs. Write-Error

| Cmdlet | Use it for |
|---|---|
| `Write-Output` | The actual result — goes into the pipeline, can be captured or piped further. Default choice. |
| `Write-Host` | Console-only text, can't be redirected or captured — status messages meant purely for a human watching. |
| `Write-Verbose` | Extra detail, only shown when the script is run with `-Verbose`. Good for step-by-step tracing without cluttering normal output. |
| `Write-Error` | A non-terminating error message — use alongside `exit 1`, not instead of it, if the script should actually stop. |

## Exit codes

```powershell
exit 0   # success
exit 1   # failure
```

Doesn't matter for a script you run and read by eye. Matters the moment anything else — a CI pipeline, a scheduled task, another script — calls this one and needs to know whether it succeeded without parsing output text.

---

## Full worked example: `Get-VmPowerReport.ps1`

Built up in pieces, then shown whole.

**Piece 1 — the interface.** What does this script need to run, and what does it promise to do?

```powershell
<#
.SYNOPSIS
    Reports the power state of every VM in a resource group.
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName
)
```

**Piece 2 — confirm the session before doing anything else.** Don't let a script run five minutes of work only to fail on a missing login at the end.

```powershell
if (-not (Get-AzContext)) {
    Write-Error "Not connected to Azure. Run Connect-AzAccount first."
    exit 1
}
```

**Piece 3 — do the actual work, wrapped in error handling.**

```powershell
try {
    $vms = Get-AzVM -ResourceGroupName $ResourceGroupName -Status -ErrorAction Stop
}
catch {
    Write-Error "Could not query resource group '$ResourceGroupName': $_"
    exit 1
}
```

**Piece 4 — handle the empty case explicitly.** A script that silently prints nothing when a resource group has no VMs looks broken, even when it's working correctly.

```powershell
if ($vms.Count -eq 0) {
    Write-Output "No VMs found in resource group '$ResourceGroupName'."
    exit 0
}
```

**Piece 5 — the report itself, using the pipeline concepts from Lesson 3.**

```powershell
$vms |
    Select-Object Name, @{Name = "PowerState"; Expression = { $_.PowerState } } |
    Sort-Object Name |
    Format-Table -AutoSize
```

The `@{Name=...; Expression=...}` piece is a **calculated property** — `Select-Object` normally just picks existing properties by name, but this syntax lets you define a new column instead, here just aliasing `PowerState` for a cleaner table header. You'll see this pattern often once you start shaping output for readability.

**Whole script, assembled:**

```powershell
<#
.SYNOPSIS
    Reports the power state of every VM in a resource group.
.PARAMETER ResourceGroupName
    The resource group to query.
.EXAMPLE
    ./Get-VmPowerReport.ps1 -ResourceGroupName "rg-compute"
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName
)

if (-not (Get-AzContext)) {
    Write-Error "Not connected to Azure. Run Connect-AzAccount first."
    exit 1
}

try {
    $vms = Get-AzVM -ResourceGroupName $ResourceGroupName -Status -ErrorAction Stop
}
catch {
    Write-Error "Could not query resource group '$ResourceGroupName': $_"
    exit 1
}

if ($vms.Count -eq 0) {
    Write-Output "No VMs found in resource group '$ResourceGroupName'."
    exit 0
}

$vms |
    Select-Object Name, @{Name = "PowerState"; Expression = { $_.PowerState } } |
    Sort-Object Name |
    Format-Table -AutoSize
```

## Closing out a script — your checklist

- Run it against a real resource group and confirm the output matches the Portal/CLI.
- Confirm it doesn't error on an empty result — should print a clear message, not crash.
- No hardcoded subscription IDs, resource group names, or secrets — everything that changes between runs goes through `param()`.
- Comment-based help block at the top.
- Commit it once it does what it's supposed to.

## What's next

`GLOSSARY.md` in this folder has every term from all seven lessons in one place. From here, the weekly rhythm is the [weekend study guide](../powershell-weekend-study-guide.md) — same tools, applied to that week's Azure lab.
