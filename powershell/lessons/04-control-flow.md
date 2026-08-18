# Lesson 4 — Control Flow

## if / elseif / else

```powershell
$vmCount = 3

if ($vmCount -eq 0) {
    Write-Output "No VMs found"
} elseif ($vmCount -gt 5) {
    Write-Output "More than expected — check for stragglers"
} else {
    Write-Output "$vmCount VMs found"
}
```

Comparison operators are words, not symbols — this trips up almost everyone coming from another language:

| Operator | Meaning |
|---|---|
| `-eq` | equals |
| `-ne` | not equals |
| `-gt` / `-lt` | greater than / less than |
| `-ge` / `-le` | greater or equal / less or equal |
| `-like` | wildcard string match (`"az104*"`) |
| `-match` | regex match |
| `-contains` | does a collection contain this value |

## switch

For checking one value against several possibilities, `switch` reads cleaner than a chain of `elseif`:

```powershell
switch ($vm.PowerState) {
    "VM running"      { Write-Output "Active" }
    "VM deallocated"  { Write-Output "Stopped — no compute charge" }
    "VM stopped"      { Write-Output "Stopped — still billing" }
    default           { Write-Output "Unknown state" }
}
```

## foreach (the keyword) vs. ForEach-Object (the cmdlet)

These look similar and do similar things, but they're not the same tool, and the distinction is worth being precise about:

- **`foreach`** is a language keyword. It loops over a collection that's already fully loaded in memory.
- **`ForEach-Object`** is a cmdlet, meant for the pipeline (see Lesson 3) — it processes one object at a time *as it flows through*, without needing the whole collection loaded first.

```powershell
# foreach — collection already in a variable
$vms = Get-AzVM
foreach ($vm in $vms) {
    Write-Output $vm.Name
}

# ForEach-Object — inside a pipeline
Get-AzVM | ForEach-Object { Write-Output $_.Name }
```

For small scripts against a handful of Azure resources, either works and the performance difference is irrelevant. Use `foreach` when you already have the data in a variable and want to act on it; use `ForEach-Object` when you're chaining it directly off another cmdlet's output.

## for and while

Less common in Azure automation scripts specifically, but standard tools:

```powershell
for ($i = 0; $i -lt 5; $i++) {
    Write-Output "Iteration $i"
}

$attempts = 0
while ($attempts -lt 3) {
    Write-Output "Attempt $attempts"
    $attempts++
}
```

## break and continue

```powershell
foreach ($vm in $vms) {
    if ($vm.ProvisioningState -eq "Failed") {
        continue    # skip this one, move to the next
    }
    if ($vm.Name -eq "critical-vm") {
        break       # stop the loop entirely
    }
    Write-Output $vm.Name
}
```

## What's next

Lesson 5 covers functions — how to package a piece of logic like the ones above so you can reuse it instead of retyping it.
