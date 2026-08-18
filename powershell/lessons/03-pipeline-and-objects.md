# Lesson 3 — The Pipeline and Objects

This is the concept that makes PowerShell genuinely different from Bash or a raw CLI, and it's worth slowing down on.

## Cmdlet naming: Verb-Noun

Every built-in command follows **Verb-Noun**: `Get-AzVM`, `Set-AzVMSize`, `New-AzResourceGroup`, `Remove-AzVM`, `Start-AzVM`, `Stop-AzVM`. The verbs are a fixed, approved list (`Get-Verb` shows all of them), which means once you've learned the pattern, you can often *guess* the right cmdlet name for something you haven't used yet.

## Objects, not text

Run this in Bash and you get a block of plain text you'd have to parse with `grep`/`awk`/`cut` to pull one field out of. Run the PowerShell equivalent:

```powershell
Get-AzVM
```

and what comes back isn't text — it's a collection of full **objects**, each with named properties (`Name`, `ResourceGroupName`, `Location`, `ProvisioningState`, and dozens more). You don't parse anything. You just ask for the property you want:

```powershell
$vm = Get-AzVM -Name "az104-vm-01" -ResourceGroupName "rg-compute"
$vm.Name              # -> az104-vm-01
$vm.ProvisioningState # -> Succeeded
```

This is the single biggest mental shift coming from Python or Bash: PowerShell cmdlets return live data structures, not printed strings.

## Get-Member — seeing what an object actually contains

You rarely need to guess what properties exist. Pipe anything into `Get-Member` and it lists every property and method:

```powershell
Get-AzVM -Name "az104-vm-01" -ResourceGroupName "rg-compute" | Get-Member
```

This is how you discover `.ProvisioningState`, `.HardwareProfile.VmSize`, and everything else — not by memorizing a reference, by asking the object directly.

## The pipeline: `|`

The pipe character passes the *output object* of one cmdlet in as the *input* to the next. This is how you filter, sort, and transform without ever writing a loop by hand.

```powershell
Get-AzVM | Where-Object { $_.PowerState -eq "VM running" }
```

`$_` means "the current object flowing through the pipeline, right now." `Where-Object` runs its script block once per object and keeps only the ones where the block returns `$true`.

## The core filtering/shaping cmdlets

| Cmdlet | What it does |
|---|---|
| `Where-Object` | Filters — keeps objects matching a condition. |
| `Select-Object` | Picks specific properties, or the first/last N objects. |
| `Sort-Object` | Sorts by a property. |
| `ForEach-Object` | Runs a script block once per object in the pipeline — for side effects, not filtering. |

```powershell
Get-AzVM |
    Where-Object { $_.Location -eq "eastus" } |
    Select-Object Name, ResourceGroupName, ProvisioningState |
    Sort-Object Name
```

Read that as a sentence: get every VM, keep only the ones in East US, show just three fields, sort by name. Each stage only has to think about the one thing it does — that's the actual value of the pipeline over one dense line of code.

## What's next

Lesson 4 covers control flow — `if`, loops, and the important distinction between the `foreach` keyword and the `ForEach-Object` cmdlet you just saw above.
