# Lesson 2 — Variables and Data Types

## Variables

Every variable starts with `$`. No `let`, `var`, or `const` — just the dollar sign and a name.

```powershell
$vmName = "az104-vm-01"
$vmCount = 3
$isRunning = $true
```

PowerShell is **dynamically typed** — you don't declare a type up front, it figures it out from the value. You can check what something is at any point:

```powershell
$vmName.GetType().Name    # -> String
$vmCount.GetType().Name   # -> Int32
```

## Common types you'll actually use

| Type | Example | Notes |
|---|---|---|
| String | `"az104-vm-01"` | Text. Double quotes allow interpolation (below), single quotes don't. |
| Int | `3` | Whole numbers. |
| Bool | `$true` / `$false` | Note the `$` — they're variables, not keywords, unlike most languages. |
| Array | `@("vm1", "vm2", "vm3")` | Ordered list of values. |
| Hashtable | `@{ Name = "vm1"; Size = "Standard_B2s" }` | Key-value pairs — the closest thing to a Python dict. |

## String interpolation

Double quotes let you drop a variable straight into a string. Single quotes treat everything literally.

```powershell
$env = "az104-training"
Write-Output "Deploying to $env"          # -> Deploying to az104-training
Write-Output 'Deploying to $env'          # -> Deploying to $env  (literal, not substituted)
```

For anything more complex than a bare variable name — a property, a method call, an expression — wrap it in `$()`:

```powershell
$vm = Get-AzVM -Name "az104-vm-01" -ResourceGroupName "rg-compute"
Write-Output "VM state: $($vm.ProvisioningState)"
```

## Arrays

```powershell
$vmNames = @("az104-vm-01", "az104-vm-02", "az104-vm-03")

$vmNames[0]              # -> az104-vm-01  (zero-indexed, same as Python)
$vmNames.Count            # -> 3
$vmNames += "az104-vm-04" # append — creates a new array under the hood, arrays are fixed-size
```

That last line matters: PowerShell arrays are fixed size. `+=` doesn't grow the array in place — it silently creates a new one and reassigns the variable. Fine for small automation scripts; worth knowing so it doesn't look like magic.

## Hashtables

```powershell
$vmConfig = @{
    Name         = "az104-vm-01"
    Size         = "Standard_B2s"
    ResourceGroup = "rg-compute"
}

$vmConfig.Name              # -> az104-vm-01
$vmConfig["ResourceGroup"]  # -> rg-compute  (bracket access also works)
```

You'll see hashtables constantly in Azure PowerShell — a lot of cmdlets accept a hashtable of tags or parameters instead of ten separate flags.

## What's next

Lesson 3 covers the pipeline and objects — the concept that makes PowerShell behave differently from every shell you've used before.
