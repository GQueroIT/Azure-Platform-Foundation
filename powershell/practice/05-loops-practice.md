# Practice 05 - Loops and Repetition

## Goal

Scale from checking one resource to checking many.

## Local Practice

```powershell
$names = @("vm01", "vm02", "vm03")

foreach ($name in $names) {
    Write-Output "Checking $name"
}
```

Then perform the same task with `ForEach-Object`.

## Explain

Write one sentence explaining when you would choose:

- `foreach`
- `ForEach-Object`

## Azure Application

Retrieve every resource in one resource group.

Loop through them and print:

```text
Resource Name
Resource Type
Location
```

## Governance Drill

Loop through every resource and report whether `Service` exists as a tag.

Output should make missing tags obvious.

## Challenge

Count:

- total resources
- resources with Service tag
- resources missing Service tag

Do not modify missing tags yet.
